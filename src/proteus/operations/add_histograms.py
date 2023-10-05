import uproot
import numpy as np

def add_1D_hists(files, hist_name):
    bins = -1
    for path in files:
        with uproot.open(path) as file:
            hist = file[hist_name] # Try catch?
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
            # elif hist.member('fName') != hist_name:
            #     raise ValueError(
            #         "Names must be the same, not " + hist_name + " and " + hist.member('fName')
            #     )
            else:
                member_data += [
                                hist.member('fEntries'), 
                                hist.member('fTsumw'),
                                hist.member('fTsumw2'),
                                hist.member('fTsumwx'),
                                hist.member('fTsumwx2'),
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

def add_hists(destination, files, hist_names=None, tree_reduction=False):
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
        with uproot.open(files[0]) as h:
            array = h.classnames()
            hist_names = np.array([h[i].member("fName") for i in array if (array.get(i).startswith("TH1") or array.get(i).startswith("TH2") or array.get(i).startswith("TH3"))])
 

    with uproot.open(files[0]) as file:
        hist = file[[str(hist_names)][0]]
        num_axes = len(hist.axes)

    if tree_reduction == True:
        h_sum = tree_reduction_add(files, hist_names)

    if type(hist_names) == str:
        if tree_reduction == True:
            h_sum = tree_reduction_add(files, hist_names)
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
            if tree_reduction == True:
                h_sum = tree_reduction_add(files, name)
            if num_axes == 1:
                h_sum = add_1D_hists(files, name)
            elif num_axes == 2:
                h_sum = add_2D_hists(files, name)
            elif num_axes == 3:
                h_sum = add_3D_hists(files, name)
            file_out[h_sum.member("fName")] = h_sum

def tree_reduction_add(files, hist_name):
    # *** Partial tree reduction...

    # Get rid of need for all the dtype conversions?
    indx = int(0) 
    i = int(len(files)/2)
    member_data = np.ndarray((i,5))
    values, variances = np.ndarray(i), np.ndarray(i)

    if type(files) != list: # Will this always work?
        import glob
        files = sorted(
            glob.glob(files + f"/**/*{'.root'}", recursive=True)
        )

    x_axis = ""
    title = ""
    while indx+1 <= i:
        with uproot.open(files[indx]) as file1:
            with uproot.open(files[indx+1]) as file2:
                    try:
                        hist1, hist2 = file1[hist_name], file2[hist_name]
                    except:
                        raise ValueError("Names of histograms must all be the same.") # How get other hist name?
                    title = hist1.member("fTitle")
                    x_axis = hist1.member("fXaxis")
                    hist1, hist2 = file1[hist_name], file2[hist_name]
                    i = indx/int(2)
                    member_data[:] = np.add(np.array([
                            hist1.member('fEntries'), 
                            hist1.member('fTsumw'),
                            hist1.member('fTsumw2'),
                            hist1.member('fTsumwx'),
                            hist1.member('fTsumwx2'),
                        ]), np.array([
                            hist2.member('fEntries'), 
                            hist2.member('fTsumw'),
                            hist2.member('fTsumw2'),
                            hist2.member('fTsumwx'),
                            hist2.member('fTsumwx2'),
                        ]))
                    variances = np.add(hist1.variances(flow=True), hist2.variances(flow=True))
                    values = np.add(hist1.values(flow=True), hist2.values(flow=True))
                    indx+=2
        if(len(files)%2==1):
            with uproot.open(files[-1]) as file:
                try:
                    hist = file[hist_name]
                except:
                    raise ValueError("Names of histograms must all be the same.") # How get other hist name?

                member_data[-1] += np.array([
                                    hist.member('fEntries'), 
                                    hist.member('fTsumw'),
                                    hist.member('fTsumw2'),
                                    hist.member('fTsumwx'),
                                    hist.member('fTsumwx2'),
                                ])
                variances += hist.variances(flow=True)
                values += hist.values(flow=True)
        try:
            return uproot.writing.identify.to_TH1x(hist_name, title, # pass Title? It may end up random
                values, *np.sum(member_data, axis=0), variances, x_axis)
        except:
            print("Write failed.")
            print("Bins must be the same size.") # Change!