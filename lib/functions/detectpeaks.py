#!/usr/bin python
# -*- coding: utf-8 -*-

import sys
from scipy import signal
import numpy as np
from general import isNumpyDatetime
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt
from datetime import datetime as dtime
import logging
from python_log_indenter import IndentedLoggerAdapter

logger = IndentedLoggerAdapter(logging.getLogger(__name__), spaces=4)


def remove_region(peak_value_array, peak_index_array, order=1):
    """ function will compare values in <peak_values_array> and remove
        the regions of equal values leaving only one entry for each region
        
        Args:
        -----
            peak_value_array (1-D array_like):
                array with detected peak values
            peak_index_array (1-D array_like):
                array with detected peak indeces. These indeces indicate
                the position of peaks within original signal
            order (int):
                the length of the region to consider. Default = 1.
                Two peaks at `i` and `i+1` will be considered as the "region"
                if following two conditions are met:
                    1) peak_value_array[i+1] == peak_value_array[i]
                    2) peak_index_array[i+1] - peak_index_array[i] <= order
                This param has been introduced while solving ISSUE#9

        Return:
        -------
            (new_peak_value_array, new_peak_index_array):
                numpy 1D arrays with removed regions

        Example:
        --------
            data   = [1, 2, 3, 4, 4, 4, 4, 3, 2, 1, 0, 1, 2, 3, 4]
            isPeak = [Y, N, N, Y, Y, Y, Y, N, N, N, Y, N, N, N, Y]  # yes/no
            (this is usually produced by scipy.signal.argrelextrema())

            peaks_indeces = [0, 3, 4, 5, 6, 10, 14]
            peaks_values  = [1, 4, 4, 4, 4, 0 , 4 ]
            new_peaks_indeces, new_peaks_values = remove_region(peaks_values, peaks_indeces)
            
            new_peaks_indeces = [0, 5, 10, 14]
            new_peaks_values  = [1, 4, 0 , 4 ]
    """
    if int(order) < 1:
        raise ValueError('Invalid integer: `order` must be >=1. Received `order=%i`' % int(order))
    diffs_v = np.diff(peak_value_array)
    diffs_i = np.diff(peak_index_array)
    if len(diffs_i) != len(diffs_v):
        raise ValueError('Length of the passed "Index" and "Values" arrays is not equal')
    
    indices_to_be_deleted = list()
    regionIndices = list()
    
    # if there is no two neighbour-entries which are equal (difference between them is 0)
    if 0 not in diffs_v:
        del diffs_i
        del diffs_v
        return peak_value_array, peak_index_array

    def close_region(ind2bDel, region, log=False):
        middleRegion = int(len(region)/2)
        if log: print ("regionIndices:", region)
        if log: print ("middleRegion:", middleRegion)
        region.pop(middleRegion)
        if log: print( "regionIndices after poping middle:", region)
        # we have removed our region-middle value(the one we want to keep), from the
        # to_be_deleted list with <pop()> method. Thus it will stay
        ind2bDel += region
        if log: print( "indices_to_be_deleted:", ind2bDel)
        # clear and re-init region list
        del region



    for j, (diff_i, diff_v) in enumerate(zip(diffs_i, diffs_v)):
        ##print( '>>> j', j, '>>> i`s', peak_index_array[j], peak_index_array[j+1])
        ##print( '>>> REGION', regionIndices)
        #if diff_v == 0 and diff_i == 1:  # This was the original part. Check (Issue#9)
        if diff_v == 0 and diff_i <= order:  # values at <j> and <j+1> are of same value, difference between them is 0
            if len(regionIndices) == 0 or regionIndices[-1] != j:
                ##print( "appending regionIndices:", j)
                regionIndices.append(j)
            regionIndices.append(j+1)

        else:  # close region!
            # this can happen due to...
            #   - values at <j> and <j+1> are different values.
            #   - <j> and <j+1> are not near each other >>> diff_i > order
            # now we need to process our previously created region, delete it, and start searching for the new one
            
            # find middle value of the region, if region exists
            # >>> if region has even number of elements >>> [2, 3, 4, 5] => middle = 2
            # >>> if region has odd number of elements  >>> [2, 3, 4, 5, 6] => middle = 2
            if len(regionIndices) > 1:
                close_region(indices_to_be_deleted, regionIndices, log=False)
                regionIndices = list()
            else:
                pass

        if (j == len(diffs_i)-1) and len(regionIndices) > 1:
            #   - we have reached the last value (so explicitly close our region)
            ##print( 'last index, cosing region')
            close_region(indices_to_be_deleted, regionIndices, log=False)
    del diffs_i
    del diffs_v
    # now delete entries under indexes that we have found...
    return np.delete(peak_value_array, indices_to_be_deleted), np.delete(peak_index_array, indices_to_be_deleted)


