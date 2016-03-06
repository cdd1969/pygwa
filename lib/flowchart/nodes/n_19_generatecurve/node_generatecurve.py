#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import division
from pyqtgraph.Qt import QtCore

from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.tide import generate_tide
import numpy as np


class genCurveNode(NodeWithCtrlWidget):
    """Generate Curve"""
    nodeName = "Generate Curve"
    uiTemplate = [
            {'title': 'Curve Label', 'name': 'label', 'type': 'str', 'value': 'Generated Curve', 'tip': 'Label of the curve to be displayed in pd.DataFrame'},
            {'title': 'Governing Equation', 'name': 'eq', 'type': 'list', 'values':
                {"Simple Tide Equation": 'tide',
                "Ferris 1951 Equation": "ferris",
                "Xia 2007 Equation": 'xia'
                },
                'tip': 'Equation to generate curve. See documentation'
            },

            {'title': 'Constant to add', 'name': 'W', 'type': 'float', 'value': 0., 'suffix': ' m', 'tip': 'Constant value [meters] to be added to generated signal. Usefull to fit to average water level.'},

            {'title': 'Time Options', 'name': 't_grp', 'type': 'group', 'expanded': True, 'children': [
                {'title': 'Start', 'name': 't0', 'type': 'str', 'value': '2015-12-31 00:00:00', 'default': '2015-12-31 00:00:00', 'tip': 'Datetime of the initial timestep'},
                {'title': 'Stop', 'name': 'tend', 'type': 'str', 'value': '2016-01-30 00:00:00', 'default': '2016-01-30 00:00:00', 'tip': 'Datetime of the last timestep'},
                {'title': 'Delta Time', 'name': 'dt', 'type': 'int', 'value': 3600, 'limits': (0., 10.e10), 'suffix': ' s', 'step': 60, 'tip': 'Timesep duration in seconds'},
            ]},
               
            {'title': 'Tide Components', 'name': 'T_grp', 'type': 'group', 'expanded': True, 'children': [
                #{'title': 'Tide Component Eq.', 'name': 'eq', 'type': 'str', 'readonly': True, 'value': 'h = A*cos(omega*t+phi)'},
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
            
            {'title': 'Ferris Parameters', 'name': 'ferris_grp', 'type': 'group', 'expanded': False, 'children': [
                {'title': 'Diffusivity', 'name': 'D', 'type': 'float', 'suffix': ' m**2/s', 'value': 0.5, 'step': 0.1, 'tip': 'Diffusivity of the aquifer'},
                {'title': 'Distance to shore', 'name': 'x', 'type': 'float', 'suffix': ' m', 'value': 0.0, 'step': 5., 'limits': (0., 10.e10), 'tip': 'Distance between the observation point in aquifer and the shore-line'},
            ]},

            {'title': 'Xia Parameters', 'name': 'xia_grp', 'type': 'group', 'expanded': False, 'children': [

                {'title': 'Distance to shore', 'name': 'x', 'type': 'float', 'suffix': ' m', 'value': 0., 'limits': (0., 10.e10), 'tip': 'Distance between the observation point in aquifer and the shore-line'},

                {'title': 'Skeleton compressibility', 'name': 'alpha', 'type': 'float', 'suffix': ' m*s**2/kg', 'value': 1.e-8, 'step': 0.00001, 'limits': (0., 1), 'tip': 'Compressibility of the confined aquifers skeleton. Used for calculation of Specific Storage Ss'},
                {'title': 'Water compressibility', 'name': 'beta', 'type': 'float', 'suffix': ' m*s**2/kg', 'value': 4.8e-10, 'step': 0.00001, 'limits': (0., 1), 'tip': 'Compressibility of pore water in the confined aquifer. Used for calculation of Specific Storage Ss'},
                {'title': 'Porosity', 'name': 'theta', 'type': 'float', 'value': 0.40, 'step': 0.01, 'limits': (0., 1), 'tip': 'Porosity (dimensionless) of the aquifer. Used for calculation of Specific Storage Ss'},

                {'title': 'Roof length', 'name': 'L', 'type': 'float', 'suffix': ' m', 'value': 100., 'limits': (0., 10.e10), 'tip': 'Distance to which aquifers roof extends into the sea'},
                {'title': 'Infinite Roof length', 'name': 'L_inf', 'type': 'bool', 'value': False, 'tip': 'Check this to set roof length to infinity'},
                {'title': 'Kf (roof)', 'name': 'K1', 'type': 'float', 'suffix': ' m/s', 'value': 1.e-6, 'step': 0.00001, 'limits': (0., 1), 'tip': 'Vertical hydraulic conductivity of the aquifer roof'},
                {'title': 'b (roof)', 'name': 'b1', 'type': 'float', 'suffix': ' m', 'value': 5., 'step': 0.1, 'limits': (0., 100), 'tip': 'Thickness of the aquifer roof'},
                {'title': 'Kf (aquifer)', 'name': 'K', 'type': 'float', 'suffix': ' m/s', 'value': 1.e-4, 'step': 0.00001, 'limits': (0., 1), 'tip': 'Hydraulic conductivity of the (leaky) confined aquifer'},
                {'title': 'b (aquifer)', 'name': 'b', 'type': 'float', 'suffix': ' m', 'value': 20., 'step': 1, 'limits': (0., 1000), 'tip': 'Thickness of the (leaky) cofined aquifer'},
                {'title': 'Kf (capping)', 'name': 'K_cap', 'type': 'float', 'suffix': ' m/s', 'value': 1.e-6, 'step': 0.00001, 'limits': (0., 1), 'tip': 'Permeability of the outlet-capping'},
                {'title': 'b (capping)', 'name': 'b_cap', 'type': 'float', 'suffix': ' m', 'value': 1., 'step': 0.1, 'limits': (0., 100), 'tip': 'Thickness of the aquifers outlet-capping'},
                {'title': 'Specific Storage', 'name': 'Ss', 'type': 'float', 'suffix': ' 1/m', 'value': -999., 'readonly': True},
                {'title': 'Diffusivity', 'name': 'D', 'type': 'float', 'suffix': ' m**2/s', 'value': -999., 'readonly': True},
            ]}
        ]

    def __init__(self, name, parent=None):
        terms = {'pd.DataFrame': {'io': 'out'}}
        super(genCurveNode, self).__init__(name, parent=parent, terminals=terms, color=(100, 250, 100, 150))

        self.CW().param('xia_grp', 'theta').setValue(0.35)  # to trigger computation of Ss and D
    
    def _createCtrlWidget(self, **kwargs):
        return genCurveNodeCtrlWidget(**kwargs)


    def process(self):
        kwargs = self.CW().prepareInputArguments()

        if kwargs['eq'] == 'tide':
            df = generate_tide(kwargs['t0'], kwargs['dt'], kwargs['tend'], components=kwargs['tides'], label=kwargs['label'], equation=kwargs['eq'])
        elif kwargs['eq'] == 'ferris':
            df = generate_tide(kwargs['t0'], kwargs['dt'], kwargs['tend'], components=kwargs['tides'], label=kwargs['label'], equation=kwargs['eq'],
                D=kwargs['ferris']['D'], x=kwargs['ferris']['x'])
        elif kwargs['eq'] == 'xia':
            df = generate_tide(kwargs['t0'], kwargs['dt'], kwargs['tend'], components=kwargs['tides'], label=kwargs['label'], equation=kwargs['eq'],
                x=kwargs['xia']['x'],
                alpha=kwargs['xia']['alpha'], beta=kwargs['xia']['beta'], theta=kwargs['xia']['theta'],
                L=kwargs['xia']['L'], K1=kwargs['xia']['K1'], b1=kwargs['xia']['b1'],
                K=kwargs['xia']['K'], b=kwargs['xia']['b'],
                K_cap=kwargs['xia']['K_cap'], b_cap=kwargs['xia']['b_cap'])

        else:
            df = None
        return {'pd.DataFrame': df}


class genCurveNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(genCurveNodeCtrlWidget, self).__init__(**kwargs)
        self.param('eq').sigValueChanged.connect(self._on_equationChanged)


        # xia 200 signals....
        self.disconnect_valueChanged2upd(self.param('xia_grp', 'D'))
        self.disconnect_valueChanged2upd(self.param('xia_grp', 'Ss'))

        self.param('xia_grp', 'alpha').sigValueChanged.connect(self.requested_calculate_Ss)
        self.param('xia_grp', 'beta').sigValueChanged.connect(self.requested_calculate_Ss)
        self.param('xia_grp', 'theta').sigValueChanged.connect(self.requested_calculate_Ss)
        
        self.param('xia_grp', 'K').sigValueChanged.connect(self.requested_calculate_D)
        self.param('xia_grp', 'Ss').sigValueChanged.connect(self.requested_calculate_D)

        self.param('xia_grp', 'L_inf').sigValueChanged.connect(self.on_roofLengthInf_clicked)
        

    @QtCore.pyqtSlot(object, object)
    def _on_equationChanged(self, param, value):
        ''' FIX HERE EVERYTHING!'''
        #print ('_on_equationChanged:', param, value)
        # first hide everything
        for param_group in ['ferris_grp']:
            #print ('hiding:', self.param(param_group))
            self.param(param_group).setOpts(expanded=False)

        if value == 'tide':
            pass
        elif value == 'ferris':
            #print ('showing:', self.param(param_group))
            self.param('ferris_grp').setOpts(expanded=True)

    def requested_calculate_Ss(self):
        alpha = self.p['xia_grp', 'alpha']
        beta = self.p['xia_grp', 'beta']
        theta = self.p['xia_grp', 'theta']
        rho = 1000.
        g = 9.81
        Ss = rho*g*(alpha + beta*theta)
        self.param('xia_grp', 'Ss').setValue(Ss)
    
    def requested_calculate_D(self):
        Ss = self.p['xia_grp', 'Ss']
        Kf = self.p['xia_grp', 'K']
        D = Kf/Ss
        self.param('xia_grp', 'D').setValue(D)

    def on_roofLengthInf_clicked(self):
        #self.param('xia_grp', 'L').setReadonly(self.p['xia_grp', 'L_inf'])
        pass


    def prepareInputArguments(self):
        kwargs = dict()

        kwargs['eq']    = self.p['eq']
        kwargs['W']     = self.p['W']

        kwargs['t0']    = np.datetime64(self.p['t_grp', 't0'])
        kwargs['dt']    = np.timedelta64(self.p['t_grp', 'dt'], 's')
        kwargs['tend']  = np.datetime64(self.p['t_grp', 'tend'])
        kwargs['label'] = self.p['label']
        
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

        # --------  XIA ------
        kwargs['xia'] = {}
        kwargs['xia']['x']      = self.p['xia_grp', 'x']
        kwargs['xia']['alpha']  = self.p['xia_grp', 'alpha']
        kwargs['xia']['beta']   = self.p['xia_grp', 'beta']
        kwargs['xia']['theta']  = self.p['xia_grp', 'theta']
        kwargs['xia']['K']      = self.p['xia_grp', 'K']
        kwargs['xia']['b']      = self.p['xia_grp', 'b']
        kwargs['xia']['K1']     = self.p['xia_grp', 'K1']
        kwargs['xia']['b1']     = self.p['xia_grp', 'b1']
        kwargs['xia']['K_cap']  = self.p['xia_grp', 'K_cap']
        kwargs['xia']['b_cap']  = self.p['xia_grp', 'b_cap']
        kwargs['xia']['L']      = self.p['xia_grp', 'L'] if not self.p['xia_grp', 'L_inf'] else float('inf')
        return kwargs
