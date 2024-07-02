from __future__ import annotations

from pathlib import Path

import numpy as np
import uproot

from hepconvert import _utils


def _hadd_1d(summed_hists, in_file, key, first, *, n_key=None):
    """Supporting function for add_histograms.

    :param destination: Name of the output file or file path.
    :type destination: path-like
    :param file: ROOT file to read histogram from.
    :type file: path-like
    :param key: key to reference histogram to be added.
    :type key: str
    :param first: if True, special case for first of a certain histogram
        to be added to the new file.
    :type first: bool
    """
    try:
        hist = in_file[key] if n_key is None else in_file[n_key]
    except ValueError:
        msg = f"Key missing from {in_file.file_path}"
        raise ValueError(msg) from None
    if first:
        member_data = np.array(
            [
                hist.member("fEntries"),
                hist.member("fTsumw"),
                hist.member("fTsumw2"),
                hist.member("fTsumwx"),
                hist.member("fTsumwx2"),
            ]
        )
        return uproot.writing.identify.to_TH1x(
            hist.member("fName"),
            hist.member("fTitle"),
            hist.values(flow=True),
            *member_data,
            hist.variances(flow=False),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fXaxis").member("fNbins"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
            ),
        )
    if hist.member("fN") == summed_hists[key].member("fN"):
        member_data = np.array(
            [
                hist.member("fEntries"),
                hist.member("fTsumw"),
                hist.member("fTsumw2"),
                hist.member("fTsumwx"),
                hist.member("fTsumwx2"),
            ]
        )
        return uproot.writing.identify.to_TH1x(
            hist.member("fName"),
            hist.member("fTitle"),
            summed_hists[key].values(flow=True) + hist.values(flow=True),
            *np.add(
                np.array(
                    [
                        summed_hists[key].member("fEntries"),
                        summed_hists[key].member("fTsumw"),
                        summed_hists[key].member("fTsumw2"),
                        summed_hists[key].member("fTsumwx"),
                        summed_hists[key].member("fTsumwx2"),
                    ]
                ),
                member_data,
            ),
            summed_hists[key].variances(flow=False) + hist.variances(flow=False),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fXaxis").member("fNbins"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
            ),
        )
    msg = f"Bins must be the same for histograms to be added, not {summed_hists[key].member('fN')} and {hist.member('fN')}"
    raise ValueError(
        msg,
    ) from None


def _hadd_2d(summed_hists, file, key, first, *, n_key=None):
    """Supporting function for add_histograms.

    :param destination: Name of the output file or file path.
    :type destination: path-like
    :param file: ROOT file to read histogram from.
    :type file: path-like
    :param key: key to reference histogram to be added.
    :type key: str
    :param first: if True, special case for first of a certain histogram
        to be added to the new file.
    :type first: bool
    """
    try:
        hist = file[key] if n_key is None else file[n_key]
    except ValueError:
        msg = f"Key missing from {file}"
        raise ValueError(msg) from None
    if first:
        member_data = np.array(
            [
                hist.member("fEntries"),
                hist.member("fTsumw"),
                hist.member("fTsumw2"),
                hist.member("fTsumwx"),
                hist.member("fTsumwx2"),
                hist.member("fTsumwy"),
                hist.member("fTsumwy2"),
                hist.member("fTsumwxy"),
            ]
        )
        return uproot.writing.identify.to_TH2x(
            hist.member("fName"),
            hist.member("fTitle"),
            np.ravel(hist.values(flow=True), order="C"),
            *member_data,
            np.ravel(hist.variances(flow=False), order="C"),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fXaxis").member("fNbins"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
            ),
            uproot.writing.identify.to_TAxis(
                "fYaxis",
                "",
                hist.member("fYaxis").member("fNbins"),
                hist.axis(axis="y").low,
                hist.axis(axis="y").high,
            ),
        )
    if hist.member("fN") == summed_hists[key].member("fN"):
        member_data = np.array(
            [
                hist.member("fEntries"),
                hist.member("fTsumw"),
                hist.member("fTsumw2"),
                hist.member("fTsumwx"),
                hist.member("fTsumwx2"),
                hist.member("fTsumwy"),
                hist.member("fTsumwy2"),
                hist.member("fTsumwxy"),
            ]
        )
        return uproot.writing.identify.to_TH2x(
            hist.member("fName"),
            hist.member("fTitle"),
            np.ravel(summed_hists[key].values(flow=True), order="C")
            + np.ravel(hist.values(flow=True), order="C"),
            *np.add(
                np.array(
                    [
                        summed_hists[key].member("fEntries"),
                        summed_hists[key].member("fTsumw"),
                        summed_hists[key].member("fTsumw2"),
                        summed_hists[key].member("fTsumwx"),
                        summed_hists[key].member("fTsumwx2"),
                        summed_hists[key].member("fTsumwy"),
                        summed_hists[key].member("fTsumwy2"),
                        summed_hists[key].member("fTsumwxy"),
                    ]
                ),
                member_data,
            ),
            np.ravel(
                summed_hists[key].variances(flow=False) + hist.variances(flow=False),
                order="C",
            ),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fXaxis").member("fNbins"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
            ),
            uproot.writing.identify.to_TAxis(
                "fYaxis",
                "",
                hist.member("fYaxis").member("fNbins"),
                hist.axis(axis="y").low,
                hist.axis(axis="y").high,
            ),
        )
    msg = f"Bins must be the same for histograms to be added, not {summed_hists[key].member('fN')} and {hist.member('fN')}"
    raise ValueError(
        msg,
    ) from None


