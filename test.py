import uproot
import matplotlib.pyplot as plt
import ROOT
import hepconvert
import hist

gauss_1 = ROOT.TH1I("name", "title", 5, -4, 4)
gauss_1.FillRandom("gaus")
gauss_1.Sumw2()
gauss_1.SetDirectory(0)
outHistFile = ROOT.TFile.Open("hist1.root", "RECREATE")
outHistFile.cd()
gauss_1.Write()
outHistFile.Close()

g1 = uproot.from_pyroot(gauss_1)
print(g1.values())

gauss_2 = ROOT.TH1I("name", "title", 5, -4, 4)
gauss_2.FillRandom("gaus")
gauss_2.Sumw2()
gauss_2.SetDirectory(0)
outHistFile = ROOT.TFile.Open("hist2.root", "RECREATE")
outHistFile.cd()
gauss_2.Write()
outHistFile.Close()
g2 = uproot.from_pyroot(gauss_2)

print(g2.values())
hepconvert.add_histograms("new.root", ["hist1.root", "hist2.root"], same_names=True)

with uproot.open("new.root")['name'] as histogram:
    print(histogram.values())
    print("yes?", histogram.axes[0].edges(flow=True))

    with uproot.open("test.root")['name'] as correct_hist:
        print(correct_hist.values())