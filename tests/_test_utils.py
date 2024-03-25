import awkward as ak

def compare_ttrees(t1, t2):
    for key in t1.keys(cycle=False):
        assert key in t2.keys(cycle=False)
        assert ak.all(t1[key].arrays() == t2[key].arrays())