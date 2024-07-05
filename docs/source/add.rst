CLI Guide for add_histograms (add)
==================================

Instructions for function `add_histograms <https://hepconvert.readthedocs.io/en/latest/hepconvert.histogram_adding.add_histograms.html>`__.

Command:
--------

.. code-block:: bash

    hepconvert add [options] [OUT_FILE] [IN_FILES]


Examples:
---------

.. code-block:: bash

    hepconvert add -f --progress-bar --union summed_hists.root hist1.root hist2.root hist3.root

Or, if files are in a directory:

.. code-block:: bash

    hepconvert add -f --append --same_names summed_hists.root path/directory/


Options:
--------

``--force``, ``-f`` Use flag to overwrite a file if it already exists.

``--progress-bar`` Will show a basic progress bar to show how many histograms have summed, and how many files have been read.

``--append``, ``-a`` Will append histograms to an existing file.

``--compression``, ``-c`` Compression type. Options are "lzma", "zlib", "lz4", and "zstd". Default is "zlib".

``--compression-level`` Level of compression set by an integer. Default is 1.

``--union`` Use flag to add together histograms that have the same name and append all others to the new file.

``--same-names`` Use flag to only add histograms together if they have the same name.
