import uproot
import hadd
import numpy as np
import awkward as ak
def merge_files(destination, file1, file2, step_size="100MB", *, force=True, append=False, compression='LZ4', compression_level=1, skip_bad_files=False, union=True, batch=False): #hadd includes
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
        batch (bool): If True, branches and TTrees (when applicable) are written to the out-file in 
        batches of size defined by the step_size argument.

    Adds together histograms from local ROOT files of a collection of ROOT files, and writes them to
        a new or existing ROOT file.

        >>> odapt.add_histograms("destination.root", ["file1_to_hadd.root", "file2_to_hadd.root"])

    """
    # Use tmpdir? Or just do two at a time, tree reduction style...
    import tempfile
    if compression in ("ZLIB", "zlib"):
        compression_code = uproot.const.kZLIB
    elif compression in ("LZMA", "lzma"):
        compression_code = uproot.const.kLZMA
    elif compression in ("LZ4", "lz4"):
        compression_code = uproot.const.kLZ4
    elif compression in ("ZSTD", "zstd"):
        compression_code = uproot.const.kZSTD
    else:
        msg = f"unrecognized compression algorithm: {compression}. Only ZLIB, LZMA, LZ4, and ZSTD are accepted."
        raise ValueError(msg)
    p = Path(destination)
    if Path.is_file(p):
        if not force and not append:
            raise FileExistsError
        if force and append:
            msg = "Cannot append to a new file. Either force or append can be true."
            raise ValueError(msg)
        file_out = uproot.recreate(
            destination,
            compression=uproot.compression.Compression.from_code_pair(
                compression_code, compression_level
            ),
        )
    else:
        if append:
            raise FileNotFoundError(
                "File %s" + destination + " not found. File must exist to append."
            )
        file_out = uproot.recreate(
            destination,
            compression=uproot.compression.Compression.from_code_pair(
                compression_code, compression_level
            ),
        )
    
    if not isinstance(files, list):
        path = Path(files)
        files = sorted(path.glob("**/*.root"))

    if len(files) <= 1:
        msg = "Cannot hadd one file. Use root_to_root to copy a ROOT file."
        raise ValueError(msg) from None
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
        if isinstance(f1[key], uproot.TTree) and isinstance(f2[key], uproot.TTree):
            try:
                f1[key].name
                f2[key].name
            except uproot.KeyInFileError:
                raise uproot.KeyInFileError
            if f1[key].name != f2[key].name:
                print("Names must be the same")
            
            recur_merge(destination, out_file, f1, f2, key, step_size)
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
            for chunk in uproot.iterate(f1[key], step_size=step_size, how=dict):
                print("iterating?")
                if first:
                    first = False
                    out_file[key] = chunk
                else:
                    out_file[key].extend(chunk)

    for key in missing_keys:
        if isinstance(f1[key], uproot.TTree):
            tree = f1[key]
            branches = tree.branches 
            dtypes = []
            for i in branches:
                if isinstance(i.interpretation, uproot.AsJagged):
                    dtypes.append(i.interpretation.content.numpy_dtype)
                else:
                    dtypes.append(i.interpretation.numpy_dtype)

            nametypes = {branches[i].name : dtypes[i] for i, value in enumerate(branches)}
            out_file.mktree(tree.name, branch_types=nametypes)
            
            recur_copy(destination, out_file, f1[key], step_size)

        elif f1[key].classname.startswith("TH") or f1[key].classname.startswith("TProfile"):
            print("Histogram")
            if len(f1[key].axes) == 1:
                out_file[key] = hadd.hadd_1d(destination, f1, key, True)

            elif len(f1[key].axes) == 2:
                out_file[key] = hadd.hadd_2d(destination, f1, key, True)

            else:
                out_file[key] = hadd.hadd_3d(destination, f1, key, True)
        
        else:
            try:
                f1[key].iteritems()
                first = True
                for i in uproot.TBranch.iterate(f1[key], step_size=step_size, how=dict):
                    if first:
                        first = False
                        out_file[key] = i
                    out_file[key].extend(i)
            except AttributeError:
                Warning("ROOT class ", f1[key].classname, " cannot be iterated over.")
                try:
                    out_file[key] = f1[key]
                except NotImplementedError:
                    Warning("Cannot write type ", f1[key].classname, " skipping branch ", key)
            
    for key in additional_keys:
        if isinstance(f2[key], uproot.TTree):
            tree = f2[key]
            branches = tree.branches 
            dtypes = []
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

            # out_file[key] = h_sum
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
    for key in keys:
        if isinstance(tree[key], uproot.TTree):
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

def recur_merge(destination, out_file, f1, f2, k, step_size): 
    print("Recur merge")
    tree1 = f1[k]
    tree2 = f2[k]
    t1_keys = tree1.keys(recursive=False)
    t2_keys = tree2.keys(recursive=False)
    
    shared_keys = np.intersect1d(t1_keys, t2_keys)
    missing_keys = np.setdiff1d(t1_keys, shared_keys)
    additional_keys = np.setdiff1d(t2_keys, shared_keys)
    # out_file.mktree(tree1.name, tree1.typenames(recursive=False))
    # get keys for branches? for hadd
    branches = tree1.branches
    num_branches = len(tree1.items())
    dtypes1 = [None for i in range(num_branches)]
    for i in range(num_branches):
        if isinstance(branches[i].interpretation, uproot.AsJagged):
            dtypes1[i] = branches[i].interpretation.content.numpy_dtype
        else:
            dtypes1[i] = branches[i].interpretation.numpy_dtype

    branches = tree2.branches
    num_branches = len(tree2.items())
    dtypes2 = [None for i in range(num_branches)]
    for i in range(num_branches):
        if isinstance(branches[i].interpretation, uproot.AsJagged):
            dtypes2[i] = branches[i].interpretation.content.numpy_dtype
        else:
            dtypes2[i] = branches[i].interpretation.numpy_dtype

    dtypes = np.union1d(dtypes1, dtypes2)
    nametypes = {branches[i].name : dtypes[i] for i, value in enumerate(dtypes)}
    out_file.mktree(tree1.name, branch_types=nametypes)
    first = True
    for chunk in uproot.iterate(tree1, step_size=step_size, how=dict):
        if first:
            out_file[k] = chunk
        out_file[k].extend(chunk)
    # for chunk in uproot.iterate(tree2, step_size=step_size, how=dict):
    #     out_file[k].extend(chunk)
    for key in shared_keys:
        if isinstance(tree1[key], uproot.TTree) and isinstance(tree2[key], uproot.TTree):
            if tree1[key].name != tree2[key].name:
                print("Names must be the same")
            
            recur_merge(destination, out_file, tree1[key], tree2[key], key, step_size)

            # finally: 
            # Write just f1 to file???
            # msg = "Files must have similar structure."
            # raise ValueError(msg) from None
        
        elif tree1.classname.startswith("TH") or tree1.classname.startswith("TProfile"): # And check tree2 I guess...
            import tempfile

            if len(file[k].axes) == 1:
                #Make temp, add them together...then write to out_file
                fp = tempfile.TemporaryFile()
                out_file[k] = hadd.hadd_1d(f1, tree2, k, True)

            elif len(file[k].axes) == 2:
                out_file[k] = hadd.hadd_2d(f1, tree2, k, True)

            else:
                out_file[k] = hadd.hadd_3d(f1, tree2, k, True)
            

            # hadd.hadd_merge(destination, f1, key, first=True, n_key=None) #tree1? does it need to be a file?


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

f = uproot.open(data_path("uproot-Event.root"))
print(f.keys())
print(f["ProcessID0"])

# merge_files(
#     "test_dest.root",
#     data_path("uproot-HZZ.root"),
#     data_path("uproot-HZZ.root")
# )

out_file = uproot.open(data_path("uproot-HZZ.root"))
keys = out_file.keys(cycle=False, recursive=True)
print("hadd dest", out_file['events'].show())

test = uproot.open("test_dest.root")
keys = test.keys(cycle=False, recursive=True)