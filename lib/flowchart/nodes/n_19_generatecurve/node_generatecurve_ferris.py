#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import division
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.tide import generate_tide
import numpy as np


class genCurveNode(NodeWithCtrlWidget):
    """Generate Curve based on Ferris 1951 equation"""
    nodeName = "Generate Curve (Ferris)"
    uiTemplate = [
            {'title': 'Curve Label', 'name': 'label', 'type': 'str', 'value': 'Generated Curve', 'tip': 'Label of the curve to be displayed in pd.DataFrame'},

            {'title': 'Time Options', 'name': 't_grp', 'type': 'group', 'expanded': True, 'children': [
                {'title': 'Start', 'name': 't0', 'type': 'str', 'value': '2015-12-31 00:00:00', 'default': '2015-12-31 00:00:00', 'tip': 'Datetime of the initial timestep'},
                {'title': 'Stop', 'name': 'tend', 'type': 'str', 'value': '2016-01-30 00:00:00', 'default': '2016-01-30 00:00:00', 'tip': 'Datetime of the last timestep'},
                {'title': 'Delta Time', 'name': 'dt', 'type': 'int', 'value': 3600, 'limits': (0., 10.e10), 'suffix': ' s', 'step': 60, 'tip': 'Timesep duration in seconds'},
            ]},
               
            {'title': 'Tide Components', 'name': 'T_grp', 'type': 'group', 'expanded': True, 'children': [
                {'title': 'Tide Component Eq.', 'name': 'eq', 'type': 'str', 'readonly': True, 'value': 'h = A*cos(omega*t+phi)'},
                {'name': 'M2', 'type': 'bool', 'value': False, 'expanded': False, 'children': [
                    {'title': 'Angular velocity', 'name': 'omega', 'type': 'float', 'suffix': ' rad/h', 'value': 0.5056, 'readonly': True },
                    {'title': 'Amplitude', 'name': 'A', 'type': 'float', 'suffix': ' m', 'value': 0.0, 'step': 0.1 },
                    {'title': 'Phase shift', 'name': 'phi', 'type': 'float', 'suffix': ' rad', 'value': 0.0, 'step': 0.1 },
                ]},
                {'name': 'S2', 'type': 'bool', 'value': False, 'expanded': False, 'children': [
                    {'title': 'Angular velocity', 'name': 'omega', 'type': 'float', 'suffix': ' rad/h', 'value': 0.5233, 'readonly': True },
                    {'title': 'Amplitude', 'name': 'A', 'type': 'float', 'suffix': ' m', 'value': 0.0, 'step': 0.1 },
                    {'title': 'Phase shift', 'name': 'phi', 'type': 'float', 'suffix': ' rad', 'value': 0.0, 'step': 0.1 },
                ]},
                {'name': 'K1', 'type': 'bool', 'value': False, 'expanded': False, 'children': [
                    {'title': 'Angular velocity', 'name': 'omega', 'type': 'float', 'suffix': ' rad/h', 'value': 0.2624, 'readonly': True },
                    {'title': 'Amplitude', 'name': 'A', 'type': 'float', 'suffix': ' m', 'value': 0.0, 'step': 0.1 },
                    {'title': 'Phase shift', 'name': 'phi', 'type': 'float', 'suffix': ' rad', 'value': 0.0, 'step': 0.1 },
                ]},
                {'name': 'O1', 'type': 'bool', 'value': False, 'expanded': False, 'children': [
                    {'title': 'Angular velocity', 'name': 'omega', 'type': 'float', 'suffix': ' rad/h', 'value': 0.2432, 'readonly': True },
                    {'title': 'Amplitude', 'name': 'A', 'type': 'float', 'suffix': ' m', 'value': 0.0, 'step': 0.1 },
                    {'title': 'Phase shift', 'name': 'phi', 'type': 'float', 'suffix': ' rad', 'value': 0.0, 'step': 0.1 },
                ]},
            ]},
            
            {'title': 'Ferris Parameters', 'name': 'ferris_grp', 'type': 'group', 'expanded': True, 'children': [
                {'title': 'Difusivity', 'name': 'D', 'type': 'float', 'suffix': ' m**2/s', 'value': 0.5, 'step': 0.1, 'tip': 'Diffusivity of the aquifer'},
                {'title': 'Distance to shore', 'name': 'x', 'type': 'float', 'suffix': ' m', 'value': 0.0, 'step': 5., 'limits': (0., 10.e10), 'tip': 'Distance between the observation point in aquifer and the shore-line'},
               ]}
        ]

    def __init__(self, name, parent=None):
        terms = {'pd.DataFrame': {'io': 'out'}}
        super(genCurveNode, self).__init__(name, parent=parent, terminals=terms, color=(250, 250, 150, 150))
    
    def _createCtrlWidget(self, **kwargs):
        return genCurveNodeCtrlWidget(**kwargs)


    def process(self):
        kwargs = self.CW().prepareInputArguments()

        df = generate_tide(kwargs['t0'], kwargs['dt'], kwargs['tend'], components=kwargs['tides'], label=kwargs['label'], equation='ferris',
                D=kwargs['ferris']['D'], x=kwargs['ferris']['x'])

        return {'pd.DataFrame': df}


class genCurveNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(genCurveNodeCtrlWidget, self).__init__(**kwargs)

    def prepareInputArguments(self):
        kwargs = dict()

        kwargs['t0']  = np.datetime64(self.p['t_grp', 't0'])
        kwargs['dt']  = np.timedelta64(self.p['t_grp', 'dt'], 's')
        kwargs['tend']   = np.datetime64(self.p['t_grp', 'tend'])
        kwargs['label']  = self.p['label']
        
        kwargs['tides'] = {}
        for tide_param in self.param('T_grp').children():
            if tide_param.value() is True:
                kwargs['tides'][tide_param.name()] = {}
                kwargs['tides'][tide_param.name()]['A'] = self.p['T_grp', tide_param.name(), 'A']
                kwargs['tides'][tide_param.name()]['omega'] = self.p['T_grp', tide_param.name(), 'omega']
                kwargs['tides'][tide_param.name()]['phi'] = self.p['T_grp', tide_param.name(), 'phi']

        # --------  Ferris ------
        kwargs['ferris'] = {}
        kwargs['ferris']['D'] = self.p['ferris_grp', 'D']
        kwargs['ferris']['x'] = self.p['ferris_grp', 'x']
        return kwargs
