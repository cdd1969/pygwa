# Access inputs as args['input_name']
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time


def createInterpolationRanges(df, columnName, interpolateMargin=100, log=False):
    u""" Function checks data for missing values. From the missing-data indices
        it will try to create so called 'missing data index regions' based on
        *interpolateMargin* parameter. This index-regions will be used further
        for faster interpolation.

        INPUT:
        ------------------------------------------------------------------------
         *df*                - pandas.DataFrame, our data
         *columnName*        - str, column name in passed DataFrame
         *interpolateMargin* - int, number of data-points to consider left and
                               right from current NaN value.

        OUTPUT:
        ------------------------------------------------------------------------
         *regions*           - list of 2-length-lists, indices of the missing
                               data regions (i.e. [[1, 12], [45, 50], [60, 100]]
                               OR None (if no missing data in columnName)
        ------------------------------------------------------------------------
         Example 1:
            >>> s = [1, 2, 3, np.nan, 5, 4, 3, 2, 1]
            >>> df = pd.DataFrame(data=s, columns=['col1'])
            >>> print createInterpolationRanges(df,'col1',interpolateMargin=2)
            [[1, 5]]

            This for further interpolation we will consider not full array *s*
            but only its part *s'* = [2, 3, np.nan, 5, 4], where [[1, 5]]
            corresponds to the indices of [2] and [4] in the *s'*

         Example 2:
            >>> s = [1, 2, 3, np.nan, 5, 4, 3, np.nan, 1]
            >>> df = pd.DataFrame(data=s, columns=['col1'])
            >>> print createInterpolationRanges(df,'col1',interpolateMargin=2)
            [[1, 5], [5, 8]]

            Here we have two regions. Note that the "8" value in the second
            region is the maximum index of the array *s*
         
         Example 3:
            >>> s = [np.nan, 5, 6, 7, 8, 7, 6, 5, 4, 3, np.nan, 1, np.nan, -1, np.nan, -1, 0, 1, 2]
            >>> df = pd.DataFrame(data=s, columns=['col1'])
            >>> print createInterpolationRanges(df, 'col1', interpolateMargin = 3)
            [[0, 3], [7, 17]]

            Here we have two regions and the second one is joined from multiple
            NaN occurences
    """
    N = len(df.index)
    validN = df[columnName].count()
    nanN = (N-validN)
    if log: print 'createInterpolationRanges(): Column <{0}>: entries - {1}, NaNs - {2}'.format(columnName, N, nanN)
    
    if nanN > 0:
        # indeces of NaN values
        nanIndeces = np.where(df[columnName].isnull())[0]
        #print nanIndeces

        # create regions...
        regions = list()
        region = list()

        for i, v in enumerate(nanIndeces):
            if i == 0:  # treat first element
                region.append(v)
                continue
            elif i == len(nanIndeces)-1 and len(region) == 1:  # treat last element
                region.append(nanIndeces[i])
                regions.append(region)
                continue
            if v - nanIndeces[i-1] > interpolateMargin:  # distance is too big, save previous region, start new region
                region.append(nanIndeces[i-1])
                regions.append(region)
                region = list()
                region.append(v)

        # now add and substract interpolation margins:
        iMin = 0
        iMax = N-1

        for r in regions:
            #print r
            r[0] = max(iMin, r[0]-interpolateMargin)
            r[1] = min(iMax, r[1]+interpolateMargin)

        #for r in regions:
        #    print r
        return regions
    else:  # no NaN values detected. Interpolation is not needed. Return None
        if log: print 'createInterpolationRanges(): Column *{0}* has no missing data. Nothing to interpolate. Aborting... '.format(columnName)
        return None


def applyInterpolationBasedOnRanges(df, columnName, ranges, suffix='_interpolated', **kwargs):
    u""" Function interpolates data within given *ranges* (*ranges* should be
         generated with *createInterpolationRanges()*)


        INPUT:
        ------------------------------------------------------------------------------
         *df*                - pandas.DataFrame, our data
         *columnName*        - str, column name in passed DataFrame
         *ranges*            - list 2D, kist of indix regions (*ranges* should
                               be generated with *createInterpolationRanges()*)
         *suffix*            - str, *suffix* will be appended to the *columnName*
                               to create new data-column in *df*
         ***kwargs*          - are passed to pandas function *DataFrame.interpolate()*

        OUTPUT:
        ------------------------------------------------------------------------------
         Note: There is no output, because function MODIFIES passed dataframe.
         The result will be appended there.
        ------------------------------------------------------------------------------

    """
    if ranges is None:  # nothing to interpolate
        return
    columnNameNew = columnName+suffix
    columnNameBak = columnName+suffix+'_bak'
    df[columnNameNew] = df[columnName]
    df[columnNameBak] = df[columnName]

    for r in ranges:
        df[columnNameBak] = df[columnName][r[0]:r[1]].interpolate(**kwargs)

    # now finally copy only those values that were missing. This can be useful since we are not sure
    # if interpolation will work perfectly
    for i in np.where(df[columnName].isnull())[0]:
        df[columnNameNew][i] = df[columnNameBak][i]

    del df[columnNameBak]







if __name__ == '__main__':
    # define X, Y
    x = np.arange(0, 100, 0.1)
    y = np.sin(x)

    # set some missing data
    y[0] = np.nan
    y[38] = np.nan
    y[40:60] = np.nan
    y[70:75] = np.nan
    y[400:450] = np.nan
    y[453] = np.nan
    y[457] = np.nan
    y[459] = np.nan
    y[466] = np.nan
    y[800:825] = np.nan
    y[990:992] = np.nan

    #create Pandas DataFrame
    df = pd.DataFrame(data=y, columns=['one'])

    # column names
    cn = 'one'
    cni = cn+'_interpolated'

    # define number of points left and right from NaN value to consider for interpolation
    interpolateMargin = 100
    # find NaN regions - to increase performance
    Regions = createInterpolationRanges(df, cn, interpolateMargin=interpolateMargin)
    print Regions
    # apply interpolation to NaN regions
    applyInterpolationBasedOnRanges(df, cn, Regions, suffix='_interpolated', method='polynomial', order=15)
    
    # check new column if it has NaN or not (if not - will be printed)
    createInterpolationRanges(df, cni, interpolateMargin=interpolateMargin)

    #plot
    ax = plt.subplot(211)

    df[cn].plot(ax=ax, marker='x', color='b')

    criterion = df.index.isin(np.where(df[cn].isnull())[0])
    x = df[criterion].index
    y = df[cni][criterion].values
    plt.scatter(x=x, y=y, marker='o', color='r', label='interpolated', s=100)

    plt.legend(loc='best')
    plt.ylim([-2, 2])



    ax2 = plt.subplot(212)
    df[cni].plot(ax=ax2, marker='x', color='g')
    plt.ylim([-2, 2])
    plt.legend(loc='best')

    plt.show()
