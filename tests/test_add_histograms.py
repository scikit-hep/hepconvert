from __future__ import annotations

import os

import numpy as np
import pytest
import uproot

import hepconvert

ROOT = pytest.importorskip("ROOT")

# ruff: noqa: PTH118


def test_simple(tmp_path):
    gauss_1 = ROOT.TH1I("name", "title", 5, -4, 4)
    gauss_1.FillRandom("gaus")
    gauss_1.Sumw2()
    gauss_1.SetDirectory(0)
    outHistFile = ROOT.TFile.Open(os.path.join(tmp_path, "file1.root"), "RECREATE")
    outHistFile.cd()
    gauss_1.Write()
    outHistFile.Close()
    h1 = uproot.from_pyroot(gauss_1)

    gauss_2 = ROOT.TH1I("name", "title", 5, -4, 4)
    gauss_2.FillRandom("gaus")
    gauss_2.Sumw2()
    gauss_2.SetDirectory(0)
    outHistFile = ROOT.TFile.Open(os.path.join(tmp_path, "file2.root"), "RECREATE")
    outHistFile.cd()
    gauss_2.Write()
    outHistFile.Close()
    h2 = uproot.from_pyroot(gauss_2)

    gauss_3 = ROOT.TH1I("name", "title", 5, -4, 4)
    gauss_3.FillRandom("gaus")
    gauss_3.Sumw2()
    gauss_3.SetDirectory(0)
    outHistFile = ROOT.TFile.Open(os.path.join(tmp_path, "file3.root"), "RECREATE")
    outHistFile.cd()
    gauss_3.Write()
    outHistFile.Close()
    h3 = uproot.from_pyroot(gauss_3)

    destination = os.path.join(tmp_path, "destination.root")
    hepconvert.add_histograms(
        destination,
        [
            os.path.join(tmp_path, "file1.root"),
            os.path.join(tmp_path, "file2.root"),
            os.path.join(tmp_path, "file3.root"),
        ],
        force=True,
        progress_bar=True,
    )
    with uproot.open(destination) as file:
        added = uproot.from_pyroot(
            gauss_1 + gauss_2 + gauss_3
        )  # test hepconvert vs Pyroot histogram adding
        assert file["name"].member("fN") == added.member("fN")
        assert file["name"].member("fTsumw") == added.member("fTsumw")
        assert np.equal(file["name"].values(flow=True), added.values(flow=True)).all
        assert file["name"].member("fTsumw") == h1.member("fTsumw") + h2.member(
            "fTsumw"
        ) + h3.member("fTsumw")
        assert np.equal(
            file["name"].values(flow=True),
            np.array(h1.values(flow=True) + h2.values(flow=True)),
        ).all


