#!/usr/bin python
# -*- coding: utf-8 -*-
'''
    This files contains solution to the one-dimensional tidal groundwater flow in a coastal
    unconfined aquifer. The solution is taken from the publication of Song et al 2007

        "A new analytical solution of tidal water table fluctuations in a coastal unconfined aquifer"

        http://dx.doi.org/10.1016/j.jhydrol.2007.04.015

'''


from __future__ import division
from math import exp
from math import sqrt
import numpy as np


def h(order=3, t=[], A=0., omega=0., phi=0., D=0., x=0., n_e=0.35, K=10e-4):
    ''' Calculate groundwater amplitude `h(x, t)` based on equation of Song et al 2007

            Following boundary conditions are introduced:
                
                1) h(x=0, t=0) = A
                2) h(x=inf) = 0
    Args:
    -----
        order (int (1,2,3)):
            the order of the solution. Can be 1, 2 or 3. The 3rd order solution gives
            the most accurate results
        x (float) [m]:
            Distance from shoreline/river in cross-shore direction
        t (float|np.array(float)) [s]:
            Time elapsed from reference point in [s]. Can be numpy array with floats
        D (float) [m]:
            Mean aquifer thickness
        n_e (float) [-]:
            Effective porosity of the aquifer
        K (float) [m/s]:
            Hydraulic conductivity of the aquifer
        
        A (float) [m]:
            Amplitude of a tidal oscillation
        omega (float) [rad/s]:
            Angular velocity
        phi (float) [rad]:
            Initial phase shift

    Return:
    ------
        h (float|np.array(float)) [m]:
            groundwater head at distance `x` from shoreline at time `t` with respect to the horizontal, impermeable aquifer base
    '''
    alpha = A / D  # perturbation parameter of Parlange et al. 1984
    
    D_inf = D * sqrt(1. + alpha**2 / 2.)  # maximum time-averaged water table height in the unconfined aquifer (eq.9)

    beta = A / D_inf  # perturbation parameter of Song et al. 2007 (eq.9)
    L = sqrt(D_inf * K / (n_e * omega))   # decay length scale of the water tale fluctuation (eq.10c)
    
    # non-dimensional variables
    X = x / L           # (eq.10a)
    T = t / omega       # (eq.10b)
    #H = h / D_inf       # (eq.10c)

    Lambda = 1./sqrt(2.)  # dimensionless wave number for the primary signal (eq.21)

    # --------------------------------------------------------------------------------------------
    # since my method includes many tidal harmonics with different amplitude and phase-shift it
    # is requred to get the solution, when the seaward boundary is expressed with equation
    #       h(x,t) = D + A * cos(omega*t + phi)
    # The solution of Song et al. 2007 exploits the simplified form
    #       h(x,t) = D + A * cos(omega*t)
    #
    # When eqs. 21, 22 and 24 are calculated with term `T = t*omega +phi` istead of `T = t*omega`,
    # the coefficients stays the same and doenot affect differentials. THerefore we are allowed
    # to substitute the `original T` with our version (which has the `phi`-term added)

    T = T + phi
    # --------------------------------------------------------------------------------------------
    
    H1 = exp(-Lambda * X) * np.cos(T - Lambda*X)  # (eq.21)
        
    if order in [2, 3]:  #if order == 2 or order == 3:

        # eq.22
        H2 = 1./2. * ( exp(- sqrt(2.)*Lambda*X) * np.cos(2.*T - sqrt(2.)*Lambda*X) -
            exp(- 2.*Lambda*X) * np.cos(2. * (T - Lambda*X))) - 1./4. * exp(-2.*Lambda*X)  # (eq.22)

        if order == 3:
            gamma1 = -sqrt(3.)*Lambda*X
            gamma2 = -(sqrt(2.)+1)*Lambda*X


            # eq. 24
            H3 = (
                (3.*sqrt(2.)-2)/16. * exp(gamma1)*np.cos(3.*T+gamma1) - (3.*sqrt(2.)+4)/16. * exp(gamma2) *
                np.cos(3.*T+gamma2) + sqrt(2.)/16.*exp(gamma2) *
                np.sin(T - (sqrt(2.)-1)*Lambda*X) - 1./4.*exp(gamma2) *
                np.cos(T - (sqrt(2.)-1)*Lambda*X) + 3./8.*exp(sqrt(3.)*gamma1) *
                np.cos(3.*(T - Lambda*X)) + 1./20.*(11*exp(sqrt(3.)*gamma1) - 6.*exp(-Lambda*X)) *
                np.cos(T - Lambda*X) - 1./80.*(8.*exp(sqrt(3.)*gamma1) + (5.*sqrt(2.)-8.)*exp(-Lambda*X) ) *
                np.sin(T - Lambda*X)
                    )  # eq.24
    
    # finally combine parts based on the Equation 14
    if order == 1:
        H = 1 + beta * H1  # (eq. 14)
    elif order == 2:
        H = 1 + beta * H1 + beta**2 * H2  # (eq. 14)
    elif order == 3:
        H = 1 + beta * H1 + beta**2 * H2 + beta**3 * H3  # (eq. 14)
    else:
        raise NotImplementedError('invalid `order`={0}'.format(order))

    h = H * D_inf  # eq. 10c
    return h
