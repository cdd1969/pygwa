import pandas as pd
from datetime import datetime


def f_dateparser(string):
    return datetime.strptime(string.strip(), '%d.%m.%Y %H:%M')


def read_hydrographs_into_pandas(fname, datetime_indexes=False, log=False, decimal='.', delimiter=';', usecols=[0, 1, 2, 3, 4, 5, 6, 7], skiprows=1):
    """
        for reading ALL waterlevels
    """
    print "reading hydrographs..."
    # this function is usefull for hydrographs from 1n file
    
    dateparser = lambda x: datetime.strptime(x, '%d.%m.%Y %H:%M')
    nrow = None

    if datetime_indexes:
        df = pd.read_csv(fname, sep=delimiter, usecols=usecols, header=0, skiprows=skiprows, index_col=0,
                        parse_dates=['Datetime'], nrows=nrow, date_parser=dateparser, decimal=decimal)
    else:
        df = pd.read_csv(fname, sep=delimiter, usecols=usecols, header=0, skiprows=skiprows, decimal=decimal, nrows=nrow)
        df.insert(0, "datetime", df.apply(lambda x: f_dateparser(x[0]), axis=1))
        col_names = list(df.columns.values)
        col_names[1] = "to_delete"
        df.columns = col_names
        del df['to_delete']

    if log:
        print df
    return df
    #return df.ix[1100:, :]  # slicing of pandas DataFrame (example: df[30:50, :"GW_4"] will slice ROWS 30 to 50, and all COLUMNS up to GW_1)


def read_mean_hydrographs_into_pandas(fname, datetime_indexes=False, log=False, decimal='.', delimiter=';', usecols=None, skiprows=4, names=None, na_values=None):
    """
        for reading ALL waterlevels
    """
    print "reading hydrographs..."
    # this function is usefull for hydrographs from 1n file
    
    dateparser = lambda x: datetime.strptime(x, '%d.%m.%Y %H:%M')
    nrow = None

    if datetime_indexes:
        df = pd.read_csv(fname, sep=delimiter, usecols=usecols, header=0, skiprows=skiprows, index_col=0,
                        parse_dates=['Datetime'], nrows=nrow, date_parser=dateparser, decimal=decimal, names=names, na_values=na_values)
    else:
        df = pd.read_csv(fname, sep=delimiter, usecols=usecols, header=0, skiprows=skiprows, decimal=decimal, names=names, na_values=na_values)
        df.insert(0, "datetime", df.apply(lambda x: f_dateparser(x[0]), axis=1))
        col_names = list(df.columns.values)
        col_names[1] = "to_delete"
        df.columns = col_names
        del df['to_delete']

    if log:
        print df
    return df
    #return df.ix[1100:, :]  # slicing of pandas DataFrame (example: df[30:50, :"GW_4"] will slice ROWS 30 to 50, and all COLUMNS up to GW_1)



def read_amplitudes_into_pandas(fname):
    """
        for reading amplitudes
    """
    # this function is usefull for hydrographs from 1n file
    print "reading amplitudes..."
    usecols1 = [0, 2]
    usecols2 = [1, 3]
    usecols3 = [4]
    skiprows = 1
    delimiter = ';'



    df_high = pd.read_csv(fname, sep=delimiter, usecols=usecols1, header=0, skiprows=skiprows)
    
    df_high.insert(0, "datetime", df_high.apply(lambda x: f_dateparser(x[0]), axis=1))
    col_names = list(df_high.columns.values)
    col_names[1] = "to_delete"
    col_names[-1] = "y"
    df_high.columns = col_names
    del df_high['to_delete']
    
    df_low = pd.read_csv(fname, sep=delimiter, usecols=usecols2, header=0, skiprows=skiprows)
    df_low.insert(0, "datetime", df_low.apply(lambda x: f_dateparser(x[0]), axis=1))
    col_names = list(df_low.columns.values)
    col_names[1] = "to_delete"
    col_names[-1] = "y"
    df_low.columns = col_names
    del df_low['to_delete']

    df_amp = pd.read_csv(fname, sep=delimiter, usecols=usecols3, header=0, skiprows=skiprows)
    df_amp.columns = ['amplitude']

    return list((df_high, df_low, df_amp))


def read_xlx_into_pandas(fname, sheetname=0):
    return pd.io.excel.read_excel(fname, sheetname=sheetname)