.. hepconvert documentation master file, created by
   sphinx-quickstart on Tue Dec  5 14:19:03 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: main.toctree
.. include:: guide.toctree
.. include:: cli.toctree
.. toctree::
    :caption: Modules
    :hidden:

.. image:: https://raw.githubusercontent.com/scikit-hep/hepconvert/main/docs/docs-img/hepconvert_logo.svg
    :width: 450px
    :alt: hepconvert
    :target: https://github.com/scikit-hep/hepconvert

|

Welcome to hepconvert's documentation!
======================================

``hepconvert`` is an easy-to-use converter tool for columnar file formats ROOT, Parquet, Feather, and HDF5.
This package aims to allow users to higher control of file conversions (memory management, compression settings, etc.)
all from one function call. We are adding new features at user request, so please share your ideas on our
`github page <https://github.com/zbilodea/hepconvert/discussions/categories/ideas>`__!

How to install
==============
hepconvert can be installed `from PyPI <https://pypi.org/project/hepconvert>`__ using pip.

.. code-block:: bash

    pip install hepconvert

hepconvert is not yet available using conda.

Motivation
**********
Many users are all writing similar blocks of code each time they need to convert columnar files. It takes time to learn how to use different I/O packages,
write code, and work through bugs that may come up in this sometimes finicky process. ``hepconvert`` allows users to find and call just one function.

Limitations:
************
Currently works best with data in nanoAOD-like formats.
