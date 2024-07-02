from __future__ import annotations

from pathlib import Path

import awkward as ak
import numpy as np
import pytest
import uproot

from hepconvert import merge

skhep_testdata = pytest.importorskip("skhep_testdata")


def test_simple(tmp_path):
    merge.merge_root(
        Path(tmp_path) / "test_simple.root",
        [
            skhep_testdata.data_path("uproot-HZZ.root"),
            skhep_testdata.data_path("uproot-HZZ.root"),
        ],
        counter_name=lambda counted: "N" + counted,
    )
    hepconvert_file = uproot.open(Path(tmp_path) / "test_simple.root")
    hadd_file = uproot.open("/hepconvert/src/hepconvert/tests/samples/HZZ-hadd.root")
    assert ak.all(hepconvert_file.keys() == hadd_file.keys())
    for key in hepconvert_file["events"]:
        assert ak.all(
            hepconvert_file["events"].arrays()[key] == hadd_file["events"].arrays()[key]
        )


def test_hists(tmp_path):
    merge.merge_root(
        Path(tmp_path) / "test_hists.root",
        [
            skhep_testdata.data_path("uproot-hepdata-example.root"),
            skhep_testdata.data_path("uproot-hepdata-example.root"),
        ],
        step_size=100,
        counter_name=lambda counted: "N" + counted,
    )
    hepconvert_file = uproot.open(Path(tmp_path) / "test_hists.root")
    hadd_file = uproot.open(
        "/hepconvert/src/hepconvert/tests/samples/hadd-hepdata.root"
    )

    assert ak.all(hepconvert_file["hpx"].values() == hadd_file["hpx"].values())


def test_force(tmp_path):
    uproot.recreate(Path(tmp_path) / "test_force.root")
    merge.merge_root(
        Path(tmp_path) / "test_force.root",
        [
            skhep_testdata.data_path("uproot-HZZ.root"),
            skhep_testdata.data_path("uproot-HZZ.root"),
        ],
        force=True,
    )
    with pytest.raises(FileExistsError) as excinfo:
        merge.merge_root(
            Path(tmp_path) / "test_force.root",
            [
                skhep_testdata.data_path("uproot-HZZ.root"),
                skhep_testdata.data_path("uproot-HZZ.root"),
            ],
            force=False,
        )
    assert "file exists " in str(excinfo.value)
    try:
        merge.hadd_and_merge(
            Path(tmp_path) / "test_force.root",
            [
                skhep_testdata.data_path("uproot-HZZ.root"),
                skhep_testdata.data_path("uproot-HZZ.root"),
                "nonexistent_file.root",
            ],
            force=True,
        )
    except FileExistsError:
        pytest.fail("Error with force argument")


def test_skip_bad_files(tmp_path):
    merge.merge_root(
        Path(tmp_path) / "test_skip_files.root",
        [
            skhep_testdata.data_path("uproot-HZZ.root"),
            skhep_testdata.data_path("uproot-HZZ.root"),
            "nonexistent_file.root",
        ],
        force=True,
        skip_bad_files=True,
    )

    with pytest.raises(FileNotFoundError) as excinfo:
        merge.merge_root(
            Path(tmp_path) / "test_skip_files.root",
            [
                skhep_testdata.data_path("uproot-HZZ.root"),
                skhep_testdata.data_path("uproot-HZZ.root"),
                "nonexistent_file.root",
            ],
            skip_bad_files=False,
        )
    assert "does not exist or is corrupt." in str(excinfo.value)


def realistic_data(tmp_path):
    merge.merge_root(
        "test_existing_file.root",
        [
            skhep_testdata.data_path("nanoAOD_2015_CMS_Open_Data_ttbar.root"),
            skhep_testdata.data_path("nanoAOD_2015_CMS_Open_Data_ttbar.root"),
            skhep_testdata.data_path("nanoAOD_2015_CMS_Open_Data_ttbar.root"),
        ],
        step_size="100 MB",
    )

    hepconvert_file = uproot.open(Path(tmp_path) / "test_existing_file.root")
    hadd_file = uproot.open(Path(tmp_path) / "test_existing.root")
    for key in hadd_file["Events"]:
        assert np.equal(
            hepconvert_file["Events"].arrays()[key].to_numpy,
            hadd_file["Events"].arrays()[key].to_numpy,
        ).all


def test_branchtypes(tmp_path):
    with uproot.recreate(Path(tmp_path) / "four_trees.root") as file:
        file["tree"] = {
            "x": np.array([1, 2, 3, 4, 5]),
            "y": np.array([4, 5, 6, 7, 8]),
            "x1": np.array([1, 2, 3, 4, 5]),
            "y1": np.array([4, 5, 6, 7, 8]),
        }
        file["tree1"] = {
            "x": np.array([8, 9, 10, 11, 12]),
            "y": np.array([14, 15, 16, 71, 18]),
            "x1": np.array([11, 22, 33, 44, 55]),
            "y1": np.array([4, 5, 6, 7, 8]),
        }
    with uproot.recreate(Path(tmp_path) / "two_trees.root") as file:
        file["tree"] = {
            "x": np.array([8, 9, 10, 11, 12]),
            "y": np.array([14, 15, 16, 71, 18]),
            "x1": np.array([1, 2, 3, 4, 9]),
            "y1": np.array([4, 5, 6, 7, 8]),
        }
        file["tree1"] = {
            "x": np.array([8, 9, 10, 11, 12]),
            "y": np.array([14, 15, 16, 71, 18]),
            "x1": np.array([16, 27, 37, 47, 57]),
            "y1": np.array([4, 5, 6, 7, 8]),
        }
    merge.merge_root(
        Path(tmp_path) / "test_branch_types.root",
        [Path(tmp_path) / "four_trees.root", Path(tmp_path) / "two_trees.root"],
        drop_branches=["y*"],
        force=True,
    )
    with uproot.open(Path(tmp_path) / "test_branch_types.root") as new_file:
        assert new_file["tree"].keys() == ["x", "x1"]
        assert new_file["tree1"].keys() == [
            "x",
            "x1",
        ]
        assert ak.all(
            new_file["tree"]["x"].array() == [1, 2, 3, 4, 5, 8, 9, 10, 11, 12]
        )
        assert ak.all(new_file["tree"]["x1"].array() == [1, 2, 3, 4, 5, 1, 2, 3, 4, 9])
        assert ak.all(
            new_file["tree1"]["x"].array() == [8, 9, 10, 11, 12, 8, 9, 10, 11, 12]
        )
        assert ak.all(
            new_file["tree1"]["x1"].array() == [11, 22, 33, 44, 55, 16, 27, 37, 47, 57]
        )

    merge.merge_root(
        Path(tmp_path) / "test_branch_types.root",
        [Path(tmp_path) / "four_trees.root", Path(tmp_path) / "two_trees.root"],
        keep_branches={"tree": "x*", "tree1": "y"},
        force=True,
    )
    with uproot.open(Path(tmp_path) / "test_branch_types.root") as new_file:
        assert new_file["tree"].keys() == ["x", "x1"]
        assert ak.all(
            new_file["tree"]["x"].array() == [1, 2, 3, 4, 5, 8, 9, 10, 11, 12]
        )
        assert ak.all(new_file["tree"]["x1"].array() == [1, 2, 3, 4, 5, 1, 2, 3, 4, 9])
        assert new_file["tree1"].keys() == ["y"]
        assert ak.all(
            new_file["tree1"]["y"].array() == [14, 15, 16, 71, 18, 14, 15, 16, 71, 18]
        )
