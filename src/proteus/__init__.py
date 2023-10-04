"""
Copyright (c) 2023 Zoë Bilodeau. All rights reserved.

Proteus: File conversion package.
"""


from __future__ import annotations

from proteus._version import version as __version__

from proteus.operations import add_histograms

__all__ = [x for x in globals() if not x.startswith("_")]

def __dir__():
    return __all__