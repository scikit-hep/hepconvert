from __future__ import annotations

from pathlib import Path

import awkward as ak
import pytest
import uproot

import hepconvert

skhep_testdata = pytest.importorskip("skhep_testdata")


def HZZ_test(tmp_path):
    f = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))
    original = f["events"].arrays()
    hepconvert.root_to_parquet(
        in_file=skhep_testdata.data_path("uproot-HZZ.root"),
        out_file=Path(tmp_path) / "test.parquet",
        step_size="100 MB",
        force=True,
    )
    from_parquet = ak.from_parquet(Path(tmp_path) / "test.parquet")
    for key in f["events"].keys():
        assert ak.all(from_parquet[key] == original[key])


def specify_tree(tmp_path):
    f = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))
    original = f["events"].arrays()
    hepconvert.root_to_parquet(
        in_file=skhep_testdata.data_path("uproot-HZZ.root"),
        out_file=Path(tmp_path) / "test.parquet",
        tree="events",
        step_size="100 MB",
        force=True,
    )
    from_parquet = ak.from_parquet(Path(tmp_path) / "test.parquet")
    for key in f["events"].keys():
        assert ak.all(from_parquet[key] == original[key])


def Zmumu_test(tmp_path):
    f = uproot.open(skhep_testdata.data_path("uproot-Zmumu.root"))
    original = f["events"].arrays()
    hepconvert.root_to_parquet(
        in_file=skhep_testdata.data_path("uproot-Zmumu.root"),
        out_file=Path(tmp_path) / "test1.parquet",
        step_size="100 MB",
        force=True,
    )
    from_parquet = ak.from_parquet(Path(tmp_path) / "test1.parquet")
    for key in f["events"].keys():
        assert ak.all(from_parquet[key] == original[key])


def break_trees(tmp_path):
    with pytest.raises(AttributeError):
        hepconvert.root_to_parquet(
            in_file=skhep_testdata.data_path("uproot-hepdata-example.root"),
            out_file=Path(tmp_path) / "test2.parquet",
            step_size="100 MB",
        )


def check_row_group_size(tmp_path):
    f = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))
    original = f["events"].arrays()
    hepconvert.root_to_parquet(
        in_file=skhep_testdata.data_path("uproot-HZZ.root"),
        out_file=Path(tmp_path) / "test.parquet",
        step_size=1000,
        force=True,
    )
    from_parquet = ak.from_parquet(Path(tmp_path) / "test.parquet")
    for key in f["events"].keys():
        assert ak.all(from_parquet[key] == original[key])
    assert (
        ak.metadata_from_parquet(Path(tmp_path) / "test.parquet")["num_row_groups"] == 3
    )


def drop_branches(tmp_path):
    f = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))
    original = f["events"].arrays()
    hepconvert.root_to_parquet(
        in_file=skhep_testdata.data_path("uproot-HZZ.root"),
        out_file=Path(tmp_path) / "test.parquet",
        step_size=1000,
        drop_branches="Jet*",
        force=True,
    )
    from_parquet = ak.from_parquet(Path(tmp_path) / "test.parquet")
    for key in f["events"].keys():
        if key.startswith("Jet"):
            with pytest.raises(ak.errors.FieldNotFoundError):
                from_parquet[key]
        else:
            assert ak.all(from_parquet[key] == original[key])
    assert (
        ak.metadata_from_parquet(Path(tmp_path) / "test.parquet")["num_row_groups"] == 3
    )


def keep_branch(tmp_path):
    f = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))
    original = f["events"].arrays()
    hepconvert.root_to_parquet(
        in_file=skhep_testdata.data_path("uproot-HZZ.root"),
        out_file=Path(tmp_path) / "test.parquet",
        step_size=1000,
        keep_branches="Jet*",
        force=True,
    )
    from_parquet = ak.from_parquet(Path(tmp_path) / "test.parquet")
    for key in f["events"].keys():
        if not key.startswith("Jet"):
            with pytest.raises(ak.errors.FieldNotFoundError):
                from_parquet[key]
        else:
            assert ak.all(from_parquet[key] == original[key])
    assert (
        ak.metadata_from_parquet(Path(tmp_path) / "test.parquet")["num_row_groups"] == 3
    )


def keep_branches(tmp_path):
    f = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))
    original = f["events"].arrays()
    hepconvert.root_to_parquet(
        in_file=skhep_testdata.data_path("uproot-HZZ.root"),
        out_file=Path(tmp_path) / "test.parquet",
        step_size=1000,
        keep_branches=["Jet_*", "Muon_*"],
        force=True,
    )
    from_parquet = ak.from_parquet(Path(tmp_path) / "test.parquet")
    for key in f["events"].keys():
        if not key.startswith("Jet") and not key.startswith("Muon"):
            with pytest.raises(ak.errors.FieldNotFoundError):
                from_parquet[key]
        else:
            assert ak.all(from_parquet[key] == original[key])
    assert (
        ak.metadata_from_parquet(Path(tmp_path) / "test.parquet")["num_row_groups"] == 3
    )
