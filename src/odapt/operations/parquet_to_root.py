import awkward as ak
import dask_awkward as dak
import uproot
import numpy as np

def parquet_to_root(
    in_file,
    out_file,
    *,
    name="tree",
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
    # Will users want to control which columns/row_groups get written?

    # dak.from_parquet(read_path, split_row_groups=True)
    metadata = ak.metadata_from_parquet(in_file)
    
    of = uproot.recreate(out_file)

    data = ak.from_parquet(in_file, row_groups=[0])
    typenames = {name: data[name].type for name in data.fields}
    group_names = [] #len data?
    print(data['Jet'])
    group_names = np.unique(group_names)

    of.mktree(name, typenames)
    of[name].extend(data)

    for i in range(1,metadata['num_row_groups']):
        of[name].extend(ak.from_parquet(in_file, row_groups=[i])) # Set size with extend.
        
    
# Setup example: CHANGE TO ZIPPED

from skhep_testdata import data_path
file = uproot.open(data_path("uproot-HZZ.root"))
tree = file['events']
groups = []
count_branches = []
temp_branches = [branch.name for branch in tree.branches]
temp_branches1 = [branch.name for branch in tree.branches]
cur_group = 0
for branch in temp_branches:
    if len(tree[branch].member("fLeaves")) > 1:
        msg = "Cannot handle split objects."
        raise NotImplementedError(msg)
    if tree[branch].member("fLeaves")[0].member("fLeafCount") is None:
        continue
    groups.append([])
    groups[cur_group].append(branch)
    for branch1 in temp_branches1:
        if tree[branch].member("fLeaves")[0].member("fLeafCount") is tree[
            branch1
        ].member("fLeaves")[0].member("fLeafCount") and (
            tree[branch].name != tree[branch1].name
        ):
            groups[cur_group].append(branch1)
            temp_branches.remove(branch1)
    count_branches.append(tree[branch].count_branch.name)
    temp_branches.remove(tree[branch].count_branch.name)
    temp_branches.remove(branch)
    cur_group += 1

edit = tree.arrays()
chunks = {name: array for name, array in zip(ak.fields(edit), ak.unzip(edit))}
# for chunk in uproot.iterate(tree, step_size=10000, how=dict):
for key in count_branches:
    del chunks[key]
for group in groups:
    if (len(group)) > 1:
        chunks.update(
                {group[0][0 : (group[0].index("_"))]: ak.zip(
                    {
                        name[
                            group[0].index("_") + 1 :
                        ]: array
                        for name, array in zip(
                            ak.fields(edit), ak.unzip(edit)
                        )
                        if name in group
                    }
                )
            }
        )
    for key in group:
        del chunks[key]
    
# array = file['events'].arrays()
print(chunks['Jet'])
array = ak.from_iter({i: chunks[i] for i in chunks})
print(array['Jet'])
ak.to_parquet(array, "uproot-HZZ.parquet")

parquet_to_root("tests/samples/uproot-HZZ.parquet", "tests/samples/parquet_test.parquet", name="tree")
test = uproot.open("tests/samples/parquet_test.parquet")
print(test["tree"].show())