#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import division
from math import pi
from math import sqrt
from math import log
from math import exp
from math import sin
from math import cos
import numpy as np
from numpy import arctan


def diffusivity_from_tidal_efficiency(E, x0, t0):
    ''' Calculate Diffusivity `D` (ratio of Transmissivity `T` to Storage `S`) based on
    equation of Ferris 1951 for a groundwater head in a tidal influenced aquifer.
    Calculations are done based on Tidal Efficiency (amplitude dumping). Input para-
    meters represent properties of an observation well (E, x0) and of the governing
    tide (t0).

        Ferris 1951 equation:

            h(x,t) = h0 * exp(-x*(pi/t0*S/T)**0.5) * sin(2*pi*t/t0 - x*(pi/t0*S/T)**0.5)

        From there:
            (eq.1) E = exp(-x*(pi/t0*S/T)**0.5)

    Args:
    -----
        E (float) [-]:
            Dimensionless Tidal Efficiency Factor. The value can be estimated with
            Erskine 1991 method, as the ration of standart deviations of two sets
            of readings
        t0 (float) [s]:
            Period of a tidal oscillation in [seconds]
        x0 (float) [m]:
            Distance from an observation well to shoreline/river in [METERS]

    Return:
    ------
        D_e (float) [m**2/s]:
            Diffusivity (T/S) calculated from (eq.1) in [m**2/s]
    '''
    alpha=beta=theta=rho=b=K1=b1=omega=K_cap=b_cap=K=T=L= 0.
    g = 9.81  #gravity acceleration [m/s**2]

    # DETERMINE THE CASE
    if L == float('inf') and K1 != 0. and b1 != float('inf'):
        CASE = 1  # infinite roof, leakage
    elif L == float('inf') and (K1 == 0. or b1 == float('inf')):
        CASE = 2  # infinite roof, no leakage
    else:
        raise NotImplementedError()

    # -------------------------------------------------------------------
    # Ss = specific storage [1/m]
    Ss = rho*g*(alpha + beta*theta)
    # S = dimensionless storativity of the confined aquifer [-]
    S = Ss * b
   
    # -------------------------------------------------------------------
    # Le = dimensionless loading efficiency
    Le = alpha / (alpha+theta*beta)

    # Ls = leackance rate (or specific leakage) of the roof [1/s]
    Ls = K1/b1

    # a = Confined aquifer's tidal wave propogation parameter [1/m]
    a = sqrt(omega/2.*S/T)

    # u = dimensionless leakage of the semipermeable layer
    u = Ls/(omega*S)

    # sigma = dimensionlesss leakance of the outlet-capping
    sigma = K_cap/(a*b_cap*K)

    # -------------------------------------------------------------------
    p = sqrt(sqrt(1+u**2)+u)  # [-]
    q = sqrt(sqrt(1+u**2)-u)  # [-]
    Lambda = (u**2 + Le)/(u**2 + 1)
    mu = - ((1-Le)*u)/(u**2+1)


    if CASE == 1:
        # -------------------------------------------------------------------
        # Case 1.
        # Confined aquifer extending under the sea infinitely
        # -------------------------------------------------------------------
        C_inf = 0.5 * sqrt( (u**2+Le**2)/(u**2+1) )
        phi_inf = arctan( ((1-Le)*u)/(u**2+Le) )
        
        if x >= 0.:
            h = A * C_inf * exp(-a*p*x) * np.cos(omega*t - a*q*x - phi_inf + phi0)
        else:
            raise NotImplementedError()

    elif CASE == 2:
        # -------------------------------------------------------------------
        # Case 2.
        # Confined aquifer extending under the sea infinitely
        # with impermeable roof
        # -------------------------------------------------------------------
        if x >= 0.:
            h = 0.5*Le*A*exp(a*x)*np.cos(omega*t - a*x + phi0)
        else:
            h = Le*A*np.cos(omega*t+phi0) - 0.5*Le*A*exp(a*x)*np.cos(omega*t + a*x + phi0)
    

    D = ((-x0)**2 * (pi/t0)) / (log(E)**2)
    return D


def diffusivity_from_time_lag(tlag, x0, t0):
    ''' Calculate Diffusivity `D` (ratio of Transmissivity `T` to Storage `S`) based on
    equation of Ferris 1951 for a groundwater head in a tidal influenced aquifer.
    Calculations are done based on Time Lag (phase shifting). Input parameters represent
    properties of an observation well (tlag, x0) and of the governing tide (t0).

        Ferris 1951 equation:

            h(x,t) = h0 * exp(-x*(pi/t0*S/T)**0.5) * sin(2*pi*t/t0 - x*(pi/t0*S/T)**0.5)

        From there:
            tlag = x*(pi/t0*S/T)**0.5

    Args:
    -----
        tlag (float) [s]:
            Time lag (phase shift) of the signal in [seconds]
        t0 (float) [seconds]:
            Period of a tidal oscillation in [seconds]
        x0 (float) [m]:
            Distance from an observation well to shoreline/river in [METERS]

    Return:
    ------
        D_tlag (float) [m**2/s]:
            Diffusivity (T/S) calculated from (eq.2) in [m**2/s]
    '''
    D = (t0*x0**2) / (4*pi*tlag**2)
    return D


