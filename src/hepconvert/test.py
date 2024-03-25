import uproot
from skhep_testdata import data_path

with uproot.open(data_path("uproot-histograms.root")) as file:
    print(file[0])