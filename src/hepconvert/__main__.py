from __future__ import annotations

import click

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS, cls=click.Group)
def main() -> None:
    """
    Must provide a subcommand:
    parquet-to-root, root-to-parquet, copy-root, add, or add
    """


@main.command()
@click.argument("destination", type=click.Path())
@click.argument("file")
@click.option("--progress-bar", is_flag=True)
@click.option("--name", type=str, required=False, default="")
@click.option("--title", type=str, required=False, default="")
@click.option(
    "--initial-basket-capacity",
    default=10,
    help="Number of TBaskets that can be written to the TTree without rewriting the TTree metadata to make room.",
)
@click.option(
    "--resize-factor",
    default=10.0,
    help="When the TTree metadata needs to be rewritten, this specifies how many more TBasket slots to allocate as a multiplicative factor.",
)
@click.option(
    "-c",
    "--compression",
    default="zlib",
    help='Sets compression level for root file to write to. Can be one of "ZLIB", "LZMA", "LZ4", or "ZSTD". By default the compression algorithm is "LZ4".',
)
@click.option(
    "--compression-level",
    default=1,
    help="Use a compression level particular to the chosen compressor. By default the compression level is 1.",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="If True, overwrites destination file if it already exists.",
)
def parquet_to_root(
    destination,
    file,
    *,
    name="tree",
    branch_types=None,
    progress_bar,
    title="",
    field_name=lambda outer, inner: inner if outer == "" else outer + "_" + inner,
    initial_basket_capacity=10,
    counter_name=lambda counted: "n" + counted,
    resize_factor=10.0,
    compression="zlib",
    compression_level=1,
    force,
):
    """
    Convert Parquet file to ROOT file.
    """
    import hepconvert.parquet_to_root  # pylint: disable=import-outside-toplevel

    hepconvert.parquet_to_root(
        destination,
        file,
        name=name,
        branch_types=branch_types,
        progress_bar=progress_bar,
        title=title,
        field_name=field_name,
        initial_basket_capacity=initial_basket_capacity,
        counter_name=counter_name,
        resize_factor=resize_factor,
        compression=compression,
        compression_level=compression_level,
        force=force,
    )


