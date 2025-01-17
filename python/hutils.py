import math

from hist import Hist

# ----------------------------------------------------------------------------------------
def set_bins(values, n_bins, is_log_x, xbins, var_type='float'):  # NOTE this fcn/signature is weird because it mimics an old root fcn (for search: log_bins log bins)
    assert len(values) > 0
    values = sorted(values)
    if is_log_x:
        log_xmin = math.log(pow(10.0, math.floor(math.log10(values[0]))))  # round down to the nearest power of 10 from the first entry
        log_xmax = math.log(pow(10.0, math.ceil(math.log10(values[-1]))))  # round up to the nearest power of 10 from the last entry
        log_dx = (log_xmax - log_xmin) / float(n_bins)
        log_xmin -= 0.1*log_dx  # expand a little to avoid overflows
        log_xmax += 0.1*log_dx
        log_dx = (log_xmax - log_xmin) / float(n_bins)
        for ib in range(n_bins+1):
            low_edge = math.exp(log_xmin + ib*log_dx)
            xbins[ib] = low_edge
    else:
        dx, xmin, xmax = 0, 0, 0
        if var_type == 'string':
            xmin = 0.5
            xmax = n_bins + 0.5
        else:
            dx = float(values[-1] - values[0]) / n_bins
            if dx == 0:  # hackey, but effective
                dx = max(1e-5, values[0])
            xmin = values[0] - 0.1*dx  # expand a little to avoid underflows
            xmax = values[-1] + 0.1*dx  # and overflows
        dx = float(xmax - xmin) / n_bins  # then recalculate dx
        for ib in range(n_bins+1):
            xbins[ib] = xmin + ib*dx

# ----------------------------------------------------------------------------------------
def make_hist_from_list_of_values(vlist, var_type, hist_label, is_log_x=False, xmin_force=0.0, xmax_force=0.0, sort_by_counts=False):
    vdict = {v : vlist.count(v) for v in set(vlist)}
    return make_hist_from_dict_of_counts(vdict, var_type, hist_label, is_log_x=is_log_x, xmin_force=xmin_force, xmax_force=xmax_force, sort_by_counts=sort_by_counts)

# ----------------------------------------------------------------------------------------
# <values> is of form {<bin 1>:<counts 1>, <bin 2>:<counts 2>, ...}
def make_hist_from_dict_of_counts(values, var_type, hist_label, is_log_x=False, xmin_force=0.0, xmax_force=0.0, sort_by_counts=False, default_n_bins=30):  # default_n_bins is only used if is_log_x set we're doing auto log bins
    """ Fill a histogram with values from a dictionary (each key will correspond to one bin) """
    assert var_type == 'int' or var_type == 'string'  # floats should be handled by Hist class in hist.py

    if len(values) == 0:
        print 'WARNING no values for %s in make_hist' % hist_label
        return Hist(1, 0, 1)

    bin_labels = sorted(values)  # by default sort by keys in dict (i.e. these aren't usually actually string "labels")
    if sort_by_counts:  # instead sort by counts
        bin_labels = sorted(values, key=values.get, reverse=True)

    if var_type == 'string':
        n_bins = len(values)
    else:
        n_bins = bin_labels[-1] - bin_labels[0] + 1 if not is_log_x else default_n_bins

    hist = None
    xbins = [0. for _ in range(n_bins+1)]  # NOTE the +1 is 'cause you need the lower edge of the overflow bin
    if xmin_force == xmax_force:  # if boundaries aren't set explicitly, work out what they should be
        if var_type == 'string':
            set_bins(bin_labels, n_bins, is_log_x, xbins, var_type)
            hist = Hist(n_bins, xbins[0], xbins[-1], xbins=xbins)
        else:
            if is_log_x:  # get automatic log-spaced bins
                set_bins(bin_labels, n_bins, is_log_x, xbins, var_type)
                hist = Hist(n_bins, xbins[0], xbins[-1], xbins=xbins)
            else:
                hist = Hist(n_bins, bin_labels[0] - 0.5, bin_labels[-1] + 0.5)  # for integers, just go from the first to the last bin label (they're sorted)
    else:
      hist = Hist(n_bins, xmin_force, xmax_force)

    for ival in range(len(values)):
        if var_type == 'string':
            label = bin_labels[ival]
            ibin = ival + 1
        else:
            label = ''
            ibin = hist.find_bin(bin_labels[ival])
        hist.set_ibin(ibin, values[bin_labels[ival]], error=math.sqrt(values[bin_labels[ival]]), label=label)

    # make sure there's no overflows
    if hist.bin_contents[0] != 0.0 or hist.bin_contents[-1] != 0.0:
        for ibin in range(hist.n_bins + 2):
            print '%d %f %f' % (ibin, hist.low_edges[ibin], hist.bin_contents[ibin])
        raise Exception('overflows in ' + hist_label)

    return hist
