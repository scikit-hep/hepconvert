from __future__ import annotations

import numpy as np


def group_branches(tree, keep_branches):
    """
    Creates groups for ak.zip to avoid duplicate counters being created.
    Groups created if branches have the same branch.member("fLeafCount")
    """
    groups = []
    count_branches = []
    temp_branches = tree.keys(filter_name=keep_branches)
    temp_branches1 = tree.keys(filter_name=keep_branches)
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
        temp_branches.remove(branch)
        cur_group += 1
    return groups, count_branches


def get_counter_branches(tree):
    """
    Gets counter branches to remove them in merge etc.
    """
    count_branches = []
    for branch in tree.keys():  # noqa: SIM118
        if tree[branch].member("fLeaves")[0].member("fLeafCount") is None:
            continue
        count_branches.append(tree[branch].count_branch.name)
    return np.unique(count_branches, axis=0)


def filter_branches(tree, keep_branches, drop_branches, count_branches):
    """
    Creates lambda function for filtering branches based on keep_branches or drop_branches.
    """
    if drop_branches and keep_branches:
        msg = "Can specify either drop_branches or keep_branches, not both."
        raise ValueError(msg) from None
    branches = drop_branches if drop_branches else keep_branches
    keys = []
    if branches:
        if isinstance(branches, dict):  # noqa: SIM102
            if (
                len(branches) > 1
                and tree.name in branches
                or tree.name == next(iter(branches.keys()))
            ):
                keys = branches.get(tree.name)
        if isinstance(branches, str) or len(branches) == 1:
            keys = tree.keys(filter_name=branches)
        else:
            for i in branches:
                keys = np.union1d(keys, tree.keys(filter_name=i))
        if drop_branches:
            return [
                b.name
                for b in tree.branches
                if b.name not in count_branches and b.name not in keys
            ]
        return [
            b.name
            for b in tree.branches
            if b.name not in count_branches and b.name in keys
        ]
    return [b.name for b in tree.branches]


def check_tqdm():
    """
    Imports and returns ``tqdm``.
    """
    try:
        import tqdm  # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError as err:
        msg = """to use a 'tqdm' progress bar, install the 'tqdm' package with:
                    pip install tqdm
                            or
                    conda install conda-forge::tqdm"""
        raise ModuleNotFoundError(msg) from err
    return tqdm
