import uproot
import awkward as ak
import odapt as od
import pytest

skhep_testdata = pytest.importorskip("skhep_testdata")


def HZZ_test():
    f = uproot.open(data_path("uproot-HZZ.root"))
    original = f["events"].arrays()
    od.root_to_parquet(
        input_file=data_path("uproot-HZZ.root"),
        output_file="test.parquet",
        step_size="100 MB",
    )
    from_parquet = ak.from_parquet("/Users/zobil/Documents/odapt/test.parquet")
    for key in f["events"].keys():
        assert ak.all(from_parquet[0][key] == original[key])


def Zmumu_test():
    f = uproot.open(data_path("uproot-Zmumu.root"))
    original = f["events"].arrays()
    od.root_to_parquet(
        input_file=data_path("uproot-Zmumu.root"),
        output_file="test1.parquet",
        step_size="100 MB",
    )
    from_parquet = ak.from_parquet("/Users/zobil/Documents/odapt/test1.parquet")
    for key in f["events"].keys():
        assert ak.all(from_parquet[0][key] == original[key])


def break_trees():
    with pytest.raises(AttributeError):
        od.root_to_parquet(
            input_file=data_path("uproot-hepdata-example.root"),
            output_file="test2.parquet",
            step_size="100 MB",
        )
    # with pytest.raises(AttributeError):


break_trees()
