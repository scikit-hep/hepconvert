from __future__ import annotations

from pathlib import Path

import awkward as ak
import pytest
import uproot

import hepconvert

skhep_testdata = pytest.importorskip("skhep_testdata")


def test_copy(tmp_path):
    file = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))
    cut_exp = "Jet_Px >= 10"
    hepconvert.copy_root(
        Path(tmp_path) / "copy.root",
        skhep_testdata.data_path("uproot-HZZ.root"),
        keep_branches="Jet_",
        counter_name=lambda counted: "N" + counted,
        force=True,
        expressions="Jet_Px",
        cut=cut_exp,
    )
    hepconvert_file = uproot.open(Path(tmp_path) / "copy.root")
    for key in hepconvert_file["events"].keys():
        if key.startswith("Jet_Px"):
            assert key in file["events"].keys()
            assert len(hepconvert_file["events"][key].arrays()) == 2321


def test_trigger(tmp_path):
    file = uproot.open(
        skhep_testdata.data_path("nanoAOD_2015_CMS_Open_Data_ttbar.root")
    )

    hepconvert.copy_root(
        Path(tmp_path) / "copy.root",
        skhep_testdata.data_path("nanoAOD_2015_CMS_Open_Data_ttbar.root"),
        keep_branches=["Photon_*"],
        force=True,
        cut="HLT_Photon30",
    )
    hepconvert_file = uproot.open(Path(tmp_path) / "copy.root")
    correct_len = 0
    for i in file["Events"]["HLT_Photon30"].array():
        if i is True:
            correct_len += 1
    for key in hepconvert_file["Events"].keys():
        if key.startswith("Jet_"):
            assert key in file["Events"].keys()
            assert len(hepconvert_file["Events"][key].array()) == correct_len
            assert ak.all(
                hepconvert_file["Events"][key].array()
                == file["Events"][key].array()[file["Events"]["HLT_Photon30"].array()]
            )


def test_incorrect_shape(tmp_path):
    cut_exp = "Jet_Px >= 10"
    with pytest.raises(IndexError):
        hepconvert.copy_root(
            Path(tmp_path) / "copy.root",
            skhep_testdata.data_path("uproot-HZZ.root"),
            counter_name=lambda counted: "N" + counted,
            force=True,
            cut=cut_exp,
        )


def test_merge_cut(tmp_path):
    file = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))["events"]

    hepconvert.merge_root(
        Path(tmp_path) / "test_simple.root",
        [
            skhep_testdata.data_path("uproot-HZZ.root"),
            skhep_testdata.data_path("uproot-HZZ.root"),
        ],
        cut="Jet_Px >= 10",
        keep_branches="Jet_*",
        progress_bar=True,
        force=True,
        counter_name=lambda counted: "N" + counted,
    )
    hepconvert_file = uproot.open(Path(tmp_path) / "test_simple.root")
    for key in hepconvert_file["events"].keys():
        if key.startswith("Jet_"):
            assert key in file.keys()
            assert ak.all(
                hepconvert_file["events"][key].array()[:2421]
                == file[key].array()[file["Jet_Px"].array() >= 10]
            )
