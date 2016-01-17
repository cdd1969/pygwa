''' Plots figure with 6 subplots, to determine outcrop distance,
    - 3 top subplots >>> from Tidal efficiency
    - 3 bottom subplots >>> from Time lag
    - three columns represent different well selection

    Note the inputs after __main__ !!!
'''

import os
import sys
import inspect
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from numpy import log as ln


# use this if you want to include modules from a subfolder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(
                    inspect.getfile( inspect.currentframe() ))[0], "lib")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import plot_pandas
import datetime
import numpy as np


def plot(sh_dist, effs=None, tlags=None, labels=None):
    """ Calculate so-called "Outcrop-distance" based on Ferris 1961 equation
    for tidal propogation of the groundwater. This equation implies that, at
    the place, where the aquifer is hydraulically connected to the sea, the
    logarithm of Tidal Efficiency factor is 0, and the Timelag is not present.

    Plot scatter field for (x, lg(E)) and (x, Tlag), where `x` is the distance
    between observation well and the shoreline. Then evaluate trendlines f(x),
    find the ordinate `x0` where f(x0) = 0. Then the `x0` is requested "Outcrop-
    distance".


    Args:
    -----
        effs (1-D array_like):
            array with floats representing tidal efficiencies for each
            groundwater observation well

        tlags (1-D array_like):
            array of timelag values for each groundwater observation well.
            Values can be stored in one of the three different dtype:
            int/float/datetime.timedelta. If int/float dtype is used, values
            are interpreted as number of minutes

        sh_dist (1-D array_like):
            array with floats representing distance to shore in meters from
            each groundwater observation well.

        labels (1-D array_like):
            array with strings - label of each groundwater observation well.
    """
    pass

    # determine how many plots we will have... (mode)
    if effs is None and tlags is not None:
        mode = 'tlags'
    if effs is not None and tlags is None:
        mode = 'effs'
    elif effs is not None and tlags is not None:
        mode = 'both'
    else:
        raise ValueError('No *timelags* or *tidal efficiencies* has been specified. Aborting')

    # determine the dtype of tlag
    if tlags is not None:
        if isinstance(tlags[0], datetime.timedelta):
            # convert to minutes
            tlags = np.array([tlag.total_seconds()/60. for tlag in tlags])
        elif not isinstance(tlags[0], (int, float)):
            raise TypeError('Array `tlags` have values with invalid dtype <{0}>. Must be one of <int>, <float>, <timedelta>'.format(type(tlags[0])))




