from __future__ import annotations

import importlib.metadata

import hepconvert as m


def test_version():
    assert importlib.metadata.version("hepconvert") == m.__version__
