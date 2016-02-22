#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import division
from math import pi as pi
from math import log as log
from math import exp as exp
from math import sin as sin
from math import cos as cos


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
        t0 (float) [hours]:
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


def h(x, t, h0, t0, D):
    ''' Calculate groundwater amplitude `h(x, t)` based on equation of Ferris 1951 for a
    groundwater head in a tidal influenced aquifer.

        Ferris 1951 equation with COS:
            h(x,t) = h0 * exp(-x*(pi/t0*S/T)**0.5) * cos(2*pi*t/t0 - x*(pi/t0*S/T)**0.5)

            Following boundary conditions are introduced:
                
                1) h(x=0, t=0) = h0
                2) h(x=inf) = 0
    Args:
    -----
        x (float) [m]:
            Distance from shoreline/river in
        t (float) [s]:
            Time elapsed from reference point
        h0 (float) [m]:
            Amplitude of a tidal oscillation
        t0 (float) [hours]:
            Period of a tidal oscillation
        D (float) [m2/s]:
            Diffusivity (or T/S ration) of an aquifer

    Return:
    ------
        h (x,t) [m]:
            groundwater head at distance `x` from shoreline at time `t` with respect to
            the mean groundwater level (i.e. amplitude)
    '''

    h = h0 * exp(-x*(pi/t0/D)**0.5) * cos(2*pi*t/t0 - x*(pi/t0/D)**0.5)

    return h
