import uproot
import numpy as np
import awkward as ak

def add_1D_hists(files, hist_name):
    bins = -1
    for path in files:
        with uproot.open(path) as file:
            hist = file[hist_name]
            if bins == -1:
                bins = hist.member('fN')
                member_data = np.array([
                            hist.member('fEntries'), 
                            hist.member('fTsumw'),
                            hist.member('fTsumw2'),
                            hist.member('fTsumwx'),
                            hist.member('fTsumwx2'),
                           ])
                variances = hist.variances(flow=True)
                values = hist.values(flow=True)
            elif bins != hist.member('fN'):
                raise ValueError(
                    "Bins must be equal, not ", bins, " and ", hist.member('fN')
                )
            elif hist.member('fName') != hist_name:
                raise ValueError(
                    "Names must be the same, not " + hist_name + " and " + hist.member('fName')
                )
            else:
                member_data += [
                                hist.member('fEntries'), 
                                hist.member('fTsumw'),
                                hist.member('fTsumw2'),
                                hist.member('fTsumwx'),
                                hist.member('fTsumwx2')
                            ]
                variances += hist.variances(flow=True)
                values += hist.values(flow=True)
    return uproot.writing.identify.to_TH1x(hist.member("fName"), hist.member("fTitle"),
        values, *member_data, variances, hist.member("fXaxis"))

def add_2D_hists(files, hist_name):
    bins = -1
    for path in files:
        with uproot.open(path) as file:
            hist = file[hist_name]
            if bins == -1:
                bins = hist.member('fN')
                member_data = np.array([
                            hist.member('fEntries'), 
                            hist.member('fTsumw'),
                            hist.member('fTsumw2'),
                            hist.member('fTsumwx'),
                            hist.member('fTsumwx2'),
                            hist.member('fTsumwy'),
                            hist.member('fTsumwy2'),
                            hist.member('fTsumwxy'),
                           ])
                variances = np.array(hist.variances(flow=True))
                values = np.array(hist.values(flow=True))
            elif bins != hist.member('fN'):
                raise ValueError(
                    "Bins must be equal, not ", bins, " and ", hist.member('fN')
                )
            elif hist.member('fName') != hist_name:
                raise ValueError(
                    "Names must be the same, not " + hist_name + " and " + hist.member('fName')
                )
            else:
                member_data += [
                                hist.member('fEntries'), 
                                hist.member('fTsumw'),
                                hist.member('fTsumw2'),
                                hist.member('fTsumwx'),
                                hist.member('fTsumwx2'),
                                hist.member('fTsumwy'),
                                hist.member('fTsumwy2'),
                                hist.member('fTsumwxy')
                            ]
                variances += hist.variances(flow=True)
                values += hist.values(flow=True)
    return uproot.writing.identify.to_TH2x(hist.member("fName"), hist.member("fTitle"),
        values, *member_data, variances, hist.member("fXaxis"), hist.member("fYaxis"))

def add_3D_hists(files, hist_name):
    bins = -1
    for path in files:
        with uproot.open(path) as file:
            hist = file[hist_name]
            if bins == -1:
                bins = hist.member('fN')
                member_data = np.array([
                            hist.member('fEntries'), 
                            hist.member('fTsumw'),
                            hist.member('fTsumw2'),
                            hist.member('fTsumwx'),
                            hist.member('fTsumwx2'),
                            hist.member('fTsumwy'),
                            hist.member('fTsumwy2'),
                            hist.member('fTsumwxy'),
                            hist.member('fTsumwz'),
                            hist.member('fTsumwz2'),
                            hist.member('fTsumwxz'),
                            hist.member('fTsumwyz')
                           ])
                variances = np.array(hist.variances(flow=True))
                values = np.array(hist.values(flow=True))
            elif bins != hist.member('fN'):
                raise ValueError(
                    "Bins must be equal, not ", bins, " and ", hist.member('fN')
                )
            elif hist.member('fName') != hist_name:
                raise ValueError(
                    "Names must be the same, not " + hist_name + " and " + hist.member('fName')
                )
            
            else:    
                member_data += [
                            hist.member('fEntries'), 
                            hist.member('fTsumw'),
                            hist.member('fTsumw2'),
                            hist.member('fTsumwx'),
                            hist.member('fTsumwx2'),
                            hist.member('fTsumwy'),
                            hist.member('fTsumwy2'),
                            hist.member('fTsumwxy'),
                            hist.member('fTsumwz'),
                            hist.member('fTsumwz2'),
                            hist.member('fTsumwxz'),
                            hist.member('fTsumwyz')
                        ]
                variances += hist.variances(flow=True)
                values += hist.values(flow=True)
    return uproot.writing.identify.to_TH2x(hist.member("fName"), hist.member("fTitle"),
        values, *member_data, variances, hist.member("fXaxis"), hist.member("fYaxis"), hist.member("fZaxis"))

def find_histograms(file):
    with uproot.open(file) as h:
        array = h.classnames()
        list = np.array([h[i].member("fName") for i in array if (array.get(i).startswith("TH1") or array.get(i).startswith("TH2") or array.get(i).startswith("TH3"))])
    return list

def add_hists(destination, files, hist_names=None):
    """
    Args:
        destination (path-like): Name of the output file or file path.
        files (Str or list of str): List of local ROOT files to read histograms from.
        hist_names (None, str, or list of str): Names of histograms to be added together, must be specified if files contain different numbers of histograms.

    Adds together histograms from local ROOT files of a collection of ROOT files, and writes them to one ROOT file.
    """
    if type(files) != list: # Will this always work?
        import glob
        files = sorted(
            glob.glob(files + f"/**/*{'.root'}", recursive=True)
        )

    if hist_names == None: # if histogram names are not provided
        hist_names = find_histograms(files[0])
        # print(hist_names[0].member("fName"))

    with uproot.open(files[0]) as file: # This file may never close until the end...
        hist = file[hist_names[0]]
        num_axes = len(hist.axes)

    if type(hist_names) == str:
        if num_axes == 1:
            h_sum = add_1D_hists(files, hist_names)
        elif num_axes == 2:
            h_sum = add_2D_hists(files, hist_names)
        elif num_axes == 3:
            h_sum = add_3D_hists(files, hist_names)
        file_out = uproot.recreate(destination) # What compression level?
        file_out[h_sum.member("fName")] = h_sum
    else:
        file_out = uproot.recreate(destination) # What compression level? Would it still be recreate?
        for name in hist_names:
            if num_axes == 1:
                h_sum = add_1D_hists(files, name)
            elif num_axes == 2:
                h_sum = add_2D_hists(files, name)
            elif num_axes == 3:
                h_sum = add_3D_hists(files, name)
            file_out[h_sum.member("fName")] = h_sum