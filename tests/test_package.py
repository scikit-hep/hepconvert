from __future__ import annotations

import importlib.metadata

import odapt as m


def test_version():
    assert importlib.metadata.version("odapt") == m.__version__
