import uproot
import numpy as np
import argparse
import os

def get_1d_data(hist):
    return np.array([
                    hist.member('fEntries'), 
                    hist.member('fTsumw'),
                    hist.member('fTsumw2'),
                    hist.member('fTsumwx'),
                    hist.member('fTsumwx2'),
                    ])

def add_1D_hists(destination, file, key, union, first, keys, skip_errors):
    outfile = uproot.open(destination)
    try:
        hist = file[key] # Try catch?
    except:
        if union:
            print('New key')
            return keys.append(), None
        elif skip_errors:
            return keys, None
        else:
            ValueError("Histogram ", key, " missing from other files")
    if first:
        member_data = np.array([
                        hist.member('fEntries'), 
                        hist.member('fTsumw'),
                        hist.member('fTsumw2'),
                        hist.member('fTsumwx'),
                        hist.member('fTsumwx2'),
                    ])
        return keys, uproot.writing.identify.to_TH1x(hist.member("fName"), hist.member("fTitle"),
            hist.values(flow=True), *member_data, hist.variances(flow=True), hist.member("fXaxis"))
    elif hist.member('fN') == outfile[key].member('fN'):
        member_data = np.array([
                        hist.member('fEntries'), 
                        hist.member('fTsumw'),
                        hist.member('fTsumw2'),
                        hist.member('fTsumwx'),
                        hist.member('fTsumwx2'),
                    ])
        h_sum = uproot.writing.identify.to_TH1x(hist.member("fName"), hist.member("fTitle"), outfile[key].values(flow=True) + hist.values(flow=True), 
                        *np.add(np.array([outfile[key].member('fEntries'), outfile[key].member('fTsumw'), outfile[key].member('fTsumw2'), outfile[key].member('fTsumwx'), 
                                    outfile[key].member('fTsumwx2')]), member_data), outfile[key].variances(flow=True) + hist.variances(flow=True), hist.member("fXaxis"))    
        file.close()
        return keys, h_sum


def add_2D_hists(destination, file, key, union, first, keys, skip_errors):
       # bins = -1
    # for path in files:
    outfile = uproot.open(destination)
    # keys = {keys}
    # for key in keys:
    try:
        hist = file[key] # Try catch?
    except:
        if union:
            print('New key')
            keys.append()
        elif skip_errors:
            return keys, None
        else:
            ValueError("Histogram ", key, " missing from other files")
    if first:
        member_data = np.array([
                        hist.member('fEntries'), 
                        hist.member('fTsumw'),
                        hist.member('fTsumw2'),
                        hist.member('fTsumwx'),
                        hist.member('fTsumwx2'),
                        hist.member('fTsumwy'),
                        hist.member('fTsumwy2'),
                        hist.member('fTsumwxy')
                    ])
        return keys, uproot.writing.identify.to_TH1x(hist.member("fName"), hist.member("fTitle"),
            np.ravel(hist.values(flow=True), order='C'), *member_data, np.ravel(hist.variances(flow=True), order='C'), hist.member("fXaxis"), hist.member("fYaxis"))
    elif hist.member('fN') == outfile[key].member('fN'):
        member_data = np.array([
                        hist.member('fEntries'), 
                        hist.member('fTsumw'),
                        hist.member('fTsumw2'),
                        hist.member('fTsumwx'),
                        hist.member('fTsumwx2'),
                        hist.member('fTsumwy'),
                        hist.member('fTsumwy2'),
                        hist.member('fTsumwxy')
                    ])
        h_sum = uproot.writing.identify.to_TH1x(hist.member("fName"), hist.member("fTitle"), outfile[key].values(flow=True) + hist.values(flow=True), 
                        *np.add(np.array([outfile[key].member('fEntries'), outfile[key].member('fTsumw'), outfile[key].member('fTsumw2'), outfile[key].member('fTsumwx'), 
                                    outfile[key].member('fTsumwx2')]), member_data), outfile[key].variances(flow=True) + hist.variances(flow=True), hist.member("fXaxis"))    
        file.close()
        return keys, h_sum


