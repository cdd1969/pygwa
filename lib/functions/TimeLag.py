#!/usr/bin python
# -*- coding: utf-8 -*-
import sys
import numpy as np
import datetime


def timelag_erskine1991_method(df_gw, cn_gw_v, cn_gw_t,
                               df_w,  cn_w_v,  cn_w_t,
                               E,
                               tlag_tuple=(0, 60, 1)):
    '''
    Calculating Timelag after Erskine 1991 approach.

    Args:
    -----
        df_gw (pd.DataFrame):
            dataframe with groundwater data
        df_w  (pd.DataFrame):
            dataframe with river data
        cn_gw_v (str):
            name of the column with hydrograph values in `df_gw` dataframe
        cn_gw_t (str):
            name of the column with datetime values in `df_gw` dataframe
        cn_w_v (str):
            name of the column with hydrograph values in `df_w` dataframe
        cn_w_t (str):
            name of the column with datetime values in `df_w` dataframe
        E (float):
            tidal efficiency, calculated from hydrographs
            `df_gw[cn_gw_v]` and `df_w[cn_w_v]`
        tlag_tuple (tuple(int, int, int)):
            Bruteforce iterating over suggested timelags. These three values
            will be passed to function `xrange`, giving user the way to
            create an iterator over possible timelags. Values have *minute*
            units.
            Example:
                tlag_tuple=(0, 60, 1)
                I will do calculations for all timelags
                from 0 to 59 minutes with step 1 min
                (i.e 0 min, 1 min, 2 min, ..., 59 min)

    Return:
    -------
        timelag (np.datetime64):
            estimated timelag between two hydrographs
            `df_gw[cn_gw_v]` and `df_w[cn_w_v]`

    '''

    # ---------------------------------------
    # END user inputs END
    # ---------------------------------------
    if E in [None, np.nan, 0]:
        raise ValueError('Tidal Efficiency is not set')
    if df_gw is None or df_w is None:
        raise ValueError('Input datasets are not set')
    # make copies... with datetime indexes
    df_GW = df_gw.set_index(cn_gw_t)
    df_GW[cn_gw_t] = df_GW.index
    
    df_W  = df_w.set_index(cn_w_t)
    df_W[cn_w_t] = df_W.index


    #print( 'shifting, amplifying well data...')
    # h'(t) = <T> + (h(t)- <h>)/E
    #   where <T> means "mean T"
    df_GW['shifted_amplified_'+cn_gw_v] = df_W[cn_w_v].mean() + (df_GW[cn_gw_v] - df_GW[cn_gw_v].mean()) / float(E)


    # loop over gw wells and USERDEFINED possible timelags
    #   i.e. timetuple=(20, 30) means that the script will try to match all timelags in list [20, 21, 22, ..., 30]
    #   we use these timetuples to increase speed of calculation, cause this approach of Erskine is timeconsuming
    #   by default it is recommended to set all of the timetuples to (0, 60) or some other awaited region
    #   then user can play around with the values.
    #print( 'Calculating timelag...')


    if len(tlag_tuple) == 3:
        tlag_iterator = xrange(tlag_tuple[0], tlag_tuple[1], tlag_tuple[2])
    elif len(tlag_tuple) == 2:
        tlag_iterator = xrange(tlag_tuple[0], tlag_tuple[1])
    else:
        raise NotImplementedError('tlag_iterator should be a tuple of 2 or 3 elements')

    SUMM_LIST = list()
    TLAG_LIST = list()
    for tlag in tlag_iterator:        # try all timelags specified in 'tlag_iterator'
        ### now loop over all records in GROUNDWATERLEVEL data... and calculate sum according to Erskine 1991 equation

        tlag_timedelta = datetime.timedelta(minutes=tlag)  # convert minutes to timedelta object
        df_GW['current_t_minus_tlag'] = df_GW[cn_gw_t] - tlag_timedelta
        df_GW['current_river_h'] = df_W.loc[df_GW['current_t_minus_tlag']][cn_w_v].values
        df_GW['current_erskine_to_sum'] = (df_GW[cn_gw_v] - df_GW['current_river_h'])**2
        
        summ = df_GW['current_erskine_to_sum'].sum()
        print( 'timelag=', tlag_timedelta, ' >>> summ =', summ)
        SUMM_LIST.append(summ)
        TLAG_LIST.append(tlag_timedelta)


    print('-'*100)
    print( '\t minimal SUMM       :', min(SUMM_LIST))
    print( '\t corresponding TLAG :', TLAG_LIST[SUMM_LIST.index(min(SUMM_LIST))])
    print( '-'*100)
    timelag = TLAG_LIST[SUMM_LIST.index(min(SUMM_LIST))]



    del df_GW
    del df_W

    del SUMM_LIST
    del TLAG_LIST
    return timelag



# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////


if __name__ == '__main__':
    import matplotlib.pyplot as plt
