import awkward as ak
import dask_awkward as dak
import uproot
def parquet_to_root(in_file,
    out_file,
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
    ):
    # dak.from_parquet(read_path, split_row_groups=True)
    metadata = ak.metadata_from_parquet(in_file)
    of = uproot.recreate(out_file)
    first = True
    for i in range(metadata['num_row_groups']): # So, we want Tbaskets to be about 1 mb? I forget. But something specific
        if first:
            print(type(ak.from_parquet(in_file, row_groups=[i])))
            of['tree'] = ak.from_parquet(in_file, row_groups=[i])
            first = False
        else:
            of['tree'].extend(ak.from_parquet(in_file, row_groups=[i])) # Set size with extend.
    
from skhep_testdata import data_path
parquet_to_root("https://pivarski-princeton.s3.amazonaws.com/chicago-taxi.parquet", "large_out.root")