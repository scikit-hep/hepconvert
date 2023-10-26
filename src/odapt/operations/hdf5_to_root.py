import h5py
import awkward as ak
import uproot
import numpy as np

def hdf5_to_root(read_path, write_path, *, chunk_shape=True, compression=None,):
    f = h5py.File(read_path, 'r') # 'r' for read only, file must exist (it's the default though)
    # print(f.ref_dtype)
    
    keys = [key for key in f.keys()] # keys may or not be for groups
    # print([key for key in f.keys()])
    out_file = uproot.recreate(write_path)
    # tree.mktree("tree", branch_types=type(dset), ) # Fix type obv
    for key in keys:
        print(type(f[key]))
        if isinstance((f[key]), h5py.Group): #group or whatever...
            recur_in_group(group, out_file)
        else:
            print("true?")
            print([f[key][s] for s in f[key].iter_chunks()])
            out_file[key] = ({key:[f[key][s] for s in f[key].iter_chunks()]})
            out_file[key].extend({key:[f[key][s] for s in f[key].iter_chunks()]})
    # del f or something - CLOSE FILE!

def recur_in_group(group, out_file):
    keys = [key for key in group.keys()] #Does this not work?
    for key in keys:
        if isinstance((group[key]), h5py.Group): #group or swhatever...
            recur_in_group(group[key], out_file)
        else:
            print("true?")
            print([group[key][s] for s in group[key].iter_chunks()])
            out_file[key] = ({key:[group[key][s] for s in group[key].iter_chunks()]})
            out_file[key].extend({key:[group[key][s] for s in group[key].iter_chunks()]})

f = h5py.File("/Users/zobil/Documents/odapt/tests/samples/mytestfile.hdf5", "w")
group = f.create_group("test")
from numpy.random import Generator, PCG64
rng = Generator(PCG64())
array = rng.standard_normal([10000])
group = f.create_group("datasets", track_order=True)
dset = group.create_dataset("mydataset", data=(array), dtype='f', chunks=True)

array1 = rng.standard_normal([10000])
dset1 = group.create_dataset("mydataset1", data=(array1), dtype='f', chunks=True)
hdf5_to_root("/Users/zobil/Documents/odapt/tests/samples/mytestfile.hdf5", "/Users/zobil/Documents/odapt/tests/samples/destination.root")
with uproot.open("/Users/zobil/Documents/odapt/tests/samples/destination.root") as file:
    keys = file.keys(cycle=False)
    ttree1 = file[keys[0]]
    branches = ttree1.branches
    print(file[keys[0]].name == "mydataset")
    print(keys[0])
    print(ttree1[keys[0]].arrays())
    ttree2 = file[keys[1]]
    branches = ttree2.branches
    print(ttree2.name == "mydataset1")
    print(keys[1])
    print(ttree2.arrays())

# When writing with Uproot, every time you call uproot.WritableTree.extend,
# you create a new TBasket (for all TBranches, so you create a new cluster).
# You can use extend inside of iterate to resize TBaskets from an input 
# file to an output file.

