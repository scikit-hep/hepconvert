import uproot
import hadd
import numpy as np
import awkward as ak
from pathlib import Path 
# Could just automatically filter with typenames
def merge_files(destination, files, tree_key, NanoAOD=False, intersection=False, tree_name=None, branch_types=None, counter_name=None, field_name=None, initial_basket_capacity=10, resize_factor=10.0, step_size=0, *, force=True, append=False, compression='LZ4', compression_level=1, skip_bad_files=False, union=True): #hadd includes
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
        compression_level (int): Use a compression level particular to the chosen compressor..
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

        groups = []
        count_branches = []
        temp_branches = [branch.name for branch in tree.branches]
        temp_branches1 = [branch.name for branch in tree.branches]
        cur_group = 0
        first = True
        for branch in temp_branches:
            if len(tree[branch].member('fLeaves')) > 1:
                NotImplementedError("Cannot handle split objects.")
            if tree[branch].member('fLeaves')[0].member('fLeafCount') == None:
                continue
            groups.append([])
            groups[cur_group].append(branch)
            for branch1 in temp_branches1:
                if tree[branch].member('fLeaves')[0].member('fLeafCount') is tree[branch1].member('fLeaves')[0].member('fLeafCount') and (tree[branch].name != tree[branch1].name):
                    groups[cur_group].append(branch1)
                    temp_branches.remove(branch1)
            
            count_branches.append(tree[branch].count_branch.name)
            temp_branches.remove(tree[branch].count_branch.name)
            temp_branches.remove(branch)
            cur_group+=1
        print(count_branches)
        # out_file.mktree(tree_name, branch_types)
        
        writable_hists = []
        for key in histograms:
            print("histogram")
            if len(f[key].axes) == 1:
                writable_hists.append(hadd.hadd_1d(destination, f, key, True))

            elif len(f[key].axes) == 2:
                writable_hists.append(hadd.hadd_2d(destination, f, key, True))

            else:
                writable_hists.append(hadd.hadd_3d(destination, f, key, True))

        first = True
        for chunk in uproot.iterate(tree, step_size=step_size, how=dict):
            print("here",chunk.keys())
            for group in groups:
                chunk.update({group[0][0:(group[0].index("_"))]: ak.zip({name[group[0].index("_")+1:]: array for name, array in zip(ak.fields(chunk), ak.unzip(chunk)) if name in group})})
                for key in group:
                    del chunk[key]
            if first:
                print("first", chunk.keys())
                for key in count_branches:
                    del chunk[key]
                out_file[tree_name] = chunk
                first = False
            else:
                out_file[tree_name].show()
                out_file[tree_name].extend(chunk)
            out_file.mktree(tree_name, branch_types)

        for key in histograms:
            out_file[key] = writable_hists

        # if i.hasmember(fLeaf.classname)...
        
# REMEMBER TO FILTER BRANCHES TO THOSE IN BRANCH_TYPES (for histograms?) OR WHATEVER WHEN ITERATING/EXTENDING OTHERWISE IT MAY BREAK

    for f in files[1:]:
        with uproot.open(f) as file:
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
            # print(chunk)
            for group in groups:
                # print(group)
                chunk.update({group[0][0:(group[0].index("_"))]: ak.zip({name[group[0].index("_")+1:]: array for name, array in zip(ak.fields(chunk), ak.unzip(chunk)) if name in group})})
                for key in group:
                    del chunk[key]
            try:
                out_file[tree_name].extend(chunk)
            except AssertionError:
                msg="TTrees must have the same structure to be merged"
            
            out_file.mktree(tree_name, branch_types)
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