def detectPeaks(array1D, order=5, split=False, removeRegions=True, mode='clip', plot=False):
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
            log (bool):
                if True will print some logs in console
            plot (bool):
                if True will plot results
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
            peakVals_max, peakIndices_max = remove_region(peakVals_max, peakIndices_max, order=order)
            peakVals_min, peakIndices_min = remove_region(peakVals_min, peakIndices_min, order=order)
        if plot:
            f = plt.figure()
            ax = f.add_subplot(111)
            ax.plot(array1D, label='original signal', marker='o', markersize=5, zorder=1)
            ax.scatter(x=peakIndices_max, y=peakVals_max, color='r', s=40, label='detected MAX peaks', zorder=2)
            ax.scatter(x=peakIndices_min, y=peakVals_min, color='k', s=40, label='detected MIN peaks', zorder=2)
            plt.legend()
            f.show()
        return ([peakVals_min, peakVals_max], [peakIndices_min, peakIndices_max])

    else:
        peakIndices_all = np.sort(np.concatenate((peakIndices_max, peakIndices_min)))  #all local peaks (maxima+minima)
        peakVals_all = array1D[peakIndices_all]
        
        if removeRegions:
            # remove those nasty regions (see example at docstring of the `remove_region` func)
            peakVals_all, peakIndices_all = remove_region(peakVals_all, peakIndices_all)
        if plot:
            f = plt.figure()
            ax = f.add_subplot(111)
            ax.plot(array1D, label='original signal', marker='o', markersize=5, zorder=1)
            ax.scatter(x=peakIndices_max, y=peakVals_max, color='r', s=40, label='detected MAX peaks', zorder=2)
            ax.scatter(x=peakIndices_min, y=peakVals_min, color='k', s=40, label='detected MIN peaks', zorder=2)
            plt.legend()
            f.show()
        return ([peakVals_all], [peakIndices_all])


