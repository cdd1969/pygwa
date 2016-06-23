''' MODULE CONTAINING PLOTTING FUNCTIONS...
'''
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import math


def r_squared(actual, ideal):
    ''' Calculate coefficient of determination (R2)
        actual - 1D-array of y-values of measured points
        ideal  - 1D-array of y-values of trendline (ideal) points
    '''
    actual_mean = np.mean(actual)
    ideal_dev   = np.sum([(val - actual_mean)**2 for val in ideal])
    actual_dev  = np.sum([(val - actual_mean)**2 for val in actual])

    return ideal_dev / actual_dev



def plot_pandas_scatter(df, x=[0], y=[1], saveName=None, xlabel=None, ylabel=None, title=None, trendlinemode=None, legendlabels=[None], N_DEVIATIONS=10,
                        xlim=None, ylim=None, ax=None, legend_location=0, draw_axes=False,
                        df_scatter_kwargs={'marker': "o", 'markersize': 6., 'style': '.', 'markeredgecolor': 'black', 'markeredgewidth': 0.2, 'legend': False},
                        trendline_kwargs={'style': '-', 'color': None, 'lw': 4.},
                        axeslabel_fontsize=10., title_fontsize=20., axesvalues_fontsize=10., annotation_fontsize=10., legend_fontsize=8.):
    """
        df              - pandas.DataFrame timeseries for original hydrographs
        x, y            - list with keys or indexes of X and Y data columns
        saveName        - None, or string with figure name to be saved
        title           - title for figure
        xlabel          - None, or string for labeling x-axes
        ylabel          - None, or string for labeling y-axes
        trendlinemode   - 1, 2, 3 or None:
                            1    - draw trendlines using all data points
                            2    - draw trendlines using only <N_DEVIATIONS> data points, that are most farlying (see code)
                            3    - draw trendlines using all data points, and shift them to the most-far-lying points
                            None - do not draw trendline

        N_DEVIATIONS    - (used only if trenlinemode=2); int, (i.e. N_DEVIATIONS=10) create trend-lines based on this number of points
        legendlabels    - List of legendnames or [None]. If default ([None]) - standart names are used
        ylim         - None, or list for y-limits [ymin, ymax] of the plot. (i.e. ylim=[0., 1.])
        xlim         - None, or list for x-limits [xmin, xmax] of the plot. (i.e. xlim=[-0.5, 0.5])
        
    """
    if len(x) != len(y):
        raise ValueError('Number of keys for X and Y dimension should be equal. Got: {0} for X and {1} for y'.format(len(x), len(y)))
    
    print( "plotting scatter data...")

    # if no axes has been passed - create figure, and remember that is was created by _ax
    _ax = True
    if not ax:
        fig = plt.figure(tight_layout=True)
        _ax = False
        ax = fig.add_subplot(111)

    # plot scatter data....
    for xi, yi in zip(x, y):
        df.plot(x=xi, y=yi, ax=ax, **df_scatter_kwargs)


    # set some plot margins...
    minx, maxx = min([df[X].min() for X in x]), max([df[X].max() for X in x])
    miny, maxy = min([df[Y].min() for Y in y]), max([df[Y].max() for Y in y])
    x_5proc, y_5proc = abs(minx - maxx)*0.1, abs(miny - maxy)*0.1  # additinal 10% margins to make plot nicer
    ax.set_xlim([minx - x_5proc, maxx + x_5proc])
    ax.set_ylim([miny - y_5proc, maxy + y_5proc])
    # try to apply user defined plot-margins
    if ylim:
        miny = ylim[0]
        maxy = ylim[1]
        ax.set_ylim(ylim)
    if xlim:
        minx = xlim[0]
        maxx = xlim[1]
        ax.set_xlim(xlim)
    
    #draw axes
    if draw_axes:
        ax.axhline(0, color='black', linewidth=0.5)
        ax.axvline(0, color='black', linewidth=0.5)

    # now working with trendlines ...
    if trendlinemode:
        print( 'plotting trendlines...')
        # get colors...
        handles, labels = ax.get_legend_handles_labels()
        colors = list()
        for h in handles:
            colors.append(h.get_color())
        # trendline calculations...
        
        
        for i, X, Y, c in zip(xrange(len(x)), x, y, colors):
            
            # OVERWRITING STANDART DATA!!!
            # CAREFUKL HERE!
            df = df[np.isfinite(df[Y])]  # Select only rows that are not NaN in column Y
            

            print( '\t>>> {0}/{1}'.format(i+1, len(x)))
            # calc the trendline (it is simply a linear fitting)
            z = np.polyfit(df[X], df[Y], 1)
            p = np.poly1d(z)
            
            ideal = z[1] + (z[0] * df[X])
            r_sq = r_squared(df[Y], ideal)
            trendline_equation = 'y=%.3fx+(%.3f)' % (z[0], z[1])
            
            if trendlinemode == 1:
                ax.plot([minx, maxx], p([minx, maxx]),
                    trendline_kwargs['style'],
                    lw=trendline_kwargs['lw'],
                    color=c if trendline_kwargs['color'] is None else trendline_kwargs['color'],
                    label='Trendline\n{0}\nr^2={1:.3f}'.format(trendline_equation, r_sq))
            
            else:  # if <trendlinemode> is 2 or 3

                # now find out the deviation of the points... above (!!!) the trendline...
                def ideal(value, z):
                    return z[1] + (z[0] * float(value))
                
                deviation_from_trendline = list()
                deviation_from_trendline_index = list()
                
                for index, currentY in enumerate(df[Y]):
                    currentX = df.ix[index, X]
                    deviation_from_trendline_i = currentY - ideal(currentX, z)
                    if deviation_from_trendline_i > 0.:  #
                        deviation_from_trendline.append(deviation_from_trendline_i)
                        deviation_from_trendline_index.append(index)


                if trendlinemode == 2:  # trendline of n-points...
                    # plot those maximum lines....

                    # now find <N_DEVIATIONS> maximum deviations...
                    list_indexes      = np.argsort( np.array(deviation_from_trendline) )[-N_DEVIATIONS:]
                    dataframe_indexes = [deviation_from_trendline_index[ind] for ind in list_indexes]

                    ERRORS  = df.ix[dataframe_indexes, :]
                    # ERRORS => XERRORS = df.ix[dataframe_indexes, X]
                    # ERRORS => YERRORS = df.ix[dataframe_indexes, Y]

                    # VISUALIZE POINTS THAT ARE USED FOR CREATING BORDER LINE
                    #ERRORS.plot(x=X, y=Y, ax=ax, marker="x", markersize=16., color='red', style='.', markeredgecolor='black', markeredgewidth=0.2, legend=False)
                    
                    # calc the trendline (it is simply a linear fitting)
                    z = np.polyfit(ERRORS[X], ERRORS[Y], 1)
                    p = np.poly1d(z)
                    
                    trendline_equation1 = 'y=%.3fx+(%.3f)' % (z[0], z[1])
                    #ax.plot([minx, maxx], p([minx, maxx]), '-', lw=0.8, color=c, label='trendline of {1} maximum \ndeviations above mean trendline\n{0}'.format(trendline_equation1, N_DEVIATIONS))
                    ax.plot([minx, maxx], p([minx, maxx]), '-', lw=0.8, color=c)

                elif trendlinemode == 3:  # shifted trendlines
                    # now find one maximum deviation...
                    N_DEVIATIONS = 1  # create lines based on N_DEVIATIONS points
                    
                    list_indexes = np.argsort( np.array(deviation_from_trendline) )[-N_DEVIATIONS:]  # now find 5 maximum deviations...
                    dataframe_indexes = [deviation_from_trendline_index[ind] for ind in list_indexes]

                    ERRORS  = df.ix[dataframe_indexes, :]
                    XERRORS = df.ix[dataframe_indexes, X]
                    YERRORS = df.ix[dataframe_indexes, Y]

                    # VISUALIZE POINTS THAT ARE USED FOR CREATING BORDER LINE
                    #ERRORS.plot(x=X, y=Y, ax=ax, marker="x", markersize=16., color='red', style='.', markeredgecolor='black', markeredgewidth=0.2, legend=False)
                    
                    # lift trendline up....
                    #   determine dy at current x
                    y_trendline = z[0]*XERRORS.iat[0] + z[1]
                    y_deviation = YERRORS.iat[0]
                    dy = y_deviation - y_trendline
                    z = np.array([z[0], z[1]+dy])  # shifting trendline by dy
                    
                    p = np.poly1d(z)  # shifted trendline
                    trendline_equation = 'y=%.3fx+(%.3f)' % (z[0], z[1])

                    #ax.plot([minx, maxx], p([minx, maxx]), '-', lw=0.8, color=c, label='Shifted trendline\n{0}'.format(trendline_equation))
                    ax.plot([minx, maxx], p([minx, maxx]), '-', lw=0.8, color=c)

    if not _ax: figManager = plt.get_current_fig_manager()
    if not _ax: figManager.window.showMaximized()

    ax.legend()
    
    if not trendlinemode:
        divisor = 1
    elif trendlinemode == 2:
        divisor = 3
    elif trendlinemode in [1, 3]:
        divisor = 2
    
    # setting legend labels
    handles, labels = ax.get_legend_handles_labels()
    for i in xrange(len(labels)/divisor):
        labels[i] = legendlabels[i] if legendlabels[0] else y[i]





    ax.legend(handles, labels, fontsize=legend_fontsize, loc=legend_location)
    ax.xaxis.grid(True, which='both')
    ax.yaxis.grid(True, which='both')
    if xlabel: ax.set_xlabel(xlabel, fontsize=axeslabel_fontsize)
    if ylabel: ax.set_ylabel(ylabel, fontsize=axeslabel_fontsize)
    if title: ax.set_title(title, fontsize=title_fontsize)
    ax.tick_params(axis='both', labelsize=axesvalues_fontsize)


    if saveName and not _ax:
        fig.savefig(saveName, dpi=300, tight_layout=True)#, format='pdf')
        print( 'saving figure... :', saveName)
    if not _ax: plt.show()






















