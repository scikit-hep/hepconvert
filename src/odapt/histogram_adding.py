from __future__ import annotations

from pathlib import Path

import numpy as np
import uproot


def hadd_1d(destination, file, key, first, *, n_key=None):
    """Supporting function for hadd.

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
        msg = "Key missing from {file}"
        raise ValueError(msg) from None
    # if file[key].classname == "TProfile":
    #     return TProfile_1d(destination, file, key, first, n_key=n_key)
    outfile = uproot.open(destination)
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
            hist.variances(flow=True),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fN"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
                fXbins=hist.member("fXaxis").edges(flow=True),
            ),
        )
    if hist.member("fN") == outfile[key].member("fN"):
        member_data = np.array(
            [
                hist.member("fEntries"),
                hist.member("fTsumw"),
                hist.member("fTsumw2"),
                hist.member("fTsumwx"),
                hist.member("fTsumwx2"),
            ]
        )
        h_sum = uproot.writing.identify.to_TH1x(
            hist.member("fName"),
            hist.member("fTitle"),
            outfile[key].values(flow=True) + hist.values(flow=True),
            *np.add(
                np.array(
                    [
                        outfile[key].member("fEntries"),
                        outfile[key].member("fTsumw"),
                        outfile[key].member("fTsumw2"),
                        outfile[key].member("fTsumwx"),
                        outfile[key].member("fTsumwx2"),
                    ]
                ),
                member_data,
            ),
            outfile[key].variances(flow=True) + hist.variances(flow=True),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fN"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
                fXbins=hist.member("fXaxis").edges(flow=True),
            ),
        )
        outfile.close()
        return h_sum

    msg = "Bins must be the same for histograms to be added, not "
    raise ValueError(
        msg,
        hist.member("fN"),
        " and ",
        outfile[key].member("fN"),
    ) from None


def hadd_2d(destination, file, key, first, *, n_key=None):
    """Supporting function for hadd.

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
        msg = "Key missing from {file}"
        raise ValueError(msg) from None
    # if file[key].classname == "TProfile2D":
    #     return TProfile_2d(destination, file, key, first, n_key=n_key)
    outfile = uproot.open(destination)
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
            np.ravel(hist.variances(flow=True), order="C"),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fXaxis").member("fNbins"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
                fXbins=hist.member("fXaxis").edges(flow=True),
            ),
            uproot.writing.identify.to_TAxis(
                "fYaxis",
                "",
                hist.member("fYaxis").member("fNbins"),
                hist.axis(axis="y").low,
                hist.axis(axis="y").high,
            ),
        )
    if hist.member("fN") == outfile[key].member("fN"):
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
        h_sum = uproot.writing.identify.to_TH2x(
            hist.member("fName"),
            hist.member("fTitle"),
            np.ravel(outfile[key].values(flow=True), order="C")
            + np.ravel(hist.values(flow=True), order="C"),
            *np.add(
                np.array(
                    [
                        outfile[key].member("fEntries"),
                        outfile[key].member("fTsumw"),
                        outfile[key].member("fTsumw2"),
                        outfile[key].member("fTsumwx"),
                        outfile[key].member("fTsumwx2"),
                        outfile[key].member("fTsumwy"),
                        outfile[key].member("fTsumwy2"),
                        outfile[key].member("fTsumwxy"),
                    ]
                ),
                member_data,
            ),
            np.ravel(
                outfile[key].variances(flow=True) + hist.variances(flow=True), order="C"
            ),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fXaxis").member("fNbins"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
                fXbins=hist.member("fXaxis").edges(flow=True),
            ),
            uproot.writing.identify.to_TAxis(
                "fYaxis",
                "",
                hist.member("fYaxis").member("fNbins"),
                hist.axis(axis="y").low,
                hist.axis(axis="y").high,
            ),
        )
        outfile.close()
        return h_sum

    msg = "Bins must be the same for histograms to be added, not "
    raise ValueError(
        msg,
        hist.member("fN"),
        " and ",
        outfile[key].member("fN"),
    ) from None


