import dask_awkward as dak
import uproot
def parquet_to_root(read_path,
    write_path,
    *,
    columns,
    storage_options,
    max_gap,
    max_block,
    footer_sample_size,
    generate_bitmasks,
    highlevel,
    behavior,
    ):
    arrays = dak.from_parquet(read_path, split_row_groups=True)
    tree = uproot.recreate(write_path)
    tree.mktree("tree", {arrays.partitions[0]}) #name? But root files aren't just TTrees...
    for i in range(1,arrays.npartitions):
        tree["tree"].extend(arrays.partitions[i])
        