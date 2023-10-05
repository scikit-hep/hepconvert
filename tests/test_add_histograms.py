import os
import uproot
import sys
sys.path.append("/Users/zobil/Documents/Proteus/src/")
import proteus
import ROOT
import numpy as np

def gen_1d_root(file_paths):
    h1 = ROOT.TH1I("name", "title", 5, -4, 4)
    h1.FillRandom("gaus")
    h1.Sumw2()
    h1.SetDirectory(0)
    outHistFile = ROOT.TFile.Open(file_paths[0], "RECREATE")
    outHistFile.cd()
    h1.Write()
    outHistFile.Close()
    h1 = uproot.from_pyroot(h1)

    h2 = ROOT.TH1I("name", "title", 5, -4, 4)
    h2.FillRandom("gaus")
    h2.Sumw2()
    h2.SetDirectory(0)
    outHistFile = ROOT.TFile.Open(file_paths[1], "RECREATE")
    outHistFile.cd()
    h2.Write()
    outHistFile.Close()
    h2 = uproot.from_pyroot(h2)

    h3 = ROOT.TH1I("name", "title", 5, -4, 4)
    h3.FillRandom("gaus")
    h3.Sumw2()
    h3.SetDirectory(0)
    outHistFile = ROOT.TFile.Open(file_paths[2], "RECREATE")
    outHistFile.cd()
    h3.Write()
    outHistFile.Close()
    h3 = uproot.from_pyroot(h3)
    return h1, h2, h3

def test_simple(tmp_path, file_paths):
    h1, h2, h3 = gen_1d_root(file_paths)

    destination = os.path.join(tmp_path, "destination.root")
    proteus.operations.add_hists(destination, ["tests/directory/file1.root", "tests/directory/file2.root"], hist_names="name")

    with uproot.open(destination) as file:
        assert file["name"].member("fN") == h1.member("fN")
        assert file["name"].member("fTsumw") == h1.member("fTsumw") + h2.member("fTsumw") + h3.member("fTsumw")
        assert np.equal(file["name"].values(flow=True), np.array(h1.values(flow=True) + h2.values(flow=True))).all

def test_3_glob(tmp_path, file_paths):
    h1, h2, h3 = gen_1d_root(file_paths)

    # destination = os.path.join(tmp_path, "destination.root")
    proteus.operations.add_hists(os.path.join(tmp_path, "place.root"), "tests/directory")
    
    with uproot.open("tests/place.root") as file:
        assert file["name"].member("fN") == h1.member("fN")
        assert file["name"].member("fTsumw") == h1.member("fTsumw") + h2.member("fTsumw") + h3.member("fTsumw")
        assert np.equal(file["name"].values(flow=True), np.array(h1.values(flow=True) + h2.values(flow=True) + h3.values(flow=True))).all

def test_2dim(tmp_path):
    xedges = [0, 1, 3, 5]
    yedges = [0, 2, 3, 4, 6]
    x = np.random.normal(2, 1, 100)
    y = np.random.normal(1, 1, 100)
    H, xedges, yedges = np.histogram2d(x, y, bins=(xedges, yedges))

    h1 = ROOT.TH2I("name", "title", len(xedges), 0.0, 5.0, len(yedges), 0.0, 6.0)
    h1.Sumw2()
    h1.Fill(0,0)
    h1.SetDirectory(0)
    outHistFile = ROOT.TFile.Open("tests/file2dim1.root", "RECREATE")
    outHistFile.cd()
    h1.Write()
    outHistFile.Close()

    h2 = ROOT.TH2I("name", "title", len(xedges), 0.0, 5.0, len(yedges), 0.0, 6.0)
    h2.Sumw2()
    h2.Fill(0,0)
    h2.SetDirectory(0)
    outHistFile = ROOT.TFile.Open("tests/file2dim2.root", "RECREATE")
    outHistFile.cd()
    h2.Write()
    outHistFile.Close()

    proteus.operations.add_hists("tests/place2.root", ["file2dim1.root", "file2dim2.root"], hist_names="name")

    with uproot.open("tests/place2.root") as file:
        assert file["name"].member("fN") == h1.member("fN")
        assert file["name"].member("fTsumw") == h1.member("fTsumw") + h2.member("fTsumw")
        assert np.equal(file["name"].values(flow=True), np.array(h1.values(flow=True) + h2.values(flow=True))).all

test_3_glob("",["tests/directory/file1.root","tests/directory/file2.root","tests/directory/file3.root"])
