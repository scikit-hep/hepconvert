import ROOT
import uproot

# h1 = ROOT.TH1I("name", "title", 10, -4, 4)
# h1.FillRandom("gaus")
# h2 = ROOT.TH1I("name", "title", 10, -4, 4)
# h2.FillRandom("gaus")

def gen_gause_hists_uproot():
    file_out = uproot.recreate("file1.root")
    h1 = uproot.from_pyroot(h1)
    h_1 = uproot.writing.identify.to_TH1x(h1.member("fName"),
    h1.member("fTitle"),
    h1.values(flow=True),
    h1.member("fEntries"),
    h1.member("fTsumw"),
    h1.member("fTsumw2"),
    h1.member("fTsumwx"),
    h1.member("fTsumwx2"),
    h1.variances(flow=True),
    h1.member("fXaxis"),
    )
    print(h_1)
    file_out[h_1.member("fName")] = h_1

    file_out = uproot.recreate("file2.root")
    h2 = uproot.from_pyroot(h2)
    h_2 = uproot.writing.identify.to_TH1x(h2.member("fName"),
    h2.member("fTitle"),
    h2.values(flow=True),
    h2.member("fEntries"),
    h2.member("fTsumw"),
    h2.member("fTsumw2"),
    h2.member("fTsumwx"),
    h2.member("fTsumwx2"),
    h2.variances(flow=True),
    h2.member("fXaxis"),
    )

    file_out[h_2.member("fName")] = h_2

def gen_gaus_hists_pyroot(names, file_names):
    # Will create histograms with same names and bins for files in file_names
    for file in file_names:
        for name in names:
            h = ROOT.TH1I(name, name, 10, -4, 4)
            h.FillRandom("gaus")
            h.Sumw2()
            h.SetDirectory(0)
            outHistFile = ROOT.TFile.Open(file, "RECREATE")
            outHistFile.cd()
            h.Write()
            outHistFile.Close()

def gen_gaus_hists_pyroot():
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

def gen_2dim_hists_pyroot(num_hists, num_files, names):
    import numpy as np
    xedges = [0, 1, 3, 5]
    yedges = [0, 2, 3, 4, 6]
    x = np.random.normal(2, 1, 100)
    y = np.random.normal(1, 1, 100)
    H, xedges, yedges = np.histogram2d(x, y, bins=(xedges, yedges))

    h1 = ROOT.TH2I("name", "title", len(xedges), 0.0, 5.0, len(yedges), 0.0, 6.0)
    h1.Sumw2()
    h1.Fill(0,0)
    h1.SetDirectory(0)
    outHistFile = ROOT.TFile.Open("file2dim1.root", "RECREATE")
    outHistFile.cd()
    h1.Write()
    outHistFile.Close()

    
    h2 = ROOT.TH2I("name", "title", len(xedges), 0.0, 5.0, len(yedges), 0.0, 6.0)
    h2.Sumw2()
    h2.Fill(0,0)
    h2.SetDirectory(0)
    outHistFile = ROOT.TFile.Open("file2dim2.root", "RECREATE")
    outHistFile.cd()
    h2.Write()
    outHistFile.Close()