def _hadd_3d(summed_hists, file, key, first, *, n_key=None):
    """Supporting function for add_histograms.

    :param destination: Name of the output file or file path.
    :type destination: path-like
    :param file: ROOT file to read histogram from.
    :type file: path-like
    :param key: key to reference histogram to be added.
    :type key: str
    :param first: if True, special case for first of a certain histogram
        to be added to the new file.
    :type first: bool
    """
    try:
        hist = file[key] if n_key is None else file[n_key]
    except ValueError:
        msg = f"Key missing from {file}"
        raise ValueError(msg) from None
    if first:
        member_data = np.array(
            [
                hist.member("fEntries"),
                hist.member("fTsumw"),
                hist.member("fTsumw2"),
                hist.member("fTsumwx"),
                hist.member("fTsumwx2"),
                hist.member("fTsumwy"),
                hist.member("fTsumwy2"),
                hist.member("fTsumwxy"),
                hist.member("fTsumwz"),
                hist.member("fTsumwz2"),
                hist.member("fTsumwxz"),
                hist.member("fTsumwyz"),
            ]
        )
        return uproot.writing.identify.to_TH3x(
            hist.member("fName"),
            hist.member("fTitle"),
            np.ravel(hist.values(flow=True), order="C"),
            *member_data,
            np.ravel(hist.variances(flow=False), order="C"),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fXaxis").member("fNbins"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
            ),
            uproot.writing.identify.to_TAxis(
                "fYaxis",
                "",
                hist.member("fYaxis").member("fNbins"),
                hist.axis(axis="y").low,
                hist.axis(axis="y").high,
            ),
            uproot.writing.identify.to_TAxis(
                "fZaxis",
                "",
                hist.member("fZaxis").member("fNbins"),
                hist.axis(axis="z").low,
                hist.axis(axis="z").high,
            ),
        )
    if hist.member("fN") == summed_hists[key].member("fN"):
        member_data = np.add(
            np.array(
                [
                    hist.member("fEntries"),
                    hist.member("fTsumw"),
                    hist.member("fTsumw2"),
                    hist.member("fTsumwx"),
                    hist.member("fTsumwx2"),
                    hist.member("fTsumwy"),
                    hist.member("fTsumwy2"),
                    hist.member("fTsumwxy"),
                    hist.member("fTsumwz"),
                    hist.member("fTsumwz2"),
                    hist.member("fTsumwxz"),
                    hist.member("fTsumwyz"),
                ]
            ),
            np.array(
                [
                    hist.member("fEntries"),
                    summed_hists[key].member("fTsumw"),
                    summed_hists[key].member("fTsumw2"),
                    summed_hists[key].member("fTsumwx"),
                    summed_hists[key].member("fTsumwx2"),
                    summed_hists[key].member("fTsumwy"),
                    summed_hists[key].member("fTsumwy2"),
                    summed_hists[key].member("fTsumwxy"),
                    summed_hists[key].member("fTsumwz"),
                    summed_hists[key].member("fTsumwz2"),
                    summed_hists[key].member("fTsumwxz"),
                    summed_hists[key].member("fTsumwyz"),
                ]
            ),
        )
        return uproot.writing.identify.to_TH3x(
            hist.member("fName"),
            hist.member("fTitle"),
            np.ravel(
                summed_hists[key].values(flow=True) + hist.values(flow=True), order="C"
            ),
            *member_data,
            (
                np.ravel(summed_hists[key].variances(flow=False), order="C")
                + np.ravel(
                    hist.variances(flow=False),
                    order="C",
                )
            ),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fXaxis").member("fNbins"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
            ),
            uproot.writing.identify.to_TAxis(
                "fYaxis",
                "",
                hist.member("fYaxis").member("fNbins"),
                hist.axis(axis="y").low,
                hist.axis(axis="y").high,
            ),
            uproot.writing.identify.to_TAxis(
                "fZaxis",
                "",
                hist.member("fZaxis").member("fNbins"),
                hist.axis(axis="z").low,
                hist.axis(axis="z").high,
            ),
        )

    msg = f"Bins must be the same for histograms to be added, not {summed_hists[key].member('fN')} and {hist.member('fN')}"
    raise ValueError(
        msg,
    ) from None


