from __future__ import annotations

from pathlib import Path

import awkward as ak
import uproot

from odapt.operations.hadd import hadd_1d, hadd_2d, hadd_3d


# Could just automatically filter with typenames
def hadd_and_merge(
    destination,
    files,
    *,
    fieldname_separator="_",
    branch_types=None,
    title="",
    field_name=lambda outer, inner: inner if outer == "" else outer + "_" + inner,
    initial_basket_capacity=10,
    resize_factor=10.0,
    counter_name=lambda counted: "n" + counted,
    step_size="100 MB",
    force=True,
    append=False,
    compression="LZ4",
    compression_level=1,
    skip_bad_files=False,
):
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
        if not force and not append:
            raise FileExistsError
        if force and append:
            msg = "Cannot append to an empty file. Either force or append can be true."
            raise ValueError(msg)
        if append:
            out_file = uproot.update(
                destination,
                compression=uproot.compression.Compression.from_code_pair(
                    compression_code, compression_level
                ),
            )
            first = False
        else:
            out_file = uproot.recreate(
                destination,
                compression=uproot.compression.Compression.from_code_pair(
                    compression_code, compression_level
                ),
                first=True,
            )
    else:
        if append:
            raise FileNotFoundError(
                "File %s" + destination + " not found. File must exist to append."
            )
        out_file = uproot.recreate(
            destination,
            compression=uproot.compression.Compression.from_code_pair(
                compression_code, compression_level
            ),
        )
        first = True

    if not isinstance(files, list):
        path = Path(files)
        files = sorted(path.glob("**/*.root"))

    if len(files) <= 1:
        msg = "Only one file was input. Use root_to_root to copy a ROOT file."
        raise ValueError(msg) from None

    try:
        f = uproot.open(files[0])
    except FileNotFoundError:
        if skip_bad_files:
            for file in files:
                try:
                    f = uproot.open(file)
                    break
                except FileNotFoundError:
                    continue

        msg = "File: {files[0]} does not exist or is corrupt."
        raise FileNotFoundError(msg) from None
    hist_keys = f.keys(
        filter_classname=["TH*", "TProfile"], cycle=False, recursive=False
    )
    for key in f.keys(cycle=False, recursive=False):
        if key in hist_keys:
            # first_layer_hists.append(hist)
            if len(f[key].axes) == 1:
                h_sum = hadd_1d(destination, f, key, True)
                out_file[key] = h_sum
            elif len(f[key].axes) == 2:
                out_file[key] = hadd_2d(destination, f, key, True)
            else:
                out_file[key] = hadd_3d(destination, f, key, True)

    trees = f.keys(filter_classname="TTree", cycle=False, recursive=False)

    for t in trees:
        tree = f[t]
        histograms = tree.keys(filter_typename=["TH*", "TProfile"], recursive=False)
        groups = []
        count_branches = []
        temp_branches = [branch.name for branch in tree.branches]
        temp_branches1 = [branch.name for branch in tree.branches]
        cur_group = 0
        for branch in temp_branches:
            if len(tree[branch].member("fLeaves")) > 1:
                msg = "Cannot handle split objects."
                raise NotImplementedError(msg)
            if tree[branch].member("fLeaves")[0].member("fLeafCount") is None:
                continue
            groups.append([])
            groups[cur_group].append(branch)
            for branch1 in temp_branches1:
                if tree[branch].member("fLeaves")[0].member("fLeafCount") is tree[
                    branch1
                ].member("fLeaves")[0].member("fLeafCount") and (
                    tree[branch].name != tree[branch1].name
                ):
                    groups[cur_group].append(branch1)
                    temp_branches.remove(branch1)
            count_branches.append(tree[branch].count_branch.name)
            temp_branches.remove(tree[branch].count_branch.name)
            temp_branches.remove(branch)
            cur_group += 1

        writable_hists = {}
        if len(histograms) > 1:
            for key in histograms:
                if len(f[key].axes) == 1:
                    writable_hists[key] = hadd_1d(destination, f, key, True)

                elif len(f[key].axes) == 2:
                    writable_hists[key] = hadd_2d(destination, f, key, True)

                else:
                    writable_hists[key] = hadd_3d(destination, f, key, True)

        elif len(histograms) == 1:
            if len(f[histograms[0]].axes) == 1:
                writable_hists = hadd_1d(destination, f, histograms[0], True)

            elif len(f[histograms[0]].axes) == 2:
                writable_hists = hadd_2d(destination, f, histograms[0], True)

            else:
                writable_hists = hadd_3d(destination, f, histograms[0], True)

        first = True
        for chunk in uproot.iterate(tree, step_size=step_size, how=dict):
            for key in count_branches:
                del chunk[key]
            for group in groups:
                if (len(group)) > 1:
                    chunk.update(
                        {
                            group[0][0 : (group[0].index(fieldname_separator))]: ak.zip(
                                {
                                    name[
                                        group[0].index(fieldname_separator) + 1 :
                                    ]: array
                                    for name, array in zip(
                                        ak.fields(chunk), ak.unzip(chunk)
                                    )
                                    if name in group
                                }
                            )
                        }
                    )
                for key in group:
                    del chunk[key]

            if branch_types is None:
                branch_types = {name: array.type for name, array in chunk.items()}

            if first:
                out_file.mktree(
                    tree.name,
                    branch_types,
                    title=title,
                    counter_name=counter_name,
                    field_name=field_name,
                    initial_basket_capacity=initial_basket_capacity,
                    resize_factor=resize_factor,
                )
                try:
                    out_file[tree.name].extend(chunk)
                except AssertionError:
                    msg = "TTrees must have the same structure to be merged"
                first = False

            else:
                try:
                    out_file[tree.name].extend(chunk)
                except AssertionError:
                    msg = "TTrees must have the same structure to be merged"

        for i, _value in enumerate(histograms):
            out_file[histograms[i]] = writable_hists[i]

        f.close()

    for file in files[1:]:
        try:
            f = uproot.open(file)
        except FileNotFoundError:
            if skip_bad_files:
                continue
            msg = "File: {input_file} does not exist or is corrupt."
            raise FileNotFoundError(msg) from None

        for key in f.keys(cycle=False, recursive=False):
            if key in hist_keys:
                if len(f[key].axes) == 1:
                    h_sum = hadd_1d(destination, f, key, False)
                elif len(f[key].axes) == 2:
                    h_sum = hadd_2d(destination, f, key, False)
                else:
                    h_sum = hadd_3d(destination, f, key, False)

                out_file[key] = h_sum

        writable_hists = {}
        for t in trees:
            tree = f[t]
            writable_hists = []
            for key in histograms:
                if len(f[key].axes) == 1:
                    writable_hists[key] = hadd_1d(destination, out_file, key, False)

                elif len(f[key].axes) == 2:
                    writable_hists[key] = hadd_2d(destination, out_file, key, False)

                else:
                    writable_hists[key] = hadd_3d(destination, out_file, key, False)

            for chunk in uproot.iterate(tree, step_size=step_size, how=dict):
                for group in groups:
                    if len(group) > 1:
                        chunk.update(
                            {
                                group[0][
                                    0 : (group[0].index(fieldname_separator))
                                ]: ak.zip(
                                    {
                                        name[
                                            group[0].index(fieldname_separator) + 1 :
                                        ]: array
                                        for name, array in zip(
                                            ak.fields(chunk), ak.unzip(chunk)
                                        )
                                        if name in group
                                    }
                                )
                            }
                        )
                    for key in group:
                        del chunk[key]
                for key in count_branches:
                    del chunk[key]
                try:
                    out_file[tree.name].extend(chunk)

                except AssertionError:
                    msg = "TTrees must have the same structure to be merged"

            for key in histograms:
                out_file[key] = writable_hists[key]

        f.close()
