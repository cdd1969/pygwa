#!/usr/bin python
# -*- coding: utf-8 -*-
import pandas as pd
from ..flowchart import package
import numpy as np


def returnPandasDf(obj):
    """ Unfortunately the pyqtgraph Nodes cannot transmit pandas.DataFrame
        objects through its terminals. Therefore in this project these objects
        are wrapped into Package.Package() class, before pushed to terminal.

        This function is a convinient helper to unwrap them

        Typical usage will include the reimplemintation of Node's `process()`
        method:
            def process(self, Input):
                Input = returnPandasDf(Input)
                # now `Input` is surely pd.DataFrame or pd.Series
                #... process `Input`
    """
    if isinstance(obj, (pd.DataFrame, pd.Series)):
        return obj
    elif isinstance(obj, package.Package):
        return returnPandasDf(obj.unpack())
    else:
        raise TypeError('Unsupported data received. Expected pd.DataFrame, pd.Series or Package, received:', type(obj))


def isNumpyDatetime(dtype):
    #numpy_dtype_endings = ['Y' , 'M' , 'W' , 'B' , 'D' , 'h' , 'm' , 's' , 'ms', 'us', 'ns', 'ps', 'fs', 'as']
    # for some reason 'B' - fails
    numpy_dtype_endings = ['Y' , 'M' , 'W' ,        'D' , 'h' , 'm' , 's' , 'ms', 'us', 'ns', 'ps', 'fs', 'as']
    numpy_datetime_dtypes = [np.dtype('datetime64[{0}]'.format(suffix)) for suffix in numpy_dtype_endings]
    if dtype in numpy_datetime_dtypes:
        return True
    else:
        return False


if __name__ == '__main__':
    import numpy as np
    a = 1
    print isNumpyDatetime(type(a))