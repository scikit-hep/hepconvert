from __future__ import annotations

from pathlib import Path

import awkward as ak
import uproot

from odapt.histogram_adding import hadd_1d, hadd_2d, hadd_3d

# ruff: noqa: B023


def copy_root(
    destination,
    file,
    *,
    drop_branches=None,
    drop_trees=None,
    force=True,
    fieldname_separator="_",
    branch_types=None,
    title="",
    field_name=lambda outer, inner: inner if outer == "" else outer + "_" + inner,
    initial_basket_capacity=10,
    resize_factor=10.0,
    counter_name=lambda counted: "n" + counted,
    step_size=100,
    compression="LZ4",
    compression_level=1,
):
    """
    :param destination: Name of the output file or file path.
    :type destination: path-like
    :param files: Local ROOT file to copy. May contain glob patterns.
    :type files: str
    :param drop_branches: To remove branches from a tree, pass a list of names of branches to remove.
        Defaults to None. Command line option: ``--drop-branches``.
    :type drop_branches: list of str, optional
    :param fieldname_separator: If data includes jagged arrays, pass the character that separates
        TBranch names for columns, used for grouping columns (to avoid duplicate counters in ROOT file). Defaults to "_".
    :type fieldname_separator: str, optional
    :param branch_types: Name and type specification for the TBranches. Defaults to None.
    :type branch_types: dict or pairs of str → NumPy dtype/Awkward type, optional
    :param title: to change the title of the ttree, pass a new name. Defaults to None. Command line option: ``--title``.
    :type title: str, optional
    :param field_name: Function to generate TBranch names for columns of an Awkward record array or a
        Pandas DataFrame. Defaults to ``lambda outer, inner: inner if outer == "" else outer + "_" +
        inner``.
    :type field_name: callable of str → str, optional
    :param initial_basket_capacity: Number of TBaskets that can be written to the TTree without
        rewriting the TTree metadata to make room. Defaults to 10. Command line option: ``--initial-basket-capacity``.
    :type initial_basket_capacity: int, optional
    :param resize_factor: When the TTree metadata needs to be rewritten, this specifies how many more
        TBasket slots to allocate as a multiplicative factor. Defaults to 10.0. Command line option: ``--resize-factor``.
    :type resize_factor: float, optional.
    :param counter_name: Function to generate counter-TBranch names for Awkward Arrays of variable-length
        lists. Defaults to ``lambda counted: "n" + counted``.
    :type counter_name: callable of str \u2192 str, optional
    :param step_size: If an integer, the maximum number of entries to include in each iteration step; if
        a string, the maximum memory size to include. The string must be a number followed by a memory unit, such as “100 MB”.
        Defaults to \100. Command line option: ``--step-size``.
    :type step_size: int or str, optional
    :param compression: Sets compression level for root file to write to. Can be one of "ZLIB", "LZMA", "LZ4", or "ZSTD".
        Defaults to "LZ4". Command line option: ``--compression``.
    :type compression: str
    :param compression_level: Use a compression level particular to the chosen compressor. Defaults to 1. Command line option: ``--compression-level``.
    :type compression_level: int


    Examples:
    ---------
    Copies contents of one ROOT file to a new file. If the file is in nanoAOD-format, ``copy_root`` can drop branches from a tree while copying. RNTuple can not yet be copied.

        >>> odapt.copy_root("copied_file.root", "original_file.root")

    To copy a file and drop branches with names "branch1" and "branch2":

        >>> odapt.copy_root("copied_file.root", "original_file.root", drop_branches=["branch1", "branch2"])

    Command Line Instructions:
    --------------------------
    This function can be run from the command line. Use command

        >>> odapt copy-root [options] [OUT_FILE] [IN_FILE]

    """
    if compression in ("LZMA", "lzma"):
        compression_code = uproot.const.kLZMA
    elif compression in ("ZLIB", "zlib"):
        compression_code = uproot.const.kZLIB
    elif compression in ("LZ4", "lz4"):
        compression_code = uproot.const.kLZ4
    elif compression in ("ZSTD", "zstd"):
        compression_code = uproot.const.kZSTD
    else:
        msg = f"unrecognized compression algorithm: {compression}. Only ZLIB, LZMA, LZ4, and ZSTD are accepted."
        raise ValueError(msg)
    path = Path(destination)
    if Path.is_file(path):
        if not force:
            raise FileExistsError
        out_file = uproot.recreate(
            destination,
            compression=uproot.compression.Compression.from_code_pair(
                compression_code, compression_level
            ),
        )
        first = (True,)
    else:
        out_file = uproot.recreate(
            destination,
            compression=uproot.compression.Compression.from_code_pair(
                compression_code, compression_level
            ),
        )
        first = (True,)
    try:
        f = uproot.open(file)
    except FileNotFoundError:
        msg = "File: ", file, " does not exist or is corrupt."
        raise FileNotFoundError(msg) from None

    hist_keys = f.keys(
        filter_classname=["TH*", "TProfile"], cycle=False, recursive=False
    )

    for key in f.keys(cycle=False, recursive=False):
        if key in hist_keys:
            if len(f[key].axes) == 1:
                h_sum = hadd_1d(destination, f, key, True)
                # if isinstance(h_sum, uproot.models.TH.Model_TH1F_v3):
                #     print(h_sum.member('fXaxis'))
                out_file[key] = h_sum
            elif len(f[key].axes) == 2:
                out_file[key] = hadd_2d(destination, f, key, True)
            else:
                out_file[key] = hadd_3d(destination, f, key, True)

    trees = f.keys(filter_classname="TTree", cycle=False, recursive=False)

    # Check that drop_trees keys are valid/refer to a tree:
    if drop_trees:
        if isinstance(drop_trees, list):
            for key in drop_trees:
                if key not in trees:
                    msg = (
                        "TTree ",
                        key,
                        " does not match any TTree in ROOT file",
                        destination,
                    )
                    raise ValueError(msg)
                trees.remove(key)
        if isinstance(drop_trees, str):
            found = False
            for key in trees:
                if key == drop_trees:
                    found = True
                    trees.remove(key)
            if found is False:
                msg = (
                    "TTree ",
                    key,
                    " does not match any TTree in ROOT file",
                    destination,
                )
                raise ValueError(msg)

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

        if drop_branches:
            keep_branches = [
                branch.name
                for branch in tree.branches
                if branch.name not in drop_branches
                and branch.name not in count_branches
            ]
        else:
            keep_branches = [
                branch.name
                for branch in tree.branches
                if branch.name not in count_branches
            ]

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
        for chunk in uproot.iterate(
            tree,
            step_size=step_size,
            how=dict,
            filter_branch=lambda b: b.name in keep_branches,
        ):
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
                    if key in keep_branches:
                        del chunk[key]
            if first:
                if not branch_types and not drop_branches:
                    branch_types = {name: array.type for name, array in chunk.items()}
                elif branch_types is None and drop_branches:
                    branch_types = {
                        name: array.type
                        for name, array in chunk.items()
                        if name not in drop_branches
                    }
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
                    msg = "Are the branch_names correct?"
                first = False

            else:
                try:
                    out_file[tree.name].extend(chunk)
                except AssertionError:
                    msg = "Are the branch-names correct?"

        for i, _value in enumerate(histograms):
            out_file[histograms[i]] = writable_hists[i]

        f.close()