def plot_pandas_scatter_special1(df, x=[0], y=[1], saveName=None, xlabel=None, ylabel=None, title=None, trendlinemode=None, legendlabels=[None],
                                N_DEVIATIONS=10, xlim=None, ylim=None, HYDR_VALS=None, s=10, marker='o',
                                axeslabel_fontsize=10., title_fontsize=20., axesvalues_fontsize=10., annotation_fontsize=10., legend_fontsize=8.):
    """
        df              - pandas.DataFrame timeseries for original hydrographs
        x, y            - list with keys or indexes of X and Y data columns
        saveName        - None, or string with figure name to be saved
        title           - title for figure
        marker          - marker for plotting scatter field
        s               - size of the scatter points
        xlabel          - None, or string for labeling x-axes
        ylabel          - None, or string for labeling y-axes
        trendlinemode   - 1, 2, 3 or None:
                            1    - draw trendlines using all data points
                            2    - draw trendlines using only <N_DEVIATIONS> data points, that are most farlying (see code)
                            3    - draw trendlines using all data points, and shift them to the most-far-lying points
                            None - do not draw trendline

        N_DEVIATIONS    - (used only if trenlinemode=2); int, (i.e. N_DEVIATIONS=10) create trend-lines based on this number of points
        legendlabels    - List of legendnames or [None]. If default ([None]) - standart names are used
        ylim         - None, or list for y-limits [ymin, ymax] of the plot. (i.e. ylim=[0., 1.])
        xlim         - None, or list for x-limits [xmin, xmax] of the plot. (i.e. xlim=[-0.5, 0.5])
        HYDR_VALS    - dictionary with special hydrological values (see code below)
        
    """
    if len(x) != len(y):
        raise ValueError('Number of keys for X and Y dimension should be equal. Got: {0} for X and {1} for y'.format(len(x), len(y)))
    
    print( "plotting scatter data...", trendlinemode)
    #fig = plt.figure(figsize=(11.69, 8.27))
    fig = plt.figure(figsize=(6, 4), tight_layout=True)
    
    ax = fig.add_subplot(111)
    for xi, yi in zip(x, y):
        df.plot(x=xi, y=yi, ax=ax, marker=marker, markersize=s, style='.', markeredgecolor='black', markeredgewidth=0.2, legend=False)
        #df.plot.scatter(x=xi, y=yi, ax=ax, marker=marker, s=s, legend=False)




    if xlim:
        minx = xlim[0]
        maxx = xlim[1]
    else:
        minx, maxx = None, None
    
    if ylim:
        miny = ylim[0]
        maxy = ylim[1]
    else:
        miny, maxy = None, None


    if minx is None:
        minx = min([df[X].min() for X in x])
    if maxx is None:
        maxx = max([df[X].max() for X in x])
    if miny is None:
        miny = min([df[Y].min() for Y in y])
    if maxy is None:
        maxy = max([df[Y].max() for Y in y])
    x_5proc, y_5proc = abs(minx - maxx)*0.1, abs(miny - maxy)*0.1  # additinal 10% margins to make plot nicer
    #ax.set_ylim([miny - y_5proc, maxy + y_5proc])
    #ax.set_xlim([minx - x_5proc, maxx + x_5proc])
    ax.set_ylim([miny, maxy])
    ax.set_xlim([minx, maxx])


    if trendlinemode in [1, 2, 3, 'Normal', 'Shifted']:
        print( 'plotting trendlines...')
        # get colors...
        handles, labels = ax.get_legend_handles_labels()
        colors = list()
        for h in handles:
            colors.append(h.get_color())

        for i, X, Y, c in zip(xrange(len(x)), x, y, colors):
            print( '\t>>> {0}/{1}'.format(i+1, len(x)))
            

            # OVERWRITING STANDART DATA!!!
            # CAREFUKL HERE!
            df = df[np.isfinite(df[Y])]  # Select only rows that are not NaN in column Y
            

            # calc the trendline (it is simply a linear fitting)
            z = np.polyfit(df[X], df[Y], 1)
            p = np.poly1d(z)
            
            ideal = z[1] + (z[0] * df[X])

            if trendlinemode in [1, 'Normal']:
                r_sq = r_squared(df[Y], ideal)
                trendline_equation = 'y=%.3fx+(%.3f)' % (z[0], z[1])
                ax.plot([minx, maxx], p([minx, maxx]), '--', lw=0.8, color=c, label='Trendline\n{0}\nr^2={1:.3f}'.format(trendline_equation, r_sq))
            
            elif trendlinemode in [2, 3, 'Shifted']:
                # now find out the maximum deviating point... above the trendline...
                def ideal(value, z):
                    return z[1] + (z[0] * float(value))
                
                # find deviation from ideal trendline of all points for given column_name X
                # note that we are interested only in positive (>0) deviations
                deviation_from_trendline = list()
                deviation_from_trendline_index = list()
                
                for index, currentY in enumerate(df[Y]):
                    currentX = df[X].iloc[index]
                    deviation_from_trendline_i = currentY - ideal(currentX, z)
                    if deviation_from_trendline_i > 0.:  #
                        deviation_from_trendline.append(deviation_from_trendline_i)
                        deviation_from_trendline_index.append(index)
                #print ('Number of deviation that are (>0):', len(deviation_from_trendline))

                if trendlinemode in [3, 'Shifted']:
                    # overwriting N_DEVIATIONS to one single point
                    N_DEVIATIONS = 1  # create lines based on N_DEVIATIONS points
                    # now find 1 maximum deviation...

                list_indexes = np.argsort( np.array(deviation_from_trendline) )[-N_DEVIATIONS::]  # now find 5 maximum deviations...
                dataframe_indexes = [deviation_from_trendline_index[ind] for ind in list_indexes]

                ERRORS  = df.iloc[dataframe_indexes]
                XERRORS = df[X].iloc[dataframe_indexes]
                YERRORS = df[Y].iloc[dataframe_indexes]
                # VISUALIZE POINTS THAT ARE USED FOR CREATING BORDER LINE
                #ERRORS.plot(x=X, y=Y, ax=ax, marker="x", markersize=16., color='red', style='.', markeredgecolor='black', markeredgewidth=0.2, legend=False)
                
                # lift trendline up....
                #   determine dy at current x
                y_trendline = z[0]*XERRORS.iat[0] + z[1]
                y_deviation = YERRORS.iat[0]
                dy = y_deviation - y_trendline
                z = np.array([z[0], z[1]+dy])  # shifting trendline by dy
                
                p = np.poly1d(z)  # shifted trendline
                trendline_equation = 'y=%.3fx+(%.3f)' % (z[0], z[1])
                ax.plot([minx, maxx], p([minx, maxx]), '--', lw=0.8, color=c, label='Shifted Trendline\n{0}'.format(trendline_equation))

            
    if HYDR_VALS and trendlinemode:
        for key, val in HYDR_VALS.iteritems():
            overhead = z[0]*val + z[1]
            ax.plot([val, val], [miny, overhead], '--', color='gray')
            ax.annotate('{0} = {1:.2f}'.format(key, val), xy=(val, miny), xytext=(-7, 10), textcoords='offset points', va='bottom', ha='center',
                        size=annotation_fontsize, rotation=90.)
            ax.annotate('{0:.2f}'.format(overhead), xy=(val, overhead), xytext=(10, 50),
                        textcoords='offset points', va='bottom', arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5', color='k'), size=annotation_fontsize)
               
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()

    ax.legend()
    
    if not trendlinemode:
        divisor = 1
    elif trendlinemode in [2]:
        divisor = 3
    else:
        divisor = 2
    
    # setting legend labels
    handles, labels = ax.get_legend_handles_labels()
    for i in xrange(len(labels)/divisor):
        labels[i] = legendlabels[i] if legendlabels[0] else y[i]

    ax.legend(handles, labels, fontsize=legend_fontsize)

    ax.xaxis.grid(True, which='both')
    ax.yaxis.grid(True, which='both')
    if xlabel: ax.set_xlabel(xlabel, fontsize=axeslabel_fontsize)
    if ylabel: ax.set_ylabel(ylabel, fontsize=axeslabel_fontsize)
    if title: ax.set_title(title, fontsize=title_fontsize)
    ax.tick_params(axis='both', labelsize=axesvalues_fontsize)
    
    if saveName:
        fig.savefig(saveName, dpi=300, tight_layout=True, format='pdf')
        print( 'saving figure... :', saveName)
    fig.show()






















def plot_mean_waterlevel(df, df_names, legend_names, saveName=None, ax=None):
    """
        df           - PandasDataFrame with time-averaged hydrographs
        df_names     - list with column names
        legend_names - list with strings
        ax           - already created axes.... if not - creates new figure
    """

    if not ax:
        fig = plt.figure(tight_layout=True)
        
        ax = fig.add_subplot(111)
        for name in df_names:
            df[name].plot(ax=ax, legend=True, title="Farge: Averaged water-level after Serfes(1991)")

        handles, labels = ax.get_legend_handles_labels()
        for i, l_name in enumerate(legend_names):
            labels[i] = l_name
        ax.legend(handles, labels)

        ax.grid(True, which='major')
        ax.set_ylabel("m AMSL")
        ax.set_xlabel("Datetime")
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()

        if saveName:
            fig.savefig(saveName, dpi=300, tight_layout=True)#, format='pdf')
            print( 'saving figure... :', saveName)
        plt.show()
    else:
        for name in df_names:
            df[name].plot(ax=ax, legend=True, title="Farge: Averaged water-level after Serfes(1991)")

        handles, labels = ax.get_legend_handles_labels()
        for i, l_name in enumerate(legend_names):
            labels[i] = l_name
        ax.legend(handles, labels)

        ax.grid(True, which='major')
        ax.set_ylabel("m AMSL")
        ax.set_xlabel("Datetime")





















def calculate_mean_std(signal):
    mean = np.mean(signal)
    std = np.std(signal)
    return mean, std



def plot_statistical_analysis(data,
            bins=10,
            hist_type=0,
            plot_title='Original signal',
            data_units='',
            axeslabel_fontsize=15., title_fontsize=20., axesvalues_fontsize=15., annotation_fontsize=15., legend_fontsize=15.,
            plot_normDist=True):
    '''
        Plot a distribution analysis of an array. Function produces a figure with 3 subplots:
            1) The line graph of the original array
            2) Histogram of the array
            3) Cummulative histogram of the array
    
    Args:
    -----
        data (np.ndarray, pd.DataFrame, pd.Series):
            Original signal, data to be investigated. If of type 'DataFrame'
            will use the first column

        bins (int):
            number of bins for the histogram

        hist_type (int or str):
            switch to select the histogram type:
            0, 'Frequency'          - frequency hist (y-values are the number of samples in a bin)
            1, 'Relative Frequency' - relative frequency hist (y-values are the % of samples in a bin)
            2, 'Normalized'         - normalized hist (y-values are the density (area of the bars equals to 1))

        plot_title (str):
            title of the plot

        data_units (str):
            units of the signal (will be displayed on the plots)

        plot_normDist (bool):
            flag to plot the normal distribution with a given mean and std. Mean and std are determened
            from the input data-set
    '''
    
    if hist_type in [0, 'Frequency']:
        y_label = 'Frequency'
        label2 = 'Frequency Histogram'
        label3 = 'Cumulative Frequency Histogram'
    
    elif hist_type in [1, 'Relative Frequency']:
        y_label = 'Relative Frequency'
        label2 = 'Relative Frequency Histogram'
        label3 = 'Cumulative Rel.Frequency Histogram'

    elif hist_type in [2, 'Normalized']:
        y_label = 'Density'
        label2 = 'Density Histogram'
        label3 = 'Cumulative Density Histogram'


    fig = plt.figure(tight_layout=True)

    ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=2)
    ax2 = plt.subplot2grid((2, 2), (1, 0))
    ax3 = plt.subplot2grid((2, 2), (1, 1))

    # we can pass to data not only Array, but also pandas DataFrame or Timeseries
    # where indexes are DatetimeIndex. Lets figure it out...
    # The thing is, for calculations we need raw arrays without datetime indexes
    raw_data = data

    ax1.set_xlabel('Number of data-points', fontsize=axeslabel_fontsize)

    if isinstance(data, (pd.Series, pd.DataFrame)):
        if type(data.index) is pd.tseries.index.DatetimeIndex:
            #print( 'pd.tseries.index.DatetimeIndex detected')
            raw_data = data.iloc[:, 0].values  # select all time-entries for first column 
                                               # (note we have ONLY one column in raw_data)
            ax1.set_xlabel('')
            
    

    mu, std = calculate_mean_std(raw_data)

    
    # -------------
    # subplot 1
    # -------------
    if isinstance(data, (pd.Series, pd.DataFrame)):
        data.plot(ax=ax1, lw=1.)
    else:
        ax1.plot(data, label='Signal')



    # since we have plotted timeseries, we can reset pointer to use raw data (array) instead of timeseries
    data = raw_data

    ax1.set_title(plot_title, fontsize=title_fontsize)
    ax1.set_ylabel(data_units, fontsize=axeslabel_fontsize)
    ax1.tick_params(axis='both', labelsize=axesvalues_fontsize)
    
    ax1.legend(loc='upper right')
    handles, labels = ax1.get_legend_handles_labels()
    labels[0] = labels[0]+'\n'+(r'$\mu$'+' = {0:.2f}\n'+r'$\sigma$'+' = {1:.3f}').format(mu, std)
    ax1.legend(handles, labels, fontsize=legend_fontsize)
    
    # -------------
    # subplot 2
    # -------------

    # the histogram of the data
    #n, bins, patches = ax2.hist(data, bins, normed=True, facecolor='#75bbfd', alpha=0.5)
    ## add a 'best fit' line
    #y = mlab.normpdf( bins, mu, std)
    #l = ax2.plot(bins, y, 'r--', linewidth=1)

    #sns.distplot(data, bins=bins, norm_hist=False, ax=ax2, kde=False)
    if hist_type in [0, 'Frequency']:
        sns.distplot(data, bins=bins, norm_hist=False, kde=False, ax=ax2)
    
    elif hist_type in [1, 'Relative Frequency']:
        sns.distplot(data, bins=bins, norm_hist=False, kde=False, ax=ax2, hist_kws={'weights': np.ones_like(data)/float(data.size)})

    elif hist_type in [2, 'Normalized']:
        sns.distplot(data, bins=bins, ax=ax2, kde_kws={"label": "KDE"})
        
        #if plot_normDist:  #additionally plot normal distribution
        #    norm_dist_y = norm.pdf(data, loc=mu, scale=std)
        #    ax2.plot(data, norm_dist_y, 'r', label='Norm Dist', lw=1.)

    ax2.axvline(mu, ymax=1., color='k', linestyle='--', lw=1, label=('Mean: '+r'$\mu$'+' = {0:.2f}').format(mu))
    


    ax2.set_title(label2, fontsize=title_fontsize)
    ax2.set_xlabel(data_units, fontsize=axeslabel_fontsize)
    ax2.set_ylabel(y_label, fontsize=axeslabel_fontsize)
    ax2.tick_params(axis='both', labelsize=axesvalues_fontsize)


    handles, labels = ax2.get_legend_handles_labels()
    ax2.legend(handles, labels, fontsize=legend_fontsize)


    # -------------
    # subplot 3
    # -------------
    if hist_type in [0, 'Frequency']:
        sns.distplot(data, bins=bins, kde=False, ax=ax3, hist_kws={'cumulative': True})
        ax3.set_ylim([0, data.size])
    
    elif hist_type in [1, 'Relative Frequency']:
        sns.distplot(data, bins=bins, kde=False, ax=ax3, hist_kws={'cumulative': True, 'weights': np.ones_like(data)/float(data.size)})
        ax3.set_ylim([0, 1])

    elif hist_type in [2, 'Normalized']:
        sns.distplot(data, bins=bins, ax=ax3, kde_kws={"label": "KDE", 'cumulative': True}, hist_kws={'cumulative': True})
        ax3.set_ylim([0, 1])

    
    ax3.set_title(label3, fontsize=title_fontsize)
    ax3.set_ylabel(y_label, fontsize=axeslabel_fontsize)
    ax3.set_xlabel(data_units, fontsize=axeslabel_fontsize)
    ax3.tick_params(axis='both', labelsize=axesvalues_fontsize)
    handles, labels = ax3.get_legend_handles_labels()
    ax3.legend(handles, labels, fontsize=legend_fontsize)
    
    
    plt.get_current_fig_manager().window.showMaximized()
    fig.show()










