import uproot
import awkward as ak
import odapt as od
import pytest

skhep_testdata = pytest.importorskip("skhep_testdata")


def HZZ_test():
    f = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))
    original = f["events"].arrays()
    od.root_to_parquet(
        in_file=skhep_testdata.data_path("uproot-HZZ.root"),
        out_file="test.parquet",
        step_size="100 MB",
    )
    from_parquet = ak.from_parquet("/Users/zobil/Documents/odapt/test.parquet")
    for key in f["events"].keys():
        assert ak.all(from_parquet[0][key] == original[key])

def specify_tree():
    f = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))
    original = f["events"].arrays()
    od.root_to_parquet(
        in_file=skhep_testdata.data_path("uproot-HZZ.root"),
        out_file="test.parquet",
        tree="events",
        step_size="100 MB",
    )
    from_parquet = ak.from_parquet("/Users/zobil/Documents/odapt/test.parquet")
    for key in f["events"].keys():
        assert ak.all(from_parquet[0][key] == original[key])


def Zmumu_test():
    f = uproot.open(skhep_testdata.data_path("uproot-Zmumu.root"))
    original = f["events"].arrays()
    od.root_to_parquet(
        in_file=skhep_testdata.data_path("uproot-Zmumu.root"),
        out_file="test1.parquet",
        step_size="100 MB",
    )
    from_parquet = ak.from_parquet("/Users/zobil/Documents/odapt/test1.parquet")
    for key in f["events"].keys():
        assert ak.all(from_parquet[0][key] == original[key])


def break_trees():
    with pytest.raises(AttributeError):
        od.root_to_parquet(
            in_file=skhep_testdata.data_path("uproot-hepdata-example.root"),
            out_file="test2.parquet",
            step_size="100 MB",
        )


break_trees()