def mult_1D(tmp_path, file_paths):
    gauss_1 = ROOT.TH1I("name1", "title", 5, -4, 4)
    gauss_1.FillRandom("gaus")
    gauss_1.Sumw2()
    gauss_1.SetDirectory(0)
    outHistFile = ROOT.TFile.Open(file_paths[0], "RECREATE")
    outHistFile.cd()
    gauss_1.Write()
    outHistFile.Close()
    h1 = uproot.from_pyroot(gauss_1)

    gauss_2 = ROOT.TH1I("name2", "title", 5, -4, 4)
    gauss_2.FillRandom("gaus")
    gauss_2.Sumw2()
    gauss_2.SetDirectory(0)
    outHistFile = ROOT.TFile.Open(file_paths[0], "UPDATE")
    outHistFile.cd()
    gauss_2.Write()
    outHistFile.Close()
    h2 = uproot.from_pyroot(gauss_2)

    gauss_3 = ROOT.TH1I("name3", "title", 5, -4, 4)
    gauss_3.FillRandom("gaus")
    gauss_3.Sumw2()
    gauss_3.SetDirectory(0)
    outHistFile = ROOT.TFile.Open(file_paths[1], "RECREATE")
    outHistFile.cd()
    gauss_3.Write()
    outHistFile.Close()
    h3 = uproot.from_pyroot(gauss_3)

    gauss_4 = ROOT.TH1I("name4", "title", 5, -4, 4)
    gauss_4.FillRandom("gaus")
    gauss_4.Sumw2()
    gauss_4.SetDirectory(0)
    outHistFile = ROOT.TFile.Open(file_paths[1], "UPDATE")
    outHistFile.cd()
    gauss_4.Write()
    outHistFile.Close()
    h4 = uproot.from_pyroot(gauss_4)

    gauss_5 = ROOT.TH1I("name5", "title", 5, -4, 4)
    gauss_5.FillRandom("gaus")
    gauss_5.Sumw2()
    gauss_5.SetDirectory(0)
    outHistFile = ROOT.TFile.Open(file_paths[2], "RECREATE")
    outHistFile.cd()
    gauss_5.Write()
    outHistFile.Close()
    h5 = uproot.from_pyroot(gauss_5)

    gauss_6 = ROOT.TH1I("name6", "title", 5, -4, 4)
    gauss_6.FillRandom("gaus")
    gauss_6.Sumw2()
    gauss_6.SetDirectory(0)
    outHistFile = ROOT.TFile.Open(file_paths[2], "UPDATE")
    outHistFile.cd()
    gauss_6.Write()
    outHistFile.Close()
    h6 = uproot.from_pyroot(gauss_6)

    destination = os.path.join(tmp_path, "destination.root")
    hepconvert.add_histograms(destination, file_paths, force=True, same_names=False)

    with uproot.open(destination) as file:
        added = uproot.from_pyroot(
            gauss_1 + gauss_3 + gauss_5
        )  # test hepconvert vs Pyroot histogram adding
        assert file["name1"].member("fN") == added.member("fN")
        assert file["name1"].member("fTsumw") == added.member("fTsumw")
        assert np.equal(file["name1"].values(flow=True), added.values(flow=True)).all
        assert file["name1"].member("fTsumw") == h1.member("fTsumw") + h3.member(
            "fTsumw"
        ) + h5.member("fTsumw")
        added = uproot.from_pyroot(
            gauss_2 + gauss_4 + gauss_6
        )  # test hepconvert vs Pyroot histogram adding
        assert file["name2"].member("fN") == added.member("fN")
        assert file["name2"].member("fTsumw") == added.member("fTsumw")
        assert np.equal(file["name1"].values(flow=True), added.values(flow=True)).all
        assert file["name2"].member("fTsumw") == h2.member("fTsumw") + h4.member(
            "fTsumw"
        ) + h6.member("fTsumw")


def test_3_glob(tmp_path):
    gauss_1 = ROOT.TH1I("name", "title", 5, -4, 4)
    gauss_1.FillRandom("gaus")
    gauss_1.Sumw2()
    gauss_1.SetDirectory(0)
    outHistFile = ROOT.TFile.Open(os.path.join(tmp_path, "hist1.root"), "RECREATE")
    outHistFile.cd()
    gauss_1.Write()
    outHistFile.Close()
    h1 = uproot.from_pyroot(gauss_1)

    gauss_2 = ROOT.TH1I("name", "title", 5, -4, 4)
    gauss_2.FillRandom("gaus")
    gauss_2.Sumw2()
    gauss_2.SetDirectory(0)
    outHistFile = ROOT.TFile.Open(os.path.join(tmp_path, "hist2.root"), "RECREATE")
    outHistFile.cd()
    gauss_2.Write()
    outHistFile.Close()
    h2 = uproot.from_pyroot(gauss_2)

    gauss_3 = ROOT.TH1I("name", "title", 5, -4, 4)
    gauss_3.FillRandom("gaus")
    gauss_3.Sumw2()
    gauss_3.SetDirectory(0)
    outHistFile = ROOT.TFile.Open(os.path.join(tmp_path, "hist3.root"), "RECREATE")
    outHistFile.cd()
    gauss_3.Write()
    outHistFile.Close()
    h3 = uproot.from_pyroot(gauss_3)

    hepconvert.add_histograms(
        os.path.join(tmp_path, "place.root"),
        os.path.join(tmp_path, "samples"),
        force=True,
    )

    with uproot.open("tests/place.root") as file:
        assert file["name"].member("fN") == h1.member("fN")
        assert file["name"].member("fTsumw") == h1.member("fTsumw") + h2.member(
            "fTsumw"
        ) + h3.member("fTsumw")
        assert np.equal(
            file["name"].values(flow=True),
            np.array(
                h1.values(flow=True) + h2.values(flow=True) + h3.values(flow=True)
            ),
        ).all


