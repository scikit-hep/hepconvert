from __future__ import annotations

from pathlib import Path

import awkward as ak
import uproot


def root_to_parquet(
    input_file=None,
    output_file=None,
    *,
    list_to32=False,
    string_to32=True,
    bytestring_to32=True,
    emptyarray_to=None,
    categorical_as_dictionary=False,
    extensionarray=True,
    count_nulls=True,
    compression="zstd",
    compression_level=None,
    row_group_size=64 * 1024 * 1024,
    data_page_size=None,
    parquet_flavor=None,
    parquet_version="2.4",
    parquet_page_version="1.0",
    parquet_metadata_statistics=True,
    parquet_dictionary_encoding=False,
    parquet_byte_stream_split=False,
    parquet_coerce_timestamps=None,
    parquet_old_int96_timestamps=None,
    parquet_compliant_nested=False,
    parquet_extra_options=None,
    storage_options=None,
    tree=None,
    force=True,
    step_size=100,
):
    """
    :param destination: Name of the output file or file path.
    :type destination: path-like
    :param files: Local ROOT file to copy. May contain glob patterns.
    :type files: str
    :param drop_branches: To remove branches from a tree, pass a list of names of branches to remove.
        Defaults to None.
    :type drop_branches: list of str, optional
    :param fieldname_separator: If data includes jagged arrays, pass the character that separates
        TBranch names for columns, used for grouping columns (to avoid duplicate counters in ROOT file). Defaults to "_".
    :type fieldname_separator: str, optional
    :param branch_types: Name and type specification for the TBranches. Defaults to None.
    :type branch_types: dict or pairs of str → NumPy dtype/Awkward type, optional
    :param title: to change the title of the ttree, pass a new name. Defaults to None.
    :type title: str, optional
    :param field_name: Function to generate TBranch names for columns of an Awkward record array or a
        Pandas DataFrame. Defaults to ``lambda outer, inner: inner if outer == "" else outer + "_" +
        inner``.
    :type field_name: callable of str → str, optional
    :param initial_basket_capacity: Number of TBaskets that can be written to the TTree without
        rewriting the TTree metadata to make room. Defaults to 10.
    :type initial_basket_capacity: int, optional
    :param resize_factor: When the TTree metadata needs to be rewritten, this specifies how many more
        TBasket slots to allocate as a multiplicative factor. Defaults to 10.0.
    :type resize_factor: float, optional.
    :param counter_name: Function to generate counter-TBranch names for Awkward Arrays of variable-length
        lists. Defaults to ``lambda counted: "n" + counted``.
    :type counter_name: callable of str \u2192 str, optional
    :param step_size: If an integer, the maximum number of entries to include in each iteration step; if
        a string, the maximum memory size to include. The string must be a number followed by a memory unit, such as “100 MB”. Defaults to \100.
    :type step_size: int or str, optional
    :param compression: Sets compression level for root file to write to. Can be one of "ZLIB", "LZMA", "LZ4", or "ZSTD". Defaults to "LZ4".
    :type compression: str
    :param compression_level: Use a compression level particular to the chosen compressor. Defaults to 1.
    :type compression_level: int


    Examples:
    ---------
    Copies contents of one ROOT to an empty file. If the file is in nanoAOD-format, ``copy_root`` can drop branches from a tree while copying. TProfile and RNTuple can not yet be copied.

        >>> odapt.copy_root("copied_file.root", "original_file.root")

    To copy a file and drop branches with names "branch1" and "branch2":

        >>> odapt.copy_root("copied_file.root", "original_file.root", drop_branches=["branch1", "branch2"])


    """
    path = Path(output_file)
    if Path.is_file(path) and not force:
        raise FileExistsError

    try:
        f = uproot.open(input_file)
    except FileNotFoundError:
        msg = "File: ", input_file, " does not exist or is corrupt."
        raise FileNotFoundError(msg) from None

    if not tree:
        tree = f.keys(filter_classname="TTree", cycle=False, recursive=False)
        if len(tree) != 1:
            msg = "Must specify 1 tree to write, not ", len(tree)
            raise AttributeError(msg) from None

        # if drop_branches:
        # drop branches better
    ak.to_parquet(
        list(
            f[tree[0]].iterate(
                step_size=step_size,
            )
        ),
        output_file,
        list_to32=list_to32,
        string_to32=string_to32,
        bytestring_to32=bytestring_to32,
        emptyarray_to=emptyarray_to,
        categorical_as_dictionary=categorical_as_dictionary,
        extensionarray=extensionarray,
        count_nulls=count_nulls,
        compression=compression,
        compression_level=compression_level,
        row_group_size=row_group_size,
        data_page_size=data_page_size,
        parquet_flavor=parquet_flavor,
        parquet_version=parquet_version,
        parquet_page_version=parquet_page_version,
        parquet_metadata_statistics=parquet_metadata_statistics,
        parquet_dictionary_encoding=parquet_dictionary_encoding,
        parquet_byte_stream_split=parquet_byte_stream_split,
        parquet_coerce_timestamps=parquet_coerce_timestamps,
        parquet_old_int96_timestamps=parquet_old_int96_timestamps,
        parquet_compliant_nested=parquet_compliant_nested,
        parquet_extra_options=parquet_extra_options,
        storage_options=storage_options,
    )

    f.close()
