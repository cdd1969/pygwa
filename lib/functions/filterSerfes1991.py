#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np
import time
import gc



#@profile
def filter_wl_71h_serfes1991(data, datetime=None, verbose=False, log=False):
    ''' Calculate mean water-level according to Serfes1991

    Perform a column-wise time averaging in three iterations.

    Args:
        data (pd.DataFrame): input data, where indexes are Datetime objects,
            see `parse_dates` parameters of `pd.read_csv()`

        datetime (Optional[str]): Location of the datetime objects.
            By default is `None`, meaning that datetime objects are
            loacated within `pd.DataFrame.index`. If not `None` - pass the
            column-name of dataframe where datetime objects are located.
        
        verbose (Optional[bool]): if `True` - will keep all three iterations
            in the output. If `False` - will save only final (3rd) iteration.
            This may useful for debugging, or checking this filter.
        
        log (Optional[bool]): flag to show some prints in console

    Returns:
        data (pd.DataFrame): input dataframe with appended timeavaraged values.
            these values are appended into new columns

    '''
    
    # select only numeric columns...
    numeric_columns = list()
    for col_name in data.columns:  # cycle through each column...
        if data[col_name].dtype in (np.float64 , np.int64, np.float32, np.int32):
            numeric_columns.append(col_name)

    
    nEntries = len(data.index)
    # ok, we see, that we have 144 measurements per day....
    if datetime is None:
        entriesPerDay = data.groupby(data.index.date).count()  # series for all the timespan
    else:
        if datetime in data.columns:
            try:
                dfts = data.set_index(datetime)  # we need to aply group method only to timeseries (index=datetime). Thus we will create a fake one
                entriesPerDay = data.groupby(dfts.index.date).count()  # series for all the timespan
            except:
                raise ValueError('Passed column <{0}> is not of type <datetime64>. Received type : {1}'.format(datetime, data[datetime].dtype))
        else:
            raise KeyError('Passed columnname <{0}> not found in dataframe. DataFrame has following columns: {1}'.format(datetime, list(data.columns)))
    del dfts
    N = entriesPerDay.ix[1, 0]  # pick one value from series
    halfN = int(N/2)


    if log:
        print ('All column names:', list(data.columns))
        print ('Numeric colums:', numeric_columns)
        print (entriesPerDay)
        print ('i will use following number of entries per day: ', N)

    

    overallProgress = len(numeric_columns)*3  # three averagings...
    progress = 0
    df['ind'] = np.arange(len(df), dtype=np.int32)  # dummy row with row indeces as integer. will be deleted

    # for displaying progress, since this is a very long operation
    overallProgress = len(numeric_columns)*3  # three averagings...
    progress = 0


    # function that will be applied row-wise
    def averaging(row):
        currentIndex = int(row['ind'])
        val = df.ix[currentIndex-halfN:currentIndex+halfN, col4averaging].mean()
        return val

    st = time.time()
    for col_name in numeric_columns:
        if log: print ("Working with numeric column:", col_name)
        data[col_name+'_averaging1'] = np.nan
        data[col_name+'_averaging2'] = np.nan
        data[col_name+'_timeAverage'] = np.nan

        
        if log: print ("[{0}/{1}]\t Calculating first mean".format(progress, overallProgress))
        col4averaging = col_name
        data.loc[halfN:nEntries-halfN, col_name+'_averaging1'] = data.apply(averaging, axis=1)
        progress += 1
        
        if log: print ("[{0}/{1}]\t Calculating second mean".format(progress, overallProgress))
        col4averaging = col_name+'_averaging1'
        data.loc[N:nEntries-N, col_name+'_averaging2'] = data.apply(averaging, axis=1)
        progress += 1
        

        if log: print ("[{0}/{1}]\t Calculating third mean".format(progress, overallProgress))
        col4averaging = col_name+'_averaging2'
        data.loc[N+halfN:nEntries-N-halfN, col_name+'_timeAverage'] = data.apply(averaging, axis=1)
        progress += 1

        if not verbose: del data[col_name+'_averaging1']
        if not verbose: del data[col_name+'_averaging2']
    del data['ind']
    if log: print ("[{0}/{1}]\t Finished".format(progress, overallProgress))
    fn = time.time()

    if log: print ('Time averaging took {0} seconds'.format(int(fn-st)))

    gc.collect()
    return data


if __name__ == '__main__':
    import process2pandas

    df = process2pandas.read_hydrographs_into_pandas('/home/nck/prj/FARGE_project_work/data/SLICED_171020141500_130420150600/hydrographs/Farge-ALL_10min.all', datetime_indexes=True, usecols=[0, 1], nrows=None)

    da = filter_wl_71h_serfes1991(df, datetime='Datetime', log=True)
    #print (da)
