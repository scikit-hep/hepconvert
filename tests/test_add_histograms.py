import os

import pytest

import proteus

import ROOT

def make_hists():
    h1 = ROOT.TH1I("name", "title", 10, -4, 4)
    h1.FillRandom("gaus")
    h1.Sumw2()
    h1.SetDirectory(0)
    outHistFile = ROOT.TFile.Open("file1.root", "RECREATE")
    outHistFile.cd()
    h1.Write()
    outHistFile.Close()

    h2 = ROOT.TH1I("name", "title", 10, -4, 4)
    h2.FillRandom("gaus")
    h2.Sumw2()
    h2.SetDirectory(0)
    outHistFile = ROOT.TFile.Open("file2.root", "RECREATE")
    outHistFile.cd()
    h2.Write()
    outHistFile.Close()

    h3 = ROOT.TH1I("name", "title", 10, -4, 4)
    h3.FillRandom("gaus")
    h3.Sumw2()
    h3.SetDirectory(0)
    outHistFile = ROOT.TFile.Open("file3.root", "RECREATE")
    outHistFile.cd()
    h3.Write()
    outHistFile.Close()

def test_simple(tmp_path):
    # 1-Dimensional Histograms, list of files, one histogram per file
    destination = os.path.join(tmp_path, "destination.root")
    make_hists()
    proteus.operations.add_hists("place.root", filenames=["file1.root", "file2.root", "file3.root"], hist_names="name")

    # assert get hists from destination file and compare?

# hadd_like("place.root",  directory="/Users/zobil/Documents/Proteus/tests/")

test_simple("/")