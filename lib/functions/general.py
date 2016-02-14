#!/usr/bin python
# -*- coding: utf-8 -*-
import pandas as pd
from ..flowchart import package
import numpy as np


def returnPandasDf(obj, raiseException=False):
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


        Args:
        ------
            obj : object of any dtype, but it is expected to recieve pd.DataFrame
                or package with this dtype

            raiseException (Optional[bool]): if `True` when data is not what it is
                expected - will raise Error. If `False` (default) - will return
                `None` instead

        Returns:
        --------
            [pd.DataFrame/pd.Series/None]
    """
    if isinstance(obj, (pd.DataFrame, pd.Series)):
        return obj
    elif isinstance(obj, package.Package):
        return returnPandasDf(obj.unpack())
    else:
        if raiseException:
            raise TypeError('Unsupported data received. Expected pd.DataFrame, pd.Series or Package, received:', type(obj))
        else:
            return None


def isNumpyDatetime(dtype):
    #numpy_dtype_endings = ['Y' , 'M' , 'W' , 'B' , 'D' , 'h' , 'm' , 's' , 'ms', 'us', 'ns', 'ps', 'fs', 'as']
    # for some reason 'B' - fails
    numpy_dtype_endings = ['Y' , 'M' , 'W' ,        'D' , 'h' , 'm' , 's' , 'ms', 'us', 'ns', 'ps', 'fs', 'as']
    numpy_datetime_dtypes = [np.dtype('datetime64[{0}]'.format(suffix)) for suffix in numpy_dtype_endings]
    if dtype in numpy_datetime_dtypes:
        return True
    else:
        return False


def isNumpyNumeric(dtype):
    if dtype in (int, float, np.float64 , np.int64, np.float32, np.int32):
        return True
    else:
        return False


def flatten_dict(d, sep='.'):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    yield key + sep + subkey, subvalue
            else:
                yield key, value

    return dict(items())

def walkdict(d, key):
    stack = d.items()
    while stack:
        k, v = stack.pop()
        if isinstance(v, dict):
            stack.extend(v.iteritems())
        else:
            if k == key:
                return v




if __name__ == '__main__':
    import numpy as np
    a = 1
    print (isNumpyDatetime(type(a)))