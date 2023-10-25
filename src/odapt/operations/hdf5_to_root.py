import h5py
import awkward as ak
import uproot
import numpy as np

def hdf5_to_root(read_path, write_path, *, chunk_shape=True, compression=None,):
    f = h5py.File(read_path, 'r') # 'r' for read only, file must exist (it's the default though)
    print(f.ref_dtype)
    
    keys = [key for key in f.keys()] # keys may or not be for groups
    # print([key for key in f.keys()])
    file = uproot.recreate(write_path)
    # tree.mktree("tree", branch_types=type(dset), ) # Fix type obv
    for key in keys:
        print(key)
        if type(f[key]) != 'group': #group or whatever...
            print([f[key][s] for s in f[key].iter_chunks()])
            if key == keys[0]:
                file[key] = ak.Array({key:[f[key][s] for s in f[key].iter_chunks()]})
            file[key].extend({key:f[key][s] for s in f[key].iter_chunks()})

# def recur_in_group(group, ):
#     keys = group.keys() #Does this not work?
#     for key in keys:
#         if type(f[key]) != 'group': #group or swhatever...
#             data = f[key].read_direct(data)
#             if key == keys[0]:
#                 file[key] = ak.Array([f[key][s] for s in f[key].iter_chunks().items()])
#                 #Use extend in iterate...make extnesions as large as is feasible 
#                 # within memory constraints. Don't want a ROOT file full of small TBaskets...slow
#             print(f[key][s] for s in f[key].iter_chunks().items())
#             file[key].extend([f[key][s] for s in f[key].iter_chunks().items()])

f = h5py.File("/Users/zobil/Documents/odapt/tests/samples/mytestfile.hdf5", "w")
# group = f.create_group("test")
from numpy.random import Generator, PCG64
rng = Generator(PCG64())
array = rng.standard_normal([10000])
dset = f.create_dataset("mydataset", data=(array), dtype='f', chunks=True)

array = rng.standard_normal([10000])
dset = f.create_dataset("mydataset1", data=(array), dtype='f', chunks=True)
hdf5_to_root("/Users/zobil/Documents/odapt/tests/samples/mytestfile.hdf5", "/Users/zobil/Documents/odapt/tests/samples/destination.root")
with uproot.open("/Users/zobil/Documents/odapt/tests/samples/destination.root") as file:
    print(file.keys())



# When writing with Uproot, every time you call uproot.WritableTree.extend,
# you create a new TBasket (for all TBranches, so you create a new cluster).
# You can use extend inside of iterate to resize TBaskets from an input 
# file to an output file.

