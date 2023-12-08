"""
Copyright (c) 2023 Zoë Bilodeau. All rights reserved.

odapt: File conversion package.
"""
from __future__ import annotations

from odapt._version import __version__
from odapt.root import (
    copy,  # noqa: F401
    hadd,  # noqa: F401
    merge,  # noqa: F401
)

__all__ = ["__version__"]
