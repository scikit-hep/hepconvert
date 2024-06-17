from __future__ import annotations

from pathlib import Path

import awkward as ak
import numpy as np
import pytest
import uproot

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
    ak.to_parquet(arr1, "/Users/zobil/Documents/hepconvert/tests/samples/arr1.parquet")
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
    ak.to_parquet(arr2, "/Users/zobil/Documents/hepconvert/tests/samples/arr2.parquet")
    arr3 = ak.Array(
        {
            "a": [10, 11, 12, 13, 14],
            "c": [3, 4, 5, 6, 7],
            "d": [1, 2, 3, 4, 5],
        }
    )
    ak.to_parquet(arr3, "/Users/zobil/Documents/hepconvert/tests/samples/arr3.parquet")

    merge.merge_parquet(
        "/Users/zobil/Documents/hepconvert/tests/samples/new.parquet",
        [
            "/Users/zobil/Documents/hepconvert/tests/samples/arr1.parquet",
            "/Users/zobil/Documents/hepconvert/tests/samples/arr2.parquet",
            "/Users/zobil/Documents/hepconvert/tests/samples/arr3.parquet",
        ],
        force=True,
    )
    array = ak.from_parquet("/Users/zobil/Documents/hepconvert/tests/samples/new.parquet")
    
