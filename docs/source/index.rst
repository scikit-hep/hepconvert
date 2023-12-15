.. odapt documentation master file, created by
   sphinx-quickstart on Tue Dec  5 14:19:03 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
    :caption: Tutorials
    :hidden:

    intro

.. include:: main.toctree

.. toctree::
    :caption: Modules
    :hidden:

.. include:: odapt.toctree

.. include:: odapt.root.toctree

.. include:: odapt.parquet.toctree

.
Welcome to odapt's documentation!
=================================

``odapt`` is an easy-to-use file converter tool for columnar file formats like ROOT, Parquet, Feather, and HDF5. This is a user-request driven package, feature requests, feedback,

How to install
==============
odapt can be installed `from PyPI <https://pypi.org/project/odapt>`__ using pip.

.. code-block:: bash

    pip install odapt

odapt is not yet available using conda.

Motivation
**********
The goal of this package is to simplify the process of converting large files between common columnar file formats while maintaining the correct structure.

Limitations:
************
Currently works best with data in nanoAOD formats. Will expand at user request.

.. Indices and tables
.. ==================

.. * :ref:`modindex`
.. * :ref:`search`
