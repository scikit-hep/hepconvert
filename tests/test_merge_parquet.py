from __future__ import annotations

from pathlib import Path

import awkward as ak
import pytest

from hepconvert import merge

skhep_testdata = pytest.importorskip("skhep_testdata")


def simple_test(tmp_path):
    arr1 = ak.Array(
        {
            "a": [
                1,
                2,
            ],
            "b": [
                1,
                2,
            ],
            "c": [
                1,
                2,
            ],
        }
    )
    ak.to_parquet(arr1, Path(tmp_path / "arr1.parquet"))
    arr2 = ak.Array(
        {
            "a": [7, 8, 9],
            "b": [
                3,
                4,
                5,
            ],
        }
    )
    ak.to_parquet(arr2, Path(tmp_path / "arr2.parquet"))
    arr3 = ak.Array(
        {
            "a": [10, 11, 12, 13, 14],
            "c": [3, 4, 5, 6, 7],
            "d": [1, 2, 3, 4, 5],
        }
    )
    ak.to_parquet(arr3, Path(tmp_path / "arr3.parquet"))

    merge.merge_parquet(
        Path(tmp_path / "new.parquet"),
        [
            Path(tmp_path / "arr1.parquet"),
            Path(tmp_path / "arr2.parquet"),
            Path(tmp_path / "arr3.parquet"),
        ],
        force=True,
    )
    array = ak.from_parquet(Path(tmp_path / "new.parquet"))
    assert ak.all(array["a"] == [1, 2, 7, 8, 9, 10, 11, 12, 13, 14])
    assert ak.all(
        array["b"]
        == [
            1,
            2,
            3,
            4,
            5,
            None,
            None,
            None,
            None,
            None,
        ]
    )
    assert ak.all(array["c"] == [1, 2, None, None, None, 3, 4, 5, 6, 7])
    assert ak.all(
        array["d"]
        == [
            None,
            None,
            None,
            None,
            None,
            1,
            2,
            3,
            4,
            5,
        ]
    )
