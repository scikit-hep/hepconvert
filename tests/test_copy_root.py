import uproot
from skhep_testdata import data_path
import odapt as od
import awkward as ak
import pytest

def test_copy():
    od.copy_root(
        "/Users/zobil/Documents/odapt/tests/samples/copy.root",
        data_path("uproot-HZZ.root"),
        counter_name=lambda counted: "N" + counted,
    )
    od_file = uproot.open("/Users/zobil/Documents/odapt/tests/samples/copy.root")
    file = uproot.open(data_path("uproot-HZZ.root"))
    print(file["events"].keys())
    for key in od_file["events"].keys():
        assert key in file["events"].keys()
        assert ak.all(od_file["events"][key].array() == file["events"][key].array())


def test_drop_branch():
    od.copy_root(
        "/Users/zobil/Documents/odapt/tests/samples/drop_branches.root",
        data_path("uproot-HZZ.root"),
        drop_branches=["MClepton_py", "Jet_Px"],
        counter_name=lambda counted: "N" + counted,
    )
    original = uproot.open(data_path("uproot-HZZ.root"))
    file = uproot.open("/Users/zobil/Documents/odapt/tests/samples/drop_branches.root")
    assert "MClepton_py" not in file["events"]
    assert "Jet_Px" not in file["events"]

    for key in original["events"].keys():
        if key != "MClepton_py" and key != "Jet_Px":
            assert key in file["events"].keys()
            assert ak.all(
                file["events"][key].array() == original["events"][key].array()
            )


def test_add_branch():
    od.copy_root(
        "/Users/zobil/Documents/odapt/tests/samples/drop_branches.root",
        data_path("uproot-HZZ.root"),
        drop_branches=["MClepton_py", "Jet_Px"],
        counter_name=lambda counted: "N" + counted,
    )
    arrays = file["events"].arrays()
    branch_types = {
        name: array.type
        for name, array in zip(ak.fields(arrays), ak.unzip(arrays))
        if not name.startswith("n") and not name.startswith("N")
    }

    branches = {
        file["events"]["MClepton_py"].name: file["events"]["MClepton_py"].arrays(),
        file["events"]["Jet_Px"].name: file["events"]["Jet_Px"].arrays(),
    }
    jet_px = {file["events"]["Jet_Px"].name: file["events"]["Jet_Px"].arrays()}
    od.copy_root(
        "/Users/zobil/Documents/odapt/tests/samples/add_branches.root",
        "/Users/zobil/Documents/odapt/tests/samples/drop_branches.root",
        branch_types=branch_types,
    )

    file = uproot.open("/Users/zobil/Documents/odapt/tests/samples/add_branches.root")

def test_hepdata_example():
    od.copy_root(
        "/Users/zobil/Documents/odapt/tests/samples/copy_hepdata.root",
        data_path("uproot-hepdata-example.root"),
        counter_name=lambda counted: "N" + counted,
    )
    od_file = uproot.open("/Users/zobil/Documents/odapt/tests/samples/copy_hepdata.root")
    file = uproot.open(data_path("uproot-hepdata-example.root"))
    print(file['hprof'].classname)
    print(od_file.classnames())
    for key in od_file.keys(cycle=False):
        assert key in file.keys(cycle=False)
        print(key)
        if key == "hpxpy":
            for array in od_file[key].values():
                assert array in file[key].values() # did check if this works and it does 