def detectPeaks_ts(data, col, T=None, datetime=None, hMargin=1., detectPeaksFlag=True, peakIndices_all=None, drop_dummy_rows=True, plot=False, log=False, **kwargs):
    '''
    Detect peaks of the given timeseries, and check the detection by comparing
    the time-difference (dt) between the peaks with period (PERIOD) using the following
    condition:
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
        drop_dummy_rows (bool):
            if `True` will delete rows with dummy peaks. Since it is hard-coded
            that tidal-cycle starts with MIN-peak and ends with MAX-peak,
            the first and the last detected cycles may have dummy values (i.e.
                Cycle |   t_min   |   t_max
                -----------------------------
                  1   |   dummy   | 00:00:00
                  2   | 06:12:00  | 12:24:00
                  3   | 18:36:00  |   dummy
            ) In this example, rows 1 and 3 will be deleted
        plot (bool):
            if `True` - generate a new matplotlib plot with thing that
            have been done.
        log (bool):
            if `True` - prints some logs to console
        **kwargs:
            are passed to detectpeaks.detectPeaks()

    Returns:
    --------
        peaks (pd.DataFrame):
            dataframe contains following columns:
            'N'    - number of the peak
            'ind'  - index of the peak within the original data-array
            'time' - datetime of the peak
            'val'  - value of the peaks, consecutively max,min,max,min,...
            'time_diff'  - difference in time between two neighbor peaks
            'check'  - if the condition (T/2 - hMargin < time_diff < T/2 + hMargin) is met
            'name'  - name of the signal

    '''
    logger.debug('Starting `detectPeaks_ts()`').add()

    if datetime is None:
        # this is not yet tested
        date = pd.DataFrame(data.index)[0]  # series for the all timespan
    else:
        if datetime in data.columns and col in  data.columns:
            date = data[datetime]  # we need to apply group method only to timeseries (index=datetime). Thus we will create a fake one
        else:
            raise KeyError('Passed column name <{0}> not found in dataframe. DataFrame has following columns: {1}'.format(datetime, list(data.columns)))
    if not isNumpyDatetime(date.dtype):
        raise ValueError('Datetime data is not of type <np.datetime64>. Received type : {0}'.format(date.dtype))
    

    peaks = pd.DataFrame()

    if kwargs['split'] is False:
        logger.debug('Proceeding with combined peaks (min, max together)')
        
        peakIndices_all = detectPeaks(data[col].values, **kwargs)[1][0]

        peaks['N']          = np.arange(len(peakIndices_all))
        peaks['ind']        = peakIndices_all
        peaks['time']       = date.iloc[peakIndices_all].values
        peaks['val']        = data.iloc[peakIndices_all][col].values
        peaks['time_diff']  = peaks['time'].diff()

    else:  # kwargs['split'] is True
        logger.debug('Proceeding with splitted peaks (min, max separately)')
        # -----------------------------------------------------------------
        # Find the peaks
        # -----------------------------------------------------------------
        peakIndices_min, peakIndices_max = detectPeaks(data[col].values, **kwargs)[1]
        
        logger.debug('Raw Min ({0} values) and Max ({0} values) peaks detected'.format(len(peakIndices_min), len(peakIndices_max)))
        if len(peakIndices_min) > 6 and len(peakIndices_max) > 6:
            logger.add().debug('peakIndices_min = [{0}, {1}, {2}, ... , {3}, {4}, {5}]  ({6} values)'.format(peakIndices_min[0], peakIndices_min[1], peakIndices_min[2], peakIndices_min[-3], peakIndices_min[-2], peakIndices_min[-1], peakIndices_min.size )).sub()
            logger.add().debug('peakIndices_max = [{0}, {1}, {2}, ... , {3}, {4}, {5}]  ({6} values)'.format(peakIndices_max[0], peakIndices_max[1], peakIndices_max[2], peakIndices_max[-3], peakIndices_max[-2], peakIndices_max[-1], peakIndices_max.size )).sub()
        # -----------------------------------------------------------------
        
        # -----------------------------------------------------------------
        # Check the distance between the peaks...
        # -----------------------------------------------------------------
        logger.push()
        logger.debug('Checking the distance between the peaks').add()
        tol = 0.4  # tolerance
        
        # 1) Distance between the combined peaks (sum of min and max)
        peakIndices_all = np.concatenate((peakIndices_min, peakIndices_max))
        peakIndices_all.sort()
        
        ERRORS = dict()
        for index_array, which in zip( (peakIndices_all, peakIndices_min, peakIndices_max), ('all', 'min', 'max')):
            logger.add().debug('...distance between the `{0}` peaks'.format(which)).sub()
            
            d_indexes      = np.diff(index_array)  #array with differences in index positions between two neighbour peaks
            d_indexes_mean = d_indexes.mean()

            logger.add().debug('Mean distance between the a pair of peaks is {0} indexes. With a given tolerance {1}, the valid distance between a pair of peaks should fall in range [{2}:{3}]'.format(d_indexes_mean, tol, d_indexes_mean*(1.-tol), d_indexes_mean*(1.+tol))).sub()
            
            d_indexes_masked  = np.ma.masked_inside(d_indexes, d_indexes_mean*(1.-tol), d_indexes_mean*(1.+tol) )  # mask correct values that fall inside the valid region
            n_p_all_errors = d_indexes_masked.count()  #count non-masked elements, e.g. errors
            
            if n_p_all_errors > 0:
                logger.add().debug('{n} pairs of peaks do exceed the allowed index-distance'.format(n=n_p_all_errors)).sub()

                # get the indexes of the "error" pairs
                d_indexes_errors_indexes = np.ma.masked_array(np.arange(d_indexes_masked.size), d_indexes_masked.mask).compressed()

                # explicitly create the index-array of the "error" pairs
                logger.add().debug('The indexes of these pairs are (in the combined min/max peaks-array):...').sub()
                ERROR_PAIRS = list()
                for i in d_indexes_errors_indexes:
                    ERROR_PAIRS.append(index_array[i:i+2])  #is the same as [index_array[i], index_array[i+1]]
                    logger.add().debug(str(ERROR_PAIRS[-1])).sub()

            ERRORS[which] = ERROR_PAIRS
        logger.pop()
        # -----------------------------------------------------------------


        # it can happen, that the first detected index was MAX and not MIN,
        # We want to generalize it to Min-Max, so we prepend dummy value to
        # MIN list, so that the real MAX value has its pair (even though dummy-value)
        DUMMIES    = list()
        DUMMY_ROWS = list()

        logger.debug('Checking the first and the last peaks').add()
        # -----------------------------------------------------------------
        # Check if the first min is smaller than the first max
        # -----------------------------------------------------------------
        if peakIndices_min[0] > peakIndices_max[0]:
            logger.debug('peakIndices_min[0] > peakIndices_max[0] detected => inserting dummy-value `0` at the first position of the `peakIndices_min` ')

            peakIndices_min = np.insert(peakIndices_min, 0, 0)
            DUMMIES.append('first_min')
            DUMMY_ROWS.append(0)

            if len(peakIndices_min) > 6 and len(peakIndices_max) > 6:
                logger.add().debug('modified peakIndices_min = [{0}, {1}, {2}, ... , {3}, {4}, {5}]  ({6} values)'.format(peakIndices_min[0], peakIndices_min[1], peakIndices_min[2], peakIndices_min[-3], peakIndices_min[-2], peakIndices_min[-1], peakIndices_min.size )).sub()
                logger.add().debug('modified peakIndices_max = [{0}, {1}, {2}, ... , {3}, {4}, {5}]  ({6} values)'.format(peakIndices_max[0], peakIndices_max[1], peakIndices_max[2], peakIndices_max[-3], peakIndices_max[-2], peakIndices_max[-1], peakIndices_max.size )).sub()
        # -----------------------------------------------------------------

        # -----------------------------------------------------------------
        # # Check if the last min is smaller than the last max
        # -----------------------------------------------------------------
        if peakIndices_min[-1] > peakIndices_max[-1]:
            logger.debug('peakIndices_min[-1] > peakIndices_max[-1] detected => inserting dummy-value `0` at the last position of the `peakIndices_max` ')

            peakIndices_max = np.append(peakIndices_max, 0)
            DUMMIES.append('last_max')
            DUMMY_ROWS.append(-1)

            if len(peakIndices_min) > 6 and len(peakIndices_max) > 6:
                logger.add().debug('modified peakIndices_min = [{0}, {1}, {2}, ... , {3}, {4}, {5}]  ({6} values)'.format(peakIndices_min[0], peakIndices_min[1], peakIndices_min[2], peakIndices_min[-3], peakIndices_min[-2], peakIndices_min[-1], peakIndices_min.size )).sub()
                logger.add().debug('modified peakIndices_max = [{0}, {1}, {2}, ... , {3}, {4}, {5}]  ({6} values)'.format(peakIndices_max[0], peakIndices_max[1], peakIndices_max[2], peakIndices_max[-3], peakIndices_max[-2], peakIndices_max[-1], peakIndices_max.size )).sub()
        # -----------------------------------------------------------------
        logger.sub().debug('Finished checking the first and the last peaks')


        # -----------------------------------------------------------------
        # Now test the number of MIN MAX peaks
        # -----------------------------------------------------------------
        n_min = len(peakIndices_min)
        n_max = len(peakIndices_max)
        
        if n_min != n_max:
            if plot:
                # Do the plotting of the detected peaks, additionally show possible failures
                f = plt.figure()
                ax = f.add_subplot(111)
                ax.plot(data[col].values, label='original signal', marker='o', markersize=4, zorder=1)
                ax.scatter(x=peakIndices_max, y=data[col].values[peakIndices_max], color='g', s=40, label='detected MAX peaks', zorder=2)
                ax.scatter(x=peakIndices_min, y=data[col].values[peakIndices_min], color='k', s=40, label='detected MIN peaks', zorder=2)
                for key, err_pairs in ERRORS.iteritems():
                    if key == 'all':
                        c = 'red'
                    elif key == 'min':
                        c = 'magenta'
                    elif key == 'max':
                        c = 'orange'
                    for error in err_pairs:
                        plt.plot(error, data[col].values[error], color=c, lw=3, label='wrong distance between {0}-peaks'.format(key), zorder=3)
                plt.legend()
                ax.set_xlabel('Value Index (0-indexed)')
                ax.set_ylabel('Value')
                f.show()
            raise Exception('Number of min and max peaks is not equal: {0} != {1}'.format(n_min, n_max))
        # -----------------------------------------------------------------
        


        #
        # -----------------------------------------------------------------
        # At this step everything is OK. Continue creating DataFrame
        # -----------------------------------------------------------------

        peaks['N'] = np.arange(max(n_min, n_max))
        peaks['ind_min'] = peakIndices_min
        peaks['ind_max'] = peakIndices_max
        peaks['time_min'] = date.iloc[peakIndices_min].values
        peaks['time_max'] = date.iloc[peakIndices_max].values
        peaks['val_min'] = data.iloc[peakIndices_min][col].values
        peaks['val_max'] = data.iloc[peakIndices_max][col].values

        if len(DUMMIES) > 0:
            if 'first_min' in DUMMIES:
                peaks.iloc[0, peaks.columns.get_loc('ind_min')] = -999
                peaks.iloc[0, peaks.columns.get_loc('time_min')] = dtime.now()
                peaks.iloc[0, peaks.columns.get_loc('val_min')] = np.nan
            if 'last_max' in DUMMIES:
                peaks.iloc[-1, peaks.columns.get_loc('ind_max')] = -999
                peaks.iloc[-1, peaks.columns.get_loc('time_max')] = dtime.now()
                peaks.iloc[-1, peaks.columns.get_loc('val_max')] = np.nan
        
        peaks['time_diff'] = peaks['time_max'] - peaks['time_min']
        peaks['tidal_range'] = np.abs(peaks['val_max'] - peaks['val_min'])

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
        return halfT-epsilon < peaks.iloc[currentIndex]['time_diff'] < halfT+epsilon

    peaks['check'] = peaks.apply(checkDT, axis=1)
    peaks['name']  = col
    
    if drop_dummy_rows and kwargs['split'] and len(DUMMY_ROWS) > 0:
        peaks = peaks.drop(peaks.index[DUMMY_ROWS])

    if plot:
        plot_signal_peaks_and_errors(data, date, peaks, col, T, halfT, hMargin, epsilon, kwargs['split'])

    logger.sub().debug('Finished `detectPeaks_ts()`. Returning peaks DataFrame...')
    return peaks


