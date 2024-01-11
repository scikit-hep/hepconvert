.. odapt documentation master file, created by
   sphinx-quickstart on Tue Dec  5 14:19:03 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: main.toctree

.. toctree::
    :caption: Modules
    :hidden:


Welcome to odapt's documentation!
=================================

``odapt`` is an easy-to-use converter tool for columnar file formats ROOT, Parquet, Feather, and HDF5.
This package aims to allow users to higher control of file conversions (memory management, compression settings, etc.)
all from one function call. We are adding new features at user request, so please share your ideas on our
`github page <https://github.com/zbilodea/odapt/discussions/categories/ideas>`__!

How to install
==============
odapt can be installed `from PyPI <https://pypi.org/project/odapt>`__ using pip.

.. code-block:: bash

    pip install odapt

odapt is not yet available using conda.

Motivation
**********
Many users are all writing similar blocks of code each time they need to convert columnar files. It takes time to learn how to use different I/O packages,
write code, and work through bugs that may come up in this sometimes finicky process. ``odapt`` allows users to find and call just one function.

Limitations:
************
Currently works best with data in nanoAOD-like formats.
