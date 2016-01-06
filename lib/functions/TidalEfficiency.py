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





def tidalEfficiency_method2(river_cycle_amp, gw_cycle_amp):
    '''
    Calculate Tidal Efficiency according to Smith 1994, as the mean
    of the amplitude ratios for every tidal-cycle.
        
        E = sum(Ei)/n

        where:
            Ei = h0/h   - ration of amplitude in gw well to river stage amplitude at cycle i
            n           - total number of cycles

    Args:
    -----
        river_cycle_amp (pandas.Series, 1-D array_like):
            amplitudes of the river for every tidal cycle
            Note, DATA MUST BE CLEAN!
        gw_cycle_amp (pandas.Series, 1-D array_like):
            amplitudes of the groundwater well for every tidal cycle
            Note, DATA MUST BE CLEAN!

    Returns:
    --------
        E (float):
            tidal efficiency factor
    '''
    
    # 1. check amplitudes
    #   1.1 they should have equal length
    if len(river_cycle_amp) != len(gw_cycle_amp):
        raise Exception('Length of *peak* arrays is not equal: peaks_river = % d, peaks_gw = % d' % len(river_cycle_amp), len(gw_cycle_amp))
        # Error


    # 2. now do the calculations
    ERROR = False
    # if pd.Series or np.ndarray - do quick
    try:
        E_array = gw_cycle_amp/river_cycle_amp
        if len(E_array) != len(gw_cycle_amp):
            ERROR = True
        else:
            E_sum = E_array.sum()
    except:
        ERROR = True

    # if not... do with row-iterations, slow
    if ERROR:
        E_sum = 0.
        for a_w, a_gw in zip(river_cycle_amp, gw_cycle_amp):
            E_sum += a_gw/float(a_w)

    E = E_sum/len(gw_cycle_amp)

    return E, len(gw_cycle_amp)



def tidalEfficiency_method3(df, river, gw, datetime_col, river_cycle_time_min, river_cycle_time_max,
        gw_cycle_time_min, gw_cycle_time_max):
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
        river_cycle_time_min (pandas.Series, 1-D array_like):
            datetime of the MIN peak (lowwater) of the river for every tidal cycle
            Note, DATA MUST BE CLEAN!
        river_cycle_time_max (pandas.Series, 1-D array_like):
            datetime of the MAX peak (highwater) of the river for every tidal cycle
            Note, DATA MUST BE CLEAN!
        gw_cycle_time_min (pandas.Series, 1-D array_like):
            datetime of the MIN peak (lowwater) of the grondwater in well
            for every tidal cycle
            Note, DATA MUST BE CLEAN!
        gw_cycle_time_max (pandas.Series, 1-D array_like):
            datetime of the MAX peak (highwater) of the grondwater in well
            for every tidal cycle
            Note, DATA MUST BE CLEAN!
    Returns:
    --------
        E (float):
            tidal efficiency factor
    '''
    
    # 1. check peaks
    #   1.1 they should have equal length
    l1 = len(river_cycle_time_min)
    l2 = len(river_cycle_time_max)
    l3 = len(gw_cycle_time_min)
    l4 = len(gw_cycle_time_max)
    if (3*l1 - l2 - l3 - l4) != 0:
        raise Exception('Length of *peak* arrays is not equal. Aborting')



    # 2. Determine period
    T = (river_cycle_time_max-river_cycle_time_min).mean()*2


    # 3. Do the calculations
    E_sum = 0.
    N = 0  # number of cycles

    for w_tmin, w_tmax, gw_tmin, gw_tmax in zip(river_cycle_time_min, river_cycle_time_max, gw_cycle_time_min, gw_cycle_time_max):
        # 3.2 find the index of the entry closest to specific datetime
        try:
            w_i1 = df[datetime_col].searchsorted(w_tmin-T/4)[0]  # note, here we assume that between peak1 and peak2 is T/2
            w_i2 = df[datetime_col].searchsorted(w_tmax+T/4)[0]  # note, here we assume that between peak1 and peak2 is T/2
            
            gw_i1 = df[datetime_col].searchsorted(gw_tmin-T/4)[0]  # note, here we assume that between peak1 and peak2 is T/2
            gw_i2 = df[datetime_col].searchsorted(gw_tmax+T/4)[0]  # note, here we assume that between peak1 and peak2 is T/2
        except:
            continue
            
        std_w  = df.ix[w_i1:w_i2, river].std()
        std_gw  = df.ix[gw_i1:gw_i2, gw].std()

        E_i = std_gw/std_w
        E_sum += E_i
        N += 1


    E = E_sum/float(N)

    return E, N

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
    