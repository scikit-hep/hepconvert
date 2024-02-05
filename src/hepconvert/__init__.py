"""
Copyright (c) 2023 Zoë Bilodeau. All rights reserved.

hepconvert: File conversion package.
"""
from __future__ import annotations

from hepconvert._version import __version__
from hepconvert.copy_root import copy_root
from hepconvert.histogram_adding import add_histograms
from hepconvert.merge import merge_root
from hepconvert.parquet_to_root import parquet_to_root
from hepconvert.root_to_parquet import root_to_parquet

__all__ = [
    "__version__",
    "add_histograms",
    "merge_root",
    "copy_root",
    "parquet_to_root",
    "root_to_parquet",
]
