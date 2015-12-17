#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np
import time


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
    if log: print ("Passed data has shape:", data.shape)
    
    # select only numeric columns...
    numeric_columns = list()
    for col_name in data.columns:  # cycle through each column...
        if data[col_name].dtype in (np.float64 , np.int64, np.float32, np.int32):
            numeric_columns.append(col_name)
    if log: print ('All columns:', list(data.columns))
    if log: print ('Numeric colums:', numeric_columns)
    
    #print number of items per day
    #print(data.groupby(data.index.date).count())
    # ok, we see, that we have 144 measurements per day....
    nEntries = len(data.index)
    entriesPerDay = data.groupby(data.index.date).count()  # series for all the timespan
    N = entriesPerDay.ix[1, 0]  # pick one value from series
    halfN = int(N/2)
    if log: print (entriesPerDay)
    if log: print ('i will use following number of entries per day: ', N)

    
    if log: print ('Now I will apply Serfes Filter to numeric-columns')
    st = time.time()
    overallProgress = len(numeric_columns)*3  # three averagings...
    progress = 0
    for col_name in numeric_columns:
        if log: print ("working with numeric column:", col_name)
        data[col_name+'_averaging1'] = np.nan
        data[col_name+'_averaging2'] = np.nan
        data[col_name+'_timeAverage'] = np.nan
        
        print ("[{0}/{1}]\t Calculating first mean: {2}".format(progress, overallProgress, col_name))
        for i in xrange(halfN, nEntries-halfN):  # cycle trough correct indexes
            data.ix[i, col_name+'_averaging1'] = data.ix[i-halfN:i+halfN, col_name].mean()
        
        progress += 1
        print ("[{0}/{1}]\t Calculating second mean: {2}".format(progress, overallProgress, col_name))
        for i in xrange(N, nEntries-N):  # cycle trough correct indexes
            data.ix[i, col_name+'_averaging2'] = data.ix[i-halfN:i+halfN, col_name+'_averaging1'].mean()
        
        progress += 1
        print ("[{0}/{1}]\t Calculating third mean: {2}".format(progress, overallProgress, col_name))
        for i in xrange(N+halfN, nEntries-N-halfN):  # cycle trough correct indexes
            data.ix[i, col_name+'_timeAverage'] = data.ix[i-halfN:i+halfN, col_name+'_averaging2'].mean()
        
        progress += 1
        if not verbose: del data[col_name+'_averaging1']
        if not verbose: del data[col_name+'_averaging2']
    fn = time.time()

    if log: print ('Time averaging took {0} seconds'.format(int(fn-st)))
    

    if log: print ('\n\n\n METHOD 2')
    st = time.time()
    df['ind'] = np.arange(len(df), dtype=np.int32)

    overallProgress = len(numeric_columns)*3  # three averagings...
    progress = 0
    for col_name in numeric_columns:
        if log: print ("working with numeric column:", col_name)
        data[col_name+'_averaging1_2'] = np.nan
        data[col_name+'_averaging2_2'] = np.nan
        data[col_name+'_timeAverage_2'] = np.nan

        def averaging(row):
            currentIndex = int(row['ind'])
            val = df.loc[currentIndex-halfN:currentIndex+halfN, col4averaging].mean()
            return val
        
        print ("[{0}/{1}]\t Calculating first mean: {2}".format(progress, overallProgress, col_name))
        col4averaging = col_name
        data.loc[halfN:nEntries-halfN, col_name+'_averaging1_2'] = data.apply(averaging, axis=1)
        progress += 1
        
        print ("[{0}/{1}]\t Calculating second mean: {2}".format(progress, overallProgress, col_name))
        col4averaging = col_name+'_averaging1_2'
        data.loc[N:nEntries-N, col_name+'_averaging2_2'] = data.apply(averaging, axis=1)
        progress += 1
        

        print ("[{0}/{1}]\t Calculating third mean: {2}".format(progress, overallProgress, col_name))
        col4averaging = col_name+'_averaging2_2'
        data.loc[N+halfN:nEntries-N-halfN, col_name+'_timeAverage_2'] = data.apply(averaging, axis=1)
        progress += 1

        if not verbose: del data[col_name+'_averaging1_2']
        if not verbose: del data[col_name+'_averaging2_2']
    del data['ind']
    print ("[{0}/{1}]\t Finished".format(progress, overallProgress))
    fn = time.time()

    if log: print ('Time averaging took {0} seconds'.format(int(fn-st)))





    return data


if __name__ == '__main__':
    import process2pandas

    df = process2pandas.read_hydrographs_into_pandas('/home/nck/prj/FARGE_project_work/data/SLICED_171020141500_130420150600/hydrographs/Farge-ALL_10min.all', datetime_indexes=True, usecols=[0, 1], nrows=None)
    da = filter_wl_71h_serfes1991(df, log=True)
    print (da)
    print ((da['GW_1_timeAverage']-da['GW_1_timeAverage_2']).sum())
    print (da['GW_1_timeAverage'].equals(da['GW_1_timeAverage_2']))




    #df['ind'] = np.arange(len(df), dtype=np.int32)
    #df['test'] = df['ind']*2
    #dataColumnName = 'test'
    #offset = 1
    #
    #def rowIndex(row):
    #    print (row['ind'], type(row['ind']), '>>>', df.ix[int(row['ind']), 'test'])
    #    currentIndex = int(row['ind'])
    #    val = df.ix[currentIndex-offset:currentIndex+offset+1, dataColumnName].sum()
    #    return val
    #
    #df.loc[2:8, 'rowIndex'] = df.apply(rowIndex, axis=1)
    #print (df)