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
    E = df[river].std()/float(df[gw].std())

    return E





def tidalEfficiency_method2(df, river, gw, log=False):
    '''
    Calculate Tidal Efficiency according to Smith 1994, as the mean
    of the amplitude ratios for every tidal-cycle.
        
        E = sum(Ei)/n

        where:
            Ei = h0/h   - ration of amplitude in river and gw well at cycle i
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

    return E



# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import random
    