def hadd_3d(destination, file, key, first, *, n_key=None):
    """Supporting function for hadd.

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
        msg = "Key missing from {file}"
        raise ValueError(msg) from None
    # if file[key].classname == "TProfile3D":
    #     return TProfile_3d(destination, file, key, first, n_key=n_key)
    outfile = uproot.open(destination)
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
            np.ravel(hist.variances(flow=True), order="C"),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fXaxis").member("fNbins"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
                fXbins=hist.member("fXaxis").edges(flow=True),
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
    if hist.member("fN") == outfile[key].member("fN"):
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
                    outfile[key].member("fTsumw"),
                    outfile[key].member("fTsumw2"),
                    outfile[key].member("fTsumwx"),
                    outfile[key].member("fTsumwx2"),
                    outfile[key].member("fTsumwy"),
                    outfile[key].member("fTsumwy2"),
                    outfile[key].member("fTsumwxy"),
                    outfile[key].member("fTsumwz"),
                    outfile[key].member("fTsumwz2"),
                    outfile[key].member("fTsumwxz"),
                    outfile[key].member("fTsumwyz"),
                ]
            ),
        )
        h_sum = uproot.writing.identify.to_TH3x(
            hist.member("fName"),
            hist.member("fTitle"),
            np.ravel(
                outfile[key].values(flow=True) + hist.values(flow=True), order="C"
            ),
            *member_data,
            (
                np.ravel(outfile[key].variances(flow=True), order="C")
                + np.ravel(
                    hist.variances(flow=True),
                    order="C",
                )
            ),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fXaxis").member("fNbins"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
                fXbins=hist.member("fXaxis").edges(flow=True),
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
        outfile.close()
        return h_sum

    msg = "Bins must be the same for histograms to be added, not "
    raise ValueError(
        msg,
        hist.member("fN"),
        " and ",
        outfile[key].member("fN"),
    ) from None


def hadd(
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
    """Adds together histograms from local ROOT files of a collection of ROOT files, and writes them to a new or existing ROOT file.

    :param destination: Name of the output file or file path.
    :type destination: path-like
    :param files: List of local ROOT files to read histograms from.
        May contain glob patterns.
    :type files: str or list of str
    :param force: If True, overwrites destination file if it exists. Force and append
        cannot both be True. Defaults to True. Command line options: ``-f`` or ``--force``.
    :type force: bool, optional
    :param append: If True, appends histograms to an existing file. Force and append
        cannot both be True. Defaults to False. Command line option: ``--append``.
    :type append: bool, optional
    :param compression: Sets compression level for root file to write to. Can be one of
        "ZLIB", "LZMA", "LZ4", or "ZSTD". By default the compression algorithm is "LZ4".
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
        >>> odapt.hadd("destination.root", ["file1_to_hadd.root", "file2_to_hadd.root"])

    Command Line Instructions:
    --------------------------
    This function can be run from the command line. Use command

        >>> odapt add [options] [OUT_FILE] [IN_FILES]

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
            msg = "Cannot append to a new file. Either force or append can be true."
            raise ValueError(msg)
        file_out = uproot.recreate(
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
        file_out = uproot.recreate(
            destination,
            compression=uproot.compression.Compression.from_code_pair(
                compression_code, compression_level
            ),
        )

    if not isinstance(files, list):
        path = Path(files)
        files = sorted(path.glob("**/*.root"))

    if len(files) <= 1:
        msg = "Cannot hadd one file. Use root_to_root to copy a ROOT file."
        raise ValueError(msg) from None

    with uproot.open(files[0]) as file:
        keys = file.keys(filter_classname="TH[1|2|3][I|S|F|D|C]", cycle=False)
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
    for input_file in files:
        p = Path(input_file)
        if Path.is_file(p):
            file_out = uproot.update(destination)
        else:
            file_out = uproot.recreate(
                destination,
                compression=uproot.compression.Compression.from_code_pair(
                    compression_code, compression_level
                ),
            )

        try:
            file = uproot.open(input_file)
        except FileNotFoundError:
            if skip_bad_files:
                continue
            msg = "File: {input_file} does not exist or is corrupt."
            raise FileNotFoundError(msg) from None
        if same_names:
            for key in keys:
                try:
                    file[key]
                except ValueError:
                    if not union:
                        continue
                    msg = "Union key filter error."
                    raise ValueError(msg) from None
                if len(file[key].axes) == 1:
                    h_sum = hadd_1d(destination, file, key, first)

                elif len(file[key].axes) == 2:
                    h_sum = hadd_2d(destination, file, key, first)

                else:
                    h_sum = hadd_3d(destination, file, key, first)

        else:
            n_keys = file.keys(filter_classname="TH[1|2|3][I|S|F|D|C]", cycle=False)
            for i, _value in enumerate(keys):
                if len(file[n_keys[i]].axes) == 1:
                    h_sum = hadd_1d(destination, file, keys[i], first, n_key=n_keys[i])

                elif len(file[n_keys[i]].axes) == 2:
                    h_sum = hadd_2d(destination, file, keys[i], first, n_key=n_keys[i])

                else:
                    h_sum = hadd_3d(destination, file, keys[i], first, n_key=n_keys[i])

                if h_sum is not None:
                    file_out[keys[i]] = h_sum

        first = False
        file.close()


def tprofile_1d(destination, file, key, first, *, n_key=None):
    """
    Args:
    :param destination: Name of the output file or file path.
    :type destination: path-like
    :param file: ROOT file to read histogram from.
    :type file: ReadOnlyDirectory
    :key: key to reference histogram to be added.
    :type key: str
    :param first: if True, special case for first of a certain histogram
        to be added to the new file.
    :type first: str
    """
    hist = file[key] if n_key is None else file[n_key]
    outfile = uproot.open(destination)
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
            ]
        )
        return uproot.writing.identify.to_TProfile(
            hist.member("fName"),
            hist.member("fTitle"),
            hist.values(flow=True),
            *member_data,
            hist.member("fSumw2"),
            hist.member("fBinEntries"),
            hist.member("fBinSumw2"),
            hist.variances(flow=True),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fN"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
                fXbins=hist.member("fXaxis").edges(flow=True),
            ),
        )
    if hist.member("fN") == outfile[key].member("fN"):
        member_data = np.array(
            [
                hist.member("fEntries"),
                hist.member("fTsumw"),
                hist.member("fTsumw2"),
                hist.member("fTsumwx"),
                hist.member("fTsumwx2"),
                hist.member("fTsumwy"),
                hist.member("fTsumwy2"),
            ]
        )
        h_sum = uproot.writing.identify.to_TProfile(
            hist.member("fName"),
            hist.member("fTitle"),
            outfile[key].values(flow=True) + hist.values(flow=True),
            *np.add(
                np.array(
                    [
                        outfile[key].member("fEntries"),
                        outfile[key].member("fTsumw"),
                        outfile[key].member("fTsumw2"),
                        outfile[key].member("fTsumwx"),
                        outfile[key].member("fTsumwx2"),
                        outfile[key].member("fTsumwy"),
                        outfile[key].member("fTsumwy2"),
                        outfile[key].member("fSumw2"),
                        outfile[key].member("fBinEntries"),
                        outfile[key].member("fBinSumw2"),
                    ]
                ),
                member_data,
            ),
            outfile[key].member("fSumw2") + hist.member("fSumw2"),
            outfile[key].member("fBinEntries") + hist.member("fBinEntries"),
            outfile[key].member("fBinEntries") + hist.member("fBinSumw2"),
            outfile[key].variances(flow=True) + hist.variances(flow=True),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fN"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
                fXbins=hist.member("fXaxis").edges(flow=True),
            ),
        )
        outfile.close()
        return h_sum

    msg = "Bins must be the same for histograms to be added, not "
    raise ValueError(
        msg,
        hist.member("fN"),
        " and ",
        outfile[key].member("fN"),
    ) from None


