from __future__ import annotations

from pathlib import Path

import awkward as ak
import pytest
import uproot

from hepconvert.parquet_to_root import parquet_to_root

skhep_testdata = pytest.importorskip("skhep_testdata")


def test_hepdata(tmp_path):
    arrays = uproot.open(skhep_testdata.data_path("uproot-hepdata-example.root"))[
        "ntuple;1"
    ].arrays()

    ak.to_parquet(arrays, Path(tmp_path) / "uproot-hepdata-example.parquet")
    parquet_to_root(
        Path(tmp_path) / "uproot-hepdata-example.root",
        Path(tmp_path) / "uproot-hepdata-example.parquet",
        name="ntuple",
    )
    test = uproot.open(Path(tmp_path) / "uproot-hepdata-example.root")
    original = uproot.open(skhep_testdata.data_path("uproot-hepdata-example.root"))

    for key in original["ntuple"].keys():
        assert key in test["ntuple"].keys()
    for key in test["ntuple"].keys():
        assert key in original["ntuple"].keys()
    for key in test["ntuple"].keys():
        assert ak.all(test["ntuple"].arrays()[key] == original["ntuple"].arrays()[key])


def test_hzz(tmp_path):
    file = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))

    tree = file["events"]
    groups = []
    count_branches = []
    temp_branches = [branch.name for branch in tree.branches]
    temp_branches1 = [branch.name for branch in tree.branches]
    cur_group = 0
    for branch in temp_branches:
        if len(tree[branch].member("fLeaves")) > 1:
            msg = "Cannot handle split objects."
            raise NotImplementedError(msg)
        if tree[branch].member("fLeaves")[0].member("fLeafCount") is None:
            continue
        groups.append([])
        groups[cur_group].append(branch)
        for branch1 in temp_branches1:
            if tree[branch].member("fLeaves")[0].member("fLeafCount") is tree[
                branch1
            ].member("fLeaves")[0].member("fLeafCount") and (
                tree[branch].name != tree[branch1].name
            ):
                groups[cur_group].append(branch1)
                temp_branches.remove(branch1)
        count_branches.append(tree[branch].count_branch.name)
        temp_branches.remove(tree[branch].count_branch.name)
        temp_branches.remove(branch)
        cur_group += 1

    edit = tree.arrays()
    chunks = dict(zip(ak.fields(edit), ak.unzip(edit)))
    for key in count_branches:
        del chunks[key]
    for group in groups:
        if (len(group)) > 1:
            chunks.update(
                {
                    group[0][0 : (group[0].index("_"))]: ak.zip(
                        {
                            name[group[0].index("_") + 1 :]: array
                            for name, array in zip(ak.fields(edit), ak.unzip(edit))
                            if name in group
                        }
                    )
                }
            )
        for key in group:
            del chunks[key]
    record = ak.Record(chunks)
    ak.to_parquet(record, "uproot-HZZ.parquet")
    parquet_to_root(
        Path(tmp_path) / "parquet_HZZ.root",
        "uproot-HZZ.parquet",
        name="events",
        progress_bar=True,
        counter_name=lambda counted: "N" + counted,
    )
    test = uproot.open(Path(tmp_path) / "parquet_HZZ.root")
    original = uproot.open(skhep_testdata.data_path("uproot-HZZ.root"))

    for key in original["events"].keys():
        assert key in test["events"].keys()
    for key in test["events"].keys():
        assert key in original["events"].keys()
    for key in test["events"].keys():
        assert ak.all(test["events"].arrays()[key] == original["events"].arrays()[key])
