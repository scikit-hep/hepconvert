from __future__ import annotations

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
    """
    Args:
    destination (path-like): Name of the output file or file path.
    file (ReadOnlyDirectory): ROOT file to read histogram from.
    key (str): key to reference histogram to be added.
    first (bool): if True, special case for first of a certain histogram
        to be added to the new file.
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
    """
    Args:
    destination (path-like): Name of the output file or file path.
    file (ReadOnlyDirectory): ROOT file to read histogram from.
    key (str): key to reference histogram to be added.
    first (bool): if True, special case for first of a certain histogram
        to be added to the new file.
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


def TProfile_1d(destination, file, key, first, *, n_key=None):
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


def TProfile_2d(destination, file, key, first, *, n_key=None):
    """
    Args:
    destination (path-like): Name of the output file or file path.
    file (ReadOnlyDirectory): ROOT file to read histogram from.
    key (str): key to reference histogram to be added.
    first (bool): if True, special case for first of a certain histogram
        to be added to the new file.
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


def TProfile_3d(destination, file, key, first, *, n_key=None):
    """
    Args:
    destination (path-like): Name of the output file or file path.
    file (ReadOnlyDirectory): ROOT file to read histogram from.
    key (str): key to reference histogram to be added.
    first (bool): if True, special case for first of a certain histogram
        to be added to the new file.
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
