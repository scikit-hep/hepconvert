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
from odapt.cli import cli

__all__ = ["__version__"]

if __name__ == "__main__":
    cli()
