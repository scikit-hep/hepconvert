import awkward as ak
import uproot

def parquet_to_root(
    destination,
    file,
    *,
    name="tree",
    # columns=None,
    # row_groups=None, # a range or something?
    compression="lz4",
    compression_level=1,
    ):
    # Will users want to control which columns/row_groups get written?
    # dak.from_parquet(read_path, split_row_groups=True)
    metadata = ak.metadata_from_parquet(file)
    
    out_file = uproot.recreate(destination)
    chunk = ak.from_parquet(file, row_groups=[0])
    typenames = {name: chunk[name].type for name in chunk.fields}

    out_file.mktree(name, typenames)
    out_file[name].extend({name: chunk[name] for name in chunk.fields})

    for i in range(1,metadata['num_row_groups']):
        out_file[name].extend(ak.from_parquet(file, row_groups=[i])) # Set size with extend.
        