def plot_signal_peaks_and_errors(data, date, peaks, col, T, halfT, hMargin, epsilon, split):
    '''
    This function is called by <detectpeaks.detectPeaks_ts()>
    It is not wrapped inside, because we want to call it with PLOT button from Node UI.

    Do not use this function alone. Check input as locals in <detectpeaks.detectPeaks_ts()>
    '''
    fig = plt.figure()
    plt.title('Period (T) check.\n T/2 - margin < dt < T/2 + margin.\n T={0}. margin={1} hours\n {2} < dt < {3}'.format(T, hMargin,  halfT-epsilon, halfT+epsilon), fontsize=15)
    ax = plt.subplot(111)
    plot_df = pd.DataFrame(index=date.values)
    plot_df[col] = data[col].values
    plot_df.plot(ax=ax)

    if not split:
        peaks.plot(x='time', y='val', style='.' , ax=ax, color='k', lw=20, label='Detected peaks')

        for index, row in peaks.iterrows():
            if row['check'] is not False:
                continue
            df_error = pd.DataFrame(index=[peaks.iloc[index-1]['time'], row['time']])
            label_i = 'Error at <{1}>: dt={0}'.format(row['time_diff'], peaks.iloc[index-1]['time'])
            df_error[label_i] = [peaks.iloc[index-1]['val'], row['val']]
            df_error.plot(ax=ax, color='r')
            del df_error
    else:
        peaks.plot(x='time_min', y='val_min', style='.' , ax=ax, color='k', lw=5, label='Detected MIN peaks', markersize=12)
        peaks.plot(x='time_max', y='val_max', style='.' , ax=ax, color='g', lw=5, label='Detected MAX peaks', markersize=12)

        for index, row in peaks.iterrows():
            if row['check'] is not False:
                continue
            df_error = pd.DataFrame(index=[row['time_min'], row['time_max']])
            label_i = '[{2}]: Error at <{1}>: dt={0}'.format(row['time_diff'], row['time_min'], index)
            df_error[label_i] = [row['val_min'], row['val_max']]
            df_error.plot(ax=ax, color='r', marker='h', lw=5)
            del df_error

    fig.show()
    del plot_df

















# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////



def find_index_closest_value(val, ts, side=None):
    ''' Find index of the entry in df[colName], which is the
    closest to `val`. Check this link

    Typical usage:
        i = find_index_closest_value(5, df, 'my_values')
        print df.iloc[i]  # gets the actual value


    Args:
    -----
        val (object):
            value to match
        ts (pd.Series):
            timeseries with data. Note, ts.dtype should be
            same as dtype of `val`
        side (str):
            search direction with respect to `val`.
            'left (<t)'   - search before `val`
            'left (<=t)'  - search before `val` or at `val`
            'right (>t)'  - search after `val`
            'right (>=t)' - search after `val` or at `val`
            'both'        - search before and after `val` or at `val`
    Return:
    -------
        (int):
            index of the closest value. The value itself
            can be accessed with ts[ ]
    '''
    # check inputs
    if side not in ['right (>t)', 'right (>=t)', 'left (<=t)', 'left (<t)', 'both']:
        raise ValueError('Invalid `side` received: %s' % side)
    

    if side == 'both':
        index = np.argmin(np.abs(ts - val))
        # index is the real index of the Series. We eant to get the row_number
        # so we can pass it explicitly to numpy functions
        # so now you can use val = ts.iloc[row]
        row = list(ts.index).index(index)  #here we find the row-number by index
    else:
        isHere = ts[ts == val].index.tolist()
        if len(isHere) > 0 and side in ['right (>=t)', 'left (<=t)']:
            # if we are allowed to take the exact value, and it is present - grab it!
            row = list(ts.index).index(isHere[0])  # same as above
            
        else:
            if side in ['right (>=t)', 'right (>t)']:
                row = ts.searchsorted(val, side='right')[0]
            elif side in ['left (<=t)', 'left (<t)']:
                row = ts.searchsorted(val, side='left')[0]

                # for some reason
                #  row = ts.searchsorted(val, side='left')[0]
                # doesnot work as expceted, returning value from
                # the right side from `val`. Thus lets's hack it manually
                while ts.iloc[row] >= val:
                    if row == 0:
                        break
                    row -= 1
    return row


