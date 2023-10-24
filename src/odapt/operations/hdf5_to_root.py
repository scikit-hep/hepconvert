from __future__ import annotations

import awkward as ak
import h5py
import numpy as np
import uproot


def hdf5_to_root(
    read_path,
    write_path,
    *,
    chunk_shape=True,
    compression=None,
):
    f = h5py.File(
        read_path, "r"
    )  # 'r' for read only, file must exist (it's the default though)
    keys = list(f.keys())  # keys may or not be for groups
    # print([key for key in f.keys()])
    file = uproot.recreate(write_path)
    # tree.mktree("tree", branch_types=type(dset), ) # Fix type obv
    for key in keys:
        if type(f[key]) != "group":  # group or whatever...
            print("here")
            data = np.empty(
                100,
            )
            data = f[key].read_direct(data)
            print("print data", data)
            if key == keys[0]:
                file[key] = ak.Array([f[key][s] for s in f[key].iter_chunks()])
            file[key].extend(ak.Array([f[key][s] for s in f[key].iter_chunks()]))


def recur_in_group(
    group,
):
    keys = f.keys()  # Does this not work?


f = h5py.File("/Users/zobil/Documents/odapt/tests/samples/mytestfile.hdf5", "w")
from numpy.random import PCG64, Generator

rng = Generator(PCG64())
array = rng.standard_normal([100])
print(array)
dset = f.create_dataset("mydataset", data=(array), dtype="i", chunks=True)
hdf5_to_root(
    "/Users/zobil/Documents/odapt/tests/samples/mytestfile.hdf5",
    "/Users/zobil/Documents/odapt/tests/samples/destination.root",
)
with uproot.open("/Users/zobil/Documents/odapt/tests/samples/destination.root") as file:
    print(file.keys())


# When writing with Uproot, every time you call uproot.WritableTree.extend,
# you create a new TBasket (for all TBranches, so you create a new cluster).
# You can use extend inside of iterate to resize TBaskets from an input
# file to an output file.
