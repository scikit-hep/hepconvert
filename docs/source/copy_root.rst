Command Line Interface Guide: copy_root
=======================================

Instructions for function `hepconvert.copy_root <https://hepconvert.readthedocs.io/en/latest/hepconvert.copy_root.copy_root.html>`__

Command:
--------

.. code-block:: bash

    hepconvert copy-root [options] [OUT_FILE] [IN_FILE]


Examples:
---------

.. code-block:: bash

    hepconvert copy-root -f --progress-bar --keep-branches 'Jet_*' out_file.root in_file.root


Branch skimming using ``cut``:

.. code-block:: bash

    hepconvert copy-root -f --keep-branches 'Jet_*' --cut 'Jet_Px > 5' out_file.root in_file.root

Options:
--------

``--drop-branches``, ``-db`` and ``--keep-branches``, ``-kb``  list, str or dict. Specify branch names to remove from the ROOT file. Either a str, list of str (for multiple branches), or a dict with form {'tree': 'branches'} to remove branches from certain ttrees. Wildcarding accepted.

``--drop-trees``, ``-dt`` and ``--keep-trees``, ``-kt`` list of str, or str. Specify tree names to remove/keep TTrees in the ROOT files. Wildcarding accepted.

``--cut`` For branch skimming, passed to `uproot.iterate <https://uproot.readthedocs.io/en/latest/uproot.behaviors.TBranch.iterate.html>`__. str, if not None, this expression filters all of the expressions.

``--expressions`` For branch skimming, passed to `uproot.iterate <https://uproot.readthedocs.io/en/latest/uproot.behaviors.TBranch.iterate.html>`__. Names of TBranches or aliases to convert to ararys or mathematical expressions of them. If None, all TBranches selected by the filters are included.

``--force``, ``-f`` Use flag to overwrite a file if it already exists.

``--progress-bar`` Will show a basic progress bar to show how many TTrees have merged and written.

``--append``, ``-a`` Will append new TTree to an existing file.

``--compression``, ``-c`` Compression type. Options are "lzma", "zlib", "lz4", and "zstd". Default is "zlib".

``--compression-level`` Level of compression set by an integer. Default is 1.

``--name`` Give a name to the new TTree. Default is "tree".

``--title`` Give a title to the new TTree.

``--initial-basket-capacity`` (int) Number of TBaskets that can be written to the TTree without rewriting the TTree metadata to make room. Default is 10.

``--resize-factor`` (float) When the TTree metadata needs to be rewritten, this specifies how many more TBasket slots to allocate as a multiplicative factor. Default is 10.0.

``--step-size`` Size of batches of data to read and write. If an integer, the maximum number of entries to include in each iteration step; if a string, the maximum memory size to include. The string must be a number followed by a memory unit, such as “100 MB”. Default is "100 MB"
