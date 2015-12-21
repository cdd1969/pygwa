import pandas as pd
from ..flowchart import package


def returnPandasDf(obj):
    """ Unfortunately the pyqtgraph Nodes cannot transmit pandas.DataFrame
        objects. Therefore in this project these objects are wrapped into
        Package.Package() class.

        This function is a convinient helper to unwrap them
    """
    if isinstance(obj, (pd.DataFrame, pd.Series)):
        return obj
    elif isinstance(obj, package.Package):
        return returnPandasDf(obj.unpack())
    else:
        raise TypeError('Unsupported data received. Expected pd.DataFrame, pd.Series or Package, received:', type(obj))
