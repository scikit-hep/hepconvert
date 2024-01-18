"""
Copyright (c) 2023 Zoë Bilodeau. All rights reserved.

odapt: File conversion package.
"""
from __future__ import annotations

from odapt._version import __version__

from odapt.histogram_adding import hadd  # noqa: F401
from odapt.merge import hadd_and_merge  # noqa: F401
from odapt.copy_root import copy_root  # noqa: F401
from odapt.parquet_to_root import parquet_to_root  # noqa: F401
from odapt.root_to_parquet import root_to_parquet  # noqa: F401

__all__ = ["__version__"]
