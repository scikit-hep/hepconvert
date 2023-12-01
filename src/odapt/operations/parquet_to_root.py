import awkward as ak
import dask_awkward as dak
import uproot
def parquet_to_root(
    in_file,
    out_file,
    name,
    fieldname_separator="_",
    *,
    columns=None,
    row_groups=None,
    storage_options=None,
    max_gap=64_000,
    max_block=256_000_000,
    footer_sample_size=1_000_000,
    generate_bitmasks=False,
    highlevel=True,
    behavior=None,
    compression="lz4",
    compression_level=1,
    ):

    # dak.from_parquet(read_path, split_row_groups=True)
    metadata = ak.metadata_from_parquet(in_file)
    
    of = uproot.recreate(out_file)

    data = ak.from_parquet(in_file, row_groups=[0])
    print(type(data))
    typenames = {name: data[name].type for name in data.fields}
    of.mktree(name, typenames)
    of[name].extend(data)

    for i in range(1,metadata['num_row_groups']):
        of[name].extend(ak.from_parquet(in_file, row_groups=[i])) # Set size with extend.
    
# from skhep_testdata import data_path

# file = uproot.open(data_path("uproot-HZZ.root"))

# array = file['events'].arrays()

# ak.to_parquet(array, "uproot-HZZ.parquet")

parquet_to_root("tests/samples/uproot-HZZ.parquet", "tests/samples/parquet_test.parquet", "tree")
test = uproot.open("tests/samples/parquet_test.parquet")
print(test[""].show())