def find_index_of_closest_time(t, df, colName, side='both', window=None, use_window=False):
    ''' Find time and index of the entry in `df[colName]`, which match
    passed conditions.
    
    Conditions:
        1) closest to `t` in `df[colName]`
        2) closest after `t` in `df[colName]`
        3) closest before `t` in `df[colName]`
        4) closest to `t` in `df[colName]` within time-window [t-window : t+window]
        5) combination of conditions (2)+(4) and (3)+(4)

    Args:
    -----
        t (np.datetime64):
            timestamp to match to
        df (pd.DataFrame):
            dataframe with datetime column to be matched
        colName (str):
            name of the column with datetime data for matching.
            Note: df[colName] MUST BE sorted in ascending order
        side (str):
            search direction with respect to `t`.
            'left (<t)'   - search before `t`
            'left (<=t)'  - search before `t` or at `t`
            'right (>t)'  - search after `t`
            'right (>=t)' - search after `t` or at `t`
            'both'        - search before and after `t` or at `t`
        use_window (bool):
            if True -- apply window selection. Defaults to False
        window (float):
            Number of hours to specify search-region with respect to `t`
            [t-window : t+window]. Default is `None`, meaning that will
            search matching time within all data

    Return:
    -------
        (tuple(int, np.datetime64)):
            tuple of matched index and value if found or (None, None)
    '''


    # first of all select the region of interest based on passed condition

    #   based on side....
    i = find_index_closest_value(t, df[colName], side=side)
    time = df.iloc[i, df.columns.get_loc(colName)]

    if side in ['right (>=t)']:
        if not time >= t:
            return (None, None)
    elif side in ['right (>t)']:
        if not time > t:
            return (None, None)
    elif side in ['left (<=t)']:
        if not time <= t:
            return (None, None)
    elif side in ['left (<t)']:
        if not time < t:
            return (None, None)
    
    #   based on time-window...
    if use_window not in [None, False]:
        t_min = t-timedelta(hours=window)
        t_max = t+timedelta(hours=window)

        if not (t_min <= time <= t_max):
            logger.warning('t_min <= time <= t_maxt\t\t {0} <= {1} <= {2}, where t={3}'.format(t_min, time, t_max, t))
            return (None, None)
    return (i, time)





