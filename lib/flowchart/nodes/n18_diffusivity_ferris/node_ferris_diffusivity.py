#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import division

from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.ferris1951 import diffusivity_from_tidal_efficiency, diffusivity_from_time_lag
import datetime


class ferrisDiffusivityNode(NodeWithCtrlWidget):
    """Calculate Aquifer's Difusivity based on Ferris/Jacob model from Tidal Efficiency and Timelag"""
    nodeName = "Diffusivity (Ferris)"
    uiTemplate = [
            {'title': 'Distance', 'name': 'x0', 'type': 'float', 'limits': (0., 10.e6), 'value': 0., 'default': 0., 'suffix': 'm', 'tip': 'Distance between an observed well and shoreline (in meters)'},
            {'title': 'Tide Period', 'name': 't0', 'type': 'float', 'limits': (0., 10.e10), 'value': 12.42, 'default': 12.42, 'suffix': 'hours', 'tip': 'Period of the tide (in hours)'},
            {'title': 'Tidal Efficiency Parameters', 'name': 'E_grp', 'type': 'group', 'tip': '', 'expanded': True, 'children': [
                {'title': 'Tidal Efficiency', 'name': 'E', 'type': 'float', 'value': 1., 'default': 1., 'tip': 'Estimated or guessed Tidal Efficiency of an aquifer near an observed well (dimensionless).'},
                {'title': 'Set `E` Manually', 'name': 'manual_E', 'type': 'bool', 'value': False, 'tip': 'Use Tidal Efficiency value received in terminal or set manually. If checked - set manually'}
                ]},
            {'title': 'Time Lag Parameters', 'name': 'tlag_grp', 'type': 'group', 'tip': '', 'expanded': True, 'children': [
                {'title': 'Time Lag', 'name': 'tlag', 'type': 'float', 'limits': (0., 600.), 'value': 0., 'default': 0., 'suffix': 'min', 'tip': 'Estimated or guessed Time Lag (in minutes) of the groundwater fluctuation-signal in observed well.'},
                {'title': 'Set `tlag` Manually', 'name': 'manual_tlag', 'type': 'bool', 'value': False, 'tip': 'Use Time Lag value received in terminal or set manually. If checked - set manually'}
                ]},
            {'title': 'Calculated Diffusivity', 'name': 'D_grp', 'type': 'group', 'tip': '', 'expanded': True, 'children': [
                {'title': 'Diffusivity (E)', 'name': 'D_e', 'type': 'str', 'readonly': True, 'value': ''},
                {'title': 'Diffusivity (tlag)', 'name': 'D_tlag', 'type': 'str', 'readonly': True, 'value': ''},
               ]},
               ]

    def __init__(self, name, parent=None):
        terms = {'E': {'io': 'in'},
                 'tlag': {'io': 'in'},
                 'D (E)': {'io': 'out'},
                 'D (tlag)': {'io': 'out'}}
        super(ferrisDiffusivityNode, self).__init__(name, parent=parent, terminals=terms, color=(250, 250, 150, 150))
    
    def _createCtrlWidget(self, **kwargs):
        return ferrisDiffusivityNodeCtrlWidget(**kwargs)


    def process(self, E, tlag):
       

        # process t_lag branch:
        if not self.CW().p['tlag_grp', 'manual_tlag']:
            if tlag is not None:
                tlag = self.prepare_tlag(tlag)
            self.CW().disconnect_valueChanged2upd(self.CW().param('tlag_grp', 'tlag'))
            self.CW().param('tlag_grp', 'tlag').setValue(tlag)
            self.CW().connect_valueChanged2upd(self.CW().param('tlag_grp', 'tlag'))
        
        # process E branch:
        if not self.CW().p['E_grp', 'manual_E']:
            self.CW().disconnect_valueChanged2upd(self.CW().param('E_grp', 'E'))
            self.CW().param('E_grp', 'E').setValue(E)
            self.CW().connect_valueChanged2upd(self.CW().param('E_grp', 'E'))
        
        kwargs = self.ctrlWidget().prepareInputArguments()

        if kwargs['E'] is not None:
            D_e = diffusivity_from_tidal_efficiency(kwargs['E'], kwargs['x0'], kwargs['t0'])
        else:
            D_e = None
        if kwargs['tlag'] is not None:
            D_tlag = diffusivity_from_time_lag(kwargs['tlag'], kwargs['x0'], kwargs['t0'])
        else:
            D_tlag = None

        
        self.CW().param('D_grp', 'D_tlag').setValue('{0:.4f} m**2/s'.format(D_tlag) if D_tlag is not None else None)
        self.CW().param('D_grp', 'D_e').setValue('{0:.4f} m**2/s'.format(D_e) if D_e is not None else None)

        return {'D (E)': D_e, 'D (tlag)': D_tlag}

    def prepare_tlag(self, tlag):
        if isinstance(tlag, datetime.timedelta):
            tlag_mins = tlag.total_seconds() / 60.
        else:
            try:
                tlag_mins = float(tlag)
            except:
                tlag_mins = None
                raise TypeError ('Unsupported type {0} for argument `tlag` received. Should be <timedelta>, <str>, <float>'.format(type(tlag)))
        return tlag_mins



class ferrisDiffusivityNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(ferrisDiffusivityNodeCtrlWidget, self).__init__(**kwargs)
        self.disconnect_valueChanged2upd(self.param('D_grp', 'D_e'))
        self.disconnect_valueChanged2upd(self.param('D_grp', 'D_tlag'))

    def prepareInputArguments(self):
        kwargs = dict()
        for param in self.params(ignore_groups=True):
            kwargs[param.name()] = self.p.evaluateValue(param.value())

        kwargs['tlag'] = kwargs['tlag']*60. if kwargs['tlag'] is not None else None
        kwargs['t0'] *= 3600.
        return kwargs
