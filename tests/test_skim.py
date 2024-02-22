from __future__ import annotations

from pathlib import Path

import awkward as ak
import pytest
import uproot

import hepconvert

skhep_testdata = pytest.importorskip("skhep_testdata")


def test_copy(tmp_path):
    file = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))
    cut_exp = "x >= 10"
    cut_branch = "Jet_Px"
    hepconvert.copy_root(
        Path(tmp_path) / "copy.root",
        skhep_testdata.data_path("uproot-HZZ.root"),
        keep_branches=["Jet_*"],
        counter_name=lambda counted: "N" + counted,
        force=True,
        cut_expression=cut_exp,
        cut_branch=cut_branch,
    )
    hepconvert_file = uproot.open(Path(tmp_path) / "copy.root")
    for key in hepconvert_file["events"].keys():
        if key.startswith("Jet_"):
            assert key in file["events"].keys()
            assert ak.all(
                hepconvert_file["events"][key].array()
                == file["events"][key].array()[file["events"]["Jet_Px"].array() >= 10]
            )


def test_trigger(tmp_path):
    file = uproot.open(
        skhep_testdata.data_path("nanoAOD_2015_CMS_Open_Data_ttbar.root")
    )

    hepconvert.copy_root(
        Path(tmp_path) / "copy.root",
        skhep_testdata.data_path("nanoAOD_2015_CMS_Open_Data_ttbar.root"),
        keep_branches=["Jet_*"],
        force=True,
        trigger=file["Events"]["HLT_QuadPFJet_DoubleBTagCSV_VBF_Mqq200"].array(),
    )
    hepconvert_file = uproot.open(Path(tmp_path) / "copy.root")
    for key in hepconvert_file["Events"].keys():
        if key.startswith("Jet_"):
            assert key in file["Events"].keys()
            assert ak.all(
                hepconvert_file["Events"][key].array()
                == file["Events"][key].array()[
                    file["Events"]["HLT_QuadPFJet_DoubleBTagCSV_VBF_Mqq200"].array()
                ]
            )


def test_incorrect_shape(tmp_path):
    cut_exp = "x >= 10"
    cut_branch = "Jet_Px"
    with pytest.raises(IndexError):
        hepconvert.copy_root(
            Path(tmp_path) / "copy.root",
            skhep_testdata.data_path("uproot-HZZ.root"),
            counter_name=lambda counted: "N" + counted,
            force=True,
            cut_expression=cut_exp,
            cut_branch=cut_branch,
        )


def test_merge_cut(tmp_path):
    file = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))["events"]

    hepconvert.merge_root(
        Path(tmp_path) / "test_simple.root",
        [
            skhep_testdata.data_path("uproot-HZZ.root"),
            skhep_testdata.data_path("uproot-HZZ.root"),
        ],
        cut_branch="Jet_Px",
        cut_expression="x >= 10",
        keep_branches="Jet_*",
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


def test_merge_trigger(tmp_path):
    file = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))["events"]

    hepconvert.merge_root(
        Path(tmp_path) / "test_simple.root",
        [
            skhep_testdata.data_path("uproot-HZZ.root"),
            skhep_testdata.data_path("uproot-HZZ.root"),
        ],
        trigger=file["Muon_Iso"].array() > 3,
        keep_branches="Muon_*",
        force=True,
        counter_name=lambda counted: "N" + counted,
    )
    hepconvert_file = uproot.open(Path(tmp_path) / "test_simple.root")
    for key in hepconvert_file["events"].keys():
        if key.startswith("Muon_"):
            assert key in file.keys()
            assert ak.all(
                hepconvert_file["events"][key].array()[:2421]
                == file[key].array()[file["Muon_Iso"].array() > 3]
            )
