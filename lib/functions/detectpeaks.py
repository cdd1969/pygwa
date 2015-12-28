#!/usr/bin python
# -*- coding: utf-8 -*-

import sys
from scipy import signal
import numpy as np
from general import isNumpyDatetime
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt


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

        Args:
        -----
            array1D (1D, np.ndarray):
                Our signal. Must be one-dimensional
            order (int):
                number of entries to consider around the peak. See documentation for
                scipy.signal.argrelextrema()
            mode (str):
                How the edges of the vector are treated. <wrap> (wrap around) or <clip>
                (treat overflow as the same as the last (or first) element).
            split (bool):
                toggle treatment of minima/maxima separately
                if True  will return two lists [values_min, values_max], [indices_min, indices_max]
                if False will return two lists [values_all], [indices_all]
            removeRegions (bool):
                if True will apply function <remove_region()> o remove "peak-regions"

        Returns:
        --------
            tuple of two lists (tuple[list]):
                if `split` is True  => ([vals], [indices])
                if `split` is False => ([vals_minima, vals_maxima], [indices_minima, indices_maxima])
    """

    if not isinstance(array1D, np.ndarray):
        raise TypeError('Input array must be of numpy ndarray type, received: {0}'.format(type(array1D)))
    if len(array1D.shape) != 1:
        raise TypeError('Input array must be one-dimensional, received: {0}'.format(array1D.shape))
    
    peakIndices_max = signal.argrelextrema(array1D, np.greater_equal, order=order, mode=mode)[0]  #local maxima
    peakIndices_min = signal.argrelextrema(array1D, np.less_equal, order=order, mode=mode)[0]     #local minima

    if split:  #treat separately minima/maxima, do not join them
        peakVals_max = array1D[peakIndices_max]
        peakVals_min = array1D[peakIndices_min]
        
        if removeRegions:
            peakVals_max, peakIndices_max = remove_region(peakVals_max, peakIndices_max)
            peakVals_min, peakIndices_min = remove_region(peakVals_min, peakIndices_min)

        return ([peakVals_min, peakVals_max], [peakIndices_min, peakIndices_max])

    else:
        peakIndices_all = np.sort(np.concatenate((peakIndices_max, peakIndices_min)))  #all local peaks (maxima+minima)
        peakVals_all = array1D[peakIndices_all]
        
        if removeRegions:
            peakVals_all, peakIndices_all = remove_region(peakVals_all, peakIndices_all)
        return ([peakVals_all], [peakIndices_all])


def detectPeaks_ts(data, col, T=None, datetime=None, hMargin=1., detectPeaksFlag=True, peakIndices_all=None, plot=False, **kwargs):
    '''
    Detect peaks of the given timeseries, and check the detection by comparing
    the time-difference between the peaks with period using following condition:
        PERIOD/2 - hMargin < dt < PERIOD/2 + hMargin

    Args:
    -----
        data (pd.DataFrame):
            dataframe with everything
        col (str):
            column name of the measurement data
        T (float):
            Awaited period of the signal in hours. If `None`, will calculate
            the Period `T` as the mean of difference between peaks, multiplied
            by two (i.e. T = peaks['time'].diff().mean()*2)
        datetime (Optional[str]):
            column name of the datetime data (this column must be
            of `np.datetime64` type). If None - the datetime must
            be stored within `data`'s indexes.
        hMargin (float):
            Number of hours, safety margin when comparing period length.
            See formula below:
            PERIOD/2 - hMargin < PERIOD_i/2 < PERIOD/2 + hMargin
        detectPeaksFlag (bool):
            if True - calculate peaks here
            if False - use passed peaks indices from `peakIndices_all`
        peakIndices_all (np.ndarray):
            numpy 1D array with indices of the peak values (both minima
            and maxima). Indices should be already sorted from min to max
        plot (bool):
            if `True` - generate a new matplotlib plot with thing that
            have been done.
        **kwargs:
            are passed to deteppeaks.detectPeaks()

    Returns:
    --------
        peaks (pd.DataFrame):
            dataframe contains following columns:
            'N'    - number of the peak
            'ind'  - index of the peak within the original data-array
            'time' - datetime of the peak
            'val'  - value of the peak
            'time_diff'  - difference in time between two neighbor peaks
            'check'  - if the condition (T/2 - hMargin < time_diff < T/2 + hMargin)
                is met

    '''
    if datetime is None:
        # this is not yet tested
        date = pd.DataFrame(data.index)  # series for all the timespan
    else:
        if datetime in data.columns and col in  data.columns:
            date = data[datetime]  # we need to aply group method only to timeseries (index=datetime). Thus we will create a fake one
        else:
            raise KeyError('Passed column name <{0}> not found in dataframe. DataFrame has following columns: {1}'.format(datetime, list(data.columns)))
    if not isNumpyDatetime(date.dtype):
        raise ValueError('Datetime data is not of type <np.datetime64>. Received type : {0}'.format(date.dtype))
    

    # now prepare peaks...
    if detectPeaks:
        kwargs['split'] = False  # we want to force it!
        #peakIndices_min, peakIndices_max = detectPeaks(data[col].values, **kwargs)[1]
        peakIndices_all = detectPeaks(data[col].values, **kwargs)[1][0]


    # peaks have been prepared, select time!
    peaks = pd.DataFrame()

    peaks['N'] = np.arange(len(peakIndices_all))
    peaks['ind'] = peakIndices_all
    peaks['time'] = date.iloc[peakIndices_all].values
    peaks['val'] = data.iloc[peakIndices_all][col].values
    peaks['time_diff'] = peaks['time'].diff()



    # estimate periods
    if T is None:
        T = peaks['time_diff'].mean()*2
    else:
        T = timedelta(hours=T)
    halfT = T/2


    # perform data-checks
    epsilon = timedelta(hours=hMargin)

    # function that will be applied row-wise
    def checkDT(row):
        currentIndex = int(row['N'])
        if currentIndex in [0]:
          return
        return halfT-epsilon < peaks.iloc[currentIndex]['time_diff'] < halfT+epsilon

    peaks['check'] = peaks.apply(checkDT, axis=1)

    if plot:
        plot_signal_peaks_and_errors(data, date, peaks, col, T, halfT, hMargin, epsilon)


    return peaks


def plot_signal_peaks_and_errors(data, date, peaks, col, T, halfT, hMargin, epsilon):
    '''
    This function is called by <detectpeaks.detectPeaks_ts()>
    It is not wrapped inside, because we want to call it with PLOT button from Node UI.

    Do not use this function alone. Check input as locals in <detectpeaks.detectPeaks_ts()>
    '''
    plt.figure()
    plt.title('Period (T) check.\n T/2 - margin < dt < T/2 + margin.\n T={0}. margin={1} hours\n {2} < dt < {3}'.format(T, hMargin,  halfT-epsilon, halfT+epsilon), fontsize=15)
    ax = plt.subplot(111)
    plot_df = pd.DataFrame(index=date.values)
    plot_df[col] = data[col].values
    plot_df.plot(ax=ax)

    peaks.plot(x='time', y='val', style='.' , ax=ax, color='k', lw=20, label='Detected peaks')

    for row in peaks['N']:
        if peaks.iloc[row]['check'] is not False:
            continue
        df_error = pd.DataFrame(index=[peaks.iloc[row-1]['time'], peaks.iloc[row]['time']])
        label_i = 'Error: dt={0}'.format(peaks.iloc[row]['time_diff'])
        df_error[label_i] = [peaks.iloc[row-1]['val'], peaks.iloc[row]['val']]
        df_error.plot(ax=ax, color='r')
        del df_error


    plt.show()
    del plot_df


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
