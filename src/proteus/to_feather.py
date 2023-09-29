import pyarrow as pa
import pyarrow.parquet as pq
import awkward as ak
from fsspec import AbstractFileSystem

def parquet_to_feather(
    path,
    new_path, # ?
    *,
    columns=None,
    row_groups=None,
    storage_options=None,
    max_gap=64_000,
    max_block=256_000_000,
    footer_sample_size=1_000_000,
    generate_bitmasks=False,
    highlevel=True,
    behavior=None,
):
    """
    Args:
        path (str): Local filename or remote URL, passed to fsspec for resolution.
            May contain glob patterns.
        columns (None, str, or list of str): Glob pattern(s) with bash-like curly
            brackets for matching column names. Nested records are separated by dots.
            If a list of patterns, the logical-or is matched. If None, all columns
            are read.
        row_groups (None or set of int): Row groups to read; must be non-negative.
            Order is ignored: the output array is presented in the order specified by
            Parquet metadata. If None, all row groups/all rows are read.
        storage_options: Passed to `fsspec.parquet.open_parquet_file`.
        max_gap (int): Passed to `fsspec.parquet.open_parquet_file`.
        max_block (int): Passed to `fsspec.parquet.open_parquet_file`.
        footer_sample_size (int): Passed to `fsspec.parquet.open_parquet_file`.
        generate_bitmasks (bool): If enabled and Arrow/Parquet does not have Awkward
            metadata, `generate_bitmasks=True` creates empty bitmasks for nullable
            types that don't have bitmasks in the Arrow/Parquet data, so that the
            Form (BitMaskedForm vs UnmaskedForm) is predictable.
        highlevel (bool): If True, return an #ak.Array; otherwise, return
            a low-level #ak.contents.Content subclass.
        behavior (None or dict): Custom #ak.behavior for the output array, if
            high-level.
    
    Reads data from a local or remote Parquet file a feather file (or a collection of feather files?).

    Different from ak.to_parquet etc. because...
    """
    #create feather file?
    
    # read one page of parquet file
    parquet_file = pq.ParquetFile(path) # does this put the whole thing in memory?
    metadata = ak.metadata_from_parquet(path)
    # parquet_metadata 
    # read_row_group or with metadata?
    # batch vs page? what size? 
    # with metadata['fs'].open as fp: #why would this be necessary?
    for batch in parquet_file.iter_batches():
        pa.concat(new_path, ak.to_feather(new_path, batch)) #but this shouldn't be something that sets a var to a bigger file??




    # write to feather file - find concat without 
    # feather_file = pa.concat([ak.from_parquet(file, page) for page in pages],ignore_index=True)

