#!/usr/bin python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd


def tidalEfficiency_method1(df, canal, well, log=False):
    '''
    Calculate Tidal Efficiency according to Erskine 1991, as the ratio
    of the standard deviation of the two sets of reading.

    Note, author mentions that this method is strictly applicable for
    identically formed signals symmetrical about their mean with
    continuous reading.

    Args:
    -----
        df (pandas.DataFrame):
            data to be processed; columns with names given in `canal`
            and `well` must exist
        canal (str):
            column name of the water measurements
        well (str):
            column name of the ground-water measurements

    Returns:
    --------
        E (float):
            tidal efficiency factor
    '''
    E = df[well].std()/float(df[canal].std())

    return E





def tidalEfficiency_method2(tr_canal_cycle, tr_well_cycle):
    '''
    Calculate Tidal Efficiency according to Smith 1994, as the mean
    of the amplitude ratios for every tidal-cycle.
        
        E = sum(Ei)/n

        where:
            Ei = h0/h   - ration of amplitude in gw well to river stage amplitude at cycle i
            n           - total number of cycles

    Args:
    -----
        tr_canal_cycle (pandas.Series, 1-D array_like):
            amplitudes of the river for every tidal cycle
            Note, DATA MUST BE CLEAN!
        tr_well_cycle (pandas.Series, 1-D array_like):
            amplitudes of the groundwater well for every tidal cycle
            Note, DATA MUST BE CLEAN!

    Returns:
    --------
        E (float):
            tidal efficiency factor
        E_cyclic (1D-nd.array):
            tidal efficiency caclulated for each tidal cycle
    '''
    
    # 1. check amplitudes
    #   1.1 they should have equal length
    if len(tr_canal_cycle) != len(tr_well_cycle):
        raise Exception('Length of *peak* arrays is not equal: peaks_river = % d, peaks_gw = % d' % len(tr_canal_cycle), len(tr_well_cycle))
        # Error


    # 2. now do the calculations
    # if pd.Series or np.ndarray - do quick
    if isinstance(tr_well_cycle, (pd.Series, pd.DataFrame, np.ndarray)) and isinstance(tr_canal_cycle, (pd.Series, pd.DataFrame, np.ndarray)):
        E_array = tr_well_cycle/tr_canal_cycle

    # if not... do with row-iterations, slow
    else:
        E_array = list()
        for a_w, a_gw in zip(tr_canal_cycle, tr_well_cycle):
            E_array.append(a_gw/float(a_w))
        E_array = np.array(E_array)

    E = E_array.sum()/len(E_array)

    return E, E_array



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
        E_cyclic (1D-nd.array):
            tidal efficiency caclulated for each tidal cycle
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

    if log:
        print('Period: T=', T)
        print('River: ', river)
        print('Well: ', gw)

    # 3. Do the calculations
    E_cyclic = list()

    for w_tmin, w_tmax, gw_tmin, gw_tmax in zip(river_cycle_time_min, river_cycle_time_max, gw_cycle_time_min, gw_cycle_time_max):
        # 3.2 find the index of the entry closest to specific datetime
        try:
            w_i1 = df[datetime_col].searchsorted(w_tmin-T/4)[0]  # note, here we assume that between peak1 and peak2 is T/2
            w_i2 = df[datetime_col].searchsorted(w_tmax+T/4)[0]  # note, here we assume that between peak1 and peak2 is T/2
            
            gw_i1 = df[datetime_col].searchsorted(gw_tmin-T/4)[0]  # note, here we assume that between peak1 and peak2 is T/2
            gw_i2 = df[datetime_col].searchsorted(gw_tmax+T/4)[0]  # note, here we assume that between peak1 and peak2 is T/2
        except:
            continue
            
        hydr_w  = df.ix[w_i1:w_i2, river]
        hydr_gw  = df.ix[gw_i1:gw_i2, gw]

        E_i = hydr_gw.std()/hydr_w.std()
        E_cyclic.append(E_i)
        if log:
            print('-'*50)
            print('River cycle: {0}:{1}\tSTD={2}'.format(w_i1, w_i2, hydr_w.std()))
            print('Well  cycle: {0}:{1}\tSTD={2}'.format(gw_i1, gw_i2, hydr_gw.std()))
            print('E={0:.3f}'.format(E_i))
            print('-'*50)

    E_cyclic = np.array(E_cyclic)
    if log:
        for i, e in enumerate(E_cyclic):
            print('Cycle #{0}: E={1:.3f}'.format(i, e))
    E = E_cyclic.sum()/len(E_cyclic)
    return E, E_cyclic
