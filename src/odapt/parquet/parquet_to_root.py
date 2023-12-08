from __future__ import annotations

from pathlib import Path

import awkward as ak
import uproot


def to_root(
    destination,
    file,
    *,
    name="tree",
    branch_types=None,
    title="",
    field_name=lambda outer, inner: inner if outer == "" else outer + "_" + inner,
    initial_basket_capacity=10,
    counter_name=lambda counted: "n" + counted,
    resize_factor=10.0,
    compression="lz4",
    compression_level=1,
    force=True,
):
    """_summary_

    Args:
        destination (path-like): Name of the output file or file path.
        file (path-like): Local parquet file to convert.
        name (str, optional): Name of tree to write to ROOT file (this will be the key to access
            the tree in the ROOT file). Defaults to "tree".
        compression (str, optional): Sets compression level for root file to write to. Can be one of
            "ZLIB", "LZMA", "LZ4", or "ZSTD". Defaults to "lz4".
        compression_level (int, optional): Use a compression level particular to the chosen compressor. Defaults to 1.
        force (boolean, optional): If True, overwrites destination file if it exists.
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
    if Path.is_file(path) and not force:
        raise FileExistsError
    metadata = ak.metadata_from_parquet(file)

    out_file = uproot.recreate(
        destination,
        compression=uproot.compression.Compression.from_code_pair(
            compression_code, compression_level
        ),
    )

    chunk = ak.from_parquet(file, row_groups=[0])
    if not branch_types:
        branch_types = {name: chunk[name].type for name in chunk.fields}
    out_file.mktree(
        name,
        branch_types,
        title=title,
        counter_name=counter_name,
        field_name=field_name,
        initial_basket_capacity=initial_basket_capacity,
        resize_factor=resize_factor,
    )
    out_file[name].extend({name: chunk[name] for name in chunk.fields})

    for i in range(1, metadata["num_row_groups"]):
        out_file[name].extend(ak.from_parquet(file, row_groups=[i]))
