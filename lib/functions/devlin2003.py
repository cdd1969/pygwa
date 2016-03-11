#!/usr/bin python
# -*- coding: utf-8 -*-
''' This module is a python warapper to method of DEVLIN 2003 of
estimating best fit hydraulic gradients using head data from multiple wells

see:
    J.F. Devlin 2003 "A Spreadsheet method of estimating best-fit hydraulic
    gradients uding head data from multiple wells"

    available at: www.geo.ku.edu

'''
from __future__ import division
import numpy as np
from math import sqrt
from math import atan2, pi


def devlin2003(X):
    ''' Original equation of Devlin 2003 to get gradient and direction from equation
            [X] * [A] = [D]
        which has solution
            [A] = [[X].T * [X]]**(-1) * [X].T * [D]
    Args:
    ----
        X (np.matrix of (Nx3) shape):
            (Nx3) data matrix, where N is the number of wells.
            1st column: well x-coordinate in [m]
            2nd column: well y-coordinate in [m]
            3nd column: well water table elevation [m]

        D (None|np.matrix of (Nx1) shape):
            matrix with an arbitrary non-zero value (see Devlin).
            If None - generated automatically filled with 1 values
    
    Return:
    -------
        a, b, c (float):
            tuple of matrix solution
        gradient (float):
            gradient magnitude
        angle (float):
            gradient direction, angle in degrees with respect to 0-X axis (east) counter click wise positive
    '''
    # perform datatype check
    if not isinstance(X, np.matrix):
        raise TypeError('Input argument `X` is of type {0}. Must be of type `np.matrix`'.format(type(X)))
    # perform X shape check
    if X.shape[1] != 3 and X.ndim != 2:
        raise ValueError('Matrix X is of invalid shape {0}. Must be of shape (Nx3)'.format(X.shape))

    N = X.shape[0]  # number of wells

    # generate matrix D of shape (Nx1) filled with ones
    D = np.matrix(np.ones(N)).T

    A = (X.T * X).I * X.T * D

    # coefficients
    a = float(A[0])
    b = float(A[1])
    c = float(A[2])

    gradient = sqrt(a**2 + b**2)/c
    angle = atan2(b, a)*180./pi  # angle off x-axis (east) in degrees, counter clock-wise is positive direction.

    return ((a, b, c), gradient, angle)


def angle2bearing(angle, origin='N'):
    ''' Convert angle to bearing
        see http://www.mathwords.com/b/bearing.htm
    Args:
    -----
        angle (float) [degrees]:
            angle with respect to x-axis (east), counter-clockwise positive (angle may be in range -360. to 360.)
        origin ('N'|'S'):
            origin of bearing (south/north)
            'N' >>> clockwise from N
            'S' >>> counter-clockwise from S
    '''
    if angle < -360. or angle > 360.:
        raise ValueError('Invalid angle {0}. Must be in range [-360.:360.]').format(angle)
    
    if origin == 'N':
        b = (360. - (angle - 90.)) % 360.
    elif origin == 'S':
        b = (360. + (angle + 90.)) % 360.
    else:
        raise NotImplementedError()
    return (b, origin)


def devlin2003pandas(df, x_name, y_name, z_name):
    '''
    Args:
    ----
        df (pd.DataFrame):
            dataset
        x_name, y_name, z_name (str):
            names of the columns with x, y, z coordinates
            respectively (z - ground-water elevation)
    '''
    x = df[x_name].values
    y = df[y_name].values
    z = df[z_name].values
    _, gradient, angle = devlin2003(np.matrix([x, y, z]).T)
    return (gradient, angle2bearing(angle, origin='N')[0])




if __name__ == '__main__':
    x = np.arange(5) + 1
    y = np.arange(5) + 2
    z = np.zeros(5) + np.random.random()

    X = np.matrix([x, y, z]).T
    print devlin2003(X)

    print '-'*20
    X_devlin2003_example1 = np.matrix('''
        30.00,   40.00,  99.857;
        90.00,   70.00,  99.698;
        70.00,   70.00,  99.702;
        50.00,   90.00,  99.607;
        60.00,   10.00,  100.008;
        31.72,   73.28,  99.68;
        60.00,   95.00,  99.566''')
    print devlin2003(X_devlin2003_example1)

    print 'Correct answer: gradient=0.0051347, angle=89.496 degrees'

    print '-'*20
    X_devlin2003_example2 = np.matrix('''
        0.00,   0.00,  26.20;
        150.,   0.00,  26.07;
        0.00,   165.,  26.26''')
    print devlin2003(X_devlin2003_example2)
    print 'Correct answer: gradient=0.00097, angle=23 degrees clockwise'
