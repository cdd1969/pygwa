#!/usr/bin python
# -*- coding: utf-8 -*-

import sys
from numpy import NaN, Inf, arange, isscalar, asarray, array
from scipy import signal
import numpy as np


def peakdet(v, delta, x=None):
    """
    # This script is taken from
    # https://gist.github.com/endolith/250860
    Converted from MATLAB script at http://billauer.co.il/peakdet.html
    
    Returns two arrays
    
    function [maxtab, mintab]=peakdet(v, delta, x)
    %PEAKDET Detect peaks in a vector
    %        [MAXTAB, MINTAB] = PEAKDET(V, DELTA) finds the local
    %        maxima and minima ("peaks") in the vector V.
    %        MAXTAB and MINTAB consists of two columns. Column 1
    %        contains indices in V, and column 2 the found values.
    %
    %        With [MAXTAB, MINTAB] = PEAKDET(V, DELTA, X) the indices
    %        in MAXTAB and MINTAB are replaced with the corresponding
    %        X-values.
    %
    %        A point is considered a maximum peak if it has the maximal
    %        value, and was preceded (to the left) by a value lower by
    %        DELTA.
    
    % Eli Billauer, 3.4.05 (Explicitly not copyrighted).
    % This function is released to the public domain; Any use is allowed.
    
    """
    maxtab = []
    mintab = []
       
    if x is None:
        x = arange(len(v))
    
    v = asarray(v)
    
    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')
    
    if not isscalar(delta):
        sys.exit('Input argument delta must be a scalar')
    
    if delta <= 0:
        sys.exit('Input argument delta must be positive')
    
    mn, mx = Inf, -Inf
    mnpos, mxpos = NaN, NaN
    
    lookformax = True
    
    for i in arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]
        
        if lookformax:
            if this < mx-delta:
                maxtab.append((mxpos, mx))
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn+delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True

    return array(maxtab), array(mintab)



def remove_region(peak_value_array, peak_index_array):
    """ function will compare values in <peak_values_array> and remove
        the regions of equal values leaving only one entry for each region

        <peak_index_array> is an array of indeces of peak that were found in data

        example:
            data   = [1, 2, 3, 4, 4, 4, 4, 3, 2, 1, 0, 1, 2, 3, 4]
            isPeak = [Y, N, N, Y, Y, Y, Y, N, N, N, Y, N, N, N, Y]  # yes/no
            (this is usually produced by scipy.signal.argrelextrema())

            peaks_indeces = [0, 3, 4, 5, 6, 10, 14]
            peaks_values  = [1, 4, 4, 4, 4, 0 , 4 ]
            new_peaks_indeces, new_peaks_values = remove_region(peaks_values, peaks_indeces)
            
            new_peaks_indeces = [0, 5, 10, 14]
            new_peaks_values  = [1, 4, 0 , 4 ]
    """
    diffs = np.diff(peak_value_array)
    
    indices_to_be_deleted = list()
    regionIndices = list()
    
    # if there is no two neighbour-entries which are equal (difference between them is 0)
    if 0 not in diffs:
        del diffs
        return peak_value_array, peak_index_array

    for j, diff in enumerate(diffs):
        ##print '>>>', j
        if diff == 0 and abs(peak_index_array[j]-peak_index_array[j+1]) == 1:  # values at <j> and <j+1> are of same value, difference between them is 0
            # append two indexes of our region (or only one index if already included)
            if len(regionIndices) == 0 or regionIndices[-1] != j:
                ##print "appending regionIndices:", j
                regionIndices.append(j)
            regionIndices.append(j+1)
            ##print "appending regionIndices:", j+1
        else:  # values at <j> and <j+1> are have different values. This is not region
            # now we need to process our region, delete it, and start searching for the new one
            
            # find middle value of the region, if region exists
            # >>> if region has even number of elements >>> [2, 3, 4, 5] => middle = 2
            # >>> if region has odd number of elements  >>> [2, 3, 4, 5, 6] => middle = 2
            if len(regionIndices) > 1:
                middleRegion = int(len(regionIndices)/2)
                ##print "regionIndices:", regionIndices
                ##print "middleRegion:", middleRegion
                regionIndices.pop(middleRegion)
                ##print "regionIndices:", regionIndices
                # we have removed our region-middle value(the one we want to keep), from the
                # to_be_deleted list with <pop()> method. Thus it will stay
                indices_to_be_deleted += regionIndices
                ##print "indices_to_be_deleted:", indices_to_be_deleted
                # clear and re-init region list
                del regionIndices
                regionIndices = list()
            else:
                pass
    del diffs
    # now delete entries under indexes that we have found...
    return np.delete(peak_value_array, indices_to_be_deleted), np.delete(peak_index_array, indices_to_be_deleted)


