#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np
import time
import gc



#@profile
def filter_wl_71h_serfes1991(data, datetime=None, N=None, usecols=None, verbose=False, log=False):
    ''' Calculate mean water-level according to Serfes1991.

    Perform a column-wise time averaging in three iterations. This function is
    a modified version of original Serfes filter: it is not limited to hourly
    measurements.

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
        numeric_columns = list()
        for col_name in data.columns:  # cycle through each column...
            if data[col_name].dtype in (np.float64 , np.int64, np.float32, np.int32):
                numeric_columns.append(col_name)
    # or covert only user defined columns....
    else:
        # select only numeric columns...
        numeric_columns = list()
        for col_name in usecols:  # cycle through each column...
            if data[col_name].dtype in (np.float64 , np.int64, np.float32, np.int32):
                numeric_columns.append(col_name)

    #if user has not explicitly passed number of measurements in a day, find it out!
    if N is None:
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
        N = entriesPerDay.ix[1, 0]  # pick one value from series
        if log: print (entriesPerDay)

    nEntries = len(data.index)
    halfN = int(N/2)


    if log:
        print ('All column names:', list(data.columns))
        print ('Numeric colums:', numeric_columns)
        print ('i will use following number of entries per day: ', N)

    

    overallProgress = len(numeric_columns)*3  # three averagings...
    progress = 0
    data['ind'] = np.arange(nEntries, dtype=np.int32)  # dummy row with row indexes as integer. will be deleted

    # for displaying progress, since this is a very long operation
    overallProgress = len(numeric_columns)*3  # three averagings...
    progress = 0


    # function that will be applied row-wise
    def averaging(row):
        currentIndex = int(row['ind'])
        val = data.ix[currentIndex-halfN:currentIndex+halfN, col4averaging].mean()
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
    import pyqtgraph as pg
    app = pg.mkQApp()



    df = process2pandas.read_hydrographs_into_pandas('/home/nck/prj/FARGE_project_work/data/SLICED_171020141500_130420150600/hydrographs/Farge-ALL_10min.all', datetime_indexes=True, usecols=[0, 1, 2, 3], nrows=None)

    #da = filter_wl_71h_serfes1991(df, datetime='Datetime', N=144, usecols=['GW_2'], log=True)
    #print (da[0:30])
    #print (da[700:710])
    
    with pg.ProgressDialog("Processing..", 0, 5, busyCursor=False) as dlg:
        dlg += 1
        dlg.show()
        result = filter_wl_71h_serfes1991(df,
            datetime=None,
            N=None,
            usecols=['GW_1'],
            log=True)
        dlg += 1
        if dlg.wasCanceled():
            raise Exception("Processing canceled by user")
    
    """
    import pyqtgraph.multiprocess as mp
    proc = mp.QtProcess()  # Start a remote process with its own QApplication
    rqt = proc._import('PyQt5.QtGui')

    # create a QProgressDialog in the remote process
    dlg = rqt.QProgressDialog("Processing...", "Cancel", 0, 100)

    # calling methods on this object causes the same method to be called in the remote process
    dlg.show()

    # set the value on the remote dialog, but do not wait for the process to send back a return value
    # (since waiting for a return value can be very slow)
    dlg.setValue(5, _callSync='off')

    # Ask asynchronously whether 'cancel' was clicked.
    # We could just wait for the response, but again this takes a long time.
    canceled = dlg.wasCanceled(_callSync='async')

    # Some time later, check to see if the return value has arrived:
    if canceled.hasResult() and canceled.result() is True:
        raise Exception('user cancelled processing')
    """