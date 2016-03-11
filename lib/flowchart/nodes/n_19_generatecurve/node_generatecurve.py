#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import division
from pyqtgraph.Qt import QtCore
import numpy as np

from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.tide import generate_tide
from lib.functions.general import isNumpyNumeric



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
            {'title': 'Tide Components', 'name': 'tides_grp', 'type': 'group', 'children': [
                {'title': 'N Signal Components', 'name': 'n_sig', 'type': 'int', 'readonly': True},
                {'title': 'Amplitude', 'name': 'A', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Name of the column with Amplitude data in dataframe in input terminal'},
                {'title': 'Angular Velocity', 'name': 'omega', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Name of the column with Angular Velocity data in dataframe in input terminal'},
                {'title': 'Phase Shift', 'name': 'phi', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Name of the column with Phase Shift data in dataframe in input terminal'},
            ]},
            {'title': 'Constant to add', 'name': 'W', 'type': 'float', 'value': 0., 'suffix': ' m', 'tip': 'Constant value [meters] to be added to generated signal. Usefull to fit to average water level.'},

            {'title': 'Time Options', 'name': 't_grp', 'type': 'group', 'expanded': True, 'children': [
                {'title': 'Start', 'name': 't0', 'type': 'str', 'value': '2015-12-31 00:00:00', 'default': '2015-12-31 00:00:00', 'tip': 'Datetime of the initial timestep'},
                {'title': 'Stop', 'name': 'tend', 'type': 'str', 'value': '2016-01-30 00:00:00', 'default': '2016-01-30 00:00:00', 'tip': 'Datetime of the last timestep'},
                {'title': 'Delta Time', 'name': 'dt', 'type': 'int', 'value': 3600, 'limits': (0., 10.e10), 'suffix': ' s', 'step': 60, 'tip': 'Timesep duration in seconds'},
            ]},
            
            {'title': 'Ferris Parameters', 'name': 'ferris_grp', 'type': 'group', 'expanded': False, 'children': [
                {'title': 'Diffusivity', 'name': 'D', 'type': 'float', 'suffix': ' m**2/s', 'value': 0.5, 'step': 0.1, 'tip': 'Diffusivity of the aquifer'},
                {'title': 'Distance to shore', 'name': 'x', 'type': 'float', 'suffix': ' m', 'value': 0.0, 'step': 1., 'limits': (0., 10.e10), 'tip': 'Distance between the observation point in aquifer and the shore-line'},
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
        terms = {'tides': {'io': 'in'}, 'sig': {'io': 'out'}}
        super(genCurveNode, self).__init__(name, parent=parent, terminals=terms, color=(100, 250, 100, 150))

        self.CW().param('xia_grp', 'theta').setValue(0.35)  # to trigger computation of Ss and D
        self._df_id = None
    
    def _createCtrlWidget(self, **kwargs):
        return genCurveNodeCtrlWidget(**kwargs)


    def process(self, tides):
        if tides is None:
            return
        if self._df_id != id(tides):
            #print 'df new'
            self._df_id = id(tides)
            self.CW().param('tides_grp', 'n_sig').setValue(len(tides)-1)

            self.CW().disconnect_valueChanged2upd(self.CW().param('tides_grp', 'A'))
            self.CW().disconnect_valueChanged2upd(self.CW().param('tides_grp', 'omega'))
            self.CW().disconnect_valueChanged2upd(self.CW().param('tides_grp', 'phi'))

            colname = [col for col in tides.columns if isNumpyNumeric(tides[col].dtype)]
            self.CW().param('tides_grp', 'A').setLimits(colname)
            self.CW().param('tides_grp', 'omega').setLimits(colname)
            self.CW().param('tides_grp', 'phi').setLimits(colname)

            self.CW().param('tides_grp', 'A').setValue(colname[0])
            self.CW().param('tides_grp', 'omega').setValue(colname[1])
            self.CW().param('tides_grp', 'phi').setValue(colname[2])

            self.CW().connect_valueChanged2upd(self.CW().param('tides_grp', 'A'))
            self.CW().connect_valueChanged2upd(self.CW().param('tides_grp', 'omega'))
            self.CW().connect_valueChanged2upd(self.CW().param('tides_grp', 'phi'))

            self.CW().disconnect_valueChanged2upd(self.CW().param('W'))
            W = tides[self.CW().p['tides_grp', 'A']][0]  # 1st value from column `A`
            self.CW().param('W').setValue(W)
            self.CW().param('W').setDefault(W)
            self.CW().connect_valueChanged2upd(self.CW().param('W'))


        kwargs = self.CW().prepareInputArguments()

        kwargs['tides'] = {}
        for i in xrange(len(tides)):
            if not np.isnan(tides.iloc[i][kwargs['df_A']]) and np.isnan(tides.iloc[i][kwargs['df_omega']]):
                continue  #skipping 0-frequency amplitude
            kwargs['tides'][str(i)] = {}
            kwargs['tides'][str(i)]['A']     = tides.iloc[i][kwargs['df_A']]
            kwargs['tides'][str(i)]['omega'] = tides.iloc[i][kwargs['df_omega']]
            kwargs['tides'][str(i)]['phi']   = tides.iloc[i][kwargs['df_phi']]

            #print i, ': a={0}, omega={1}, phi={2}'.format(kwargs['tides'][str(i)]['A'], kwargs['tides'][str(i)]['omega'], kwargs['tides'][str(i)]['phi']  )


        if kwargs['eq'] == 'tide':
            df = generate_tide(kwargs['t0'], kwargs['dt'], kwargs['tend'], components=kwargs['tides'], W=kwargs['W'], label=kwargs['label'], equation=kwargs['eq'])
        elif kwargs['eq'] == 'ferris':
            df = generate_tide(kwargs['t0'], kwargs['dt'], kwargs['tend'], components=kwargs['tides'], W=kwargs['W'], label=kwargs['label'], equation=kwargs['eq'],
                D=kwargs['ferris']['D'], x=kwargs['ferris']['x'])
        elif kwargs['eq'] == 'xia':
            df = generate_tide(kwargs['t0'], kwargs['dt'], kwargs['tend'], components=kwargs['tides'], W=kwargs['W'], label=kwargs['label'], equation=kwargs['eq'],
                x=kwargs['xia']['x'],
                alpha=kwargs['xia']['alpha'], beta=kwargs['xia']['beta'], theta=kwargs['xia']['theta'],
                L=kwargs['xia']['L'], K1=kwargs['xia']['K1'], b1=kwargs['xia']['b1'],
                K=kwargs['xia']['K'], b=kwargs['xia']['b'],
                K_cap=kwargs['xia']['K_cap'], b_cap=kwargs['xia']['b_cap'])

        else:
            df = None
        return {'sig': df}


class genCurveNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(genCurveNodeCtrlWidget, self).__init__(**kwargs)
        self.param('eq').sigValueChanged.connect(self._on_equationChanged)
        self.disconnect_valueChanged2upd(self.param('tides_grp', 'n_sig'))

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

        kwargs['t0']    = np.datetime64(self.p['t_grp', 't0'] + 'Z')  # zulu time
        kwargs['dt']    = np.timedelta64(self.p['t_grp', 'dt'], 's')
        kwargs['tend']  = np.datetime64(self.p['t_grp', 'tend'] + 'Z')  # zulu time
        kwargs['label'] = self.p['label']
        
        kwargs['df_A']     = self.p['tides_grp', 'A']
        kwargs['df_omega'] = self.p['tides_grp', 'omega']
        kwargs['df_phi']   = self.p['tides_grp', 'phi']

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