if __name__ == '__main__':
    # --------------------------------------------------------------------------------------
    # user inputs
    # --------------------------------------------------------------------------------------
    d = dict()
    d['well'] = ['GW_1', 'GW_2', 'GW_3', 'GW_4', 'GW_5', 'GW_6']
    d['x']   = [1., 1., 10.5, 24.1, 1., 7.]  # distance offshore (from map)
    d['E_1'] = ln([0.251, 0.312, 0.246 , 0.178, 0.331, 0.367])  #  logarithm of tidal efficiency (amplitude ration method)
    d['E_2'] = ln([0.303, 0.349, 0.292 , 0.231, 0.371, 0.473])  #  logarithm of tidal efficiency (std method)
    d['E_3'] = ln([0.254, 0.312, 0.247 , 0.179, 0.329, 0.371])  #  logarithm of tidal efficiency (cycle-std method)
    d['T_1'] = [25., 12., 16., 25., 12., 35.]  # timelag (erskine91 method)
    d['T_2'] = [26.4, 13.9, 17.8, 28.9, 13.7, 35.1]  # timelag (cyclic erskine91 method)
    # --------------------------------------------------------------------------------------
    # END user inputs END
    # --------------------------------------------------------------------------------------





    with sns.axes_style("whitegrid"):
        df1 = pd.DataFrame(data=d)  # all 6 wells
        df2 = df1.ix[0:4, :]        # first 5 wells
        df3 = df1.ix[1:3, :]        # 3 wells in a row

        fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(nrows=2, ncols=3, figsize=(11.69, 8.27))
        
        for ax, x, y, legendlabel, borders, ylabel, l_loc in zip(
            [ax1,                                   ax4],
            [['x', 'x', 'x'],                       ['x', 'x']],
            [['E_1', 'E_2', 'E_3'],                 ['T_1', 'T_2']],
            [['Method 1', 'Method 2', 'Method 3'],  ['Method 1', 'Method 2']],
            [[-100., 100., -1.8, 0.],               [-100., 100, 0., 40.]],
            ['Log Tidal Efficiency [-]',            'Timelag [min]'],
            ['upper right',                         'upper left']
            ):
            plot_pandas.plot_pandas_scatter(df1, x=x, y=y, saveName=None,
                    xlabel='Distance from shore [m]', title='Wells GWM1-GWM6', ylabel=ylabel,
                    trendlinemode=1, legendlabels=legendlabel,
                    xlim=[borders[0], borders[1]], ylim=[borders[2], borders[3]],
                    legend_location=l_loc, ax=ax, draw_axes=True,
                    df_scatter_kwargs={'marker': "o", 'markersize': 6., 'style': '.', 'markeredgecolor': 'black', 'markeredgewidth': 0.2, 'legend': False},
                    axeslabel_fontsize=18., title_fontsize=20., axesvalues_fontsize=18., annotation_fontsize=18., legend_fontsize=18.)

        for ax, x, y, legendlabel, borders, ylabel, l_loc in zip(
            [ax2,                                   ax5],
            [['x', 'x', 'x'],                       ['x', 'x']],
            [['E_1', 'E_2', 'E_3'],                 ['T_1', 'T_2']],
            [['Method 1', 'Method 2', 'Method 3'],  ['Method 1', 'Method 2']],
            [[-100., 100., -1.8 , 0.],               [-100., 100, 0., 40.]],
            ['Log Tidal Efficiency [-]',            'Timelag [min]'],
            ['upper right',                         'upper left']
            ):
            plot_pandas.plot_pandas_scatter(df2, x=x, y=y, saveName=None,
                    xlabel='Distance from shore [m]', title='Wells GWM1-GWM5', ylabel=ylabel,
                    trendlinemode=1, legendlabels=legendlabel,
                    xlim=[borders[0], borders[1]], ylim=[borders[2], borders[3]],
                    legend_location=l_loc, ax=ax, draw_axes=True,
                    df_scatter_kwargs={'marker': "o", 'markersize': 6., 'style': '.', 'markeredgecolor': 'black', 'markeredgewidth': 0.2, 'legend': False},
                    axeslabel_fontsize=18., title_fontsize=20., axesvalues_fontsize=18., annotation_fontsize=18., legend_fontsize=18.)
        
        for ax, x, y, legendlabel, borders, ylabel, l_loc in zip(
            [ax3,                                   ax6],
            [['x', 'x', 'x'],                       ['x', 'x']],
            [['E_1', 'E_2', 'E_3'],                 ['T_1', 'T_2']],
            [['Method 1', 'Method 2', 'Method 3'],  ['Method 1', 'Method 2']],
            [[-100., 100., -1.8 , 0.],              [-100., 100, 0., 40.]],
            ['Log Tidal Efficiency [-]',            'Timelag [min]'],
            ['upper right',                         'upper left']
            ):
            plot_pandas.plot_pandas_scatter(df3, x=x, y=y, saveName=None,
                    xlabel='Distance from shore [m]', title='Wells GWM2-GWM4', ylabel=ylabel,
                    trendlinemode=1, legendlabels=legendlabel,
                    xlim=[borders[0], borders[1]], ylim=[borders[2], borders[3]],
                    legend_location=l_loc, ax=ax, draw_axes=True,
                    df_scatter_kwargs={'marker': "o", 'markersize': 6., 'style': '.', 'markeredgecolor': 'black', 'markeredgewidth': 0.2, 'legend': False},
                    axeslabel_fontsize=18., title_fontsize=20., axesvalues_fontsize=18., annotation_fontsize=18., legend_fontsize=18.)
        

        plt.setp(((ax1, ax2, ax3), (ax4, ax5, ax6)), xticks=[-100, -50, 0, 50, 100], xticklabels=[-100, -50, 0, 50, 100])
        for aX in [ax2, ax3, ax5, ax6]:
            aX.set_ylabel('')

        for aX in [ax1, ax2, ax3]:
            aX.set_xticks([-100, -50, 0, 50, 100])
            plt.setp(aX.get_xticklabels(), visible=True)



        #figManager = plt.get_current_fig_manager()
        #figManager.window.showMaximized()
        plt.tight_layout()
        plt.show()
