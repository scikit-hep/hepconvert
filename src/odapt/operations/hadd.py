from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import uproot


def hadd_1d(destination, file, key, first, *, n_key=None):
    """
    Args:
    destination (path-like): Name of the output file or file path.
    file (ReadOnlyDirectory): ROOT file to read histogram from.
    key (str): key to reference histogram to be added.
    first (bool): if True, special case for first of a certain histogram
        to be added to the new file.
    """
    outfile = uproot.open(destination)
    try:
        hist = file[key] if n_key is None else file[n_key]
    except ValueError:
        msg = "Key missing from {file}"
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
    """
    Args:
    destination (path-like): Name of the output file or file path.
    file (ReadOnlyDirectory): ROOT file to read histogram from.
    key (str): key to reference histogram to be added.
    first (bool): if True, special case for first of a certain histogram
        to be added to the new file.
    """
    outfile = uproot.open(destination)
    try:
        hist = file[key] if n_key is None else file[n_key]
    except ValueError:
        msg = "Key missing from {file}"
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
    """
    Args:
    destination (path-like): Name of the output file or file path.
    file (ReadOnlyDirectory): ROOT file to read histogram from.
    key (str): key to reference histogram to be added.
    first (bool): if True, special case for first of a certain histogram
        to be added to the new file.
    """
    outfile = uproot.open(destination)
    try:
        hist = file[key] if n_key is None else file[n_key]
    except ValueError:
        msg = "Key missing from {file}"
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


def main():
    """
    Implementation of cmd-line executables.
    """
    argparser = argparse.ArgumentParser(description="Hadd ROOT histograms with Uproot")
    argparser.add_argument("destination", type=str, help="path of output file")
    argparser.add_argument(
        "input_files",
        type=str,
        nargs="+",
        help="list or directory (glob syntax accepted) of input files",
    )
    argparser.add_argument(
        "-f",
        "--force",
        action="store_true",
        default=True,
        help="force overwrite of output file",
    )
    argparser.add_argument(
        "-a", "--append", action="store", default=False, help="append to existing file"
    )
    argparser.add_argument(
        "-c",
        "--compression",
        action="store",
        default="lz4",
        help="set compression level between 1-9",
    )
    argparser.add_argument(
        "-c[0-9]",
        "--compression_level",
        action="store",
        default=1,
        help="set compression level between 1-9",
    )
    argparser.add_argument(
        "-k",
        "--skip_bad_files",
        action="store",
        default=False,
        help="corrupt or non-existent input files are ignored",
    )
    argparser.add_argument(
        "-u",
        action="union",
        default=True,
        help="all histograms get copied to new file, only those with same name get added",
    )

    args = argparser.parse_args()

    hadd(
        args.destination,
        args.input_file,
        force=args.force,
        append=args.append,
        compression=args.compression,
        compression_level=args.compression_level,
        skip_bad_files=args.skip_bad_files,
        union=args.union,
    )


# def hadd_in_merge():
