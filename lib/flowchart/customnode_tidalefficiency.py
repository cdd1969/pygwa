#!/usr/bin python
# -*- coding: utf-8 -*-

import os, sys
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.flowchart.Node import Node
from pyqtgraph import BusyCursor
import numpy as np
from package import Package
import inspect
from pyqtgraph.parametertree import Parameter, ParameterTree
from ..functions.detectpeaks import detectPeaks
from ..functions.evaluatedictionary import evaluateDict, evaluationFunction
import webbrowser
from ..common.NodeWithCtrlWidget import NodeWithCtrlWidget
from ..functions.TidalEfficiency import tidalEfficiency_method1, tidalEfficiency_method2, tidalEfficiency_method3
from ..functions.general import returnPandasDf, isNumpyDatetime



class tidalEfficiencyNode(NodeWithCtrlWidget):
    """Calculate Tidal Efficiency comparing given river and groundwater hydrogrpahs"""
    nodeName = "tidalEfficiency"


    def __init__(self, name, parent=None):
        terms = {'df': {'io': 'in'},
                 'matched_peaks': {'io': 'in'},
                 'E': {'io': 'out'}}
        super(tidalEfficiencyNode, self).__init__(name, parent=parent, terminals=terms, color=(250, 250, 150, 150))
        self._ctrlWidget = tidalEfficiencyNodeCtrlWidget(parent=self)

        
    def process(self, df, matched_peaks):
        E = None
        self._ctrlWidget.p.param('E = ').setValue(str(E))
        with BusyCursor():
            df = returnPandasDf(df)
            matched_peaks = returnPandasDf(matched_peaks)

            colname = [col for col in df.columns if not isNumpyDatetime(df[col].dtype)]
            self._ctrlWidget.p.param('river').setLimits(colname)
            self._ctrlWidget.p.param('gw').setLimits(colname)
            colname = [None]+[col for col in df.columns if isNumpyDatetime(df[col].dtype)]
            self._ctrlWidget.p.param('datetime').setLimits(colname)
            
            kwargs = self.ctrlWidget().evaluateState()
            
            if kwargs['method'] == '1) STD':
                E = tidalEfficiency_method1(df, kwargs['river'], kwargs['gw'])

            elif kwargs['method'] == '2) Cyclic amplitude':
                # select only valid cycles
                df_slice = matched_peaks.loc[~matched_peaks['md_N'].isin([np.nan, None])]
                E = tidalEfficiency_method2(df_slice['tidehub'], df_slice['md_tidehub'])

            elif kwargs['method'] == '3) Cyclic STD':
                E = tidalEfficiency_method3(df, kwargs['river'], kwargs['gw'], kwargs['datetime'], peaks_w, peaks_gw)
            else:
                raise Exception('Method <%s> not yet implemented' % kwargs['method'])
        
            self._ctrlWidget.p.param('E = ').setValue(str(E))
            return {'E': E}


    def process_method_2(self, mp_df):
        # select only valid cycles
        df_slice = mp_df.loc[mp_df['md_N'] not in [np.nan, None]]
        return tidalEfficiency_method2(df_slice['tidehub'], df_slice['md_tidehub'])




class tidalEfficiencyNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(tidalEfficiencyNodeCtrlWidget, self).__init__()
        self._parent = parent

        params = self.params()
        ## Create tree of Parameter objects
        self.p = Parameter.create(name='params', type='group', children=params)

        ## set parameter tree to <self> (parameterTreeWidget)
        self.setParameters(self.p, showTop=False)
        self.initConnections()
        # save default state
        self._savedState = self.saveState()

    def initConnections(self):

        self.p.sigValueChanged.connect(self._parent.update)
        self.p.child('Help').sigActivated.connect(self.on_help_clicked)
        self.p.child('river').sigValueChanged.connect(self._parent.update)
        self.p.child('gw').sigValueChanged.connect(self._parent.update)
        self.p.child('datetime').sigValueChanged.connect(self._parent.update)
        self.p.child('method').sigValueChanged.connect(self._parent.update)


    @QtCore.pyqtSlot()  #default signal
    def on_help_clicked(self):
        webbrowser.open('https://github.com/cdd1969/pygwa/blob/gh-pages/node_tidalEfficiency.md')

    
    def params(self):
        params = [
            {'name': 'Help', 'type': 'action'},
            {'name': 'river', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Column name with RIVER hydrograph data'},
            {'name': 'gw', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Column name with GROUNDWATER hydrograph data'},
            {'name': 'datetime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects.'},
            {'name': 'method', 'type': 'list', 'value': '1) STD', 'default': '1) STD', 'values': ['1) STD', '2) Cyclic amplitude', '3) Cyclic STD'], 'tip': 'Method to calculate Tidal Efficiency. Read docs'},
            #{'name': 'Calculate E', 'type': 'action'}
            {'name': 'E = ', 'type': 'str', 'readonly': True, 'value': None}

        ]
        return params


    def saveState(self):
        return self.p.saveState()
    
    def restoreState(self, state):
        self.p.restoreState(state)

    def evaluateState(self, state=None):
        """ function evaluates passed state , reading only necessary parameters,
            those that can be passed to pandas.read_csv() as **kwargs

            user should reimplement this function for each Node"""

        if state is None:
            state = self.saveState()
        listWithDicts = evaluateDict(state['children'], functionToDicts=evaluationFunction, log=False, validArgumnets=['river', 'gw', 'datetime', 'method'])
        kwargs = dict()
        for d in listWithDicts:
            # {'a': None}.items() >>> [('a', None)] => two times indexing
            kwargs[d.items()[0][0]] = d.items()[0][1]
        return kwargs
