import uproot
import numpy as np


def add_1D_hists(files, hist_name, members, values, bins):
    for path in files[1:]:
        with uproot.open(path) as file:
            hist = file[hist_name]
            if bins != hist.member('fN'):
                raise ValueError(
                    "Bins must be equal, not " + bins + " and " + hist.member('fN')
                )
            if hist.member('fName') != hist_name:
                raise ValueError(
                    "Names must be the same, not " + hist_name + " and " + hist.member('fName')
                )
            
            temp_members = [
                            hist.member('fEntries'), 
                            hist.member('fTsumw'),
                            hist.member('fTsumw2'),
                            hist.member('fTsumwx'),
                            hist.member('fTsumwx2'),
                            hist.variances(flow=True)
                           ]
            
            values += hist.values(flow=True)
            members += temp_members
    return uproot.writing.identify.to_TH1x(hist.member("fName"), hist.member("fTitle"), values,
                                            *members[0:6], hist.member("fXaxis"))

def add_2D_hists(files, hist_name, values, members, bins):
    for path in files[1:]:
        with uproot.open(path) as file:
            hist = file[hist_name]
            if bins != hist.member('fN'):
                raise ValueError(
                    "Bins must be equal, not "+ {members['fN']} + " and " + {hist.member('fN')}
                )
            if hist.member('fName') != hist_name:
                raise ValueError(
                    "Names must be the same, not "+ {members['fN']} + " and " + {hist.member('fName')}
                )
            
            temp_members = [
                            hist.member('fEntries'), 
                            hist.member('fTsumw'),
                            hist.member('fTsumw2'),
                            hist.member('fTsumwx'),
                            hist.member('fTsumwx2'),
                            hist.member('fTsumwy'),
                            hist.member('fTsumwy2'),
                            hist.member('fTsumxy'),
                            hist.variances(flow=True)
                           ]
            members += temp_members
            values += hist.values(flow=True)
    return uproot.writing.identify.to_TH1x(hist.member("fName"), hist.member("fTitle"), values, 
        *members[0:9],
        hist.member("fXaxis"), hist.member("fYaxis"))

def add_3D_hists(files, hist_names, values, members):
    for path in files[1:]:
        with uproot.open(path) as file:
            hist = file[hist_names]
            if members['fN'] != hist.member('fN'):
                raise ValueError(
                    "Bins must be equal, not "+ {members['fN']} + " and " + {hist.member('fN')}
                )
            if hist.member('fName') != hist_names:
                raise ValueError(
                    "Names must be the same, not "+ {members['fN']} + " and " + {hist.member('fN')}
                )
            temp_members = [
                hist.member('fEntries'), 
                hist.member('fTsumw'),
                hist.member('fTsumw2'),
                hist.member('fTsumwx'),
                hist.member('fTsumwx2'),
                hist.member('fTsumwy'),
                hist.member('fTsumwy2'),
                hist.member('fTsumxy'),
                hist.member('fTsumwz'),
                hist.member('fTsumwz2'),
                hist.member('fTsumwxz'),
                hist.member('fTsumwyz'),
                hist.variances(flow=True)
            ]
        members += temp_members
        values += hist.values(flow=True)
    return uproot.writing.identify.to_TH1x(hist.member("fName"), hist.member("fTitle"), values,
                            *members[0:14], hist.member("fXaxis"))

def find_histograms(file):
    # for i in filenames:
        with uproot.open(file) as i:
            array = i.classnames()
            list = np.array([i for i in array if (array.get(i).startswith("TH1") or array.get(i).startswith("TH2") or array.get(i).startswith("TH3"))])
        return list

def hadd_like(destination, filenames=None, directory=None, hist_names=None):
    """
    Args:
        destination (path-like): Name of the output file or file path.
        filenames (None, or list of str): 
        directory (None, str): Local path, may contain glob patterns 
        hist_names (None, str, or list of str): Names of histograms to be added together. 

    Adds together histograms from local ROOT files of a collection of ROOT files, and writes them to one ROOT file.
    """
    if directory!=None:
        import glob
        filenames = sorted(
            glob.glob(directory + f"/**/*{'.root'}", recursive=True)
        )

    if hist_names == None: # if histogram names are not provided
        hist_names = find_histograms(filenames[0])
        hist_names = hist_names[0]

    file = uproot.open(filenames[0]) # This file may never close until the end...
    hist_name = hist_names
    hist = file[hist_name]
    bins = hist.member('fN')
    if len(hist.axes) == 1:
        members = [
                    hist.member('fEntries'), 
                    hist.member('fTsumw'),
                    hist.member('fTsumw2'),
                    hist.member('fTsumwx'),
                    hist.member('fTsumwx2'),
                    hist.variances(flow=True)
                ]
        values = hist.values(flow=True)
        h_sum = add_1D_hists(filenames, hist.member('fName'), members, values, bins)
    elif len(hist.axes) == 2:
        members = [
            hist.member('fEntries'), 
            hist.member('fTsumw'),
            hist.member('fTsumw2'),
            hist.member('fTsumwx'),
            hist.member('fTsumwx2'),
            hist.member('fTsumwy'),
            hist.member('fTsumwy2'),
            hist.member('fTsumxy'),
            hist.variances(flow=True)
            ]
        values = hist.values(flow=True)
        h_sum = add_2D_hists(filenames, hist.member('fName'), members, values, bins)
    elif len(hist.axes) == 3:
        members = [
            hist.member('fEntries'), 
            hist.member('fTsumw'),
            hist.member('fTsumw2'),
            hist.member('fTsumwx'),
            hist.member('fTsumwx2'),
            hist.member('fTsumwy'),
            hist.member('fTsumwy2'),
            hist.member('fTsumxy'),
            hist.member('fTsumwz'),
            hist.member('fTsumwz2'),
            hist.member('fTsumwxz'),
            hist.member('fTsumwyz'),
            hist.variances(flow=True)
            ]
        values = hist.values(flow=True)
        h_sum = add_3D_hists(filenames, hist.member('fName'), members, values, bins)
    file_out = uproot.recreate(destination) # What compression level?
    file_out[h_sum.member("fName")] = h_sum
