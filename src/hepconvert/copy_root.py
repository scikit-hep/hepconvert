from __future__ import annotations

from pathlib import Path

import awkward as ak
import uproot

from hepconvert._utils import filter_branches, get_counter_branches, group_branches
from hepconvert.histogram_adding import _hadd_1d, _hadd_2d, _hadd_3d

# ruff: noqa: B023


def copy_root(
    destination,
    file,
    *,
    keep_branches=None,
    drop_branches=None,
    # add_branches=None, #TO-DO: add functionality for this, just specify about the counter issue
    keep_trees=None,
    drop_trees=None,
    force=False,
    fieldname_separator="_",
    # fix_duplicate_counters=False, #TO-DO: ask about this?
    title="",
    field_name=lambda outer, inner: inner if outer == "" else outer + "_" + inner,
    initial_basket_capacity=10,
    resize_factor=10.0,
    counter_name=lambda counted: "n" + counted,
    step_size=100,
    compression="ZLIB",
    compression_level=1,
):
    """
    :param destination: Name of the output file or file path.
    :type destination: path-like
    :param files: Local ROOT file to copy. May contain glob patterns.
    :type files: str
    :param drop_branches: To remove branches from all trees, pass a list of names of branches to
        remove. If removing branches from one of multiple trees, pass a dict of structure: {tree: [branch1, branch2]}
        to remove branch1 and branch2 from ttree "tree". Defaults to None. Command line option: ``--drop-branches``.
    :type drop_branches: list of str, str, or dict, optional
    :param drop_trees: To remove a ttree from a file, pass a list of names of branches to remove.
        Defaults to None. Command line option: ``--drop-trees``.
    :type drop_trees: str or list of str, optional
    :param force: If true, replaces file if it already exists. Default is False. Command line options ``-f`` or ``--force``.
    :type force: Bool, optional
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
        Defaults to "ZLIB". Command line option: ``--compression``.
    :type compression: str
    :param compression_level: Use a compression level particular to the chosen compressor. Defaults to 1. Command line option: ``--compression-level``.
    :type compression_level: int


    Examples:
    ---------
    Copies contents of one ROOT file to a new file. If the file is in nanoAOD-format, ``copy_root`` can drop branches from a tree while copying. RNTuple can not yet be copied.

        >>> hepconvert.copy_root("copied_file.root", "original_file.root")

    To copy a file and drop branches with names "branch1" and "branch2":

        >>> hepconvert.copy_root("copied_file.root", "original_file.root", drop_branches=["branch1", "branch2"])

    Command Line Instructions:
    --------------------------
    This function can be run from the command line. Use command

        >>> hepconvert copy-root [options] [OUT_FILE] [IN_FILE]

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

    for key in hist_keys:  # just pass to hadd??
        if len(f[key].axes) == 1:
            out_file[key] = _hadd_1d(destination, f, key, True)
        elif len(f[key].axes) == 2:
            out_file[key] = _hadd_2d(destination, f, key, True)
        else:
            out_file[key] = _hadd_3d(destination, f, key, True)

    trees = f.keys(filter_classname="TTree", cycle=False, recursive=False)

    # Check that drop_trees keys are valid/refer to a tree:
    if drop_trees and keep_trees:
        msg = "Can specify either drop_trees or keep_trees, not both."
        raise ValueError(msg) from None
    if keep_trees:
        if isinstance(keep_trees, list):
            for key in keep_trees:
                if key not in trees:
                    msg = (
                        "Key '"
                        + key
                        + "' does not match any TTree in ROOT file"
                        + str(file)
                    )
                    raise ValueError(msg)
        if isinstance(keep_trees, str):
            keep_trees = f.keys(filter_name=keep_trees, cycle=False)
        if len(keep_trees) != 1:
            drop_trees = [tree for tree in trees if tree not in keep_trees]
        else:
            drop_trees = [tree for tree in trees if tree != keep_trees[0]]

    if drop_trees:
        if isinstance(drop_trees, list):
            for key in drop_trees:
                if key not in trees:
                    msg = (
                        "Key '"
                        + key
                        + "' does not match any TTree in ROOT file"
                        + str(file)
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
        count_branches = get_counter_branches(tree)
        kb = filter_branches(tree, keep_branches, drop_branches, count_branches)
        groups, count_branches = group_branches(tree, kb)
        first = True
        for chunk in tree.iterate(
            step_size=step_size,
            how=dict,
            filter_name=lambda b: b in kb,
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
                    if key in kb:
                        del chunk[key]
            if first:
                if drop_branches:
                    branch_types = {
                        name: array.type
                        for name, array in chunk.items()
                        if name not in drop_branches
                    }
                else:
                    branch_types = {name: array.type for name, array in chunk.items()}

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

        f.close()
