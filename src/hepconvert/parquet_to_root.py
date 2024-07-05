from __future__ import annotations

from pathlib import Path

import awkward as ak
import uproot

from hepconvert import _utils


def parquet_to_root(
    destination,
    file,
    *,
    name="tree",
    force=False,
    branch_types=None,
    progress_bar=False,
    append=False,
    title="",
    field_name=lambda outer, inner: inner if outer == "" else outer + "_" + inner,
    initial_basket_capacity=10,
    counter_name=lambda counted: "n" + counted,
    resize_factor=10.0,
    compression="ZLIB",
    compression_level=1,
):
    """Converts a Parquet file into a ROOT file. Data is stored in one TTree, which has a name defined by argument ``name``.

    :param destination: Name of the output file or file path.
    :type destination: path-like
    :param file: Local parquet file to convert.
    :type file: path-like
    :param name: Name of tree to write to ROOT file (this will be the key to access
        the tree in the ROOT file). Defaults to "tree". Command line option: ``--name``.
    :type name: str, optional
    :param branch_types: Name and type specification for the TBranches. Defaults to None.
        Command line option: ``--branch-types``.
    :type branch_types: dict or pairs of str → NumPy dtype/Awkward type, optional
    :param title: Title for new TTree. Defaults to "". Command line option: ``--title``.
    :type title: str, optional
    :param field_name: Function to generate TBranch names for columns of an Awkward
        record array or a Pandas DataFrame.
    :type field_name: callable of str → str, optional
    :param initial_basket_capacity: Number of TBaskets that can be written to the TTree
        without rewriting the TTree metadata to make room. Command line option: ``--initial-basket-capacity``.
    :type initial_basket_capacity: int, optional
    :param resize_factor: When the TTree metadata needs to be rewritten, this specifies how
      many more TBasket slots to allocate as a multiplicative factor. Command line option: ``--resize-factor``.
    :type resize_factor: float, optional
    :param compression: Sets compression level for root file to write to. Can be one of
        "ZLIB", "LZMA", "LZ4", or "ZSTD". Defaults to "zlib". Command line option: ``--compression``.
    :type compression: str, optional
    :param compression_level: Use a compression level particular to the chosen compressor. Defaults to 1.
        Command line option: ``--compression-level``.
    :type compression_level: int, optional
    :param force: If True, overwrites destination file if it exists. Command line option: ``--force``.
    :type force: boolean, optional

    Example:
    --------
        >>> hepconvert.parquet_to_root("file.root", "file.parquet", name="tree")
        >>> f = uproot.open("file.root")
        >>> data = f["tree"]

    Command Line Instructions:
    --------------------------
    This function can be run from the command line. Use command

    .. code-block:: bash

        hepconvert parquet-to-root [options] [OUT_FILE] [IN_FILE]

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
        msg = f"File {path} already exists. To overwrite it, set force=True."
        raise FileExistsError(msg)
    if append:
        if Path.is_file(path):
            out_file = uproot.update(
                destination,
                compression=uproot.compression.Compression.from_code_pair(
                    compression_code, compression_level
                ),
            )
        else:
            msg = "Cannot append to a non-existent file."
            raise FileNotFoundError(msg)

    else:
        out_file = uproot.recreate(
            destination,
            compression=uproot.compression.Compression.from_code_pair(
                compression_code, compression_level
            ),
        )
    metadata = ak.metadata_from_parquet(file)
    if progress_bar is not False:
        number_of_items = metadata["num_row_groups"]
        if progress_bar is True:
            tqdm = _utils.check_tqdm()

            progress_bar = tqdm.tqdm(desc="Row-groups written")
        progress_bar.reset(number_of_items)

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
    if progress_bar:
        progress_bar.update(n=1)

    for i in range(1, metadata["num_row_groups"]):
        out_file[name].extend(ak.from_parquet(file, row_groups=[i]))
        if progress_bar:
            progress_bar.update(n=1)
