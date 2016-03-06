from __future__ import division
import numpy as np
import pandas as pd
from ferris1951 import h as ferris1951curve
from xia2007 import h as xia2007curve




def canalCurve(t=[], A=0., omega=0., phi=0.):
    return A*np.cos(omega*t + phi)


def generate_tide(t0, dt, tend, components={}, label='GenCurve', equation='tide', **kwargs):
    '''Generate tide amplitude signal based on multiple tidal components, for a given
    equation type hardcode below

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
                components = { 'M2':  # component name
                    {'A': 1.5,        # amplitude of tide component in [m]
                     'omega': 0.506,  # angular velocity of tide component in [rad/h]
                     'phi': -0.2}     # phase shift of tide component in [rad]
                    }
        label (str):
            Label of the column with generated column data

        equation (str):
            Type of the underlying equation. Valid are:
                * 'tide'   >>> general cos signal (ocean tide)
                * 'ferris' >>> dumped groundwater signal (ferris 1951)
                * 'xia'    >>> dumped groundwater signal (xia et al 2007)

        **kwargs:
            Additional arguments that are passed to *curve equation*

    Return:
    -------
        pd.DataFrame:
            Dataframe with two columns: 'Datetime' and `label`. Datetime is the time
            index of measurement, where column `label` is the calculated (ground)water
            signal amplitude

    '''
    if not components:
        return
    # >>> create datetime array
    T_datetime = np.arange(t0, tend+dt, dt)  # array with np.datetime64 objects for generating timeseries
    T_hours = (T_datetime - t0) / np.timedelta64(1, 'h')  # array with floats (hours) for calculating curve

    # >>> initialize curve array
    W = kwargs.get('W', 0.)  # get default elevation
    H = np.zeros(len(T_hours)) + W
    
    # >>> do curve calculations for each tide component and sum them
    for name, opts in components.iteritems():
        if equation == 'tide':
            H += canalCurve(T_hours, opts['A'], opts['omega'], opts['phi'])
        elif equation == 'ferris':
            H += ferris1951curve(t=T_hours*3600., A=opts['A'], omega=opts['omega']/3600., phi=opts['phi'], D=kwargs['D'], x=kwargs['x'])
        elif equation == 'xia':
            H += xia2007curve(t=T_hours*3600., x=kwargs['x'],
                A=opts['A'], omega=opts['omega']/3600., phi0=opts['phi'],
                alpha=kwargs['alpha'], beta=kwargs['beta'], theta=kwargs['theta'],
                L=kwargs['L'], K1=kwargs['K1'], b1=kwargs['b1'],
                K=kwargs['K'], b=kwargs['b'],
                K_cap=kwargs['K_cap'], b_cap=kwargs['b_cap'])
        else:
            return None

    return pd.DataFrame(data={'Datetime': T_datetime, label: H})