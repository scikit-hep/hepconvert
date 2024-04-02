Command Line Interface Guide: root_to_parquet
=============================================

Instructions for function `hepconvert.root_to_parquet <https://hepconvert.readthedocs.io/en/latest/hepconvert.root_to_parquet.root_to_parquet.html>`__

Command:
--------

.. code-block:: bash

    hepconvert root-to-parquet [options] [OUT_FILE] [IN_FILE]


Examples:
---------

.. code-block:: bash

    hepconvert root-to-parquet -f --progress-bar --tree 'tree1' out_file.parquet in_file.root


Options:
--------

``tree`` (str) if there are multiple TTrees in the input file, specify the name of the TTree to copy.

``--drop-branches``, ``-db``, and ``--keep-branches``, ``-kb`` (list) str or dict Specify branch names to remove from the ROOT file. Either a str, list of str (for multiple branches), or a dict with form {'tree': 'branches'} to remove branches from certain ttrees. Wildcarding accepted.

``--cut`` For branch skimming, passed to `uproot.iterate <https://uproot.readthedocs.io/en/latest/uproot.behaviors.TBranch.iterate.html>`__. str, if not None, this expression filters all of the expressions.

``--expressions`` For branch skimming, passed to `uproot.iterate <https://uproot.readthedocs.io/en/latest/uproot.behaviors.TBranch.iterate.html>`__. Names of TBranches or aliases to convert to ararys or mathematical expressions of them. If None, all TBranches selected by the filters are included.

``--force`` or ``-f`` Use flag to overwrite a file if it already exists.

``--step-size`` (int) Size of batches of data to read and write. If an integer, the maximum number of entries to include in each iteration step; if a string, the maximum memory size to include. The string must be a number followed by a memory unit, such as “100 MB”. Default is "100 MB"

``--compression`` of ``-c`` (str) Compression type. Options are "lzma", "zlib", "lz4", and "zstd". Default is "zlib".

``--compression-level`` (int) Level of compression set by an integer. Default is 1.

Options passed to `ak.to_parquet <https://awkward-array.org/doc/main/reference/generated/ak.to_parquet.html>`__:
----------------------------------------------------------------------------------------------------------------

``--list-to32`` (bool) If True, convert Awkward lists into 32-bit Arrow lists
if they're small enough, even if it means an extra conversion. Otherwise,
signed 32-bit **ak.types.ListType** maps to Arrow `ListType`,
signed 64-bit **ak.types.ListType** maps to Arrow `LargeListType`,
and unsigned 32-bit **ak.types.ListType** picks whichever Arrow type its
values fit into.

``--string-to32`` (bool) Same as the above for Arrow `string` and `large_string`.

``--bytestring-to32`` (bool) Same as the above for Arrow `binary` and `large_binary`.

``--emptyarray-to`` (None or dtype) If None, **ak.types.UnknownType** maps to Arrow's
null type; otherwise, it is converted a given numeric dtype.

``--categorical-as-dictionary`` (bool) If True, **ak.contents.IndexedArray** and
#ak.contents.IndexedOptionArray labeled with `__array__ = "categorical"`
are mapped to Arrow `DictionaryArray`; otherwise, the projection is
evaluated before conversion (always the case without
`__array__ = "categorical"`).

``--extensionarray`` (bool) If True, this function returns extended Arrow arrays
(at all levels of nesting), which preserve metadata so that Awkward to
Arrow to Awkward preserves the array's **ak.types.Type** (though not
the #ak.forms.Form). If False, this function returns generic Arrow arrays
that might be needed for third-party tools that don't recognize Arrow's
extensions. Even with `extensionarray=False`, the values produced by
Arrow's `to_pylist` method are the same as the values produced by Awkward's
#ak.to_list.

``--count-nulls`` (bool) If True, count the number of missing values at each level
and include these in the resulting Arrow array, which makes some downstream
applications faster. If False, skip the up-front cost of counting them.

``-c`` or ``--compression`` (None, str, or dict) Compression algorithm name, passed to
`pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
Parquet supports `{"NONE", "SNAPPY", "GZIP", "BROTLI", "LZ4", "ZSTD"}`
(where `"GZIP"` is also known as "zlib" or "deflate"). If a dict, the keys
are column names (the same column names that #ak.forms.Form.columns returns
and #ak.forms.Form.select_columns accepts) and the values are compression
algorithm names, to compress each column differently.

``--compression-level`` (None, int, or dict None) Compression level, passed to
`pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
Compression levels have different meanings for different compression
algorithms: GZIP ranges from 1 to 9, but ZSTD ranges from -7 to 22, for
example. Generally, higher numbers provide slower but smaller compression.

``--row-group-size`` (int or None) Will be overwritten by ``step_size``.

``--data-page-size`` (None or int) Number of bytes in each data page, passed to
`pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
If None, the Parquet default of 1 MiB is used.

``--parquet-flavor`` (None or `"spark"`) If None, the output Parquet file will follow
Arrow conventions; if `"spark"`, it will follow Spark conventions. Some
systems, such as Spark and Google BigQuery, might need Spark conventions,
while others might need Arrow conventions. Passed to
`pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
as `flavor`.

``--parquet-version`` (`"1.0"`, `"2.4"`, or `"2.6"`) Parquet file format version.
Passed to `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
as `version`.

``--parquet-page-version`` (`"1.0"` or `"2.0"`) Parquet page format version.
Passed to `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
as `data_page_version`.

``--parquet-metadata-statistics`` (bool or dict) If True, include summary
statistics for each data page in the Parquet metadata, which lets some
applications search for data more quickly (by skipping pages). If a dict
mapping column names to bool, include summary statistics on only the
specified columns. Passed to
`pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
as `write_statistics`.

``--parquet-dictionary-encoding`` (bool or dict) If True, allow Parquet to pre-compress
with dictionary encoding. If a dict mapping column names to bool, only
use dictionary encoding on the specified columns. Passed to
`pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
as `use_dictionary`.

``--parquet-byte-stream-split`` (bool or dict) If True, pre-compress floating
point fields (`float32` or `float64`) with byte stream splitting, which
collects all mantissas in one part of the stream and exponents in another.
Passed to [pyarrow.parquet.ParquetWriter](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html).
as `use_byte_stream_split`.

``--parquet-coerce-timestamps`` (None, `"ms"`, or `"us"`) If None, any timestamps
(`datetime64` data) are coerced to a given resolution depending on
`parquet_version`: version `"1.0"` and `"2.4"` are coerced to microseconds,
but later versions use the `datetime64`'s own units. If `"ms"` is explicitly
specified, timestamps are coerced to milliseconds; if `"us"`, microseconds.
Passed to `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.
as `coerce_timestamps`.

``--parquet-old-int96-timestamps`` (None or bool) If True, use Parquet's INT96 format
for any timestamps (`datetime64` data), taking priority over `parquet_coerce_timestamps`.
If None, let the `parquet_flavor` decide. Passed to
`pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__
as `use_deprecated_int96_timestamps`.

``--parquet-compliant-nested`` (bool) If True, use the Spark/BigQuery/Parquet
`convention for nested lists <https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#nested-types>`__,
in which each list is a one-field record with field name "`element`";
otherwise, use the Arrow convention, in which the field name is "`item`".
Passed to `pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__
as `use_compliant_nested_type`.

``--parquet-extra-options`` (None or dict)
Any additional options to pass to
`pyarrow.parquet.ParquetWriter <https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html>`__.

``--storage-options`` (None or dict)
Any additional options to pass to
`fsspec.core.url_to_fs <https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.core.url_to_fs>`__
to open a remote file for writing.
