import uproot
import hadd
import numpy as np
import awkward as ak
def merge_files(destination, file1, file2, step_size="100MB"): #hadd includes
    """
    Args:
        destination (path-like): Name of the output file or file path.
        files (Str or list of str): List of local ROOT files to read histograms from.
            May contain glob patterns.
        step_size (int or str): should be >100 kB
        force (bool): If True, overwrites destination file if it exists. Force and append
            cannot both be True.
        append (bool): If True, appends histograms to an existing file. Force and append
            cannot both be True.
        compression (str): Sets compression level for root file to write to. Can be one of
            "ZLIB", "LZMA", "LZ4", or "ZSTD". By default the compression algorithm is "LZ4".
        compression_level (int): Use a compression level particular to the chosen compressor.
            By default the compression level is 1.
        skip_bad_files (bool): If True, skips corrupt or non-existent files without exiting.
        max_opened_files (int): Limits the number of files to be open at the same time. If 0,
            this gets set to system limit.
        union (bool): If True, adds the histograms that have the same name and copies all others
            to the new file.
        same_names (bool): If True, only adds together histograms which have the same name (key). If False,
            histograms are added together based on TTree structure (bins must be equal).

    Adds together histograms from local ROOT files of a collection of ROOT files, and writes them to
        a new or existing ROOT file.

        >>> odapt.add_histograms("destination.root", ["file1_to_hadd.root", "file2_to_hadd.root"])

    """
    # Use tmpdir? Or just do two at a time, tree reduction style...
    import tempfile

    f1 = uproot.open(file1)
    f2 = uproot.open(file2)
    #title must be the same as the file name? maybe is just a tChain thing

    out_file = uproot.recreate(destination)

    t1_keys = f1.keys(recursive=False, cycle=False)
    t2_keys = f2.keys(recursive=False, cycle=False)

    shared_keys = np.intersect1d(t1_keys, t2_keys)
    missing_keys = np.setdiff1d(t1_keys, shared_keys)
    additional_keys = np.setdiff1d(t2_keys, shared_keys)

    for key in shared_keys:
        # print("Shared keys!", out_file.keys())
        if isinstance(f1[key], uproot.TTree) and isinstance(f2[key], uproot.TTree):
            try:
                f1[key].name
                f2[key].name
            except uproot.KeyInFileError:
                raise uproot.KeyInFileError
            if f1[key].name != f2[key].name:
                print("Names must be the same")
            recur_merge(destination, out_file, f1[key], f2[key], step_size)
            # finally: 
            # Write just f1 to file???
            # msg = "Files must have similar structure."
            # raise ValueError(msg) from None
        
        elif f1[key].classname.startswith("TH") or f1[key].classname.startswith("TProfile"):
            import tempfile

            if len(file[key].axes) == 1:
                #Make temp, add them together...then write to out_file
                fp = tempfile.TemporaryFile()
                out_file[key] = hadd.hadd_1d(file1, f2[key], key, True)

            elif len(file[key].axes) == 2:
                out_file[key] = hadd.hadd_2d(file1, f2[key], key, True)

            else:
                out_file[key] = hadd.hadd_3d(file1, f2[key], key, True)
            

            # hadd.hadd_merge(destination, f1, key, first=True, n_key=None) #tree1? does it need to be a file?
        else:
            first = True
            for chunk in uproot.iterate(f1[key]):
                if first:
                    first = False
                    out_file[key] = chunk
                else:
                    out_file[key].extend(chunk)

    for key in missing_keys:
        print("Missing keys", missing_keys)
        # print("outfile: ", out_file.keys(recursive=False))
        if isinstance(f1[key], uproot.TTree):
            tree = f1[key]
            branches = tree.branches 
            dtypes = []
            # print(branches)
            for i in branches:
                if isinstance(i.interpretation, uproot.AsJagged):
                    dtypes.append(i.interpretation.content.numpy_dtype)
                else:
                    dtypes.append(i.interpretation.numpy_dtype)

            nametypes = {branches[i].name : dtypes[i] for i, value in enumerate(branches)}
            out_file.mktree(tree.name, branch_types=nametypes)
            
            recur_copy(destination, out_file, f1[key], step_size)
            # # print("line 102:", out_file.keys(recursive=False))
            # first = True
            # for branch in branches:
            #     first = True
            #     for chunk in branch.iterate(step_size=step_size, how=dict):
            #         if first:
            #             first = False
            #             out_file[branch.name] = chunk
            #         else: 
            #             out_file[branch.name].extend(chunk)

        elif f1[key].classname.startswith("TH") or f1[key].classname.startswith("TProfile"):
            print("Histogram")
            if len(f1[key].axes) == 1:
                out_file[key] = hadd.hadd_1d(destination, f1, key, True)

            elif len(f1[key].axes) == 2:
                out_file[key] = hadd.hadd_2d(destination, f1, key, True)

            else:
                out_file[key] = hadd.hadd_3d(destination, f1, key, True)
        
        else:
            first = True
            for i in uproot.TBranch.iterate(tree[key], step_size=step_size, how=dict):
                if first:
                    first = False
                    out_file[key] = i
                out_file[key].extend(i)
    for key in additional_keys:
        # print("Additional keys", additional_keys)
        # print("outfile in additional keys:", out_file.keys(recursive=False))
        if isinstance(f2[key], uproot.TTree):
            tree = f2[key]
            branches = tree.branches 
            dtypes = []
            # print(branches)
            for i in branches:
                if isinstance(i.interpretation, uproot.AsJagged):
                    dtypes.append(i.interpretation.content.numpy_dtype)
                else:
                    dtypes.append(i.interpretation.numpy_dtype)

            nametypes = {branches[i].name : dtypes[i] for i, value in enumerate(branches)}
            out_file.mktree(tree.name, branch_types=nametypes)
            recur_copy(destination, out_file, f2[key], step_size)

        elif f2[key].classname.startswith("TH") or f2[key].classname.startswith("TProfile"):
            print("histogram")
            if len(f2[key].axes) == 1:
                h_sum = hadd.hadd_1d(destination, f2, key, True)

            elif len(f2[key].axes) == 2:
                h_sum = hadd.hadd_2d(destination, f2, key, True)

            else:
                h_sum = hadd.hadd_3d(destination, f2, key, True)

            out_file[key] = h_sum
        else:
            first = True
            for i in uproot.TBranch.iterate(tree[key], step_size=step_size, how=dict):
                if first:
                    first = False
                    out_file[key] = i
                out_file[key].extend(i)
        # write...
    #   read key - get get class name
    #   inputs(?) = tlist()
    #   if isTree:
    #       obj = obj.CloneTree?
    #       branches = obj.branches
    #   for f2 in files[1:]:
    #       other_obj = f2.getListOfKeys().readObj()
    #       inputs.Add(other_obj)