def tprofile_2d(destination, file, key, first, *, n_key=None):
    """
    Args:
    :param destination: Name of the output file or file path.
    :type destination: path-like
    :param file: ROOT file to read histogram from.
    :type file: ReadOnlyDirectory
    :key: key to reference histogram to be added.
    :type key: str
    :param first: if True, special case for first of a certain histogram
        to be added to the new file.
    :type first: str
    """
    outfile = uproot.open(destination)
    hist = file[key] if n_key is None else file[n_key]

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
                hist.member("fSumw2"),
                hist.member("fBinEntries"),
                hist.member("fBinSumw2"),
            ]
        )
        return uproot.writing.identify.to_TProfile2D(
            hist.member("fName"),
            hist.member("fTitle"),
            np.ravel(hist.values(flow=True), order="C"),
            *member_data,
            np.ravel(hist.variances(flow=True), order="C"),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fXaxis").member("fNbins"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
                fXbins=hist.member("fXaxis").edges(flow=True),
            ),
            uproot.writing.identify.to_TAxis(
                "fYaxis",
                "",
                hist.member("fYaxis").member("fNbins"),
                hist.axis(axis="y").low,
                hist.axis(axis="y").high,
            ),
        )
    if hist.member("fN") == outfile[key].member("fN"):
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
                hist.member("fSumw2"),
                hist.member("fBinEntries"),
                hist.member("fBinSumw2"),
            ]
        )
        h_sum = uproot.writing.identify.to_TH2x(
            hist.member("fName"),
            hist.member("fTitle"),
            np.ravel(outfile[key].values(flow=True), order="C")
            + np.ravel(hist.values(flow=True), order="C"),
            *np.add(
                np.array(
                    [
                        outfile[key].member("fEntries"),
                        outfile[key].member("fTsumw"),
                        outfile[key].member("fTsumw2"),
                        outfile[key].member("fTsumwx"),
                        outfile[key].member("fTsumwx2"),
                        outfile[key].member("fTsumwy"),
                        outfile[key].member("fTsumwy2"),
                        outfile[key].member("fTsumwxy"),
                        outfile[key].member("fTsumwz"),
                        outfile[key].member("fTsumwz2"),
                        outfile[key].member("fSumw2"),
                        outfile[key].member("fBinEntries"),
                        outfile[key].member("fBinSumw2"),
                    ]
                ),
                member_data,
            ),
            np.ravel(
                outfile[key].variances(flow=True) + hist.variances(flow=True), order="C"
            ),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fXaxis").member("fNbins"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
                fXbins=hist.member("fXaxis").edges(flow=True),
            ),
            uproot.writing.identify.to_TAxis(
                "fYaxis",
                "",
                hist.member("fYaxis").member("fNbins"),
                hist.axis(axis="y").low,
                hist.axis(axis="y").high,
            ),
        )
        outfile.close()
        return h_sum

    msg = "Bins must be the same for histograms to be added, not "
    raise ValueError(
        msg,
        hist.member("fN"),
        " and ",
        outfile[key].member("fN"),
    ) from None


