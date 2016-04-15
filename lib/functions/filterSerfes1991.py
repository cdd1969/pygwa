#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np
import gc
import pandas as pd
from lib.functions.general import isNumpyDatetime, isNumpyNumeric


def get_number_of_measurements_per_day(data, datetime=None, log=False):
    """ Calculate number of measurements/entries per day (per 24h) in the passed
        dataframe.


        Args:
            data (pd.DataFrame): input data, where indexes are Datetime objects,
                see `parse_dates` parameters of `pd.read_csv()`

            datetime (Optional[str]): Location of the datetime objects.
                By default is `None`, meaning that datetime objects are
                located within `pd.DataFrame.index`. If not `None` - pass the
                column-name of dataframe where datetime objects are located.
                This is needed to determine number of measurements per day.
                Note: this argument is ignored if `N` is not `None` !!!

            log (Optional[bool]): flag to show some prints in console

        Returns:
            N (int): number of entries per day
    """

    if datetime is None:
        entriesPerDay = data.groupby(data.index.date).count()  # series for all the timespan
    else:
        if datetime in data.columns:
            try:
                dfts = data.set_index(datetime)  # we need to aply group method only to timeseries (index=datetime). Thus we will create a fake one
                entriesPerDay = data.groupby(dfts.index.date).count()  # series for all the timespan
                del dfts
            except:
                raise ValueError('Passed column <{0}> is not of type <datetime64>. Received type : {1}'.format(datetime, data[datetime].dtype))
        else:
            raise KeyError('Passed column name <{0}> not found in dataframe. DataFrame has following columns: {1}'.format(datetime, list(data.columns)))
    N = entriesPerDay.ix[1, 0]  # pick one value from series (from 1st row, 0-column; because 0-0 can give false N-entries per day)
    if log:
        print (entriesPerDay)
        print ('i will use following number of entries per day: ', N)
    return N


#@profile
def filter_wl_71h_serfes1991(data, datetime=None, N=None, usecols=None, keep_origin=True, verbose=False, log=False):
    ''' Calculate mean water-level according to Serfes1991.

    Perform a column-wise time averaging in three iterations.
        1) The first sequence averages 24 hours of measurements
        2) The second sequence averages 24 hours of first sequence
        3) The third sequence averages all values of second sequence that were
        generated when the filter was applied to 71h

    This function is a modified version of original Serfes filter: it is not
    limited to hourly measurements.

    Args:
        data (pd.DataFrame): input data, where indexes are Datetime objects,
            see `parse_dates` parameters of `pd.read_csv()`

        datetime (Optional[str]): Location of the datetime objects.
            By default is `None`, meaning that datetime objects are
            located within `pd.DataFrame.index`. If not `None` - pass the
            column-name of dataframe where datetime objects are located.
            This is needed to determine number of measurements per day.
            Note: this argument is ignored if `N` is not `None` !!!
        
        N (Optional[int]): explicit number of measurements in 24 hours. By
            default `N=None`, meaning that script will try to determine
            number of measurements per 24 hours based on real datetime
            information provided with `datetime` argument.

        usecols (Optional[List[str]]): explicitly pass the name of the columns
            that will be evaluated. These columns must have numerical dtype
            (i.e. int32, int64, float32, float64). Default value is `None`
            meaning that all numerical columns will be processed.

        keep_origin (Optional[bool]): if `True` - will keep original columns
            in the output dataframe. If `False` - will return dataframe which
            has only results columns and original DateTime columns

        verbose (Optional[bool]): if `True` - will keep all three iterations
            in the output. If `False` - will save only final (3rd) iteration.
            This may useful for debugging, or checking this filter.
        
        log (Optional[bool]): flag to show some prints in console

    Returns:
        data (pd.DataFrame): input dataframe with appended time-averaged values.
            these values are appended into new columns

    '''

    # if convert all columns...
    if usecols is None:
        # select only numeric columns...
        numeric_columns = [col for col in data.columns if isNumpyNumeric(data[col].dtype)]
    # or covert only user defined columns....
    else:
        # select only numeric columns...
        numeric_columns = [col for col in data.columns if (isNumpyNumeric(data[col].dtype) and col in usecols)]
    #if user has not explicitly passed number of measurements in a day, find it out!
    if N is None:
        N = get_number_of_measurements_per_day(data, datetime=datetime, log=log)

    if log:
        print ('All column names:', list(data.columns))
        print ('Numeric colums:', numeric_columns)
        print ('i will use following number of entries per day: ', N)

    if keep_origin:
        output = data
    else:
        output = pd.DataFrame()

        #copy datetime columns
        datetime_columns = [col for col in data.columns if isNumpyDatetime(data[col].dtype)]
        for col in datetime_columns:
            output[col] = data[col]

    nX = int(N/24.*71 - (N-1))  # number of elements in sequence_1
    nY = nX - (N-1)             # number of elements in sequence_2
    #print (N, nX, nY)
    for col_name in numeric_columns:
        if float('.'.join(pd.__version__ .split('.')[0:2])) < 0.18:  # if version is less then 0.18 (OLD API)
            output[col_name+'_sequence1'] = pd.rolling_mean(data[col_name], window=N, min_periods=N, center=True).values
            output[col_name+'_sequence2'] = pd.rolling_mean(output[col_name+'_sequence1'], window=N, min_periods=N, center=True).values
            output[col_name+'_mean'] = pd.rolling_mean(output[col_name+'_sequence2'], window=nY, min_periods=nY, center=True).values
        else:
            # new API
            output[col_name+'_sequence1'] = data[col_name].rolling(window=N, min_periods=N, center=True).mean().values
            output[col_name+'_sequence2'] = output[col_name+'_sequence1'].rolling(window=N, min_periods=N, center=True).mean().values
            output[col_name+'_mean']      = output[col_name+'_sequence2'].rolling(window=nY, min_periods=nY, center=True).mean().values
        if not verbose: del output[col_name+'_sequence1']
        if not verbose: del output[col_name+'_sequence2']

    gc.collect()
    return output
