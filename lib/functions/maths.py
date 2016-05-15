import numpy as np
import pandas as pd


def rmse(predictions, targets):
    ''' Caclculate Root Mean Squared Error
        of two sets of reading
    '''
    if isinstance(predictions, (np.ndarray, pd.Series)) and isinstance(targets, (np.ndarray, pd.Series)):
        return np.sqrt( np.nanmean( ( (predictions - targets) ** 2) ) )
    else:
        raise TypeError('Usupported type in inputs `predictions`:{0}, `targets`:{1}. Expected (np.ndarray, pd.Series)'.format(type(predictions), type(targets)))