def tprofile_3d(destination, file, key, first, *, n_key=None):
    """
    Args:
    :param destination: Name of the output file or file path.
    :type destination: path-like
    :param file: ROOT file to read histogram from.
    :type file: ReadOnlyDirectory
    :key: key to reference histogram to be added.
    :type key: str
    :param first: if True, special case for first of a certain histogram
        to be added to the new file.
    :type first: str
    """
    outfile = uproot.open(destination)
    hist = file[key] if n_key is None else file[n_key]

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
                hist.member("fTsumwxyz"),
                hist.member("fTsumwt"),
                hist.member("fTsumwt2"),
                hist.member("fSumw2"),
                hist.member("fBinEntries"),
                hist.member("fBinSumw2"),
            ]
        )
        return uproot.writing.identify.to_TProfile2D(
            hist.member("fName"),
            hist.member("fTitle"),
            np.ravel(hist.values(flow=True), order="C"),
            *member_data,
            np.ravel(hist.variances(flow=True), order="C"),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fXaxis").member("fNbins"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
                fXbins=hist.member("fXaxis").edges(flow=True),
            ),
            uproot.writing.identify.to_TAxis(
                "fYaxis",
                "",
                hist.member("fYaxis").member("fNbins"),
                hist.axis(axis="y").low,
                hist.axis(axis="y").high,
            ),
        )
    if hist.member("fN") == outfile[key].member("fN"):
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
                hist.member("fTsumwxyz"),
                hist.member("fTsumwt"),
                hist.member("fTsumwt2"),
                hist.member("fSumw2"),
                hist.member("fBinEntries"),
                hist.member("fBinSumw2"),
            ]
        )
        h_sum = uproot.writing.identify.to_TH2x(
            hist.member("fName"),
            hist.member("fTitle"),
            np.ravel(outfile[key].values(flow=True), order="C")
            + np.ravel(hist.values(flow=True), order="C"),
            *np.add(
                np.array(
                    [
                        outfile[key].member("fEntries"),
                        outfile[key].member("fTsumw"),
                        outfile[key].member("fTsumw2"),
                        outfile[key].member("fTsumwx"),
                        outfile[key].member("fTsumwx2"),
                        outfile[key].member("fTsumwy"),
                        outfile[key].member("fTsumwy2"),
                        outfile[key].member("fTsumwxy"),
                        outfile[key].member("fTsumwz"),
                        outfile[key].member("fTsumwz2"),
                        outfile[key].member("fTsumwxz"),
                        outfile[key].member("fTsumwxyz"),
                        outfile[key].member("fTsumwt"),
                        outfile[key].member("fTsumwt2"),
                        outfile[key].member("fSumw2"),
                        outfile[key].member("fBinEntries"),
                        outfile[key].member("fBinSumw2"),
                    ]
                ),
                member_data,
            ),
            np.ravel(
                outfile[key].variances(flow=True) + hist.variances(flow=True), order="C"
            ),
            uproot.writing.identify.to_TAxis(
                "fXaxis",
                "",
                hist.member("fXaxis").member("fNbins"),
                hist.axis(axis="x").low,
                hist.axis(axis="x").high,
                fXbins=hist.member("fXaxis").edges(flow=True),
            ),
            uproot.writing.identify.to_TAxis(
                "fYaxis",
                "",
                hist.member("fYaxis").member("fNbins"),
                hist.axis(axis="y").low,
                hist.axis(axis="y").high,
            ),
        )
        outfile.close()
        return h_sum

    msg = "Bins must be the same for histograms to be added, not "
    raise ValueError(
        msg,
        hist.member("fN"),
        " and ",
        outfile[key].member("fN"),
    ) from None
