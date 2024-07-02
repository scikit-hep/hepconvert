from __future__ import annotations

from pathlib import Path

import awkward as ak
import pytest
import uproot

import hepconvert

skhep_testdata = pytest.importorskip("skhep_testdata")


def test_copy(tmp_path):
    hepconvert.copy_root(
        Path(tmp_path) / "copy.root",
        skhep_testdata.data_path("uproot-HZZ.root"),
        counter_name=lambda counted: "N" + counted,
        force=True,
        progress_bar=True,
    )
    hepconvert_file = uproot.open(Path(tmp_path) / "copy.root")
    file = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))
    for key in hepconvert_file["events"].keys():
        assert key in file["events"].keys()
        assert ak.all(
            hepconvert_file["events"][key].array() == file["events"][key].array()
        )


def test_drop_branch(tmp_path):
    hepconvert.copy_root(
        Path(tmp_path) / "drop_branches.root",
        skhep_testdata.data_path("uproot-HZZ.root"),
        drop_branches="MC*",
        counter_name=lambda counted: "N" + counted,
        force=True,
    )
    original = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))

    file = uproot.open(Path(tmp_path) / "drop_branches.root")


def test_keep_branch(tmp_path):
    hepconvert.copy_root(
        Path(tmp_path) / "drop_branches.root",
        skhep_testdata.data_path("uproot-HZZ.root"),
        keep_branches="MClepton_*",
        counter_name=lambda counted: "N" + counted,
        force=True,
    )
    original = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))

    file = uproot.open(Path(tmp_path) / "drop_branches.root")
    for key in original["events"].keys():
        if key.startswith(("MClepton_", "NMClepton")):
            assert key in file["events"].keys()
            assert ak.all(
                file["events"][key].array() == original["events"][key].array()
            )
        else:
            assert key not in file["events"].keys()


def test_keep_branches(tmp_path):
    hepconvert.copy_root(
        Path(tmp_path) / "drop_branches.root",
        skhep_testdata.data_path("uproot-HZZ.root"),
        drop_branches=["Jet_*", "MClepton_*"],
        counter_name=lambda counted: "N" + counted,
        force=True,
    )
    original = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))

    file = uproot.open(Path(tmp_path) / "drop_branches.root")
    for key in original["events"].keys():
        if key.startswith("MClepton_"):
            assert key in file["events"].keys()
            assert ak.all(
                file["events"][key].array() == original["events"][key].array()
            )
        else:
            assert key not in file["events"].keys()


def test_hepdata_example(tmp_path):
    hepconvert.copy_root(
        Path(tmp_path) / "copy_hepdata.root",
        skhep_testdata.data_path("uproot-hepdata-example.root"),
        counter_name=lambda counted: "N" + counted,
        force=True,
    )
    hepconvert_file = uproot.open(Path(tmp_path) / "copy_hepdata.root")
    file = uproot.open(skhep_testdata.data_path("uproot-hepdata-example.root"))
    for key in hepconvert_file.keys(cycle=False):
        assert key in file.keys(cycle=False)


def test_keep_tree(tmp_path):
    import numpy as np

    with uproot.recreate(Path(tmp_path) / "two_trees.root") as file:
        file["tree"] = {"x": np.array([1, 2, 3, 4, 5]), "y": np.array([4, 5, 6, 7, 8])}
        file["tree1"] = {
            "x1": np.array([1, 2, 3, 4, 5]),
            "y1": np.array([4, 5, 6, 7, 8]),
        }
        file["tree2"] = {
            "z": np.array([3, 77, 3, 4, 5]),
            "p": np.array([44, 55, 66, 7, 8]),
        }
        file["tree3"] = {
            "z1": np.array([3, 77, 3, 4, 5]),
            "p1": np.array([44, 55, 66, 7, 8]),
        }
    with uproot.open(Path(tmp_path) / "two_trees.root") as file:
        hepconvert.copy_root(
            Path(tmp_path) / "copied.root",
            Path(tmp_path) / "two_trees.root",
            keep_trees="tree",
            force=True,
        )
        with uproot.open(Path(tmp_path) / "copied.root") as copy:
            assert copy.keys(cycle=False) == ["tree"]
            for tree in copy.keys(cycle=False):
                for key in copy[tree].keys():
                    assert ak.all(copy[tree][key].array() == file[tree][key].array())

        hepconvert.copy_root(
            Path(tmp_path) / "copied.root",
            Path(tmp_path) / "two_trees.root",
            keep_trees=["tree", "tree2", "tree3"],
            force=True,
        )
        with uproot.open(Path(tmp_path) / "copied.root") as copy:
            assert copy.keys(cycle=False) == ["tree", "tree2", "tree3"]
            for tree in copy.keys(cycle=False):
                for key in copy[tree].keys():
                    assert ak.all(copy[tree][key].array() == file[tree][key].array())

    with pytest.raises(
        ValueError,
        match=f"Key 'tree5' does not match any TTree in ROOT file{tmp_path}two_trees.root",
    ):
        hepconvert.copy_root(
            Path(tmp_path) / "copied.root",
            Path(tmp_path) / "two_trees.root",
            keep_trees=["tree5"],
            force=True,
        )


