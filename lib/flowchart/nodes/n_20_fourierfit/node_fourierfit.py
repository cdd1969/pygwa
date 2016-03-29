#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
import pandas as pd
from pyqtgraph import BusyCursor

from lib.functions.general import isNumpyDatetime, isNumpyNumeric
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.fourier import pandas_fourier_analysis


class fourierFitNode(NodeWithCtrlWidget):
    """Decompose Sinusoidal timeseries curve with Fast Fourier Transformaions"""
    nodeName = "FFT"
    uiTemplate = [
            {'title': 'Signal', 'name': 'sig', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Name of the column with waterlevel data.'},
            {'title': 'Datetime', 'name': 'datetime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Name of the column with datetime (or __index__)'},
            
            {'title': 'Number of Waves', 'name': 'N_MAX_POW', 'type': 'int', 'value': 1, 'limits': (1, 10e10), 'tip': 'Number of partial waves used to generate equation. Partial waves with most powerful frequencies are selected at first. See docs'},

            {'title': 'Slice datetime', 'name': 'ranges', 'type': 'bool', 'value': False},

            {'title': 'Datetime Start', 'name': 't0', 'type': 'str', 'value': '2015-12-31 00:00:00', 'default': '2015-12-31 00:00:00', 'tip': 'start of the slice region'},
            {'title': 'Datetime Stop', 'name': 't1', 'type': 'str', 'value': '2016-01-30 00:00:00', 'default': '2016-01-30 00:00:00', 'tip': 'end of the slice region'},
            
            {'title': 'Generated Equation', 'name': 'eq', 'type': 'text', 'value': '', 'tip': 'This equation is generated after processing. You may copy it to buffer.\nIf you want to access parameters independently consider opening table that is stored in terminal `params`'},

            {'title': 'Display plot', 'name': 'plot', 'type': 'action'},

        ]

    def __init__(self, name, parent=None):
        terms = {'In': {'io': 'in'}, 'params': {'io': 'out'}, 'f(t)': {'io': 'out'}}
        super(fourierFitNode, self).__init__(name, parent=parent, terminals=terms, color=(250, 250, 150, 150))
        self._PLOT_REQUESTED = False
        self.fig = None
        self._df_id = None

    
    def _createCtrlWidget(self, **kwargs):
        return fourierFitNodeCtrlWidget(**kwargs)


    def process(self, In):
        df = In
        if df is None:
            return

        self.CW().param('eq').setValue('')

        if self._df_id != id(df):
            #print 'df new'
            self._df_id = id(df)
            self.CW().disconnect_valueChanged2upd(self.CW().param('datetime'))
            self.CW().disconnect_valueChanged2upd(self.CW().param('sig'))
            colname = [col for col in df.columns if isNumpyDatetime(df[col].dtype)]
            self.CW().param('datetime').setLimits(colname)
            colname = [col for col in df.columns if isNumpyNumeric(df[col].dtype)]
            self.CW().param('sig').setLimits(colname)
            self.CW().connect_valueChanged2upd(self.CW().param('datetime'))
            self.CW().connect_valueChanged2upd(self.CW().param('sig'))
            # ------------------------------------------------------
            # now update our range selectors
            kwargs = self.CW().prepareInputArguments()
            t_vals = df[kwargs['datetime']].values
            t_min = pd.to_datetime(str(min(t_vals)))
            t_max = pd.to_datetime(str(max(t_vals)))

            self.CW().disconnect_valueChanged2upd(self.CW().param('t0'))
            self.CW().disconnect_valueChanged2upd(self.CW().param('t1'))
            self.CW().param('t0').setValue(t_min.strftime('%Y-%m-%d %H:%M:%S'))
            self.CW().param('t0').setDefault(t_min.strftime('%Y-%m-%d %H:%M:%S'))
            self.CW().param('t1').setValue(t_max.strftime('%Y-%m-%d %H:%M:%S'))
            self.CW().param('t1').setDefault(t_max.strftime('%Y-%m-%d %H:%M:%S'))
            if self.CW().p['ranges'] is True:
                self.CW().connect_valueChanged2upd(self.CW().param('t0'))
                self.CW().connect_valueChanged2upd(self.CW().param('t1'))

        # get params once again
        kwargs = self.CW().prepareInputArguments()
        # ------------------------------------------------------

        with BusyCursor():
            df_out, eq_str, function, self.fig = pandas_fourier_analysis(df, kwargs['sig'], date_name=kwargs['datetime'], ranges=kwargs['ranges'], N_MAX_POW=kwargs['N_MAX_POW'], generate_plot=True)
        
        self.CW().param('eq').setValue(eq_str)
        self._PLOT_REQUESTED = False

        return {'params': df_out, 'f(t)': function}

    def on_plot_requested(self):
        self._PLOT_REQUESTED = True
        if self.fig:
            self.fig.show()



class fourierFitNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(fourierFitNodeCtrlWidget, self).__init__(**kwargs)
        self.disconnect_valueChanged2upd(self.param('eq'))
        self.param('plot').sigActivated.connect(self._parent.on_plot_requested)
        self.param('ranges').sigValueChanged.connect(self.on_rangesChecked)
    
    def on_rangesChecked(self):
        if self.p['ranges'] is True:
            self.connect_valueChanged2upd(self.param('t0'))
            self.connect_valueChanged2upd(self.param('t1'))
        else:
            self.disconnect_valueChanged2upd(self.param('t0'))
            self.disconnect_valueChanged2upd(self.param('t1'))

    def prepareInputArguments(self):
        kwargs = dict()

        kwargs['ranges']  = (np.datetime64(self.p['t0']+'Z'), np.datetime64(self.p['t1']+'Z')) if self.p['ranges'] else None
        kwargs['sig'] = self.p['sig']
        kwargs['datetime'] = self.p['datetime']
        kwargs['N_MAX_POW'] = self.p['N_MAX_POW']
        kwargs['plot'] = False
        
        return kwargs
