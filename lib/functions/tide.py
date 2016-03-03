from __future__ import division
import numpy as np
import pandas as pd
from ferris1951 import h as ferris1951curve




def curve(t=[], A=0., omega=0., phi=0., mode='cos'):
    if mode == 'cos':
        return A*np.cos(omega*t + phi)
    elif mode == 'sin':
        return A*np.sin(omega*t + phi)


def generate_tide(t0, dt, tend, components={}, mode='cos', label='GenCurve', equation='tide', **kwargs):
    '''Generate tide amplitude signal based on multiple tidal components

    Args:
    -----
        t0 (np.datetime64):
            datetime of the initial timestep
        tend (np.datetime64):
            datetime of the last timestep
        dt (np.timedelta64):
            time difference between two timesteps
        components (dict(dict)):
            Dictionary of dictionaries describing tidal constituents
            Keys of the `components` dictionary are labels of the tidal
            constituents, where values are another dictionary describing
            tidal parameters and shoud include following three keys:
                'A', 'omega', 'phi'
            Example:
                components = { 'M2':
                    {'A': 1.5,        # amplitude of tide component in [m]
                     'omega': 0.506,  # angular velocity of tide component in [rad/h]
                     'phi': -0.2}     # phase shift of tide component in [rad]
                    }
        mode ('cos'|'sin'):
            Flag to define trigonometric function for generating the curve
        label (str):
            Label of the column with generated column data

    '''
    if not components:
        return

    dt_hours = dt / np.timedelta64(1, 'h')

    # >>> create datetime array
    T_datetime = np.arange(t0, tend+dt, dt)  # array with np.datetime64 objects for generating timeseries
    #T_hours = np.arange(0, dt_hours*(len(T_datetime)+1), dt_hours)  # array with floats for calculating curve
    T_hours = (T_datetime - t0) / np.timedelta64(1, 'h')  # array with floats for calculating curve

    # >>> initialize curve array
    H = np.zeros(len(T_hours))
    # >>> do curve calculations
    for name, opts in components.iteritems():
        if equation == 'tide':
            H += curve(T_hours, opts['A'], opts['omega'], opts['phi'], mode=mode)
        elif equation == 'ferris':
            H += ferris1951curve(t=T_hours*3600., A=opts['A'], omega=opts['omega']/3600., phi=opts['phi'], D=kwargs['D'], x=kwargs['x'])
        else:
            return (None)

    return pd.DataFrame(data={'Datetime': T_datetime, label: H})


