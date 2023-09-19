from __future__ import annotations

import importlib.metadata

import proteus as m


def test_version():
    assert importlib.metadata.version("proteus") == m.__version__
