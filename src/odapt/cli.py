import click
from ._version import version as __version__

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

@click.group(context_settings=CONTEXT_SETTINGS, cls=click.Group)
def cli() -> None:
    """
    Must provide a subcommand.
    """

@cli.command()
@click.argument("destination", type=click.Path())
@click.argument("file")
@click.argument("name", required=False)
@click.argument("branch_types", required=False)
@click.argument("title", required=False)
@click.argument("field_name", required=False)
@click.argument("initial_basket_capacity", required=False)
@click.argument("resize_factor", required=False)
@click.option("--force", default=True, help="If True, overwrites destination file if it already exists.")
def parquet_to_root(destination, file, *, name="tree", branch_types=None, title="", field_name=lambda outer, inner: inner if outer == "" else outer + "_" + inner,
    initial_basket_capacity=10,
    counter_name=lambda counted: "n" + counted,
    resize_factor=10.0,
    compression="lz4",
    compression_level=1,
    force=True,):
    import odapt.parquet_to_root
    odapt.parquet_to_root(destination, file, name=name, branch_types=branch_types, title=title, 
                    field_name=field_name, initial_basket_capacity=initial_basket_capacity, counter_name=counter_name,
                    resize_factor=resize_factor, compression=compression, compression_level=compression_level, force=force)

@cli.command()
@click.argument("destination", type=click.Path())
@click.argument("file")
@click.argument("drop_branches", required=False)
@click.argument("name", required=False, default="tree")
@click.argument("branch_types", required=False)
@click.option("--title", required=False, default="")
@click.option("--field_name", default=lambda outer, inner: inner if outer == "" else outer + "_" + inner, help="Function to generate TBranch names for columns of an Awkward record array or a Pandas DataFrame.")
@click.option("--initial_basket_capacity", default=10, help="Number of TBaskets that can be written to the TTree without rewriting the TTree metadata to make room.")
@click.option("--resize_factor", default=10.0, help="When the TTree metadata needs to be rewritten, this specifies how many more TBasket slots to allocate as a multiplicative factor.")
@click.option("--force", default=True, help="If True, overwrites destination file if it already exists.")
def root_to_root(destination, file, *, name="tree", branch_types=None, title="", field_name=lambda outer, inner: inner if outer == "" else outer + "_" + inner,
    initial_basket_capacity=10,
    counter_name=lambda counted: "n" + counted,
    resize_factor=10.0,
    compression="lz4",
    compression_level=1,
    force=True,):
    import odapt.copy_root
    odapt.copy_root(destination, file, name=name, branch_types=branch_types, title=title, 
                    field_name=field_name, initial_basket_capacity=initial_basket_capacity, counter_name=counter_name,
                    resize_factor=resize_factor, compression=compression, compression_level=compression_level, force=force)
  
@click.command()
@click.argument("destination")
@click.argument("files")
@click.option("--force", default=True, help="Overwrite destination file if it already exists")
@click.option("--append", default=False, help="Append histograms to an existing file")
@click.option("--compression", required=False, default="lz4")
@click.option("--compression_level", required=False, default=1)
@click.option("--skip_bad_files", default=False, help="Skip corrupt or non-existant files without exiting")
@click.option("--union", default=True, help="Adds the histograms that have the same name and appends all others to the new file")
@click.option("--same_names", default=False, help="Only adds histograms together if they have the same name")
def add(
    destination,
    files,
    *,
    force=True,
    append=False,
    compression="lz4",
    compression_level=1,
    skip_bad_files=False,
    union=True,
    same_names=False,
):
    import odapt.histogram_adding
    odapt.hadd(    
    destination,
    files,
    force=force,
    append=append,
    compression=compression,
    compression_level=compression_level,
    skip_bad_files=skip_bad_files,
    union=union,
    same_names=same_names)

@click.command()
@click.argument("destination")
@click.argument("files")
@click.argument("fieldname_separator", required=False, default="_")
@click.argument("branch_types", required=False)
@click.option("--title", required=False, default="")
@click.option("--field_name", default=lambda outer, inner: inner if outer == "" else outer + "_" + inner, help="Function to generate TBranch names for columns of an Awkward record array or a Pandas DataFrame.")
@click.option("--initial_basket_capacity", default=10, help="Number of TBaskets that can be written to the TTree without rewriting the TTree metadata to make room.")
@click.option("--resize_factor", default=10.0, help="When the TTree metadata needs to be rewritten, this specifies how many more TBasket slots to allocate as a multiplicative factor.")
@click.option("--step_size", default=100, help="If an integer, the maximum number of entries to include in each iteration step; if a string, the maximum memory size to include. The string must be a number followed by a memory unit, such as “100 MB”.")
@click.option("--force", default=True, help="Overwrite destination file if it already exists")
@click.option("--append", default=True, help="Append histograms to an existing file")
@click.option("--compression", default="lz4", help="Sets compression level for root file to write to. Can be one of \"ZLIB\", \"LZMA\", \"LZ4\", or \"ZSTD\". By default the compression algorithm is \"LZ4\".")
@click.option("--compression_level", default=1, help="Use a compression level particular to the chosen compressor. By default the compression level is 1.")
@click.option("--skip_bad_files", default=False, help="Skip corrupt or non-existant files without exiting")
@click.option("--same_names", default=False, help="Only adds histograms together if they have the same name")
def add_and_merge(    
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
    skip_bad_files=False,):
    import odapt.merge
    odapt.hadd_and_merge(    
        destination,
        files,
        fieldname_separator=fieldname_separator,
        branch_types=branch_types,
        title=title,
        field_name=field_name,
        initial_basket_capacity=initial_basket_capacity,
        resize_factor=resize_factor,
        counter_name=counter_name,
        step_size=step_size,
        force=force,
        append=append,
        compression=compression,
        compression_level=compression_level,
        skip_bad_files=skip_bad_files,)
    
    