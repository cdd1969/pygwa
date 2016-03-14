#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import division
from math import pi
from math import sqrt
from math import log
from math import exp
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

    # -----------------------------
    # Determine part leakage status
    # -----------------------------
    # Roof confining layer
    if b1 == 0.:
        raise ValueError('ROOF-confinig layer cannot have 0. thickness')
    elif b1 > 0. and 0. < K1 < float('inf'):
        ROOF = 'permeable'
    elif b1 == float('inf') or K1 == 0.:
        ROOF = 'impermeable'
    else:
        raise NotImplementedError('ROOF detected with error')

    # Capping
    if b_cap == 0.:
        CAPPING = None
    elif b_cap > 0. and 0. < K_cap < float('inf'):
        CAPPING = 'permeable'
    elif b_cap == float('inf') or K_cap == 0.:
        CAPPING = 'impermeable'
    else:
        raise NotImplementedError('CAPPING detected with error')

    # DETERMINE THE CASE
    CASE = None
    if L == float('inf'):
        if ROOF is 'permeable':
            CASE = 1  # infinite roof, with roof leakage
    
        elif ROOF is 'impermeable':
            CASE = 2  # infinite roof, without roof leakage
    
    elif L == 0.:
        if CAPPING is 'permeable' and ROOF is 'permeable':
            CASE = 3  # zero offshore length, with capping, with leakage
    
        elif not CAPPING and ROOF is 'permeable':
            CASE = 4  # zero ofsshore length, without capping, with leakage
    
        elif not CAPPING and ROOF is 'impermeable':
            CASE = 5  # zero ofsshore length, without capping, without leakage
    
    elif L != 0.:
        if CAPPING is 'impermeable':
            CASE = 6  # confined aquifer with an impermeable outlet
    
        elif CAPPING is 'permeable' and ROOF is 'impermeable':
            CASE = 7  # confined aquifer with an impermeable roof + permeable capping
    
    
    if CASE is None:
        print('ROOF is {0}, CAPPING is {1}, ROOG LENGTH is {2}'.format(ROOF, CAPPING, L))
        raise NotImplementedError('This case is currently not implemented')

    #print('ROOF is {0}, CAPPING is {1}, ROOG LENGTH is {2}'.format(ROOF, CAPPING, L))
    #print 'xia2007 > CASE', CASE

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
    a = sqrt(omega/2.*Ss/K)

    # u = dimensionless leakage of the semipermeable layer
    u = Ls/(omega*S)

    # sigma = dimensionlesss leakance of the outlet-capping
    try:
        sigma = K_cap/(a*b_cap*K)
    except ZeroDivisionError:
        sigma = float('inf')

    # -------------------------------------------------------------------
    p = sqrt(sqrt(1+u**2)+u)  # [-]
    q = sqrt(sqrt(1+u**2)-u)  # [-]
    Lambda = (u**2 + Le)/(u**2 + 1)
    mu = - ((1-Le)*u)/(u**2+1)


    if CASE == 1:
        # -------------------------------------------------------------------
        # Case 1.
        # Leaky confined aquifer extending under the sea infinitely
        # Same as Li and Jiao 2001
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
        # Confined aquifer extending under the sea infinitely, impermeable roof
        # Same as Van der Kamp 1972
        # -------------------------------------------------------------------
        if x >= 0.:
            h = 0.5*Le*A*exp(a*x)*np.cos(omega*t - a*x + phi0)
        else:
            h = Le*A*np.cos(omega*t+phi0) - 0.5*Le*A*exp(a*x)*np.cos(omega*t + a*x + phi0)

    elif CASE == 3:
        # -------------------------------------------------------------------
        # Case 3.
        # Leaky confined aquifer with zero offshore length, with capping
        # Same as Ren et al 2007
        # -------------------------------------------------------------------
        if x >= 0.:
            h = A*sigma/sqrt((p+sigma)**2+q**2) * exp(-a*p*x)*np.cos(omega*t - a*q*x - arctan(q/(sigma+p)) + phi0)
        else:
            raise ValueError('Invalid `x` {0}. With L=0, `x` must be >= 0'.format(x))
    
    elif CASE == 4:
        # -------------------------------------------------------------------
        # Case 4.
        # Leaky confined aquifer with zero offshore length, without capping
        # Same as Jiao and Tang 1999
        # -------------------------------------------------------------------
        if x >= 0.:
            h = A*exp(-a*p*x)*np.cos(omega*t - a*q*x + phi0)
        else:
            raise ValueError('Invalid `x` {0}. With L=0, `x` must be >= 0'.format(x))
    
    elif CASE == 5:
        # -------------------------------------------------------------------
        # Case 5.
        # Confined aquifer with zero offshore length, without capping, without leakage
        # Same as Serfes 1951
        # -------------------------------------------------------------------
        if x >= 0.:
            h = A*exp(-a*x)*np.cos(omega*t - a*x + phi0)
        else:
            raise ValueError('Invalid `x` {0}. With L=0, `x` must be >= 0'.format(x))

    elif CASE == 6:
        # -------------------------------------------------------------------
        # Case 6.
        # Leaky confined aquifer with impermeable capping.
        # Tidal River scenario with x = 0 and x = -2L representing river banks
        # -------------------------------------------------------------------

        h = A/2. * (Lambda * (exp(-a*p*x)*np.cos(omega*t - a*p*x + phi0) - exp(-a*p*(x+2*L)) *
            np.cos(omega*t - a*q*(x+2*L) + phi0)) + mu*( exp(-a*p*x) * np.sin(omega*t - a*q*x + phi0) -
            exp(-a*p*(x+2*L)) * np.sin(omega*t - a*q*(x+2*L) + phi0) ) )
    
    elif CASE == 7:
        # -------------------------------------------------------------------
        # Case 7.
        # Confined aquifer with an impermeable roof and permeable capping
        # Same as Li et al 2007
        # -------------------------------------------------------------------

        mu_Li = K_cap / (b_cap * K)  # param `mu` defined by Li2007 is different from `mu` in Xia2007

        psi1 = arctan( 2.*sigma / (sigma**2 - 2.) )
        psi2 = arctan( 1. / (1. + sigma) )

        nu = Le * exp(-a*L) / (sigma**2 + 2*sigma + 2) * (1./2.*exp(-a*L) * ((sigma**2 - 2)*np.cos(2*a*L) -
            2*sigma*np.sin(2*a*L)) + (1 - Le)/Le * ((sigma**2 + sigma)*np.cos(a*L) - sigma*np.sin(a*L)))

        xi = Le * exp(-a*L) / (sigma**2 + 2*sigma + 2) * (1./2.*exp(-a*L) * (2*sigma*np.cos(2*a*L) -
            (sigma**2 - 2)*np.sin(2*a*L)) + (1 - Le)/Le * ((sigma**2 + sigma)*np.sin(a*L) - sigma*np.cos(a*L)))

        C = sqrt((nu + Le/2.)**2 + xi**2)
        phi = arctan(2*xi / (2*nu + Le))
        


        if x >= 0.:

            h = A*C*exp(-a*x) * np.cos(omega*t - a*x - phi + phi0)

        elif x < 0. and x > -L:
            
            h0 = (0.5*sqrt(sigma**4+4)/(sigma**2+2*sigma+2) * exp(-a*(x+2*L)) * np.cos(omega*t - a*(x+2*L) - psi1 + phi0) +
                sigma/sqrt(sigma**2+2*sigma+2) * (1-Le)/Le * exp(-a*(x+L)) * np.cos(omega*t - a*(x+L)) - psi2 + phi0)

            h = A*Le * (np.cos(omega*t + phi0) - 0.5*exp(a*x)*np.cos(omega*t + a*x + phi0) + h0)
        else:
            raise ValueError('Invalid `x` {0}. Should be in range [-L, +inf]'.format(x))

        
    return h