def match_peaks(peaks_w, peaks_gw, match_colName='time_min', **kwargs):
    ''' Process two dataframes created by function from this module
    <detectPeaks_ts()>, (with split=True). Find corresponding peaks
    within two datasets

    Args:
    -----
        peaks_w (pd.DataFrame):
            dataframe with peak information of river, created by <detectPeaks_ts()>
            (of course it can be prepared manually, but should have same format)
        peaks_gw (pd.DataFrame):
            dataframe with peak information of groundwater, created by <detectPeaks_ts()>
            (of course it can be prepared manually, but should have same format)
        match_colName (str):
            name of the column with datetime64 objects. Match will be performed
            based on this column
        **kwargs:
            are passed to <find_index_of_closest_time()>

    Return:
    -------
        peaks_matched (pd.DataFrame):
            dataframe with matched tidal cycles. It is a copy of `peaks_w` with
            appended seven columns:
                'md_N'        - matched cycle number
                'md_ind_min'  - matched index of min peak
                'md_ind_max'  - matched index of max peak
                'md_time_min' - matched datetime of min peak
                'md_time_max' - matched datetime of max peak
                'md_val_min'  - matched value of min peak
                'md_val_max'  - matched value of max peak
                'md_name'     - name of the matched signal
    '''
    match_col_index = peaks_w.columns.get_loc(match_colName)

    peaks_matched = peaks_w.copy(deep=True)
    del peaks_matched['check']
    del peaks_matched['time_diff']
    peaks_matched['md_N']        = np.nan
    peaks_matched['md_ind_min']  = np.nan
    peaks_matched['md_ind_max']  = np.nan
    peaks_matched['md_time_min'] = pd.NaT
    peaks_matched['md_time_max'] = pd.NaT
    peaks_matched['md_val_min']  = np.nan
    peaks_matched['md_val_max']  = np.nan
    peaks_matched['md_name']     = peaks_gw['name'].values[0]  # we take value at 0 index , since they are equal everywhere

    for row in peaks_w.itertuples():  # this adds a column `Index` at first position
        i = row.Index

        t = row[match_col_index+1]  #+1 because we have aaditional column Index now
        j = find_index_of_closest_time(t, peaks_gw, match_colName, **kwargs)[0]
        if j is not None:
            peaks_matched.ix[i, 'md_N']        = peaks_gw.iloc[j, peaks_gw.columns.get_loc('N')]
            peaks_matched.ix[i, 'md_ind_min']  = peaks_gw.iloc[j, peaks_gw.columns.get_loc('ind_min')]
            peaks_matched.ix[i, 'md_ind_max']  = peaks_gw.iloc[j, peaks_gw.columns.get_loc('ind_min')]
            peaks_matched.ix[i, 'md_time_min'] = peaks_gw.iloc[j, peaks_gw.columns.get_loc('time_min')]
            peaks_matched.ix[i, 'md_time_max'] = peaks_gw.iloc[j, peaks_gw.columns.get_loc('time_max')]
            peaks_matched.ix[i, 'md_val_min']  = peaks_gw.iloc[j, peaks_gw.columns.get_loc('val_min')]
            peaks_matched.ix[i, 'md_val_max']  = peaks_gw.iloc[j, peaks_gw.columns.get_loc('val_max')]

            # for debugging
            if i > 0 and peaks_matched.ix[i, 'md_N'] == peaks_matched.ix[i-1, 'md_N']:
                logger.debug('This row has `md_N` as the previous one. Below the current row is printed')
                logger.debug(row)

    peaks_matched['md_tidal_range']  = np.abs(peaks_matched['md_val_max'] - peaks_matched['md_val_min'])

    # check unique values. This can happen that one peak will be matched two times. This is wrong => notify user
    unique = peaks_matched['md_N'].unique()
    if peaks_matched['md_N'].size != unique.size:
        msg = 'One of the peaks matched multiple times (number of unique entries in `md_N` {0} is less than its size {1}). Try different matching mode.'.format(unique.size, peaks_matched['md_N'].size)
        logger.error(msg)
        for i, val in enumerate(peaks_matched['md_N']):
            if val not in unique:
                logger.error('The `md_N` in this line is not unique:\n'+str(peaks_matched.ix[i, ...]))
        raise ValueError(msg)
    return peaks_matched