def plot_direction_rose(df, COLNAME=None, N=18, RELATIVE_HIST=True, PLOT_LINE_SUBPLOT=False,
    R_FONTSIZE='x-small', THETA_DIRECTION=-1, THETA_ZERO_LOCATION='N',
    THETA_GRIDS_VALUES=[0, 45, 90, 135, 180, 225, 270, 315, 360],
    THETA_GRIDS_LABELS=['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'],
    R_LABEL_POS=90, BOTTOM=0):
    '''
        Plot a circular histogram of the direction data (data in range 0 to 360 degrees).

        Args:
        -----

        df (pd.DataFrame):
            pandas dataframe with data

        COLNAME (Optional[None or str]):
            name of the data-column in `df`. If `None`, will use the
            first column of the dataframe.

        N (Optional[int]):
            number of bins. If N=18, then one bin is 20 degrees

        RELATIVE_HIST (Optional[bool]):
            flag to print relative histogram values. If `False` will
            plot real number of occurences in histogram-bins

        PLOT_LINE_SUBPLOT (Optional[bool]):
            flag to plot original data-signal additionally

        R_FONTSIZE (Optional [str]):
            font size of the radial ticks

        THETA_DIRECTION (Optional [1 or -1]):
            direction of the positive theta. If `1` -- counterclockwise.
            If `-1` -- clockwise

        THETA_ZERO_LOCATION (Optional [str]):
            Sets the location of theta's zero.
            May be one of 'N', 'NW', 'W', 'SW', 'S', 'SE', 'E', or 'NE'.

        THETA_GRIDS_VALUES (Optional[list[float/int]]):
            value to draw angular grid

        THETA_GRIDS_LABELS (Optional[list[float/int/str] or None]):
            corresponding labels to the values `THETA_GRIDS_VALUES`. Either
            list of numbers/strings or `None`. If `None` -- will use values
            directly from THETA_GRIDS_VALUES.

        R_LABEL_POS (Optional[int in range [0:360]]):
            rotation angle of the radial axis values

        BOTTOM (OPTIONAL[int]):
            - only if RELATIVE_HIST=True.
            number of units (current units of circular histogram), to skip, before
            drawing the histogram, e.g. if BOTTOM=0 -- draw from the circle center;
            if BOTTOM=5 -- skip 5 units and begin drawing from there.
    '''

    data = df[COLNAME].values  # extract raw numpy array



    bins = np.linspace(0.0, 2 * np.pi, N+1, endpoint=True)/2./np.pi*360.  # bins borders in degrees, including the 360 degree border.

    if RELATIVE_HIST:
        hist, bin_edges = np.histogram(data, bins=bins, weights=np.zeros_like(data) + 1. / float(data.size))
        hist *= 100
    else:
        hist, bin_edges = np.histogram(data, bins=bins)

    x = bin_edges[:-1]*2.*np.pi/360.  # x-array -- bins borders in radians, without the last, 360 degrees, border


    fig = plt.figure()
    if PLOT_LINE_SUBPLOT:
        subplot_pos = 211
    else:
        subplot_pos = 111
    ax = fig.add_subplot(subplot_pos, projection='polar')


    width = (2*np.pi) / float(N)  # width of the bin in degrees
    bars = ax.bar(x , hist, width=width, bottom=BOTTOM)

    # convert usual angle plot to the bearing plot...
    ax.set_theta_direction(THETA_DIRECTION) 
    ax.set_theta_zero_location(THETA_ZERO_LOCATION)
    ax.set_thetagrids(THETA_GRIDS_VALUES, labels=THETA_GRIDS_LABELS, frac=1.2, fmt=None)
    ax.set_rlabel_position(R_LABEL_POS)

    if RELATIVE_HIST:
        # determine the radial ticks
        v_max = hist.max()
        if v_max >= 30.:
            # one tick every ten %
            max_val_roundeup = int(math.ceil(v_max / 10.0)) * 10
            r_ticks = np.arange(0, max_val_roundeup+10, 10)
        elif 30 > v_max >= 10:
            # one tick every five %
            max_val_roundeup = int(math.ceil(v_max / 5.0)) * 5
            r_ticks = np.arange(0, max_val_roundeup+5, 5)
        elif 10 > v_max:
            # one tick every single %
            max_val_roundeup = int(math.ceil(v_max / 5.0)) * 5
            r_ticks = np.arange(0, max_val_roundeup+1, 1)
        
        # define labels for ticks
        if BOTTOM > 0:
            r_ticks = r_ticks+BOTTOM  # we get rid of the first (r_ticks[0]=0) item, since values on the radial axis are always >=0
            r_labels = ['{0}%'.format(val-BOTTOM) for val in r_ticks ]
        elif BOTTOM == 0:
            r_ticks = r_ticks[1:]  # we get rid of the first (r_ticks[0]=0) item, since values on the radial axis are always >=0
            r_labels = ['{0}%'.format(val) for val in r_ticks ]
        
        # now apply the defined ticks and labels
        ax.set_rgrids(r_ticks, labels=r_labels, angle=R_LABEL_POS, size=R_FONTSIZE)

    # Use custom colors and opacity
    for r, bar in zip(hist, bars):
        color = 1./hist.max()*r
        bar.set_facecolor(plt.cm.Blues(color))
        bar.set_alpha(0.8)

    # ------------------------
    # Second subplot
    # ------------------------
    if PLOT_LINE_SUBPLOT:
        ax2 = fig.add_subplot(212)
        df[COLNAME].plot(ax=ax2, label='Data')
        ax2.set_ylabel('Bearing N [degrees]')
        ax2.set_xlabel('Data Points')
        plt.legend()
    # ----------------------------------------------
    # ----------------------------------------------
    # ----------------------------------------------
    fig.show()

if __name__ == '__main__':
    # Example 1
    plot_statistical_analysis(np.random.uniform(-1, 1, size=5000),
            bins=100,
            data_units='',
            hist_type=1)
    
    # Example 2
    df = pd.DataFrame(data=240. + 50 * (np.random.randn(1000)-0.5), columns=['bearing'])  # sample data
    plot_direction_rose(df, 'bearing', RELATIVE_HIST=True, BOTTOM=5)
    plt.show()

    # Example 3
