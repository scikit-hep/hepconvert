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

    if drop_branches:
        if isinstance(drop_branches, dict):  # noqa: SIM102
            if (
                len(drop_branches) > 1
                and tree.name in drop_branches
                or tree.name == next(iter(drop_branches.keys()))
            ):
                drop_branches = drop_branches.get(tree.name)
        if isinstance(drop_branches, str) or len(drop_branches) == 1:
            drop_branches = tree.keys(filter_name=drop_branches)
        return [
            b.name
            for b in tree.branches
            if b.name not in count_branches and b.name not in drop_branches
        ]
    if keep_branches:
        if isinstance(keep_branches, dict):  # noqa: SIM102
            if (
                len(keep_branches) > 1
                and tree.name in keep_branches
                or tree.name == next(iter(keep_branches.keys()))
            ):
                keep_branches = keep_branches.get(tree.name)
        if isinstance(keep_branches, str) or len(keep_branches) == 1:
            keep_branches = tree.keys(filter_name=keep_branches)
            return [
                b.name
                for b in tree.branches
                if b.name not in count_branches and b.name in keep_branches
            ]
    return [b.name for b in tree.branches if b.name not in count_branches]


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
