Command Line Interface Guide: parquet_to_root
=============================================

Instructions for function `parquet_to_root <https://hepconvert.readthedocs.io/en/latest/hepconvert.parquet_to_root.parquet_to_root.html>`__.

.. code-block:: bash

    hepconvert parquet-to-root [options] [OUT_FILE] [IN_FILE]

Example:

.. code-block:: bash

    hepconvert parquet-to-root -f --progress-bar True --name new_tree out_file.root in_file.parquet

This will write the data from a Parquet file to a flat TTree with the name "new_tree".

Options:
--------

``--force``, ``-f`` Use flag to overwrite a file if it already exists.

``--progress-bar`` Will create a basic progress bar to show how many row-groups have been written.

``--append`` Will append new TTree to an existing file.

``--compression``, ``-c`` Compression type. Options are "lzma", "zlib", "lz4", and "zstd". Default is "zlib".

``--compression-level`` Level of compression set by an integer. Default is 1.

``--name`` Give a name to the new TTree. Default is "tree".

``--title`` Give a title to the new TTree.

``--initial-basket-capacity`` (int) Number of TBaskets that can be written to the TTree without rewriting the TTree metadata to make room. Default is 10.

``--resize-factor`` (float) When the TTree metadata needs to be rewritten, this specifies how many more TBasket slots to allocate as a multiplicative factor. Default is 10.0.
