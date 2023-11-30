import pytest
import uproot
from skhep_testdata import data_path
import numpy as np
import awkward as ak
# import odapt.operations as od

# import merge
import merge
ROOT = pytest.importorskip("ROOT")

def test_simple():
    merge.hadd_and_merge(
    "od_test_simple.root",
    [data_path("uproot-HZZ.root"), data_path("uproot-HZZ.root")],
    counter_name=lambda counted: "N" + counted)
    odapt_file = uproot.open("od_test_hist.root")
    hadd_file = uproot.open("/Users/zobil/Documents/odapt/src/odapt/operations/HZZ-hadd.root")
    assert ak.all(odapt_file.keys() == hadd_file.keys())
    for key in odapt_file['events'].keys():
        assert ak.all(odapt_file['events'].arrays()[key] == hadd_file['events'].arrays()[key])


# def test_hists():
#     merge.hadd_and_merge(
#     "od_test_simple.root",
#     ["/Users/zobil/Documents/odapt/src/odapt/operations/uproot-hepdata-example.root", "/Users/zobil/Documents/odapt/src/odapt/operations/uproot-hepdata-example.root"],
#     counter_name=lambda counted: "N" + counted)
#     odapt_file = uproot.open("od_test_simple.root")
#     hadd_file = uproot.open("/Users/zobil/Documents/odapt/src/odapt/operations/hadd-hepdata.root")
#     # Is the file structure generally the same?
#     print(odapt_file.classnames())
#     assert np.equal(
#         odapt_file.keys(),
#         hadd_file.keys()
#     ).all
#     file = uproot.open("/Users/zobil/Documents/odapt/src/odapt/operations/uproot-hepdata-example.root")
#     keys1 = odapt_file.keys(recursive=False, cycle=False)
#     keys2 = hadd_file.keys(recursive=False, cycle=False)
#     assert ak.all(odapt_file['ntuple'].arrays()['px'] == hadd_file['ntuple'].arrays()['px'])
#     print(odapt_file['hpx'].values())
#     print(hadd_file['hpx'].values())
#     assert ak.all(odapt_file['hpx'].values() == hadd_file['hpx'].values())
#     # assert np.equal(odapt_file[])

    # for key in keys1:
    #     assert np.equal(len(odapt_file['events'][key].array()), len(hadd_file['events'][key].array())) # Ask someone about why is odapt writing a tuple while hadd gets an awkward array right away  
    
def test_hists():
    merge.hadd_and_merge(
        "od_test_hists.root",
        [data_path("uproot-hepdata-example.root"), data_path("uproot-hepdata-example.root")], step_size=100,
        counter_name=lambda counted: "N" + counted)
    odapt_file = uproot.open("od_test_hists.root")
    hadd_file = uproot.open("/Users/zobil/Documents/odapt/src/odapt/operations/hadd-hepdata.root")
    
    assert ak.all(odapt_file['hpx'].values() == hadd_file['hpx'].values())
    

def test_force():
    uproot.recreate("od_test_force.root")
    merge.hadd_and_merge(
    "od_test_force.root",
    [data_path("uproot-HZZ.root"), data_path("uproot-HZZ.root"), "nonexistent_file.root"],
    force=False)
    with pytest.raises(FileExistsError) as excinfo:
        merge.hadd_and_merge(
            "od_test_force.root",
            [data_path("uproot-HZZ.root"), data_path("uproot-HZZ.root"), "nonexistent_file.root"],
            force=False)
    assert "file exists " in str(excinfo.value)
    try:
        merge.hadd_and_merge(
        "od_test_force.root",
        [data_path("uproot-HZZ.root"), data_path("uproot-HZZ.root"), "nonexistent_file.root"],
        force=True)
    except FileExistsError:
        pytest.fail("Error with force argument")


def test_skip_bad_files():
    merge.hadd_and_merge(
    "od_test_skip_files.root",
    [data_path("uproot-HZZ.root"), data_path("uproot-HZZ.root"), "nonexistent_file.root"],
    skip_bad_files=True)

    with pytest.raises(FileNotFoundError) as excinfo:
        merge.hadd_and_merge(
            "od_test_skip_files.root",
            [data_path("uproot-HZZ.root"), data_path("uproot-HZZ.root"), "nonexistent_file.root"],
            skip_bad_files=False)
    assert "does not exist or is corrupt." in str(excinfo.value)


def realistic_data():
    merge.hadd_and_merge(
    "test_existing_file.root",
    [data_path("nanoAOD_2015_CMS_Open_Data_ttbar.root"), data_path("nanoAOD_2015_CMS_Open_Data_ttbar.root"), data_path("nanoAOD_2015_CMS_Open_Data_ttbar.root")],
    step_size="100 MB",)  

    odapt_file = uproot.open("test_existing_file.root")
    hadd_file = uproot.open("/Users/zobil/Documents/odapt/tests/samples/test_existing.root")
    print(hadd_file.keys(recursive=False, cycle=False))
    for key in hadd_file['Events'].keys():
        assert np.equal(odapt_file['Events'].arrays()[key].to_numpy, hadd_file['Events'].arrays()[key].to_numpy).all
