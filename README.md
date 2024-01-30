# hepconvert

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][rtd-badge]][rtd-link]

[![PyPI version][pypi-version]][pypi-link]
[![Conda-Forge][conda-badge]][conda-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

[![GitHub Discussion][github-discussions-badge]][github-discussions-link]

<!-- SPHINX-START -->

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/zbilodea/hepconvert/workflows/CI/badge.svg
[actions-link]:             https://github.com/zbilodea/hepconvert/actions
[conda-badge]:              https://img.shields.io/conda/vn/conda-forge/hepconvert
[conda-link]:               https://github.com/conda-forge/hepconvert-feedstock
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/zbilodea/hepconvert/discussions
[pypi-link]:                https://pypi.org/project/hepconvert/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/hepconvert
[pypi-version]:             https://img.shields.io/pypi/v/hepconvert
[rtd-badge]:                https://readthedocs.org/projects/hepconvert/badge/?version=latest
[rtd-link]:                 https://hepconvert.readthedocs.io/en/latest/

The hepconvert library is a bridge between columnar file formats **ROOT, Parquet, Feather, and HDF5.** It aims to simplify file conversions in Python, replacing what is usually a multi-step process with one line of code, with builtin features for managing large datasets and choosing compression levels.

# Installation

hepconvert can be installed from [PyPI](https://pypi.org/project/hepconvert) using pip:

```bash
pip install hepconvert
```

# Getting started

```python
import hepconvert as od

# To merge two or more root files with TTrees,
# and add together any histograms:
od.hadd_and_merge("destination.root",
["ttree_file1.root", "ttree_file2.root"])


# To add merge files with only histograms:
od.hadd("destination.root",
["hist_file1.root", "hist_file2.root"])

```


<!-- prettier-ignore-end -->