def simple_1dim_F(tmp_path):
    h1 = ROOT.TH1F("name", "", 10, 0.0, 10.0)
    data1 = [11.5, 12.0, 9.0, 8.1, 6.4, 6.32, 5.3, 3.0, 2.0, 1.0]
    for i in range(len(data1)):
        h1.Fill(i, data1[i])

    outHistFile = ROOT.TFile.Open(os.path.join(tmp_path, "file1dim1.root"), "RECREATE")
    outHistFile.cd()
    h1.Write()
    outHistFile.Close()
    h1 = uproot.from_pyroot(h1)

    h2 = ROOT.TH1F("name", "", 10, 0.0, 10.0)
    data2 = [21.5, 10.0, 9.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.0]

    for i in range(len(data2)):
        h2.Fill(i, data2[i])

    outHistFile = ROOT.TFile.Open(os.path.join(tmp_path, "file2dim1.root"), "RECREATE")
    outHistFile.cd()
    h2.Write()
    outHistFile.Close()
    h2 = uproot.from_pyroot(h2)

    hepconvert.add_histograms(
        os.path.join(tmp_path, "place2.root"),
        [
            os.path.join(tmp_path, "file1dim1.root"),
            os.path.join(tmp_path, "file2dim1.root"),
        ],
        force=True,
    )

    with uproot.open(os.path.join(tmp_path, "place2.root")) as file:
        assert file["name"].member("fN") == h1.member("fN")
        assert file["name"].member("fTsumw") == h1.member("fTsumw") + h2.member(
            "fTsumw"
        )
        assert np.equal(
            file["name"].member("fXaxis").edges(flow=True),
            h1.member("fXaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].member("fXaxis").edges(flow=True),
            h2.member("fXaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].member("fYaxis").edges(flow=True),
            h1.member("fYaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].member("fYaxis").edges(flow=True),
            h2.member("fYaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].values(flow=True),
            np.array(h1.values(flow=True) + h2.values(flow=True)),
        ).all


simple_1dim_F("tests/samples")


def mult_2D_hists(tmp_path):
    h1 = ROOT.TH2F("name", "", 10, 0.0, 10.0, 8, 0.0, 8.0)
    data1 = [
        [13.5, 11.0, 10.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.0],
        [11.5, 10.0, 9.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.0],
        [10.5, 10.0, 8.0, 7.2, 6.8, 5.32, 5.3, 2.0, 1.6, 1.0],
        [9.5, 9.0, 8.0, 7.2, 6.8, 5.32, 5.3, 2.0, 1.6, 1.0],
        [8.5, 8.0, 9.0, 7.2, 6.8, 5.32, 5.3, 2.0, 1.0, 0.5],
        [4.5, 7.0, 7.0, 7.2, 6.8, 5.32, 5.3, 2.0, 0.54, 0.25],
        [3.5, 4.0, 4.0, 4.2, 6.8, 5.32, 5.3, 2.0, 0.2, 0.1],
        [1.5, 1.01, 0.21, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01],
    ]
    for i in range(len(data1)):
        for j in range(len(data1[0])):
            h1.Fill(i, j, data1[i][j])

    outHistFile = ROOT.TFile.Open(os.path.join(tmp_path, "file3dim2.root"), "RECREATE")
    outHistFile.cd()
    h1.Write()
    outHistFile.Close()
    h1 = uproot.from_pyroot(h1)

    h2 = ROOT.TH2F("second", "", 10, 0.0, 10.0, 8, 0.0, 8.0)
    data2 = [
        [21.5, 10.0, 9.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.0],
        [15.5, 13.0, 9.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.5],
        [12.5, 10.0, 9.5, 8.2, 6.8, 6.32, 5.2, 3.0, 2.0, 1.25],
        [9.5, 9.0, 8.0, 7.2, 5.8, 5.32, 5.3, 2.0, 1.6, 0.5],
        [8.5, 8.0, 6.0, 7.2, 5.8, 5.32, 5.3, 2.0, 1.0, 0.4],
        [4.5, 4.0, 4.0, 7.2, 5.8, 5.32, 5.3, 2.0, 0.54, 0.3],
        [3.5, 4.0, 4.0, 4.2, 5.8, 5.32, 5.3, 2.0, 0.2, 0.1],
        [1.5, 1.01, 0.21, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.02],
    ]

    for i in range(len(data2)):
        for j in range(len(data2[0])):
            h2.Fill(i, j, data2[i][j])

    outHistFile = ROOT.TFile.Open(os.path.join(tmp_path, "file3dim2.root"), "UPDATE")
    outHistFile.cd()
    h2.Write()
    outHistFile.Close()
    h2 = uproot.from_pyroot(h2)

    h3 = ROOT.TH2F("name", "", 10, 0.0, 10.0, 8, 0.0, 8.0)
    data3 = [
        [13.5, 11.0, 10.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.0],
        [11.5, 10.0, 9.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.0],
        [10.5, 10.0, 8.0, 7.2, 6.8, 5.32, 5.3, 2.5, 1.6, 1.0],
        [9.5, 9.0, 8.0, 7.2, 6.8, 5.32, 5.3, 3.0, 3.6, 1.0],
        [8.5, 8.0, 9.0, 7.2, 6.8, 5.32, 5.3, 2.0, 2.0, 0.25],
        [4.5, 7.0, 7.0, 7.2, 6.8, 5.32, 5.3, 2.0, 0.54, 0.25],
        [3.5, 4.0, 4.0, 4.2, 6.8, 5.32, 5.3, 2.0, 1.2, 0.1],
        [1.5, 1.01, 0.21, 0.01, 0.51, 0.01, 0.41, 0.01, 0.01, 0.01],
    ]
    for i in range(len(data3)):
        for j in range(len(data3[0])):
            h3.Fill(i, j, data3[i][j])

    outHistFile = ROOT.TFile.Open(os.path.join(tmp_path, "file4dim2.root"), "RECREATE")
    outHistFile.cd()
    h3.Write()
    outHistFile.Close()
    h3 = uproot.from_pyroot(h3)

    h4 = ROOT.TH2F("second", "", 10, 0.0, 10.0, 8, 0.0, 8.0)
    data4 = [
        [21.5, 10.0, 9.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.0],
        [15.5, 13.0, 9.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.5],
        [12.5, 10.0, 9.5, 8.2, 6.8, 6.32, 5.2, 3.0, 2.0, 1.25],
        [9.5, 9.0, 8.0, 7.2, 5.8, 5.32, 5.3, 2.0, 1.6, 0.5],
        [8.5, 8.0, 6.0, 7.2, 5.8, 5.32, 5.3, 2.0, 1.0, 0.4],
        [4.5, 4.0, 4.0, 7.2, 5.8, 5.32, 5.3, 2.0, 0.54, 0.3],
        [3.5, 4.0, 4.0, 4.2, 5.8, 5.32, 5.3, 2.0, 0.2, 0.1],
        [1.5, 1.01, 0.21, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.02],
    ]

    for i in range(len(data4)):
        for j in range(len(data4[0])):
            h4.Fill(i, j, data4[i][j])

    outHistFile = ROOT.TFile.Open(os.path.join(tmp_path, "file4dim2.root"), "UPDATE")
    outHistFile.cd()
    h4.Write()
    outHistFile.Close()
    h4 = uproot.from_pyroot(h4)

    hepconvert.add_histograms(
        os.path.join(tmp_path, "place2.root"),
        [
            os.path.join(tmp_path, "file3dim2.root"),
            os.path.join(tmp_path, "file4dim2.root"),
        ],
        force=True,
    )

    with uproot.open(os.path.join(tmp_path, "place2.root")) as file:
        assert file["name"].member("fN") == h1.member("fN")
        assert file["name"].member("fTsumw") == h1.member("fTsumw") + h3.member(
            "fTsumw"
        )
        assert np.equal(
            file["name"].member("fXaxis").edges(flow=True),
            h1.member("fXaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].member("fXaxis").edges(flow=True),
            h2.member("fXaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].member("fYaxis").edges(flow=True),
            h1.member("fYaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].member("fYaxis").edges(flow=True),
            h2.member("fYaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].member("fXaxis").edges(flow=True),
            h3.member("fXaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].member("fXaxis").edges(flow=True),
            h4.member("fXaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].member("fYaxis").edges(flow=True),
            h3.member("fYaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].member("fYaxis").edges(flow=True),
            h4.member("fYaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].values(flow=True),
            np.array(h1.values(flow=True) + h3.values(flow=True)),
        ).all
        assert np.equal(
            file["second"].values(flow=True),
            np.array(h2.values(flow=True) + h4.values(flow=True)),
        ).all


def simple_2dim_F(tmp_path):
    fName = "name"
    h1 = ROOT.TH2F(fName, "", 10, 0.0, 10.0, 8, 0.0, 8.0)
    data1 = [
        [13.5, 11.0, 10.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.0],
        [11.5, 10.0, 9.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.0],
        [10.5, 10.0, 8.0, 7.2, 6.8, 5.32, 5.3, 2.0, 1.6, 1.0],
        [9.5, 9.0, 8.0, 7.2, 6.8, 5.32, 5.3, 2.0, 1.6, 1.0],
        [8.5, 8.0, 9.0, 7.2, 6.8, 5.32, 5.3, 2.0, 1.0, 0.5],
        [4.5, 7.0, 7.0, 7.2, 6.8, 5.32, 5.3, 2.0, 0.54, 0.25],
        [3.5, 4.0, 4.0, 4.2, 6.8, 5.32, 5.3, 2.0, 0.2, 0.1],
        [1.5, 1.01, 0.21, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01],
    ]
    for i in range(len(data1)):
        for j in range(len(data1[0])):
            h1.Fill(i, j, data1[i][j])

    h1 = uproot.from_pyroot(h1)

    h2 = ROOT.TH2F(fName, "", 10, 0.0, 10.0, 8, 0.0, 8.0)
    data2 = [
        [21.5, 10.0, 9.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.0],
        [15.5, 13.0, 9.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.5],
        [12.5, 10.0, 9.5, 8.2, 6.8, 6.32, 5.2, 3.0, 2.0, 1.25],
        [9.5, 9.0, 8.0, 7.2, 5.8, 5.32, 5.3, 2.0, 1.6, 0.5],
        [8.5, 8.0, 6.0, 7.2, 5.8, 5.32, 5.3, 2.0, 1.0, 0.4],
        [4.5, 4.0, 4.0, 7.2, 5.8, 5.32, 5.3, 2.0, 0.54, 0.3],
        [3.5, 4.0, 4.0, 4.2, 5.8, 5.32, 5.3, 2.0, 0.2, 0.1],
        [1.5, 1.01, 0.21, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.02],
    ]

    for i in range(len(data2)):
        for j in range(len(data2[0])):
            h2.Fill(i, j, data2[i][j])

    h2 = uproot.from_pyroot(h2)

    hepconvert.add_histograms(
        os.path.join(tmp_path, "place2.root"),
        [
            os.path.join(tmp_path, "file1dim2.root"),
            os.path.join(tmp_path, "file2dim2.root"),
        ],
        force=True,
    )

    with uproot.open("tests/place2.root") as file:
        assert file["name"].member("fN") == h1.member("fN")
        assert file["name"].member("fTsumw") == h1.member("fTsumw") + h2.member(
            "fTsumw"
        )
        assert np.equal(
            file["name"].member("fXaxis").edges(flow=True),
            h1.member("fXaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].member("fXaxis").edges(flow=True),
            h2.member("fXaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].member("fYaxis").edges(flow=True),
            h1.member("fYaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].member("fYaxis").edges(flow=True),
            h2.member("fYaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].values(flow=True),
            np.array(h1.values(flow=True) + h2.values(flow=True)),
        ).all


def simple_2D(tmp_path):
    h2 = ROOT.TH2F("name", "", 10, 0.0, 10.0, 8, 0.0, 8.0)
    data2 = [
        [21.5, 10.0, 9.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.0],
        [15.5, 13.0, 9.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.5],
        [12.5, 10.0, 9.5, 8.2, 6.8, 6.32, 5.2, 3.0, 2.0, 1.25],
        [9.5, 9.0, 8.0, 7.2, 5.8, 5.32, 5.3, 2.0, 1.6, 0.5],
        [8.5, 8.0, 6.0, 7.2, 5.8, 5.32, 5.3, 2.0, 1.0, 0.4],
        [4.5, 4.0, 4.0, 7.2, 5.8, 5.32, 5.3, 2.0, 0.54, 0.3],
        [3.5, 4.0, 4.0, 4.2, 5.8, 5.32, 5.3, 2.0, 0.2, 0.1],
        [1.5, 1.01, 0.21, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.02],
    ]

    for i in range(len(data2)):
        for j in range(len(data2[0])):
            h2.Fill(i, j, data2[i][j])
    outHistFile = ROOT.TFile.Open(os.path.join(tmp_path, "file2dim2.root"), "RECREATE")
    outHistFile.cd()
    h2.Write()
    outHistFile.Close()
    h2 = uproot.from_pyroot(h2)

    h1 = ROOT.TH2F("name", "", 10, 0.0, 10.0, 8, 0.0, 8.0)
    data1 = [
        [13.5, 11.0, 10.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.0],
        [11.5, 10.0, 9.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.0],
        [10.5, 10.0, 8.0, 7.2, 6.8, 5.32, 5.3, 2.0, 1.6, 1.0],
        [9.5, 9.0, 8.0, 7.2, 6.8, 5.32, 5.3, 2.0, 1.6, 1.0],
        [8.5, 8.0, 9.0, 7.2, 6.8, 5.32, 5.3, 2.0, 1.0, 0.5],
        [4.5, 7.0, 7.0, 7.2, 6.8, 5.32, 5.3, 2.0, 0.54, 0.25],
        [3.5, 4.0, 4.0, 4.2, 6.8, 5.32, 5.3, 2.0, 0.2, 0.1],
        [1.5, 1.01, 0.21, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01],
    ]
    for i in range(len(data1)):
        for j in range(len(data1[0])):
            h1.Fill(i, j, data1[i][j])

    outHistFile = ROOT.TFile.Open(os.path.join(tmp_path, "file1dim2.root"), "RECREATE")
    outHistFile.cd()
    h1.Write()
    outHistFile.Close()
    h1 = uproot.from_pyroot(h1)

    hepconvert.add_histograms(
        os.path.join(tmp_path, "place2.root"),
        [
            os.path.join(tmp_path, "file1dim2.root"),
            os.path.join(tmp_path, "file2dim2.root"),
        ],
        force=True,
    )

    with uproot.open(os.path.join(tmp_path, "place2.root")) as file:
        assert file["name"].member("fN") == h1.member("fN")
        assert file["name"].member("fTsumw") == h1.member("fTsumw") + h2.member(
            "fTsumw"
        )
        assert np.equal(
            file["name"].member("fXaxis").edges(flow=True),
            h1.member("fXaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].member("fXaxis").edges(flow=True),
            h2.member("fXaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].member("fYaxis").edges(flow=True),
            h1.member("fYaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].member("fYaxis").edges(flow=True),
            h2.member("fYaxis").edges(flow=True),
        ).all
        assert np.equal(
            file["name"].values(flow=True),
            np.array(h1.values(flow=True) + h2.values(flow=True)),
        ).all


def break_bins(tmp_path):
    h1 = ROOT.TH1F("name", "", 8, 0.0, 10.0)
    data1 = [11.5, 12.0, 9.0, 8.1, 6.4, 6.32, 5.3, 3.0]
    for i in range(len(data1)):
        h1.Fill(i, data1[i])

    outHistFile = ROOT.TFile.Open(
        os.path.join(tmp_path, "file1dim1break.root"), "RECREATE"
    )
    outHistFile.cd()
    h1.Write()
    outHistFile.Close()
    h1 = uproot.from_pyroot(h1)

    h2 = ROOT.TH1F("name", "", 10, 0.0, 10.0)
    data2 = [21.5, 10.0, 9.0, 8.2, 6.8, 6.32, 5.3, 3.0, 2.0, 1.0]

    for i in range(len(data2)):
        h2.Fill(i, data2[i])

    outHistFile = ROOT.TFile.Open(
        os.path.join(tmp_path, "file2dim1break.root"), "RECREATE"
    )
    outHistFile.cd()
    h2.Write()
    outHistFile.Close()
    h2 = uproot.from_pyroot(h2)

    hepconvert.add_histograms(
        os.path.join(tmp_path, "place2break.root"),
        [
            os.path.join(tmp_path, "file1dim1break.root"),
            os.path.join(tmp_path, "file2dim1break.root"),
        ],
        force=True,
    )
