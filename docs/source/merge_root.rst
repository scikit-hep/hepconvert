Command Line Interface Guide: `merge_root`
==========================================
Instructions for function `hepconvert.merge <https://github.com/zbilodea/hepconvert/blob/6e87ec51296c5623debb75a25cafcc7cc8de245a/src/hepconvert/merge.py>`__.

.. code-block:: bash

    hepconvert merge-root [options] [OUT_FILE] [IN_FILES]

Example:

.. code-block:: bash

    hepconvert merge-root --progress-bar True --keep-branches 'Jet_*' out_file.root directory/in_files/

Options:
--------
``--drop-branches``, ``--keep-branches``: list, str or dict (to select branches from specific ttrees)


``--drop-trees``, ``--keep-trees``: list or str


``--progress-bar``: bool

