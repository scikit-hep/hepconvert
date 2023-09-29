import dask_awkward as da
import _collections_abc
import awkward as ak
import pyarrow.parquet

# Feather to parquet first?
def feather_to_parquet(
    # array,
    path,
    *,
    list_to32=False,
    string_to32=True,
    bytestring_to32=True,
    emptyarray_to=None,
    categorical_as_dictionary=False,
    extensionarray=True,
    count_nulls=True,
    compression="zstd",
    compression_level=None,
    row_group_size=64 * 1024 * 1024,
    data_page_size=None,
    parquet_flavor=None,
    parquet_version="2.4",
    parquet_page_version="1.0",
    parquet_metadata_statistics=True,
    parquet_dictionary_encoding=False,
    parquet_byte_stream_split=False,
    parquet_coerce_timestamps=None,
    parquet_old_int96_timestamps=None,
    parquet_compliant_nested=False,  # https://issues.apache.org/jira/browse/ARROW-16348
    parquet_extra_options=None,
    storage_options=None,
    # Potentially need:
        # expressions=None,
        # cut=None,
        # filter_name = no_filter,
        # filter_typename = no_filter,
        # aliases=None,
        # language=uproot.language.python.python_language,
        # entry_start=None,
        # entry_stop=None,
        # step_size="100 MB",
        # library="ak",
        # how=None,
):
    
    # Do in steps. can use argument "columns" to select amount - have it be the same as the 
    # size of a page is in a parquet? Or step_size like in uproot's iterate?
    # much to read, can choose bytes, tuple, str, list (not sure what most of those mean here)
    # Data page size!
    # First read ak.feather()
    # Read feather also has columns...best to read a bit at a time and keep track?

    """
    Args:
        array: Array-like data (anything #ak.to_layout recognizes).
        destination (path-like): Name of the output file, file path, or
            remote URL passed to [fsspec.core.url_to_fs](https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.core.url_to_fs)
            for remote writing.
        list_to32 (bool): If True, convert Awkward lists into 32-bit Arrow lists
            if they're small enough, even if it means an extra conversion. Otherwise,
            signed 32-bit #ak.types.ListType maps to Arrow `ListType`,
            signed 64-bit #ak.types.ListType maps to Arrow `LargeListType`,
            and unsigned 32-bit #ak.types.ListType picks whichever Arrow type its
            values fit into.
        string_to32 (bool): Same as the above for Arrow `string` and `large_string`.
        bytestring_to32 (bool): Same as the above for Arrow `binary` and `large_binary`.
        emptyarray_to (None or dtype): If None, #ak.types.UnknownType maps to Arrow's
            null type; otherwise, it is converted a given numeric dtype.
        categorical_as_dictionary (bool): If True, #ak.contents.IndexedArray and
            #ak.contents.IndexedOptionArray labeled with `__array__ = "categorical"`
            are mapped to Arrow `DictionaryArray`; otherwise, the projection is
            evaluated before conversion (always the case without
            `__array__ = "categorical"`).
        extensionarray (bool): If True, this function returns extended Arrow arrays
            (at all levels of nesting), which preserve metadata so that Awkward \u2192
            Arrow \u2192 Awkward preserves the array's #ak.types.Type (though not
            the #ak.forms.Form). If False, this function returns generic Arrow arrays
            that might be needed for third-party tools that don't recognize Arrow's
            extensions. Even with `extensionarray=False`, the values produced by
            Arrow's `to_pylist` method are the same as the values produced by Awkward's
            #ak.to_list.
        count_nulls (bool): If True, count the number of missing values at each level
            and include these in the resulting Arrow array, which makes some downstream
            applications faster. If False, skip the up-front cost of counting them.
        compression (None, str, or dict): Compression algorithm name, passed to
            [pyarrow.parquet.ParquetWriter](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html).
            Parquet supports `{"NONE", "SNAPPY", "GZIP", "BROTLI", "LZ4", "ZSTD"}`
            (where `"GZIP"` is also known as "zlib" or "deflate"). If a dict, the keys
            are column names (the same column names that #ak.forms.Form.columns returns
            and #ak.forms.Form.select_columns accepts) and the values are compression
            algorithm names, to compress each column differently.
        compression_level (None, int, or dict None): Compression level, passed to
            [pyarrow.parquet.ParquetWriter](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html).
            Compression levels have different meanings for different compression
            algorithms: GZIP ranges from 1 to 9, but ZSTD ranges from -7 to 22, for
            example. Generally, higher numbers provide slower but smaller compression.
        row_group_size (int or None): Number of entries in each row group (except the last),
            passed to [pyarrow.parquet.ParquetWriter.write_table](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html#pyarrow.parquet.ParquetWriter.write_table).
            If None, the Parquet default of 64 MiB is used.
        data_page_size (None or int): Number of bytes in each data page, passed to
            [pyarrow.parquet.ParquetWriter](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html).
            If None, the Parquet default of 1 MiB is used.
        parquet_flavor (None or `"spark"`): If None, the output Parquet file will follow
            Arrow conventions; if `"spark"`, it will follow Spark conventions. Some
            systems, such as Spark and Google BigQuery, might need Spark conventions,
            while others might need Arrow conventions. Passed to
            [pyarrow.parquet.ParquetWriter](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html).
            as `flavor`.
        parquet_version (`"1.0"`, `"2.4"`, or `"2.6"`): Parquet file format version.
            Passed to [pyarrow.parquet.ParquetWriter](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html).
            as `version`.
        parquet_page_version (`"1.0"` or `"2.0"`): Parquet page format version.
            Passed to [pyarrow.parquet.ParquetWriter](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html).
            as `data_page_version`.
        parquet_metadata_statistics (bool or dict): If True, include summary
            statistics for each data page in the Parquet metadata, which lets some
            applications search for data more quickly (by skipping pages). If a dict
            mapping column names to bool, include summary statistics on only the
            specified columns. Passed to
            [pyarrow.parquet.ParquetWriter](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html).
            as `write_statistics`.
        parquet_dictionary_encoding (bool or dict): If True, allow Parquet to pre-compress
            with dictionary encoding. If a dict mapping column names to bool, only
            use dictionary encoding on the specified columns. Passed to
            [pyarrow.parquet.ParquetWriter](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html).
            as `use_dictionary`.
        parquet_byte_stream_split (bool or dict): If True, pre-compress floating
            point fields (`float32` or `float64`) with byte stream splitting, which
            collects all mantissas in one part of the stream and exponents in another.
            Passed to [pyarrow.parquet.ParquetWriter](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html).
            as `use_byte_stream_split`.
        parquet_coerce_timestamps (None, `"ms"`, or `"us"`): If None, any timestamps
            (`datetime64` data) are coerced to a given resolution depending on
            `parquet_version`: version `"1.0"` and `"2.4"` are coerced to microseconds,
            but later versions use the `datetime64`'s own units. If `"ms"` is explicitly
            specified, timestamps are coerced to milliseconds; if `"us"`, microseconds.
            Passed to [pyarrow.parquet.ParquetWriter](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html).
            as `coerce_timestamps`.
        parquet_old_int96_timestamps (None or bool): If True, use Parquet's INT96 format
            for any timestamps (`datetime64` data), taking priority over `parquet_coerce_timestamps`.
            If None, let the `parquet_flavor` decide. Passed to
            [pyarrow.parquet.ParquetWriter](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html).
            as `use_deprecated_int96_timestamps`.
        parquet_compliant_nested (bool): If True, use the Spark/BigQuery/Parquet
            [convention for nested lists](https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#nested-types),
            in which each list is a one-field record with field name "`element`";
            otherwise, use the Arrow convention, in which the field name is "`item`".
            Passed to [pyarrow.parquet.ParquetWriter](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html).
            as `use_compliant_nested_type`.
        parquet_extra_options (None or dict): Any additional options to pass to
            [pyarrow.parquet.ParquetWriter](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html).
        storage_options (None or dict): Any additional options to pass to
            [fsspec.core.url_to_fs](https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.core.url_to_fs)
            to open a remote file for writing.
            """
    


        # Some kind of for-structure where it checks if there is more of the file before 
    parquet_writer = pq.ParquetWriter(path, ak.to_parquet(first_batch))
    for i in hasNextPage:
        parquet_writer.write_table(i)
        
        # class pyarrow.parquet.ParquetWriter(where, schema, filesystem=None, flavor=None, version='2.6', use_dictionary=True, compression='snappy', write_statistics=True, use_deprecated_int96_timestamps=None, compression_level=None, use_byte_stream_split=False, column_encoding=None, writer_engine_version=None, data_page_version='1.0', use_compliant_nested_type=True, encryption_properties=None, write_batch_size=None, dictionary_pagesize_limit=None, store_schema=True, write_page_index=False, **options)
    parquet_writer.close()
        