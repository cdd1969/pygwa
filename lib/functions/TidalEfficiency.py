#!/usr/bin python
# -*- coding: utf-8 -*-

import sys
from numpy import NaN, Inf, arange, isscalar, asarray, array
from scipy import signal
import numpy as np



def tidalEfficiency_method1(df, river, gw, log=False):
    '''
    Calculate Tidal Efficiency according to Erskine 1991, as the ratio
    of the standard deviation of the two sets of reading.

    Note, author mentions that this method is strictly applicable for
    identically formed signals symmetrical about their mean with
    continuous reading.

    Args:
    -----
        df (pandas.DataFrame):
            data to be processed; columns with names given in `river`
            and `gw` must exist
        river (str):
            column name of the water measurements
        gw (str):
            column name of the ground-water measurements

    Returns:
    --------
        E (float):
            tidal efficiency factor
    '''
    E = df[gw].std()/float(df[river].std())

    return E





def tidalEfficiency_method2(peaks_river, peaks_gw):
    '''
    Calculate Tidal Efficiency according to Smith 1994, as the mean
    of the amplitude ratios for every tidal-cycle.
        
        E = sum(Ei)/n

        where:
            Ei = h0/h   - ration of amplitude in gw well to river stage amplitude at cycle i
            n           - total number of cycles

    Args:
    -----
        df (pandas.DataFrame):
            data to be processed; columns with names given in `river`
            and `gw` must exist
        river (str):
            column name of the water measurements
        gw (str):
            column name of the ground-water measurements

    Returns:
    --------
        E (float):
            tidal efficiency factor
    '''
    
    # 1. check peaks
    #   1.1 they should have equal length
    if len(peaks_river.index) != len(peaks_gw.index):
        raise Exception('Length of *peak* arrays are not equal: peaks_river = % d, peaks_gw = % d' % len(peaks_river.index), len(peaks_gw.index))
        # Error

    #   1.2 they should both start from min or max, so that extrema values appear matched
    if not ((peaks_river['val'][0] > peaks_river['val'][1] and peaks_gw['val'][0] > peaks_gw['val'][1]) or
            (peaks_river['val'][0] < peaks_river['val'][1] and peaks_gw['val'][0] < peaks_gw['val'][1])):
        raise Exception('Both arrays should share first peak type. It should be either MAX or MIN peak in both arrays.')
        # Error

    #   1.3 peaks should be more-or-less within same time-frame
    delta_t = datetime.timedelta(hours=24)
    if not (abs(peaks_river['time'][0] - peaks_gw['time'][0]) < delta_t and
            abs(peaks_river['time'][-1] - peaks_gw['time'][-1]) < delta_t):
       raise Exception('Both arrays should describe data within same time-range. More than % d hours timedelta detected between matching peaks.')
        
       # Error


    # 2. now do the calculations
    E_sum = 0.
    N = 0
    for i in xrange(1, len(peaks_river.index), 2):
        A_river_i = abs(peaks_river['val'][i-1] - peaks_river['val'][i])
        A_gw_i    = abs(peaks_gw['val'][i-1] - peaks_gw['val'][i])
        E_sum += A_gw_i/float(A_river_i)
        N += 1

    E = E_sum/float(N)

    return E



def tidalEfficiency_method3(df, river, gw, datetime_col, peaks_river, peaks_gw):
    '''
    Calculate Tidal Efficiency as the mean of the ratios (calculated
    separately for each tidal-cycle) of the standard deviation of the
    two sets of reading.

        E = sum(STD(H_gw_i)/STD(H_river_i))/n

        where:
            H_river_i   - hydrograph of the river at cycle i
            H_gw_i      - hydrograph of the groundwater at cycle i
            n           - total number of cycles

    Args:
    -----
        df (pandas.DataFrame):
            data to be processed; columns with names given in `river`
            and `gw` must exist
        river (str):
            column name of the water measurements
        gw (str):
            column name of the ground-water measurements
        datetime_col (str):
            column name of the Datetime information

    Returns:
    --------
        E (float):
            tidal efficiency factor
    '''
    
    # 1. check peaks
    #   1.1 they should have equal length
    if len(peaks_river.index) != len(peaks_gw.index):
        pass
        # Error

    #   1.2 they should both start from min or max, so that extrema values appear matched
    if not ((peaks_river['val'][0] > peaks_river['val'][1] and peaks_gw['val'][0] > peaks_gw['val'][1]) or
            (peaks_river['val'][0] < peaks_river['val'][1] and peaks_gw['val'][0] < peaks_gw['val'][1])):
       pass
       # Error

    #   1.3 peaks should be more-or-less within same time-frame
    delta_t = datetime.timedelta(hours=24)
    if not (abs(peaks_river['time'][0] - peaks_gw['time'][0]) < delta_t and
            abs(peaks_river['time'][-1] - peaks_gw['time'][-1]) < delta_t):
       pass
       # Error


    # 2. Determine period
    T = peaks_river['time'].diff().mean()


    # 3. Do the calculations
    E_sum = 0.
    N = 0  # number of cycles
    for i in xrange(1, len(peaks_river.index), 2):
        date_peak_1 = peaks_river['time'][i-1]
        date_peak_2 = peaks_river['time'][i]
        # 3.2 find the index of the entry closest to specific datetime
        i1 = df[datetime_col].searchsorted(date_peak_1-T/4)  # note, here we assume that between peak1 and peak2 is T/2
        i2 = df[datetime_col].searchsorted(date_peak_2+T/4)  # note, here we assume that between peak1 and peak2 is T/2
        std_w  = df.ix[i1:i2, river].std()
        std_gw  = df.ix[i1:i2, gw].std()
        E_i = std_gw/std_w
        E_sum += E_i
        N += 1

    E = E_sum/float(N)

    return E

# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import random
    import datetime
    import pandas as pd
    import numpy as np



    delta_t = datetime.timedelta(hours=24)
    now = datetime.datetime.now()
    print (now -(now+2*delta_t))
    print (now -(now+2*delta_t)) < delta_t
    print abs(now -(now+2*delta_t))
    print abs(now -(now+2*delta_t)) < delta_t
    for i in xrange(1, 5, 2):
        print i

    df = pd.DataFrame(data=np.arange(10)+10, index=np.arange(10)[::-1], columns=['a'])
    print df

    for i in xrange(1, 5, 2):
        print i, '>>>', df['a'].iloc[i]



    df = pd.DataFrame(data=[True, np.nan, True, True, False, False, True], columns=['a'])
    print df
    print df['a'].count()
    print df['a'].sum()
    print df.loc[df['a'] == True].size
    