from __future__ import annotations

from pathlib import Path

import awkward as ak
import uproot

from hepconvert import _utils
from hepconvert._utils import (
    filter_branches,
    get_counter_branches,
    group_branches,
)
from hepconvert.histogram_adding import _hadd_1d, _hadd_2d, _hadd_3d


def merge_parquet(
    out_file,
    in_files,
    *,
    # max_files=2,
    force=False,
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
    skip_bad_files=False,
):
    """Merges Parquet files together.

    Args:
        :param destination: Name of the output file or file path.
        :type destination: path-like
        :param files: List of local Parquet files to merge.
            May contain glob patterns.
        :type files: str or list of str
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

    """
    if not isinstance(in_files, list) and not isinstance(in_files, tuple):
        path = Path(in_files)
        in_files = sorted(path.glob("**/*.root"))
    if len(in_files) < 2:
        msg = f"Must have at least 2 files to merge, not {len(in_files)} files."
        raise AttributeError(msg)
    path = Path(out_file)
    if Path.is_file(path) and not force:
        raise FileExistsError

    data = False
    for file in in_files:
        try:
            ak.metadata_from_parquet(file)
        except FileNotFoundError:
            if skip_bad_files:
                continue
            msg = "File: {file} does not exist or is corrupt."
            raise FileNotFoundError(msg) from None
        if isinstance(data, bool):
            data = ak.from_parquet(file)
        else:
            data = ak.merge_union_of_records(
                ak.concatenate((data, ak.from_parquet(file))), axis=0
            )

        ak.to_parquet(
            data,
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


def merge_root(
    destination,
    files,
    *,
    keep_branches=None,
    drop_branches=None,
    keep_trees=None,
    drop_trees=None,
    cut=None,
    expressions=None,
    progress_bar=None,
    fieldname_separator="_",
    title="",
    field_name=lambda outer, inner: inner if outer == "" else outer + "_" + inner,
    initial_basket_capacity=10,
    resize_factor=10.0,
    counter_name=lambda counted: "n" + counted,
    step_size="100 MB",
    force=False,
    append=False,
    compression="zlib",
    compression_level=1,
    skip_bad_files=False,
):
    """Merges TTrees together, and adds values in histograms from local ROOT files, and writes them to a new ROOT file. Similar to ROOT's hadd function.

    :param destination: Name of the output file or file path.
    :type destination: path-like
    :param files: List of local ROOT files to merge.
        May contain glob patterns.
    :type files: str or list of str
    :param keep_branches: To keep only certain branches and remove all others. To remove certain branches from all TTrees in the file,
        pass a list of names of branches to keep, wildcarding accepted ("Jet_*"). If removing branches from one of multiple trees, pass a dict of structure: {tree: [branch1, branch2]}
        to keep only branch1 and branch2 in ttree "tree". Defaults to None. Command line option: ``--keep-branches``.
    :type keep_branches: list of str, str, or dict, optional
    :param drop_branches: To remove branches from all trees, pass a list of names of branches to
        remove. Wildcarding supported ("Jet_*"). If removing branches from one of multiple trees,
        pass a dict of structure: {tree: [branch1, branch2]} to remove branch1 and branch2 from TTree "tree". Defaults to None. Command line option: ``--drop-branches``.
    :type drop_branches: list of str, str, or dict, optional
    :param keep_trees: To keep only certain a TTrees in a file, pass a list of names of trees to keep. All others will be removed.
        Defaults to None. Command line option: ``--keep-trees``.
    :type keep_trees: str or list of str, optional
    :param drop_trees: To remove a TTree from a file, pass a list of names of trees to remove.
        Defaults to None. Command line option: ``--drop-trees``.
    :type drop_trees: str or list of str, optional
    :param cut: If not None, this expression filters all of the ``expressions``.
    :type cut: None or str
    :param expressions: Names of ``TBranches`` or aliases to convert to arrays or mathematical expressions of them.
        Uses the ``language`` to evaluate. If None, all ``TBranches`` selected by the filters are included.
    :type expressions: None, str, or list of str
    :param progress_bar: Displays a progress bar. Can input a custom tqdm progress bar object, or set ``True``
        for a default tqdm progress bar. Must have tqdm installed.
    :type progress_bar: Bool, tqdm.std.tqdm object
    :param fieldname_separator: Character that separates TBranch names for columns, used
        for grouping columns (to avoid duplicate counters in ROOT file).
    :type fieldname_separator: str, optional
    :param field_name: Function to generate TBranch names for columns
        of an Awkward record array or a Pandas DataFrame.
    :type field_name: callable of str → str, optional
    :param initial_basket_capacity: Number of TBaskets that can be written to the TTree
        without rewriting the TTree metadata to make room. Command line option: ``--initial-basket-capacity``.
    :type initial_basket_capacity: int, optional
    :param resize_factor: When the TTree metadata needs to be rewritten, this specifies how
        many more TBasket slots to allocate as a multiplicative factor. Command line option: ``--resize-factor``.
    :type resize_factor: float, optional
    :param step_size: If an integer, the maximum number of entries to include in each
        iteration step; if a string, the maximum memory size to include. The string must be
        a number followed by a memory unit, such as “100 MB”. Recommended to be >100 kB.
        Command line option: ``--step-size``.
    :type step_size: int or str
    :param force: If True, overwrites destination file if it exists. Force and append
        cannot both be True. Command line option: ``--force``.
    :type force: bool, optional
    :param append: If True, appends data to an existing file. Force and append
        cannot both be True. Command line option: ``--append``.
    :type append: bool, optional
    :param compression: Sets compression level for root file to write to. Can be one of
        "ZLIB", "LZMA", "LZ4", or "ZSTD". By default the compression algorithm is "ZLIB".
        Command line option: ``--compression``.
    :type compression: str, optional
    :param compression_level: Use a compression level particular to the chosen compressor.
        By default the compression level is 1. Command line option: ``--compression-level``.
    :type compression_level: int, optional
    :param skip_bad_files: If True, skips corrupt or non-existent files without exiting.
        Command line option: ``--skip-bad-files``.
    :type skip_bad_files: bool, optional

    Example:
    --------
        >>> hepconvert.merge_root("destination.root", ["file1.root", "file2.root"])

    Command Line Instructions:
    --------------------------
    This function can be run from the command line. Use command

    .. code-block:: bash

        hepconvert merge [options] [OUT_FILE] [IN_FILES]


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
            )
            first = True
    else:
        if append:
            msg = f"File {destination} not found. Can only append to existing files."
            raise FileNotFoundError(msg)
        out_file = uproot.recreate(
            destination,
            compression=uproot.compression.Compression.from_code_pair(
                compression_code, compression_level
            ),
        )
        first = True

    try:  # is this legal?
        step_size = int(step_size)
    except ValueError:
        step_size = str(step_size)

    if not isinstance(files, list) and not isinstance(files, tuple):
        path = Path(files)
        files = sorted(path.glob("**/*.root"))

    if len(files) <= 1:
        msg = "Only one file was input. Use copy_root to copy a ROOT file."
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

        msg = f"File: {files[0]} does not exist or is corrupt."
        raise FileNotFoundError(msg) from None
    hist_keys = f.keys(
        filter_classname=["TH*", "TProfile"], cycle=False, recursive=False
    )
    for key in f.keys(cycle=False, recursive=False):
        if key in hist_keys:
            if len(f[key].axes) == 1:
                h_sum = _hadd_1d(destination, f, key, True)
                out_file[key] = h_sum
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
                        + str(out_file)
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
                        + str(out_file)
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
    if progress_bar is not False:
        number_of_items = len(files)
        if progress_bar is True:
            tqdm = _utils.check_tqdm()
            progress_bar = tqdm.tqdm(desc="Files added")
        progress_bar.reset(number_of_items)
    for t in trees:
        branch_types = None
        tree = f[t]
        count_branches = get_counter_branches(tree)
        kb = filter_branches(tree, keep_branches, drop_branches, count_branches)
        groups, count_branches = group_branches(tree, kb)
        first = True
        for chunk in tree.iterate(
            step_size=step_size,
            how=dict,
            filter_name=lambda b: b in kb,  # noqa: B023
            cut=cut,
            expressions=expressions,
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
                    del chunk[key]
            if branch_types is None:
                branch_types = {name: array.type for name, array in chunk.items()}
            if first:
                first = False
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
                    msg = "TTrees must have the same structure to be merged. Are the branch_names correct?"

            else:
                try:
                    out_file[tree.name].extend(chunk)
                except AssertionError:
                    msg = "TTrees must have the same structure to be merged. Are the branch_names correct?"
        if progress_bar is not False:
            progress_bar.update(n=1)
        f.close()

    for file in files[1:]:
        try:
            f = uproot.open(file)
        except FileNotFoundError:
            if skip_bad_files:
                continue
            msg = "File: {file} does not exist or is corrupt."
            raise FileNotFoundError(msg) from None

        for key in f.keys(cycle=False, recursive=False):
            if key in hist_keys:
                if len(f[key].axes) == 1:
                    h_sum = _hadd_1d(destination, f, key, False)
                elif len(f[key].axes) == 2:
                    h_sum = _hadd_2d(destination, f, key, False)
                else:
                    h_sum = _hadd_3d(destination, f, key, False)

                out_file[key] = h_sum

        writable_hists = {}
        for t in trees:
            tree = f[t]
            writable_hists = []
            for key in hist_keys:
                if len(f[key].axes) == 1:
                    writable_hists[key] = _hadd_1d(destination, out_file, key, False)

                elif len(f[key].axes) == 2:
                    writable_hists[key] = _hadd_2d(destination, out_file, key, False)

                else:
                    writable_hists[key] = _hadd_3d(destination, out_file, key, False)
            if len(trees) > 1:
                count_branches = get_counter_branches(tree)
                kb = filter_branches(tree, keep_branches, drop_branches, count_branches)
            for chunk in uproot.iterate(
                tree,
                step_size=step_size,
                how=dict,
                filter_name=lambda b: b in kb,  # noqa: B023
            ):
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
                try:
                    out_file[tree.name].extend(chunk)

                except AssertionError:
                    msg = "TTrees must have the same structure to be merged"

            for key in hist_keys:
                out_file[key] = writable_hists[key]
        if progress_bar is not False:
            progress_bar.update(n=1)
        f.close()