def add_3D_hists(destination, file, key, union, first, keys, skip_errors):
    outfile = uproot.open(destination)
    try:
        hist = file[key] # Try catch?
    except:
        if union:
            print('New key')
            return keys.append(), None
        elif skip_errors:
            return keys, None
        else:
            ValueError("Histogram ", key, " missing from other files")
    if first:
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
        return uproot.writing.identify.to_TH1x(hist.member("fName"), hist.member("fTitle"),
            np.ravel(hist.values(flow=True), order='C'), *member_data, np.ravel(hist.variances(flow=True), order='C'), hist.member("fXaxis"), hist.member("fYaxis"), hist.member("fZaxis"))
    elif hist.member('fN') == outfile[key].member('fN'):
        member_data = np.add(np.array([
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
                    ]), np.array(hist.member('fEntries'), 
                            outfile[key].member('fTsumw'),
                            outfile[key].member('fTsumw2'),
                            outfile[key].member('fTsumwx'),
                            outfile[key].member('fTsumwx2'),
                            outfile[key].member('fTsumwy'),
                            outfile[key].member('fTsumwy2'),
                            outfile[key].member('fTsumwxy'),
                            outfile[key].member('fTsumwz'),
                            outfile[key].member('fTsumwz2'),
                            outfile[key].member('fTsumwxz'),
                            outfile[key].member('fTsumwyz')))
        h_sum = uproot.writing.identify.to_TH1x(hist.member("fName"), hist.member("fTitle"), np.ravel(outfile[key].values(flow=True) + hist.values(flow=True), order='C'), 
                        *member_data, np.ravel((outfile[key].variances(flow=True) + hist.variances(flow=True)), order='C'), hist.member("fXaxis"), hist.member("fYaxis"), hist.member("fZaxis"))    
        file.close()
        return keys, h_sum

def add_hists(
        destination, 
        files, 
        *,
        target_compression=1, 
        tree_reduction=False, 
        append=False, 
        force=False, 
        no_trees=True, 
        skip_errors=False, 
        max_opened_files=0,
        union=False, # Union vs intersection
        same_name_only=True
    ):

    """
    Args:
        destination (path-like): Name of the output file or file path.
        files (Str or list of str): List of local ROOT files to read histograms from.
        hist_names (None, str, or list of str): Names of histograms to be added together, must be specified if files contain different numbers of histograms.
        force (bool): If True, overwrites destination file if it exists.
        append (bool): If True, appends histograms to an existing file.
        skip_errors (bool): If True, skips corrupt or non-existant files without exiting.
        max_opened_files (int): Limits the number of files to be open at the same time. 
        skip_extra (bool): If True, ignores histograms that are not in all files. If False, writes all histograms to destination file.
        no_extra (bool): If True, throws an error if files do not have the same histograms.
        
    Adds together histograms from local ROOT files of a collection of ROOT files, and writes them to one ROOT file.
    """
    if os.path.isfile(destination):
        if not force and not append:
            raise FileExistsError
        elif force and append:
            raise ValueError("Cannot append to a new file. Either force or append can be true.")
    if force:
        file_out = uproot.recreate(destination)

    if type(files) != list: # Will this always work?
        if files.endswith('.txt'):
            readfile=readfile
        import glob
        files = sorted(
            glob.glob(files + f"/**/*{'.root'}", recursive=True)
        )

    if no_trees:
        with uproot.open(files[0]) as file:
            # iterclassnames ? https://uproot.readthedocs.io/en/latest/uproot.reading.ReadOnlyDirectory.html
            keys = file.keys(cycle=False) 
            print(type(keys))
            keys_axes = dict(zip(keys, (len(file[i].axes) for i in keys)))
            # print(file.classnames())
    else:
        with uproot.open(files[0]) as file:
            #filter for both TTrees and histograms
            keys = file.keys(filter_classname='[TH[1|2|3][I|S|F|D|C]|TTREE]', cycle=False) # Actually might account for subdirectories and everything? https://uproot.readthedocs.io/en/latest/basic.html#finding-objects-in-a-file
            keys_axes = dict(zip(keys, (len(file[i].axes) for i in keys)))

    first = True
    for file in files:
        try:
            file = uproot.open(file)
        except:
            Warning("File: " + {file} + " does not exist or is corrupt.")
            continue
        for key in keys:
            if keys_axes[key] == 1:
                keys, h_sum = add_1D_hists(destination, file, key, union, first, keys, skip_errors)
            elif keys_axes[key] == 2:
                keys, h_sum = add_2D_hists(destination, file, key, union, first, keys, skip_errors)
            else:
                keys, h_sum = add_3D_hists(destination, file, key, union, first, keys, skip_errors)
            if h_sum != None:
                file_out[key] = h_sum
            first = False
        file.close()

def args():
    argparser = argparse.ArgumentParser(description="Hadd ROOT histograms with Uproot")
    argparser.add_argument("destination", type=str, help="path of output file")
    argparser.add_argument("input_files", type=str, nargs="+", help="list or directory (glob syntax accepted) of input files")
    argparser.add_argument("-f", action="store_true",default=False, help="force overwrite of output file")

def tree_reduction(max_opened_files):
    # Root checks system max opened files
    work = work