def test_drop_tree(tmp_path):
    import numpy as np

    with uproot.recreate(Path(tmp_path) / "two_trees.root") as file:
        file["tree"] = {"x": np.array([1, 2, 3, 4, 5]), "y": np.array([4, 5, 6, 7, 8])}
        file["tree1"] = {
            "x1": np.array([1, 2, 3, 4, 5]),
            "y1": np.array([4, 5, 6, 7, 8]),
        }
        file["tree2"] = {
            "z": np.array([3, 77, 3, 4, 5]),
            "p": np.array([44, 55, 66, 7, 8]),
        }
        file["tree3"] = {
            "z1": np.array([3, 77, 3, 4, 5]),
            "p1": np.array([44, 55, 66, 7, 8]),
        }
    with uproot.open(Path(tmp_path) / "two_trees.root") as file:
        hepconvert.copy_root(
            Path(tmp_path) / "copied.root",
            Path(tmp_path) / "two_trees.root",
            drop_trees=["tree", "tree1"],
            force=True,
        )
        with uproot.open(Path(tmp_path) / "copied.root") as copy:
            assert copy.keys(cycle=False) == ["tree2", "tree3"]
            for tree in copy.keys(cycle=False):
                for key in copy[tree].keys():
                    assert ak.all(copy[tree][key].array() == file[tree][key].array())

        hepconvert.copy_root(
            Path(tmp_path) / "copied.root",
            Path(tmp_path) / "two_trees.root",
            drop_trees="tree3",
            force=True,
        )
        with uproot.open(Path(tmp_path) / "copied.root") as copy:
            assert copy.keys(cycle=False) == ["tree", "tree1", "tree2"]
            for tree in copy.keys(cycle=False):
                for key in copy[tree].keys():
                    assert ak.all(copy[tree][key].array() == file[tree][key].array())

    with pytest.raises(
        ValueError,
        match=f"Key 'tree5' does not match any TTree in ROOT {tmp_path}/two_trees.root",
    ):
        hepconvert.copy_root(
            Path(tmp_path) / "copied.root",
            Path(tmp_path) / "two_trees.root",
            drop_trees=["tree5"],
            force=True,
        )


def test_drop_tree_and_branch(tmp_path):
    import numpy as np

    with uproot.recreate(Path(tmp_path) / "two_trees.root") as file:
        file["tree"] = {"x": np.array([1, 2, 3, 4, 5]), "y": np.array([4, 5, 6, 7, 8])}
        file["tree1"] = {
            "x": np.array([1, 2, 3, 4, 5]),
            "y": np.array([4, 5, 6, 7, 8]),
        }

    with uproot.open(Path(tmp_path) / "two_trees.root") as file:
        hepconvert.copy_root(
            Path(tmp_path) / "copied.root",
            Path(tmp_path) / "two_trees.root",
            drop_branches={"tree": "x", "tree1": "y"},
            force=True,
        )

        with uproot.open(Path(tmp_path) / "copied.root") as copy:
            assert copy.keys(cycle=False) == ["tree", "tree1"]
            assert copy["tree1"].keys() == ["x"]
            assert copy["tree"].keys() == ["y"]
            for tree in copy.keys(cycle=False):
                for key in copy[tree].keys():
                    assert ak.all(copy[tree][key].array() == file[tree][key].array())


def test_keep_tree_and_branch(tmp_path):
    import numpy as np

    with uproot.recreate(Path(tmp_path) / "two_trees.root") as file:
        file["tree"] = {
            "x": np.array([1, 2, 3, 4, 5]),
            "y": np.array([4, 5, 6, 7, 8]),
            "z": np.array([4, 5, 6, 7, 8]),
        }
        file["tree1"] = {
            "x": np.array([1, 2, 3, 4, 5]),
            "y": np.array([4, 5, 6, 7, 8]),
        }

    with uproot.open(Path(tmp_path) / "two_trees.root") as file:
        hepconvert.copy_root(
            Path(tmp_path) / "copied.root",
            Path(tmp_path) / "two_trees.root",
            keep_branches={"tree": ["x", "z"], "tree1": "y"},
            force=True,
        )

        with uproot.open(Path(tmp_path) / "copied.root") as copy:
            assert copy.keys(cycle=False) == ["tree", "tree1"]
            assert copy["tree1"].keys() == ["y"]
            assert copy["tree"].keys() == ["x", "z"]
            for tree in copy.keys(cycle=False):
                for key in copy[tree].keys():
                    assert ak.all(copy[tree][key].array() == file[tree][key].array())
    hepconvert.copy_root(
        Path(tmp_path) / "copy.root",
        skhep_testdata.data_path("uproot-HZZ.root"),
        counter_name=lambda counted: "N" + counted,
        drop_trees=["events"],
        force=True,
    )
    file = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))
    assert "events" not in file.keys()
