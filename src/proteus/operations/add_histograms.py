import uproot

# Only combines one histogram per file
def hadd_like(files, destination, *, hist_name=None, hist_paths=None):
    if hist_name == None:
        # ? search through them nicely? Assume there are multiple?
        array = hist.classnames()
    try:
        hist = uproot.open(files[0])[hist_name]
    except:
        # error: name not the same!
        error = 5

    # Base case
    bins = hist.member('fN')
    values = hist.values(flow=True)
    fEntries = hist.member("fEntries")
    fTsumw = hist.member("fTsumw")
    if hist.member("fTsumw2") != None:
        fTsumw2 = hist.member("fTsumw2")
    else:
        fTsumw2 = 0
    fTsumwx = hist.member("fTsumwx")
    fTsumwx2 = hist.member("fTsumwx2")
    variances = hist.variances("flow=True")

    # Iteratively / Sequentially:
    for path in files[1:]:
        with uproot.open(path) as file:
            hist = file[hist_name]  # histogram = uproot.open("file.root:path/to/histogram") 
            if bins != hist.member('fN'):
                raise ValueError( 
                    "Bins must be the same, not " + {bins} + " and " + {hist.member('fN')}
                )

            values += hist.values(flow=True)
            fEntries += hist.member("fEntries")
            fTsumw += hist.member("fTsumw")
            if hist.member("fTsumw2") != None:
                fTsumw2 += hist.member("fTsumw2")
            fTsumwx += hist.member("fTsumwx")
            fTsumwx2 += hist.member("fTsumwx2")
            variances += hist.variances("flow=True")

    h_sum = uproot.writing.identify.to_TH1x(hist.member("fName"), hist.member("fTitle"), values,
                                            fEntries, fTsumw, fTsumw2, fTsumwx, fTsumwx2, variances, hist.member("fXaxis"))

    file_out = uproot.recreate(destination)
    file_out[h_sum.member("fName")] = h_sum


# If we can do things in parallel
def hadd_like_tree_reduction(files, destination, *, hist_name=None, threads=1):
    import numpy as np
    hist = uproot.open(files[0])
    try:
        hist = uproot.open(files[0])[hist_name]
    except:
        # error: name not the same!
        error = 5

    iterations = len(files)

    if (iterations%2) != 0:
        hist = files[-1]
        values = hist.values(flow=True)
        fEntries = hist.member("fEntries")
        fTsumw = hist.member("fTsumw")
        if hist.member("fTsumw2") != None:
            fTsumw2 = hist.member("fTsumw2")
        fTsumwx = hist.member("fTsumwx")
        fTsumwx2 = hist.member("fTsumwx2")
        variances = hist.variances("flow=True")
    else:
        values = 0
        fEntries = 0
        fTsumw = 0
        fTsumw2 = 0
        fTsumwx = 0
        fTsumwx2 = 0
        variances = 0

    for i in range(iterations/2):
        print(i)
        values, fEntries, fTsumw, fTsumw2, fTsumwx, fTsumwx2, variances += sum_hists(files[i], files[-i], hist_name)

    h_sum = uproot.writing.identify.to_TH1x(hist.member("fName"), hist.member("fTitle"), values,
                                            fEntries, fTsumw, fTsumw2, fTsumwx, fTsumwx2, variances, hist.member("fXaxis"))

    file_out = uproot.recreate(destination)
    file_out[h_sum.member("fName")] = h_sum

hadd_like_tree_reduction(["/Users/zobil/Documents/Proteus/file1.root", "/Users/zobil/Documents/Proteus/file2.root"], "place.root", hist_name="name")

def sum_hists(hist1, hist2):
    # Check bins
    hist1 = uproot.open(hist1)
    hist2 = uproot.open(hist2)
    if hist1.member("fN") != hist2.member("fN"):
        raise ValueError( 
                    "Bins must be the same, not " + {hist1.member("fN")} + " and " + {hist2.member("fN")} # Get file names
                )
    values = hist1.values(flow=True) + hist2.values(flow=True)
    fEntries = hist1.member("fEntries") + hist2.member("fEntries")
    fTsumw = hist1.member("fTsumw") + hist2.member("fTsumw")
    if hist1.member("fTsumw2") != None:
        fTsumw2 = hist1.member("fTsumw2")   
    else:
        fTsumw2 = 0
    if hist2.member("fTsumw2") != None:
        fTsumw2 += hist2.member("fTsumw2")
    fTsumwx = hist1.member("fTsumwx") + hist2.member("fTsumwx")
    fTsumwx2 = hist1.member("fTsumwx2") + hist2.member("fTsumwx")
    variances = hist1.variances("flow=True") + hist2.variances("flow=True")
    return hist1.member("fN"), values, fEntries, fTsumw, fTsumw2, fTsumwx, fTsumwx2, variances
