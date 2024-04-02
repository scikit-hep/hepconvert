General Guide and Examples:
===========================
Is something missing from this guide? Please let us know on the discussions page!

Adding Histograms
-----------------
(similar to hadd)

hepconvert's function ``hepconvert.add_histograms()`` adds the values of many histograms and writes the summed histograms to an output file.

This function can be run in the command-line, see the `add cli guide <>`__

**Parameters of note:**


Memory:
This function will


Merging TTrees
--------------
(also similar to hadd)

**Parameters of note:**

Parquet to ROOT
---------------

Writes the data from a single Parquet file to one TTree in a ROOT file.
This function creates a new TTree (which can be named)

**Parameters of note:**

``name`` str, will be the name of the new TTree. Defaults to "tree"
``progress_bar`` bool or tdqm object. If True, a basic progress bar will appear. Defaults to ``False``.

ROOT to Parquet
---------------

Writes the data from a single flat TTree to a Parquet file.

**Parameters of note:**

``tree`` str, If there are multiple TTrees in the ROOT file being read, pass the name of one TTree to write.

Branch slimming:
    ``keep_branches`` or ``drop_branches`` (list or dict):

    .. code:: python

        hepconvert.root_to_parquet("out_file.root", "in_file.root", keep_branches=[], progress_bar=True, force=True)

    .. code:: python

        hepconvert.root_to_parquet("out_file.root", "in_file.root", keep_branches={"tree1": ["branch2", "branch3"], "tree2": ["branch2"]}, progress_bar=True, force=True)

Branch skimming:

    ``cut``
    and
    ``expressions``

Remove TTrees:
    ``keep_ttrees`` or ``drop_ttrees``

How hepconvert works with ROOT
------------------------------

hepconvert uses Uproot for reading and writing ROOT files; it also has the same limitations.

As described in Uproot's documentation:

.. note::

    A small but growing list of data types can be written to files:

    * strings: TObjString
    * histograms: TH1*, TH2*, TH3*
    * profile plots: TProfile, TProfile2D, TProfile3D
    * NumPy histograms created with `np.histogram <https://numpy.org/doc/stable/reference/generated/numpy.histogram.html>`__, `np.histogram2d <https://numpy.org/doc/stable/reference/generated/numpy.histogram2d.html>`__, and `np.histogramdd <https://numpy.org/doc/stable/reference/generated/numpy.histogramdd.html>`__ with 3 dimensions or fewer
    * histograms that satisfy the `Universal Histogram Interface <https://uhi.readthedocs.io/>`__ (UHI) with 3 dimensions or fewer; this includes `boost-histogram <https://boost-histogram.readthedocs.io/>`__ and `hist <https://hist.readthedocs.io/>`__
    * PyROOT objects

hepconvert currently works with flat TTrees (nanoAOD-like data).

Progress Bars
-------------
hepconvert uses the package tqdm for progress bars.
They are controlled with the ``progress_bar`` argument.
