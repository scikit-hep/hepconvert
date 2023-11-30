from __future__ import annotations

import awkward as ak
import merge
import pytest
import uproot
from skhep_testdata import data_path

ROOT = pytest.importorskip("ROOT")


def test_simple():
    merge.hadd_and_merge(
        "od_test_simple.root",
        [data_path("uproot-HZZ.root"), data_path("uproot-HZZ.root")],
        counter_name=lambda counted: "N" + counted,
    )
    odapt_file = uproot.open("od_test_hist.root")
    hadd_file = uproot.open(
        "/Users/zobil/Documents/odapt/src/odapt/operations/HZZ-hadd.root"
    )
    assert ak.all(odapt_file.keys() == hadd_file.keys())
    for key in odapt_file["events"]:
        assert ak.all(
            odapt_file["events"].arrays()[key] == hadd_file["events"].arrays()[key]
        )


def test_hists():
    merge.hadd_and_merge(
        "od_test_hists.root",
        [
            data_path("uproot-hepdata-example.root"),
            data_path("uproot-hepdata-example.root"),
        ],
        step_size=100,
        counter_name=lambda counted: "N" + counted,
    )
    odapt_file = uproot.open("od_test_hists.root")
    hadd_file = uproot.open(
        "/Users/zobil/Documents/odapt/src/odapt/operations/hadd-hepdata.root"
    )

    assert ak.all(odapt_file["hpx"].values() == hadd_file["hpx"].values())


def test_force():
    uproot.recreate("od_test_force.root")
    merge.hadd_and_merge(
        "od_test_force.root",
        [
            data_path("uproot-HZZ.root"),
            data_path("uproot-HZZ.root"),
            "nonexistent_file.root",
        ],
        force=False,
    )
    with pytest.raises(FileExistsError) as excinfo:
        merge.hadd_and_merge(
            "od_test_force.root",
            [
                data_path("uproot-HZZ.root"),
                data_path("uproot-HZZ.root"),
                "nonexistent_file.root",
            ],
            force=False,
        )
    assert "file exists " in str(excinfo.value)
    try:
        merge.hadd_and_merge(
            "od_test_force.root",
            [
                data_path("uproot-HZZ.root"),
                data_path("uproot-HZZ.root"),
                "nonexistent_file.root",
            ],
            force=True,
        )
    except FileExistsError:
        pytest.fail("Error with force argument")


def test_skip_bad_files():
    merge.hadd_and_merge(
        "od_test_skip_files.root",
        [
            data_path("uproot-HZZ.root"),
            data_path("uproot-HZZ.root"),
            "nonexistent_file.root",
        ],
        skip_bad_files=True,
    )

    with pytest.raises(FileNotFoundError) as excinfo:
        merge.hadd_and_merge(
            "od_test_skip_files.root",
            [
                data_path("uproot-HZZ.root"),
                data_path("uproot-HZZ.root"),
                "nonexistent_file.root",
            ],
            skip_bad_files=False,
        )
    assert "does not exist or is corrupt." in str(excinfo.value)


def realistic_data():
    merge.hadd_and_merge(
        "test_existing_file.root",
        [
            data_path("nanoAOD_2015_CMS_Open_Data_ttbar.root"),
            data_path("nanoAOD_2015_CMS_Open_Data_ttbar.root"),
            data_path("nanoAOD_2015_CMS_Open_Data_ttbar.root"),
        ],
        step_size="100 MB",
    )

    # odapt_file = uproot.open("test_existing_file.root")
    # hadd_file = uproot.open(
    #     "/Users/zobil/Documents/odapt/tests/samples/test_existing.root"
    # )
    # for key in hadd_file['Events'].keys():
    #     assert np.equal(odapt_file['Events'].arrays()[key].to_numpy, hadd_file['Events'].arrays()[key].to_numpy).all
