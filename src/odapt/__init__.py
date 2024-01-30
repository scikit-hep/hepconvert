"""
Copyright (c) 2023 Zoë Bilodeau. All rights reserved.

odapt: File conversion package.
"""
from __future__ import annotations

from odapt._version import __version__
from odapt.copy_root import copy_root
from odapt.histogram_adding import hadd
from odapt.merge import hadd_and_merge
from odapt.parquet_to_root import parquet_to_root
from odapt.root_to_parquet import root_to_parquet

__all__ = [
    "__version__",
    "hadd",
    "hadd_and_merge",
    "copy_root",
    "parquet_to_root",
    "root_to_parquet",
]
