import uproot
import hadd
import numpy as np
import awkward as ak
from pathlib import Path
def merge_files(destination, file1, file2, step_size=0, *, force=True, append=False, compression='LZ4', compression_level=1, skip_bad_files=False, union=True): #hadd includes
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
        if not force:
            raise FileExistsError
        if force and append: # Does this still apply??
            msg = "Cannot append to a new file. Either force or append can be true."
            raise ValueError(msg)
        out_file = uproot.recreate(
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

    # if not isinstance(files, list):
    #     path = Path(files)
    #     files = sorted(path.glob("**/*.root"))

    # if len(files) <= 1:
    #     msg = "Cannot hadd one file. Use root_to_root to copy a ROOT file."
    #     raise ValueError(msg) from None

    f1 = uproot.open(file1)
    f2 = uproot.open(file2)
    #title must be the same as the file name? maybe is just a tChain thing

    t1_keys = f1.keys(recursive=False, cycle=False)
    t2_keys = f2.keys(recursive=False, cycle=False)

    shared_keys = np.intersect1d(t1_keys, t2_keys)
    missing_keys = np.setdiff1d(t1_keys, shared_keys)
    additional_keys = np.setdiff1d(t2_keys, shared_keys)
    
    for key in shared_keys:
        tree1 = f1[key]
        tree2 = f2[key]
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
        print(nametypes)
        out_file.mktree(tree1.name, branch_types=nametypes)
        recur_merge(destination, out_file, f1, f2, key, step_size)
        
    for key in missing_keys:
        recur_copy(destination, out_file, f1[key], step_size)

    for key in additional_keys:
        recur_copy(destination, out_file, f2[key], step_size)


def recur_copy(destination, out_file, tree, step_size):
    keys = tree.keys(recursive=False) #since cycle was false for the tree the first time, may break/be unnecessary here
    out_file[tree.name].mktree(tree[key].name, branch_types=nametypes)    
    for key in keys:
        if isinstance(tree[key], uproot.TTree):
            branches = tree[key].branches
            dtypes = []
            for i in branches:
                if isinstance(i.interpretation, uproot.AsJagged):
                    dtypes.append(i.interpretation.content.numpy_dtype)
                else:
                    dtypes.append(i.interpretation.numpy_dtype)
            
            nametypes = {branches[i].name : dtypes[i] for i, value in enumerate(branches)}
            recur_copy(destination, out_file, tree[key], step_size)

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
    first = True
    # for chunk in uproot.iterate(tree2, step_size=step_size, how=dict):
    #     out_file[k].extend(chunk)
    counter = 0
    t1_keys = tree1.keys(recursive=False)
    t2_keys = tree2.keys(recursive=False)
    shared_keys = np.intersect1d(t1_keys, t2_keys)
    missing_keys = np.setdiff1d(t1_keys, shared_keys)
    additional_keys = np.setdiff1d(t2_keys, shared_keys)

    for key in shared_keys:
        if isinstance(tree1[key], uproot.TTree) and isinstance(tree2[key], uproot.TTree):
            if tree1[key].name != tree2[key].name:
                print("Names must be the same")
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
            out_file[k].mktree(tree1[key].name, branch_types=nametypes)
            recur_merge(destination, out_file, tree1[key], tree2[key], key, step_size)

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
        else:
            if step_size != 0:
                for chunk in uproot.iterate(tree1, step_size=step_size, how=dict):
                    if first:
                        out_file[k] = chunk
                    out_file[k].extend(chunk)
            else:
                print("before", out_file.keys(cycle=False))
                print(k)
                out_file[k].extend({tree1[key].name : tree1[key].items()})
                # out_file[k] = {branch.name : branch.items() for branch in tree1.branches}
                # # print("rewritten?",out_file[k].show())
                # out_file[k] = {branch.name : branch.items() for branch in tree2.branches} # Will they be rewritten?? How to check?
                # # print("See:",out_file[k].show())
                

            # hadd.hadd_merge(destination, f1, key, first=True, n_key=None) #tree1? does it need to be a file?
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

from skhep_testdata import data_path

file = uproot.open("/Users/zobil/Documents/odapt/src/odapt/operations/uproot-hepdata-example.root")
keys = file.keys(recursive=True, cycle=False)
# print(keys)
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

# f = uproot.open(data_path("uproot-Event.root"))
# print(f.keys())
# print(f["ProcessID0"])

merge_files(
    "test_dest.root",
    data_path("uproot-HZZ.root"),
    data_path("uproot-HZZ.root")
)

# out_file = uproot.open(data_path("uproot-HZZ.root"))
# keys = out_file.keys(cycle=False, recursive=True)
# print("hadd dest", out_file['events'].show())

test = uproot.open("test_dest.root")
keys = test.keys(cycle=False, recursive=True)
print(test['events'].show())


import uproot
import hadd
import numpy as np
import awkward as ak
from pathlib import Path 
# Could just automatically filter with typenames
def merge_files(destination, files, tree_key, intersection=False, tree_name=None, branch_types=None, counter_name=None, field_name=None, initial_basket_capacity=10, resize_factor=10.0, step_size=0, *, force=True, append=False, compression='LZ4', compression_level=1, skip_bad_files=False, union=True): #hadd includes
    # Include rest of mktree capacity??
    """
    Args:
        destination (path-like): Name of the output file or file path.
        files (Str or list of str): List of local ROOT files to read histograms from.
            May contain glob patterns.
        branch_types (dict or pairs of str → NumPy dtype/Awkward type): Name and type specification for the TBranches.
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
        if not force:
            raise FileExistsError
        if force and append: # Does this still apply??
            msg = "Cannot append to a new file. Either force or append can be true."
            raise ValueError(msg)
        out_file = uproot.recreate(
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

    with uproot.open(files[0]) as f:
        # keys = f.keys(recursive=False, cycle=False)
        # print(f[keys[0]].members['fLeaves'].members)
        tree = f[tree_key]
        
        if branch_types != None:
            b = branch_types
        else:
            dtypes = get_dtypes(tree)
            branch_types = {tree[i].name : dtypes[i] for i, value in enumerate(tree.branches)}
            # typenames = tree.typenames(recursive=False)
            # branch_types = {i: uproot.interpretation.identify.parse_typename(typenames[i]) for i in typenames}
        histograms = [key for key in f[tree_key].keys() if key.startswith("TH") or key.startswith("TProfile")]

        if tree_name == None:
            tree_name = f[tree_key].name
        
        if counter_name != None and field_name != None and initial_basket_capacity != None and resize_factor != None:
            out_file.mktree(tree_name, branch_types, counter_name=counter_name, field_name=field_name, initial_basket_capacity=initial_basket_capacity, resize_factor=resize_factor)
        elif counter_name != None and field_name != None:
            out_file.mktree(tree_name, branch_types, counter_name=counter_name, field_name=field_name)
        elif initial_basket_capacity != None and resize_factor != None:
            out_file.mktree(tree_name, branch_types, initial_basket_capacity=initial_basket_capacity, resize_factor=resize_factor)
        elif counter_name != None:
            out_file.mktree(tree_name, tree.classnames, counter_name=counter_name)  

        out_file.mktree(tree_name, branch_types)
        # arrays = tree.arrays(filter_name=["Jet_*", "Muon_*"])
        # nchunk = {}
        # jets = ak.zip({name[4:]: array for name, array in zip(ak.fields(arrays), ak.unzip(arrays)) if name.startswith("Jet_")})
        # print("jet", jets)
        writable_hists = []
        for key in histograms:
            print("histogram")
            if len(f[key].axes) == 1:
                writable_hists.append(hadd.hadd_1d(destination, f, key, True))

            elif len(f[key].axes) == 2:
                writable_hists.append(hadd.hadd_2d(destination, f, key, True))

            else:
                writable_hists.append(hadd.hadd_3d(destination, f, key, True))

        # for leaf in leaves:
        #     if chunk.has_member(leaf.classname):
        #         do something...

        for chunk in uproot.iterate(tree, step_size=step_size, how=dict):
            print(tree['NJet'].members)
            # chunk = {ak.zip({name: array for name, array in zip(ak.fields(chunk), chunk) if branch.members['fLeaves'] == tree[name].members['fLeaves']}) for branch in tree.branches}
            
            for branch in tree.branches:
                print(branch.name, branch.members['fLeaves'].has_member(tree['Jet_Py'].member('fLeaves').member('fName')))

                # temp = ak.zip({name: array for name, array in zip(ak.fields(chunk), ak.unzip(chunk)) if branch.has_member(name)})
                # print(chunk[branch.name])
                # nchunk.update({branch.name: temp[branch.name]})
            #         nchunk = ak.zip({name: array for name, array in zip(ak.fields(chunk), chunk) if branch.members['fLeaves'] == tree[name].members['fLeaves']})
            #         first = False
            #     else:
            #         # print(nchunk.type)
            #         nchunk = ak.zip({name: array for name, array in zip(ak.fields(chunk), chunk) if branch.members['fLeaves'] == tree[name].members['fLeaves']})
            #     counter+=1
                # nchunk.type.show()

            out_file[tree_name].extend(chunk)
            
        for key in histograms:
            out_file[key] = writable_hists

        # if i.hasmember(fLeaf.classname)...
        
# REMEMBER TO FILTER BRANCHES TO THOSE IN BRANCH_TYPES (for histograms?) OR WHATEVER WHEN ITERATING/EXTENDING OTHERWISE IT MAY BREAK

    for file in files[1:]:
        with uproot.open(file) as f:
            tree = file[tree_key]

            writable_hists = []
            for key in histograms:
                print("histogram")
                if len(f[key].axes) == 1:
                    writable_hists.append(hadd.hadd_1d(destination, f, key, True))

                elif len(f[key].axes) == 2:
                    writable_hists.append(hadd.hadd_2d(destination, f, key, True))

                else:
                    writable_hists.append(hadd.hadd_3d(destination, f, key, True))

            # for leaf in leaves:
            #     if chunk.has_member(leaf.classname):
            #         do something...

            for chunk in uproot.iterate(tree, step_size=step_size, how=dict):
                out_file[tree_name].extend(chunk)
                
            for key in histograms:
                out_file[key] = writable_hists

            try:
                out_file[tree.name].extend(tree)
            except AssertionError:
                msg = "TTrees must have the same structure and branch names must be the same accross files."

    # Maybe at the end of each tree/recursion is where to add histograms?

def get_dtypes(tree):
    dtypes = []
    for i in tree.branches:
        if isinstance(i.interpretation, uproot.AsJagged):
            dtypes.append(i.interpretation.content.numpy_dtype)
        else:
            dtypes.append(i.interpretation.numpy_dtype)
    return dtypes

from skhep_testdata import data_path

merge_files(
    "test_dest.root",
    [data_path("uproot-HZZ.root"),
    data_path("uproot-HZZ.root")],
    'events',
    step_size=100,
)

# out_file = uproot.open("/Users/zobil/Documents/odapt/tests/same_file.root")
# keys = out_file.keys(cycle=False, recursive=True)
# print(out_file['events'].show())
# print("hadd dest", out_file['events'].show())

test = uproot.open("test_dest.root")
keys = test.keys(cycle=False, recursive=True)
print(test['events'].show())


