from __future__ import annotations

import h5py
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

    keys = list(f.keys())
    out_file = uproot.recreate(write_path)
    for key in keys:
        if isinstance((f[key]), h5py.Group):
            recur_in_group(group, out_file)
        else:
            first = True
            for chunk in f[key].iter_chunks():
                if first is True:
                    out_file[key] = {key: [f[key][chunk]]}
                    first = False
                out_file[key].extend({key: [f[key][chunk]]})
    # del f or something - CLOSE FILE!


def recur_in_group(group, out_file_directory):
    keys = list(group.keys())
    tree = out_file_directory.mktree(
        group.name, {keys[i]: group[keys[i]].dtype for i, value in enumerate(keys)}
    )  # Fix type obv

    for key in keys:
        if isinstance((group[key]), h5py.Group):
            tree = recur_in_group(group[key], tree)

    chunks = list(group[key].iter_chunks())
    tree.extend({key: [[group[key][chunk]] for chunk in chunks] for key in keys})
    return tree


f = h5py.File("/Users/zobil/Documents/odapt/tests/samples/mytestfile.hdf5", "w")

group = f.create_group("test")
from numpy.random import PCG64, Generator

rng = Generator(PCG64())
array = rng.standard_normal([10000])
group = f.create_group("datasets", track_order=True)
dset = group.create_dataset("mydataset", data=(array), dtype="f", chunks=True)

array1 = rng.standard_normal([10000])
dset1 = group.create_dataset("mydataset1", data=(array1), dtype="f", chunks=True)
hdf5_to_root(
    "/Users/zobil/Documents/odapt/tests/samples/mytestfile.hdf5",
    "/Users/zobil/Documents/odapt/tests/samples/destination.root",
)