@main.command()
@click.argument("destination", type=click.Path())
@click.argument("file")
@click.option(
    "-db",
    "--drop-branches",
    default=None,
    type=list or dict or str,
    required=False,
    help="Specify branch names to remove from the ROOT file. Either a str, list of str (for multiple branches), or a dict with form {'tree': 'branches'} to remove branches from certain ttrees. Wildcarding accepted.",
)
@click.option(
    "-kb", "--keep-branches", default=None, type=list or dict or str, required=False
)
@click.option(
    "-dt",
    "--drop-trees",
    default=None,
    type=list or str,
    required=False,
    help="Specify tree names to remove from the ROOT file. Wildcarding accepted.",
)
@click.option(
    "-kt",
    "--keep-trees",
    default=None,
    type=list or str,
    required=False,
    help="Specify tree names to keep in the ROOT file. All others will be removed. Wildcarding accepted.",
)
@click.option("--progress-bar", is_flag=True)
@click.option("--cut", default=None, type=str or list, required=False)
@click.option("--expressions", default=None, type=str or list, required=False)
@click.option("--title", type=str, required=False, default="")
@click.option(
    "--initial-basket-capacity",
    default=10,
    help="Number of TBaskets that can be written to the TTree without rewriting the TTree metadata to make room.",
)
@click.option(
    "--resize-factor",
    default=10.0,
    help="When the TTree metadata needs to be rewritten, this specifies how many more TBasket slots to allocate as a multiplicative factor.",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="If True, overwrites destination file if it already exists.",
)
def copy_root(
    destination,
    file,
    *,
    drop_branches=None,
    keep_branches=None,
    drop_trees=None,
    keep_trees=None,
    cut=None,
    expressions=None,
    progress_bar,
    force,
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
    Copy root file.
    """
    import hepconvert.copy_root  # pylint: disable=import-outside-toplevel

    hepconvert.copy_root(
        destination,
        file,
        drop_branches=drop_branches,
        keep_branches=keep_branches,
        drop_trees=drop_trees,
        keep_trees=keep_trees,
        cut=cut,
        expressions=expressions,
        progress_bar=progress_bar,
        force=force,
        title=title,
        field_name=field_name,
        initial_basket_capacity=initial_basket_capacity,
        resize_factor=resize_factor,
        counter_name=counter_name,
        step_size=step_size,
        compression=compression,
        compression_level=compression_level,
    )


@main.command()
@click.argument("destination")
@click.argument("files", nargs=-1)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Overwrite destination file if it already exists",
)
@click.option("--progress-bar", is_flag=True)
@click.option(
    "-a", "--append", is_flag=True, help="Append histograms to an existing file"
)
@click.option(
    "-c",
    "--compression",
    default="zlib",
    type=str,
    help='Sets compression level for root file to write to. Can be one of "ZLIB", "LZMA", "LZ4", or "ZSTD". By default the compression algorithm is "ZLIB".',
)
@click.option(
    "--compression-level",
    default=1,
    type=int,
    help="Use a compression level particular to the chosen compressor. By default the compression level is 1.",
)
@click.option(
    "--skip-bad-files",
    is_flag=True,
    help="Skip corrupt or non-existent files without exiting",
)
@click.option(
    "--union",
    is_flag=True,
    help="Adds the histograms that have the same name and appends all others to the new file",
)
@click.option(
    "--same-names",
    is_flag=True,
    help="Only adds histograms together if they have the same name",
)
def add(
    destination,
    files,
    *,
    progress_bar,
    force,
    append,
    compression="zlib",
    compression_level=1,
    skip_bad_files,
    union,
    same_names,
):
    """
    Sums histograms and writes them to a new file.
    """
    import hepconvert.histogram_adding  # pylint: disable=import-outside-toplevel

    hepconvert.add_histograms(
        destination,
        files,
        progress_bar=progress_bar,
        force=force,
        append=append,
        compression=compression,
        compression_level=compression_level,
        skip_bad_files=skip_bad_files,
        union=union,
        same_names=same_names,
    )


@main.command()
@click.argument("destination")
@click.argument("files", nargs=-1)
@click.option("--title", required=False, default="", help="Set title of new TTree.")
@click.option(
    "--initial-basket-capacity",
    default=10,
    help="Number of TBaskets that can be written to the TTree without rewriting the TTree metadata to make room.",
)
@click.option(
    "--resize-factor",
    default=10.0,
    help="When the TTree metadata needs to be rewritten, this specifies how many more TBasket slots to allocate as a multiplicative factor.",
)
@click.option(
    "--step-size",
    default="100 MB",
    type=int or str,
    help="If an integer, the maximum number of entries to include in each iteration step; if a string, the maximum memory size to include. The string must be a number followed by a memory unit, such as “100 MB”.",
)
@click.option(
    "-db",
    "--drop-branches",
    default=None,
    type=list or dict or str,
    required=False,
    help="Specify branch names to remove from the ROOT file. Either a str, list of str (for multiple branches), or a dict with form {'tree': 'branches'} to remove branches from certain ttrees. Wildcarding accepted.",
)
@click.option(
    "-kb", "--keep-branches", default=None, type=list or dict or str, required=False
)
@click.option(
    "-dt",
    "--drop-trees",
    default=None,
    type=list or str,
    required=False,
    help="Specify tree names to remove from the ROOT file. Wildcarding accepted.",
)
@click.option(
    "-kt",
    "--keep-trees",
    default=None,
    type=list or str,
    required=False,
    help="Specify tree names to keep in the ROOT file.. Wildcarding accepted.",
)
@click.option("--progress-bar", is_flag=True)
@click.option("--cut", default=None, type=str or list, required=False)
@click.option("--expressions", default=None, type=str or list, required=False)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Overwrite destination file if it already exists",
)
@click.option(
    "-a", "--append", is_flag=True, help="Append histograms to an existing file"
)
@click.option(
    "-c",
    "--compression",
    default="zlib",
    help='Sets compression level for root file to write to. Can be one of "ZLIB", "LZMA", "LZ4", or "ZSTD". By default the compression algorithm is "LZ4".',
)
@click.option(
    "--compression-level",
    default=1,
    help="Use a compression level particular to the chosen compressor. By default the compression level is 1.",
)
@click.option(
    "--skip-bad-files",
    default=False,
    help="Skip corrupt or non-existent files without exiting",
)
def merge_root(
    destination,
    files,
    *,
    fieldname_separator="_",
    title="",
    field_name=lambda outer, inner: inner if outer == "" else outer + "_" + inner,
    drop_branches=None,
    keep_branches=None,
    drop_trees=None,
    keep_trees=None,
    cut=None,
    expressions=None,
    progress_bar,
    initial_basket_capacity=10,
    resize_factor=10.0,
    counter_name=lambda counted: "n" + counted,
    step_size="100 MB",
    force,
    append,
    compression="LZ4",
    compression_level=1,
    skip_bad_files=False,
):
    """
    Merge TTrees and add histograms.
    """
    import hepconvert.merge  # pylint: disable=import-outside-toplevel

    hepconvert.merge_root(
        destination,
        files,
        fieldname_separator=fieldname_separator,
        title=title,
        field_name=field_name,
        drop_branches=drop_branches,
        keep_branches=keep_branches,
        drop_trees=drop_trees,
        keep_trees=keep_trees,
        cut=cut,
        expressions=expressions,
        progress_bar=progress_bar,
        initial_basket_capacity=initial_basket_capacity,
        resize_factor=resize_factor,
        counter_name=counter_name,
        step_size=step_size,
        force=force,
        append=append,
        compression=compression,
        compression_level=compression_level,
        skip_bad_files=skip_bad_files,
    )


@main.command()
@click.argument("in-file", required=True)
@click.argument("out-file", required=True)
@click.option(
    "-t",
    "--tree",
    default=False,
    type=bool,
    help="Specify the name of a tree to write to Parquet, if there are multiple trees in the ROOT file.",
)
@click.option(
    "-db",
    "--drop-branches",
    default=None,
    type=list or dict or str,
    required=False,
    help="Specify branch names to remove from the ROOT file. Either a str, list of str (for multiple branches), or a dict with form {'tree': 'branches'} to remove branches from certain ttrees. Wildcarding accepted.",
)
@click.option(
    "-kb",
    "--keep-branches",
    default=None,
    type=list or dict or str,
    required=False,
    help="Specify branch names to keep in the ROOT file. Either a str, list of str (for multiple branches), or a dict with form {'tree': 'branches'} to keep only certain branches in certain ttrees. Wildcarding accepted.",
)
@click.option("--cut", default=None, type=str or list, required=False)
@click.option("--expressions", default=None, type=str or list, required=False)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    type=bool,
    help="If a file already exists at specified path, it gets replaced",
)
@click.option(
    "-s",
    "--step-size",
    type=int or str,
    default="100 MB",
    help="Specify batch size for reading ROOT file. If an integer, the maximum number of entries to include in each iteration step; if a string, the maximum memory size to include.",
)
@click.option(
    "--list-to32",
    default=False,
    type=bool,
    help="If True, convert Awkward lists into 32-bit Arrow lists if they're small enough.",
)
@click.option(
    "--string-to32",
    default=True,
    type=bool,
    help="If True, convert Awkward lists into 32-bit Arrow string if they're small enough.",
)
@click.option(
    "--bytestring-to32",
    default=True,
    type=bool,
    help="If True, convert Awkward lists into 32-bit Arrow binary if they're small enough.",
)
@click.option(
    "--emptyarray-to",
    default=None,
    help="If None, #ak.types.UnknownType maps to Arrow's null type; otherwise, it is converted a given numeric dtype.",
)
@click.option(
    "--categorical-as-dictionary",
    default=False,
    help='If True, ak.contents.IndexedArray and ak.contents.IndexedOptionArray labeled with __array__ = "categorical" are mapped to Arrow `DictionaryArray`; otherwise, the projection is evaluated before conversion.',
)
@click.option(
    "--extensionarray",
    default=True,
    type=bool,
    help="If True, this function returns extended Arrow arrays (at all levels of nesting), which preserve metadata so that Awkward \u2192 Arrow \u2192 Awkward preserves the array's ak.types.Type (though not the ak.forms.Form). If False, this function returns generic Arrow arrays that might be needed for third-party tools that don't recognize Arrow's extensions.",
)
@click.option(
    "--count-nulls",
    default=True,
    type=bool,
    help="Count the number of missing values at each level and include these in the resulting Arrow array, which makes some downstream applications faster. If False, skip the up-front cost of counting them.",
)
@click.option(
    "-c",
    "--compression",
    default=False,
    type=bool,
    help='Compression algorithm name Parquet supports {"NONE", "SNAPPY", "GZIP", "BROTLI", "LZ4", "ZSTD"}',
)
@click.option(
    "--compression-level",
    default=None,
    type=int,
    help="Set compression level for chosen compression algorithm.",
)
@click.option(
    "-rg",
    "--row-group-size",
    default=64 * 1024 * 1024,
    type=int,
    help="Choose number of entries in each row-group (except the last).",
)
@click.option(
    "--data-page-size", default=None, help="Choose number of bytes in each data page."
)
@click.option(
    "--parquet-flavor",
    default=None,
    help='Choose flavor. If None, the output Parquet file will follow Arrow conventions; if "spark", it will follow Spark conventions.',
)
@click.option(
    "--parquet-version", default="2.4", type=str, help="Parquet file format version."
)
@click.option(
    "--parquet-page-version",
    default="1.0",
    type=str,
    help="Parquet page format version.",
)
@click.option(
    "--parquet-metadata-statistics",
    default=True,
    type=bool,
    help="Include summary statistics for each data page in the Parquet metadata.",
)
@click.option(
    "--parquet-dictionary-encoding",
    default=False,
    type=bool,
    help="Allow Parquet to pre-compress with dictionary encoding.",
)
@click.option(
    "--parquet-byte-stream-split",
    default=False,
    type=bool,
    help="Pre-compress floating point fields ('float32' or 'float64') with byte stream splitting.",
)
@click.option(
    "--parquet-coerce-timestamps",
    default=None,
    type=str,
    help="Choose resolution of timestamps.",
)
@click.option(
    "--parquet-old-int96-timestamps",
    default=None,
    type=bool,
    help="Choose to use INT96 format for any timestamps.",
)
@click.option(
    "--parquet-compliant-nested",
    default=False,
    type=bool,
    help="Choose to use the Spark/BigQuery/Parquet convention for nested list.",
)
@click.option(
    "--parquet-extra-options",
    default=None,
    type=dict,
    help="Options to pass to pyarrow.parquet.ParquetWriter",
)
@click.option(
    "--storage-options",
    default=None,
    type=dict,
    help="Any additional options to pass to fsspec.core.url_to_fs to open a remote file for writing.",
)
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
    """
    Convert ROOT to Parquet.
    """
    import hepconvert.root_to_parquet  # pylint: disable=import-outside-toplevel

    hepconvert.root_to_parquet(
        in_file=in_file,
        out_file=out_file,
        tree=tree,
        drop_branches=drop_branches,
        keep_branches=keep_branches,
        cut=cut,
        expressions=expressions,
        force=force,
        step_size=step_size,
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


if __name__ == "__main__":
    main()
