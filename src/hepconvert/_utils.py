# def get_counter_branches(tree):
#     counter_branches =
from __future__ import annotations

import numpy as np


def group_branches(tree, keep_branches):
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
    count_branches = []
    for branch in tree.keys():  # noqa: SIM118
        if tree[branch].member("fLeaves")[0].member("fLeafCount") is None:
            continue
        count_branches.append(tree[branch].count_branch.name)
    return np.unique(count_branches, axis=0)