def detectPeaks(array1D, order=5, split=False, removeRegions=True, mode='clip'):
    """ try to detect peak values (local minima/maxima) of passed signal. User can decide how to treat
        values for minima/maxima -- together or separately. User can also toggle option to remove
        so called "peak regions" (see docstring at function <remove_region()>)

        Function returns indices (corresponding to peak location in array1D) and values of detected peaks

        <Input>
        -------
        array1D       - our signal. Must be one-dimensional numpy ndarrray
        order         - integer, number of entries to consider around the eak. See documentation for
                        scipy.signal.argrelextrema()
        mode          - str, How the edges of the vector are treated. <wrap> (wrap around) or <clip> (treat overflow as the same as the last (or first) element).
        split         - bool, toggle treatment of minima/maxima separately
                        if True  will return two lists [values_min, values_max], [indices_min, indices_max]
                        if False will return two lists [values_all], [indices_all]
        removeRegions - bool, if True will apply function <remove_region()> o remove "peak-regions"

        <Output>
        --------
        [vals], [indices] or
        [vals_minima, vals_maxima], [indices_minima, indices_maxima]
    """
    if not isinstance(array1D, np.ndarray):
        raise TypeError('Input array must be of numpy ndarray type, received: {0}'.format(type(array1D)))
    if len(array1D.shape) != 1:
        raise TypeError('Input array must be one-dimensional, received: {0}'.format(array1D.shape))
    
    peakIndices_max = signal.argrelextrema(array1D, np.greater_equal, order=order, mode=mode)[0]  #local maxima
    peakIndices_min = signal.argrelextrema(array1D, np.less_equal, order=order, mode=mode)[0]     #local minima

    if split:  #treat seperately minima/maxima, do not join them
        peakVals_max = array1D[peakIndices_max]
        peakVals_min = array1D[peakIndices_min]
        
        if removeRegions:
            peakVals_max, peakIndices_max = remove_region(peakVals_max, peakIndices_max)
            peakVals_min, peakIndices_min = remove_region(peakVals_min, peakIndices_min)

        return [peakVals_min, peakVals_max], [peakIndices_min, peakIndices_max]

    else:
        peakIndices_all = np.sort(np.concatenate((peakIndices_max, peakIndices_min)))  #all local peaks (maxima+minima)
        peakVals_all = array1D[peakIndices_all]
        
        if removeRegions:
            peakVals_all, peakIndices_all = remove_region(peakVals_all, peakIndices_all)
        return [peakVals_all], [peakIndices_all]

# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import random
    order = 10


    x = np.arange(0, 30, 0.1)
    #y = np.array([np.sin(xi) for xi in x])
    y = np.array([np.sin(xi)+random.random() for xi in x])
    y[30:33] = 5.
    y[50:59] = -2.
    y[60:66] = 5.
    y[90:92] = -3.

    f, axarr = plt.subplots(2, 2)
    axarr[0, 0].plot(x, y)
    
    for ax1 in axarr:
        for ax in ax1:
            ax.plot(x, y, color='k')

    axarr[0, 0].set_title('split=False, removeRegions=False')
    vals, indices = detectPeaks(y, order=order, split=False, removeRegions=False)
    valsx = x[indices]
    axarr[0, 0].scatter(valsx, vals, color='b', marker='x', s=250)
    

    axarr[0, 1].set_title('split=False, removeRegions=True')
    vals, indices = detectPeaks(y, order=order, split=False, removeRegions=True)
    valsx = x[indices]
    axarr[0, 1].scatter(valsx, vals, color='b', marker='x', s=250)

    
    axarr[1, 0].set_title('split=True, removeRegions=False')
    vals, indices = detectPeaks(y, order=order, split=True, removeRegions=False)
    valsx_min = x[indices[0]]
    valsx_max = x[indices[1]]
    axarr[1, 0].scatter(valsx_min, vals[0], color='r', marker='x', s=250)
    axarr[1, 0].scatter(valsx_max, vals[1], color='g', marker='x', s=250)


    axarr[1, 1].set_title('split=True, removeRegions=True')
    vals, indices = detectPeaks(y, order=order, split=True, removeRegions=True)
    valsx_min = x[indices[0]]
    valsx_max = x[indices[1]]
    axarr[1, 1].scatter(valsx_min, vals[0], color='r', marker='x', s=250)
    axarr[1, 1].scatter(valsx_max, vals[1], color='g', marker='x', s=250)


    plt.show()