def recur_copy(destination, out_file, tree, step_size):
    keys = tree.keys(recursive=False) #since cycle was false for the tree the first time, may break/be unnecessary here
    print(keys)
    for key in keys:
        if isinstance(tree[key], uproot.TTree):
            print("ttree")
            sub_tree = tree[key]
            branches = sub_tree.branches 
            dtypes = []
            for i in branches:
                if isinstance(i.interpretation, uproot.AsJagged):
                    dtypes.append(i.interpretation.content.numpy_dtype)
                else:
                    dtypes.append(i.interpretation.numpy_dtype)

            nametypes = {branches[i].name : dtypes[i] for i, value in enumerate(branches)}
            out_file[tree.name].mktree(sub_tree.name, branch_types=nametypes)

            for branch in branches: # use keys instead for calling recursive function
                if isinstance(branch.classname, uproot.TTree):
                    recur_copy(destination, out_file, branch, step_size)
                else:
                    first = True
                    for chunk in branch.iterate(step_size=step_size, how=dict):
                        if first:
                            first = False
                            out_file[tree.name][branch.name] = chunk
                        else: 
                            out_file[tree.name][branch.name].extend(chunk)

        elif tree[key].classname.startswith("TH") or tree[key].classname.startswith("TProfile"):
            print("histogram")
            if len(file[key].axes) == 1:
                h_sum = hadd.hadd_1d(destination, tree, key, True)

            elif len(file[key].axes) == 2:
                h_sum = hadd.hadd_2d(destination, tree, key, True)

            else:
                h_sum = hadd.hadd_3d(destination, tree, key, True)

            out_file[key] = h_sum
        else:
            first = True
            for i in uproot.TBranch.iterate(tree[key], step_size=step_size, how=dict):
                if first:
                    first = False
                    out_file[tree.name] = i
                out_file[tree.name].extend(i)

