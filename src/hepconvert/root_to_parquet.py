from __future__ import annotations

from pathlib import Path

import awkward as ak
import uproot
from numpy import union1d


def root_to_parquet(
    in_file=None,
    out_file=None,
    *,
    tree=None,
    drop_branches=None,
    keep_branches=None,
    cut=None,
    expressions=None,
    force=False,
    step_size="100 MB",
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
):
    """Converts ROOT to Parquet file using Uproot and awkward.to_parquet. Data read from 1 tree, converted to single Parquet file.

    :param in_file: Local ROOT file to convert to Parquet. May contain glob patterns.
    :type in_file: path-like
    :param out_file: Name of the output file or file path.
    :type out_file: path-like
    :param tree: If there are multiple trees in the ROOT file, specify the name of one to write to Parquet.
        Command line options: ``-t`` or ``--tree``.
    :type tree: None or str
    :param keep_branches: To keep only certain branches and remove all others. To remove certain branches from all TTrees in the file,
        pass a list of names of branches to keep, wildcarding accepted ("Jet_*"). If removing branches from one of multiple trees, pass a dict of structure: {tree: [branch1, branch2]}
        to keep only branch1 and branch2 in ttree "tree". Defaults to None. Command line option: ``--keep-branches``.
    :type keep_branches: list of str, str, or dict, optional
    :param drop_branches: To remove branches from all trees, pass a list of names of branches to
        remove. Wildcarding supported ("Jet_*"). If removing branches from one of multiple trees,
        pass a dict of structure: {tree: [branch1, branch2]} to remove branch1 and branch2 from ttree "tree". Defaults to None. Command line option: ``--drop-branches``.
    :type drop_branches: list of str, str, or dict, optional
    :param force: If true, replaces file if it already exists. Default is False. Command line options ``-f`` or ``--force``.
    :type force: Bool, optional
    :param step_size: If an integer, the maximum number of entries to include in each iteration step; if
        a string, the maximum memory size to include. The string must be a number followed by a memory unit, such as “100 MB”.
        Defaults to '100 MB'. Command line options: ``-s`` or ``--step-size``.
    :type step_size: int or str, optional
    :param list_to32: If True, convert Awkward lists into 32-bit Arrow lists if they're small enough, even if it means an extra conversion.
        Otherwise, signed 32-bit ak.types.ListType maps to Arrow ListType, signed 64-bit ak.types.ListType maps to Arrow LargeListType, and
        unsigned 32-bit ak.types.ListType picks whichever Arrow type its values fit into. Command line option ``--list-to32``.
    :type list_to32: bool
    :param string_to32: Same as the above for Arrow string and ``large_string``. Command line option: ``--string-to32``.
    :type string_to32: bool
    :param bytestring_to32: Same as the above for Arrow binary and ``large_binary``. Command line option: ``--bytestring-to32``.
    :type bytestring_to32: bool
    :param emptyarray_to: If None, #ak.types.UnknownType maps to Arrow's
        null type; otherwise, it is converted a given numeric dtype. Command line option: ``--emptyarray-to``.
    :type emptyarray_to: None or dtype
    :param categorical_as_dictionary: If True, #ak.contents.IndexedArray and
        #ak.contents.IndexedOptionArray labeled with ``__array__ = "categorical"``
        are mapped to Arrow `DictionaryArray`; otherwise, the projection is
        evaluated before conversion (always the case without
        `__array__ = "categorical"`). Command line option: ``--categorical-as-dictionary``.
    :type categorical_as_dictionary: bool
    :param extensionarray: If True, this function returns extended Arrow arrays
        (at all levels of nesting), which preserve metadata so that Awkward \u2192
        Arrow \u2192 Awkward preserves the array's #ak.types.Type (though not
        the #ak.forms.Form). If False, this function returns generic Arrow arrays
        that might be needed for third-party tools that don't recognize Arrow's
        extensions. Even with `extensionarray=False`, the values produced by
        Arrow's `to_pylist` method are the same as the values produced by Awkward's
        #ak.to_list. Command line option: ``--extensionarray``.
    :type extensionarray: bool
    :param count_nulls: If True, count the number of missing values at each level
        and include these in the resulting Arrow array, which makes some downstream
        applications faster. If False, skip the up-front cost of counting them.
        Command line option: ``--count-nulls``.
    :type count_nulls: bool
    :param compression: Compression algorithm name, passed to
        `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
        Parquet supports `{"NONE", "SNAPPY", "GZIP", "BROTLI", "LZ4", "ZSTD"}`
        (where `"GZIP"` is also known as "zlib" or "deflate"). If a dict, the keys
        are column names (the same column names that #ak.forms.Form.columns returns
        and #ak.forms.Form.select_columns accepts) and the values are compression
        algorithm names, to compress each column differently. Command line option: ``--compression``.
    :type compression: None, str, or dict
    :param compression_level: Compression level, passed to
        `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
        Compression levels have different meanings for different compression
        algorithms: GZIP ranges from 1 to 9, but ZSTD ranges from -7 to 22, for
        example. Generally, higher numbers provide slower but smaller compression. Command line option
        ``--compression-level``.
    :type compression_level: None, int, or dict None
    :param row_group_size: Maximum number of entries in each row group,
        passed to `pyarrow.parquet.ParquetWriter.write_table <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html#pyarrow.parquet.ParquetWriter.write_table>`__.
        If None, the Parquet default of 64 MiB is used. Command line options: ``-rg`` or ``--row-group-size``.
    :type row_group_size: int or None
    :param data_page_size: Number of bytes in each data page, passed to
        `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
        If None, the Parquet default of 1 MiB is used. Command line option: ``--data-page-size``.
    :type data_page_size: None or int
    :param parquet_flavor: If None, the output Parquet file will follow
        Arrow conventions; if `"spark"`, it will follow Spark conventions. Some
        systems, such as Spark and Google BigQuery, might need Spark conventions,
        while others might need Arrow conventions. Passed to
        `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
        as `flavor`. Command line option: ``--parquet-flavor``.
    :type parquet_flavor: None or `"spark"`
    :param parquet_version: Parquet file format version.
        Passed to `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
        as `version`. Command line option: ``--parquet-version``.
    :type parquet_version: `"1.0"`, `"2.4"`, or `"2.6"`
    :param parquet_page_version: Parquet page format version.
        Passed to `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html)>`__.
        as `data_page_version`. Command line option: ``--parquet-page-version``.
    :type parquet_page_version: `"1.0"` or `"2.0"`
    :param parquet_metadata_statistics: If True, include summary
        statistics for each data page in the Parquet metadata, which lets some
        applications search for data more quickly (by skipping pages). If a dict
        mapping column names to bool, include summary statistics on only the
        specified columns. Passed to
        `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
        as `write_statistics`. Command line option: ``--parquet-metadata-statistics``.
    :type parquet_metadata_statistics: bool or dict
    :param parquet_dictionary_encoding: If True, allow Parquet to pre-compress
        with dictionary encoding. If a dict mapping column names to bool, only
        use dictionary encoding on the specified columns. Passed to
        `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
        as `use_dictionary`. Command line option: ``--parquet-dictionary-encoding``.
    :type parquet_dictionary_encoding: bool or dict
    :param parquet_byte_stream_split: If True, pre-compress floating
        point fields (`float32` or `float64`) with byte stream splitting, which
        collects all mantissas in one part of the stream and exponents in another.
        Passed to `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
        as `use_byte_stream_split`. Command line option: ``--parquet-byte-stream-split``.
    :type parquet_byte_stream_split: bool or dict
    :param parquet_coerce_timestamps: If None, any timestamps
        (`datetime64` data) are coerced to a given resolution depending on
        `parquet_version`: version `"1.0"` and `"2.4"` are coerced to microseconds,
        but later versions use the `datetime64`'s own units. If `"ms"` is explicitly
        specified, timestamps are coerced to milliseconds; if `"us"`, microseconds.
        Passed to `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
        as `coerce_timestamps`. Command line option: ``--parquet-coerce-timestamps``.
    :type parquet_coerce_timestamps: None, `"ms"`, or `"us"`
    :param parquet_old_int96_timestamps: If True, use Parquet's INT96 format
        for any timestamps (`datetime64` data), taking priority over `parquet_coerce_timestamps`.
        If None, let the `parquet_flavor` decide. Passed to
        `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
        as `use_deprecated_int96_timestamps`. Command line option: ``--parquet-old-int96-timestamps``.
    :type parquet_old_int96_timestamps: None or bool
    :param parquet_compliant_nested: If True, use the Spark/BigQuery/Parquet
        `convention for nested lists <https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#nested-types>`__,
        in which each list is a one-field record with field name "`element`";
        otherwise, use the Arrow convention, in which the field name is "`item`".
        Passed to `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
        as `use_compliant_nested_type`. Command line option: ``--parquet-compliant-nested``.
    :type parquet_compliated_nested: bool
    :param parquet_extra_options: Any additional options to pass to
        `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
    :type parquet_extra_options: None or dict
    :param storage_options: Any additional options to pass to
        `fsspec.core.url_to_fs <https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.core.url_to_fs>`__
        to open a remote file for writing.
    :type storage_options: None or dict

    Examples:
    ---------
    Converts a TTree from a ROOT file to a Parquet File.

        >>> hepconvert.root_to_parquet(in_file="file.root", out_file="file.parquet")

    Command Line Instructions:
    --------------------------
    This function can be run from the command line. Use command

    .. code-block:: bash

        hepconvert root-to-parquet [options] [OUT_FILE] [IN_FILE]

    """
    path = Path(out_file)
    if Path.is_file(path) and not force:
        raise FileExistsError

    try:
        f = uproot.open(in_file)
    except FileNotFoundError:
        msg = "File: ", in_file, " does not exist or is corrupt."
        raise FileNotFoundError(msg) from None

    if not tree:
        trees = f.keys(filter_classname="TTree", cycle=False, recursive=False)
        if len(trees) != 1:
            msg = "Must specify 1 tree to write, cannot write ", len(trees), "trees."
            raise AttributeError(msg) from None
        tree = trees[0]

    filter_b = _filter_branches(f[tree], keep_branches, drop_branches)
    # if there's a counter, rid of that too...
    ak.to_parquet_row_groups(
        (
            i
            for i in f[tree].iterate(
                step_size=step_size,
                filter_name=filter_b,
                cut=cut,
                expressions=expressions,
            )
        ),
        out_file,
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


def _filter_branches(tree, keep_branches, drop_branches):
    """
    Creates lambda function for filtering branches based on keep_branches or drop_branches.
    """
    if drop_branches and keep_branches:
        msg = "Can specify either drop_branches or keep_branches, not both."
        raise ValueError(msg) from None
    keys = []
    if drop_branches:
        if isinstance(drop_branches, str):
            keys = tree.keys(filter_name=drop_branches)
        if isinstance(drop_branches, dict) and tree.name in drop_branches:
            keys = drop_branches.get(tree.name)
        else:
            for i in drop_branches:
                keys = union1d(keys, tree.keys(filter_name=i))
        return lambda b: b in [b.name for b in tree.branches if b.name not in keys]
    if keep_branches:
        if isinstance(keep_branches, str):
            keys = tree.keys(filter_name=keep_branches)
        if isinstance(keep_branches, dict) and tree.name in keep_branches:
            keys = keep_branches.get(tree.name)
        else:
            for i in keep_branches:
                keys = union1d(keys, tree.keys(filter_name=i))
        return lambda b: b in [b.name for b in tree.branches if b.name in keys]
    return None