def h(t=[], x=0,
        A=1., omega=0.5, phi0=0.,
        rho=1000.,
        alpha=1.e-8, beta=4.8e-10, theta=0.35,
        L=0., K1=1.e-6, b1=1.,
        K=1.e-4, b=10.,
        K_cap=1.e-6, b_cap=5.,
        ):
    ''' Calculate groundwater amplitude `h(x, t)` based on equation of Ferris 1951 for a
    groundwater head in a tidal influenced aquifer.

        Ferris 1951 equation with COS:
            h(x,t) = A * exp(-x*(omega/2./D)**0.5) * cos(omega*t - x*(omega/2./D)**0.5+phi)

            Following boundary conditions are introduced:
                
                1) h(x=0, t=0) = A
                2) h(x=inf) = 0
    Args:
    -----
        x (float) [m]:
            Distance from shoreline/river in
        t (float|np.array(float)) [s]:
            Time elapsed from reference point in [s]. Can be numpy array with floats

        rho [km/m**3]:
            water density
        alpha [m*s**2/kg]:
            compressibility of the confined aquifer's skeleton
        beta [m*s**2/kg]
            compressibility of pore water in the confined aquifer
        theta [-]:
            porosity (dimensionless) of the aquifer
        L [m]:
            distance to which aquifer's roof extends into the sea
        K1 [m/s]:
            vertical hydraulic conductivity of the aquifer roof
        b1 [m]:
            thickness of the aquifer roof
        A [m]:
            Amplitude of a tidal oscillation
        omega [rad/s]:
            Angular velocity of a tidal oscillation
        phi0 [rad]:
            Initial phase shift of a tidal oscillation
        b [m]:
            thickness of the cofined aquifer
        K [m/s]:
            hydraulic conductivity of the confined aquifer
        K_cap [m/s]:
            permeability of the outlet-capping (referred as `K'` in Xia et al 2007)
        b_cap [m]:
            thickness of the aquifer's outlet-capping (referred as `m` in Xia et al 2007)
    Return:
    ------
        h (float|np.array(float)) [m]:
            groundwater head at distance `x` from shoreline at time `t` with respect to
            the mean groundwater level (i.e. amplitude)
    '''
    g = 9.81  #gravity acceleration [m/s**2]

    # DETERMINE THE CASE
    if L == float('inf') and K1 != 0. and b1 != float('inf'):
        CASE = 1  # infinite roof, leakage
    elif L == float('inf') and (K1 == 0. or b1 == float('inf')):
        CASE = 2  # infinite roof, no leakage
    else:
        raise NotImplementedError('This case is currently not implemented')

    # -------------------------------------------------------------------
    # Ss = specific storage [1/m]
    Ss = rho*g*(alpha + beta*theta)
    # S = dimensionless storativity of the confined aquifer [-]
    S = Ss * b
    # T = transmissivity of the confined aquifer [m**2/s]
    T = K * b
            
    # -------------------------------------------------------------------
    # Le = dimensionless loading efficiency
    Le = alpha / (alpha+theta*beta)

    # Ls = leackance rate (or specific leakage) of the roof [1/s]
    Ls = K1/b1

    # a = Confined aquifer's tidal wave propogation parameter [1/m]
    a = sqrt(omega/2.*S/T)

    # u = dimensionless leakage of the semipermeable layer
    u = Ls/(omega*S)

    # sigma = dimensionlesss leakance of the outlet-capping
    sigma = K_cap/(a*b_cap*K)

    # -------------------------------------------------------------------
    p = sqrt(sqrt(1+u**2)+u)  # [-]
    q = sqrt(sqrt(1+u**2)-u)  # [-]
    Lambda = (u**2 + Le)/(u**2 + 1)
    mu = - ((1-Le)*u)/(u**2+1)


    if CASE == 1:
        # -------------------------------------------------------------------
        # Case 1.
        # Confined aquifer extending under the sea infinitely
        # -------------------------------------------------------------------
        C_inf = 0.5 * sqrt( (u**2+Le**2)/(u**2+1) )
        phi_inf = arctan( ((1-Le)*u)/(u**2+Le) )
        
        if x >= 0.:
            h = A * C_inf * exp(-a*p*x) * np.cos(omega*t - a*q*x - phi_inf + phi0)
        else:
            raise NotImplementedError()

    elif CASE == 2:
        # -------------------------------------------------------------------
        # Case 2.
        # Confined aquifer extending under the sea infinitely
        # with impermeable roof
        # -------------------------------------------------------------------
        if x >= 0.:
            h = 0.5*Le*A*exp(a*x)*np.cos(omega*t - a*x + phi0)
        else:
            h = Le*A*np.cos(omega*t+phi0) - 0.5*Le*A*exp(a*x)*np.cos(omega*t + a*x + phi0)
    
    return h