def recur_merge(out_file, tree1, tree2, key, step_size): 
    print("Recur")
    t1_keys = tree1.keys(recursive=False)

    t2_keys = tree2.keys(recursive=False)
    
    shared_keys = np.intersect1d(t1_keys, t2_keys)
    missing_keys = np.setdiff1d(t1_keys, shared_keys)
    additional_keys = np.setdiff1d(t2_keys, shared_keys)
    # out_file.mktree(tree1.name, tree1.typenames(recursive=False)) #will tree typenames be the same? Don't think so...
    # get keys for branches? for hadd
    for key in shared_keys:
        classname = tree1.classname
        if isinstance(classname, uproot.TTree) and isinstance(tree2.class_name(), uproot.TTree):
            if tree1.name == tree2.name:
                # Iterate here?
                # Need Union of Tbaskets or something...?
                out_file[key][tree1.name] = tree1
        # elif isinstance(f[key], uproot.histogram)
        elif classname.startswith("TH") or classname.startswith("TProfile"):
            if len(file[key].axes) == 1:
                out_file[key] = hadd.hadd_1d(file1, tree2[key], key, False)

            elif len(file[key].axes) == 2:
                out_file[key] = hadd.hadd_2d(file1, tree2[key], key, False)

            else:
                out_file[key] = hadd.hadd_3d(file1, tree2[key], key, False)
            
        else:
            # print(tree1[key].typenames(recursive=False))
            first = True
            for i in uproot.TBranch.iterate(tree1[key], step_size=step_size, how=dict):
                if first:
                    first = False
                    out_file[key] = i
                out_file[key].extend(i)

    for key in missing_keys:
        if isinstance(tree1[key], uproot.TTree):
            tree = tree1[key]
            in_keys = tree.keys(recursive=False)
            out_file.mktree(tree.name, tree.typenames(recursive=False))
            out_file[key].extend({in_key: i for i in uproot.iterate(tree[missing_keys], step_size=step_size)})
            for chunk in tree[in_key].iterate(step_size=step_size):
                print("chunk")

    for key in additional_keys:
        if isinstance(tree2[key], uproot.TTree):
            tree = tree2[key]
            in_keys = tree.keys(recursive=False)
            out_file.mktree(tree.name, tree.typenames(recursive=False))
            for in_key in tree.keys(recursive=False):
                out_file[key].extend({in_key: i for i in uproot.iterate(tree[in_key], step_size=step_size)})


def convert_typenames(dict):
    for typename in dict:
        if dict[typename] == 'int32_t':
            dict[typename] = np.int32

from skhep_testdata import data_path

file = uproot.open("/Users/zobil/Documents/odapt/src/odapt/operations/uproot-hepdata-example.root")
keys = file.keys(recursive=True, cycle=False)
print(keys)
tree = file[keys[0]]
# print(tree)
file1 = uproot.update("/Users/zobil/Documents/odapt/src/odapt/operations/uproot-HZZ.root")
temp = uproot.recreate("testfile1.root")

# first = False
# for chunk in uproot.iterate(tree):
#     if first:
#         first=False
#         file1[keys[0]] = tree
#     else:
#         file1[keys[0]].extend(chunk)
# print(file1.keys(recursive=True, cycle=False))

merge_files(
    "uproot-HZZ-hepdata.root",
    data_path("uproot-hepdata-example.root"),
    data_path("uproot-HZZ.root")
)

out_file = uproot.open("uproot-HZZ-hepdata.root")
# print(out_file.keys(recursive=True))
keys = out_file.keys(cycle=False, recursive=False)
print(out_file.keys(recursive=False, cycle=False))


# test_file = uproot.open("/Users/zobil/Documents/odapt/src/odapt/operations/test.root")
# print(test_file.keys(recursive=True))
# keys = test_file.keys(cycle=False)
# print(keys)
