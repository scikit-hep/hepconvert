General Guide and Examples:
===========================
Is something missing from this guide? Please post your questions on the `discussions page <https://github.com/scikit-hep/hepconvert/discussions>`__!

Features of all (or most) functions:
----------------------------------------

**Automatic handling of Uproot duplicate counter issue:**
If you are using a hepconvert function that goes ROOT -> ROOT (both the input and output files are ROOT)
and working with data in jagged arrays, if branches have the same "fLeafCount", hepconvert
will group branches automatically so that Uproot will not create a `counter branch for each branch <https://github.com/scikit-hep/uproot5/discussions/903>`__.

**Quick Modifications of ROOT files and TTrees:**

Functions ``copy_root``, ``merge_root``, and ``root_to_parquet`` have a few options for applying quick
modifications to ROOT files and TTree data.

**Branch slimming:**
    Parameters ``keep_branches`` or ``drop_branches`` (list or dict) control branch slimming.
    Examples:

    .. code:: python

        >>> hepconvert.root_to_parquet("out_file.root", "in_file.root", keep_branches="x*", progress_bar=True, force=True)

        # Before:

        #  name                 | typename                 | interpretation
        #  ---------------------+--------------------------+-------------------------------
        #  x1                   | int64_t                  | AsDtype('>i8')
        #  x2                   | int64_t                  | AsDtype('>i8')
        #  y1                   | int64_t                  | AsDtype('>i8')
        #  y2                   | int64_t                  | AsDtype('>i8')

        # After:

        #  name                 | typename                 | interpretation
        #  ---------------------+--------------------------+-------------------------------
        #  x1                   | int64_t                  | AsDtype('>i8')
        #  x2                   | int64_t                  | AsDtype('>i8')

    .. code:: python

       >>> hepconvert.root_to_parquet("out_file.root", "in_file.root", keep_branches={"tree1": ["branch2", "branch3"], "tree2": ["branch2"]}, progress_bar=True, force=True)

        # Before:

        # Tree1:
        #  name                 | typename                 | interpretation
        #  ---------------------+--------------------------+-------------------------------
        #  branch1              | int64_t                  | AsDtype('>i8')
        #  branch2              | int64_t                  | AsDtype('>i8')
        #  branch3              | int64_t                  | AsDtype('>i8')

        # Tree2:
        #  name                 | typename                 | interpretation
        #  ---------------------+--------------------------+-------------------------------
        #  branch1              | int64_t                  | AsDtype('>i8')
        #  branch2              | int64_t                  | AsDtype('>i8')
        #  branch3              | int64_t                  | AsDtype('>i8')

        # After:

        # Tree1:
        #  name                 | typename                 | interpretation
        #  ---------------------+--------------------------+-------------------------------
        #  branch2              | int64_t                  | AsDtype('>i8')
        #  branch3              | int64_t                  | AsDtype('>i8')

        # Tree2:
        #  name                 | typename                 | interpretation
        #  ---------------------+--------------------------+-------------------------------
        #  branch2              | int64_t                  | AsDtype('>i8')


**Branch skimming:**
    Parameters ``cut`` and ``expressions`` control branch skimming. Both of these parameters go to Uproot's `iterate
    <https://uproot.readthedocs.io/en/latest/uproot.behaviors.TBranch.iterate.html>`__
    function. See Uproot's documentation for more details.

    Basic example:

    .. code:: python

        hepconvert.copy_root("skimmed_HZZ.root", "HZZ.root", keep_branches="Jet_",
            force=True, expressions="Jet_Px", cut="Jet_Px >= 10",)


**Remove TTrees:**
    Use parameters ``keep_ttrees`` or ``drop_ttrees`` to remove TTrees.

    .. code:: python

        # Creating example data:
        with uproot.recreate("two_trees.root") as file:
            file["tree"] = {"x": np.array([1, 2, 3])}
            file["tree1"] = {"x": np.array([1, 2, 3])}

        hepconvert.copy_root("one_tree.root", "two_trees.root", keep_trees=tree,
            force=True, expressions="Jet_Px", cut="Jet_Px >= 10",)


**How hepconvert works with ROOT**

hepconvert uses Uproot for reading and writing ROOT files; it also has the same limitations.
It currently only works with flat TTrees (nanoAOD-like data), and cannot yet read or write RNTuples.

As described in Uproot's documentation:

.. note::

    A small but growing list of data types can be written to files:

    * strings: TObjString
    * histograms: TH1*, TH2*, TH3*
    * profile plots: TProfile, TProfile2D, TProfile3D
    * NumPy histograms created with `np.histogram <https://numpy.org/doc/stable/reference/generated/numpy.histogram.html>`__, `np.histogram2d <https://numpy.org/doc/stable/reference/generated/numpy.histogram2d.html>`__, and `np.histogramdd <https://numpy.org/doc/stable/reference/generated/numpy.histogramdd.html>`__ with 3 dimensions or fewer
    * histograms that satisfy the `Universal Histogram Interface <https://uhi.readthedocs.io/>`__ (UHI) with 3 dimensions or fewer; this includes `boost-histogram <https://boost-histogram.readthedocs.io/>`__ and `hist <https://hist.readthedocs.io/>`__
    * PyROOT objects

**Memory Management**

Each hepconvert function has automatic and customizable memory management for working with large files.

Functions reading **ROOT** files will read in batches controlled by the parameter ``step_size``.
Set ``step_size`` to either an `int` to set the batch size to a number of entries, or a `string` in
form of "100 MB".


**Progress Bars**
hepconvert uses the package tqdm for progress bars, if you do not have the package installed an error message will provide installation instructions.
They are controlled with the ``progress_bar`` argument.
For example, to use a default progress bar with copy_root, set progress_bar to True:

.. code:: python

    hepconvert.copy_root("out_file.root", "in_file.root", progress_bar=True)


Some functions can handle a customized tqdm progress bar.
To use a customized tqdm progress bar, make a progress bar object and pass it to the hepconvert function like so,

.. code:: python

    >>> import tqdm

    >>> bar_obj = tqdm.tqdm(colour="GREEN", desc="Description")
    >>> hepconvert.add_histograms("out_file.root", "path/in_files/", progress_bar=bar_obj)

.. image:: https://raw.githubusercontent.com/scikit-hep/hepconvert/main/docs/docs-img/progress_bar.png
    :width: 450px
    :alt: hepconvert
    :target: https://github.com/scikit-hep/hepconvert


Some types of tqdm progress bar objects may not work in this way.


**Command Line Interface**

All functions are able to be run in the command line. See the "Command Line Interface Instructions" tab on the left to see CLI
instructions on individual functions.

Adding Histograms
-----------------
``hepconvert.add_histograms`` adds the values of many histograms
and writes the summed histograms to an output file (like ROOT's hadd, but limited
to histograms).


**Parameters of note:**

``union`` If True, adds the histograms that have the same name and appends all others
to the new file.

``append`` If True, appends histograms to an existing file. Force and append
cannot both be True.

``same_names`` If True, only adds together histograms which have the same name (key). If False,
histograms are added together based on TTree structure (bins must be equal).

Memory:
``add_histograms`` has no memory customization available currently. To maintain
performance it stores the summed histograms in memory until all files have
been read, then the summed histograms are written to the output file. Only
one input ROOT file is read and kept in memory at a time.


Merging TTrees
--------------
``hepconvert.merge_root`` merges TTrees in multiple ROOT files together. The end result is a single file containing data from all input files (again like ROOT's hadd, but can handle flat TTrees and histograms).

.. warning::
    At the moment, hepconvert.merge can only merge TTrees that have the same
    number of branches, with the same names and datatypes.
    We are working on adding backfill capabilities for mismatched TTrees.

**Features:**
merge_root has parameters ``cut``, ``expressions``, ``drop_branches``, ``keep_branches``, ``drop_trees`` and ``keep_trees``.


Copying TTrees
--------------
``hepconvert.copy_root`` copies TTrees in multiple ROOT files together.

.. warning::
    At the moment, hepconvert.merge can only merge TTrees that have the same
    number of branches, with the same names and datatypes.
    We are working on adding backfill capabilities for mismatched TTrees.

**Features:**
merge_root has parameters ``cut``, ``expressions``, ``drop_branches``, ``keep_branches``, ``drop_trees`` and ``keep_trees``.


Parquet to ROOT
---------------

Writes the data from a single Parquet file to one TTree in a ROOT file.
This function creates a new TTree (name the new tree with parameter ``tree``).


ROOT to Parquet
---------------

Writes the data from one TTree in a ROOT file to a single Parquet file.
If there are multiple TTrees in the file, specify one TTree to write to the Parquet file using the ``tree`` parameter.

**Features:**
root_to_parquet  has parameters ``cut``, ``expressions``, ``drop_branches``, ``keep_branches``.