def add_histograms(
    destination,
    files,
    *,
    progress_bar=False,
    force=True,
    append=False,
    compression="zlib",
    compression_level=1,
    skip_bad_files=False,
    union=True,
    same_names=False,
):
    """Adds together histograms from local ROOT files of a collection of ROOT files, and writes them to a new or existing ROOT file. Similar to ROOT's hadd function.

    :param destination: Name of the output file or file path.
    :type destination: path-like
    :param files: List of local ROOT files to read histograms from.
        May contain glob patterns.
    :type files: str or list of str
    :param progress_bar: Displays a progress bar. Can input a custom tqdm progress bar object, or set ``True``
        for a default tqdm progress bar. Must have tqdm installed.
    :type progress_bar: Bool, tqdm.std.tqdm object
    :param force: If True, overwrites destination file if it exists. Force and append
        cannot both be True. Defaults to True. Command line options: ``-f`` or ``--force``.
    :type force: bool, optional
    :param append: If True, appends histograms to an existing file. Force and append
        cannot both be True. Defaults to False. Command line option: ``--append``.
    :type append: bool, optional
    :param compression: Sets compression level for root file to write to. Can be one of
        "ZLIB", "LZMA", "LZ4", or "ZSTD". By default the compression algorithm is "ZLIB".
        Command line option: ``--compression``.
    :type compression: path-like, optional
    :param compression_level: Use a compression level particular to the chosen compressor.
        By default the compression level is 1. Command line option: ``--compression-level``.
    :type compression: int
    :param skip_bad_files: If True, skips corrupt or non-existent files without exiting.
        Command line option: ``--skip-bad-files``.
    :type skip_bad_files: bool, optional
    :param union: If True, adds the histograms that have the same name and appends all others
        to the new file. Defaults to True. Command line option: ``--union``.
    :type union: bool, optional
    :param same_names: If True, only adds together histograms which have the same name (key). If False,
        histograms are added together based on TTree structure (bins must be equal). Defaults to True.
        Command line option: ``--same-names``.
    :type same_names: bool, optional

    Example:
    --------
        >>> hepconvert.add_histograms("destination.root", ["file1_to_add.root", "file2_to_add.root"])

    Command Line Instructions:
    --------------------------
    This function can be run from the command line. Use command

    .. code-block:: bash

        hepconvert add [options] [OUT_FILE] [IN_FILES]

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
    p = Path(destination)
    if Path.is_file(p):
        if not force and not append:
            raise FileExistsError
        if force and append:
            msg = "Cannot append to a new file. Either force or append can be true, not both."
            raise ValueError(msg)
        if append:
            out_file = uproot.update(destination)
        else:
            out_file = uproot.recreate(
                destination,
                compression=uproot.compression.Compression.from_code_pair(
                    compression_code, compression_level
                ),
            )
    else:
        if append:
            raise FileNotFoundError(
                "File %s" + destination + " not found. File must exist to append."
            )
        out_file = uproot.recreate(
            destination,
            compression=uproot.compression.Compression.from_code_pair(
                compression_code, compression_level
            ),
        )

    if not isinstance(files, list) and not isinstance(files, tuple):
        path = Path(files)
        files = sorted(path.glob("**/*.root"))

    if len(files) <= 1:
        msg = "Cannot add one file. Use copy_root to copy a ROOT file."
        raise ValueError(msg) from None

    with uproot.open(files[0]) as file:
        keys = file.keys(filter_classname="TH[1|2|3][I|S|F|D|C]", cycle=False)
    if progress_bar is not False:
        tqdm = _utils.check_tqdm()
        number_of_items = len(files)
        if progress_bar is True:
            file_bar = tqdm.tqdm(desc="Files summed")
            file_bar.reset(number_of_items)

    if same_names:
        if union:
            for i, _value in enumerate(files[1:]):
                with uproot.open(files[i]) as file:
                    keys = np.union1d(
                        keys,
                        file.keys(filter_classname="TH[1|2|3][I|S|F|D|C]", cycle=False),
                    )
        else:
            for i, _value in enumerate(files[1:]):
                with uproot.open(files[i]) as file:
                    keys = np.intersect1d(
                        keys,
                        file.keys(filter_classname="TH[1|2|3][I|S|F|D|C]", cycle=False),
                    )
    else:
        keys = file.keys(filter_classname="TH[1|2|3][I|S|F|D|C]", cycle=False)

    first = True
    hists = {}
    for input_file in files:
        try:
            in_file = uproot.open(input_file)
        except FileNotFoundError:
            if skip_bad_files:
                continue
            msg = f"File: {input_file} does not exist or is corrupt."
            raise FileNotFoundError(msg) from None
        if same_names:
            for key in keys:
                try:
                    in_file[key]
                except ValueError:
                    if not union:
                        continue
                    msg = "Union key filter error."
                    raise ValueError(msg) from None
                if len(in_file[key].axes) == 1:
                    h_sum = _hadd_1d(hists, in_file, key, first)

                elif len(in_file[key].axes) == 2:
                    h_sum = _hadd_2d(hists, in_file, key, first)

                else:
                    h_sum = _hadd_3d(hists, in_file, key, first)

                if h_sum is not None:
                    hists[key] = h_sum
        else:
            n_keys = in_file.keys(filter_classname="TH[1|2|3][I|S|F|D|C]", cycle=False)
            for i, _value in enumerate(keys):
                if len(in_file[n_keys[i]].axes) == 1:
                    h_sum = _hadd_1d(out_file, in_file, keys[i], first, n_key=n_keys[i])

                elif len(file[n_keys[i]].axes) == 2:
                    h_sum = _hadd_2d(out_file, in_file, keys[i], first, n_key=n_keys[i])

                else:
                    h_sum = _hadd_3d(out_file, in_file, keys[i], first, n_key=n_keys[i])

                if h_sum is not None:
                    out_file[keys[i]] = h_sum
        if progress_bar:
            file_bar.update(n=1)

        first = False
        in_file.close()

    for key, h_sum in hists.items():
        out_file[key] = h_sum

    out_file.close()
