#!/usr/bin python
# -*- coding: utf-8 -*-

import os, sys
from pyqtgraph.Qt import QtCore, QtGui
from package import Package
from pyqtgraph.parametertree import Parameter, ParameterTree
from ..functions.evaluatedictionary import evaluateDict, evaluationFunction
import webbrowser
from ..common.NodeWithCtrlWidget import NodeWithCtrlWidget
from ..functions.general import returnPandasDf, isNumpyDatetime
from pyqtgraph import BusyCursor, PlotDataItem
import numpy as np
import pandas as pd



class makeTimeseriesCurveNode(NodeWithCtrlWidget):
    """Prepare Timeseries for plotting. Generate curve that can be viewed with node *TimeseriesPlot*
    and pd.Series with datetime stored in Index
    """
    nodeName = "makeTimeseriesCurve"


    def __init__(self, name, parent=None):
        super(makeTimeseriesCurveNode, self).__init__(name, parent=parent, terminals={'df': {'io': 'in'}, 'pd.Series': {'io': 'out'}, 'Curve': {'io': 'out'}}, color=(150, 150, 250, 150))
        self._ctrlWidget = makeTimeseriesCurveNodeCtrlWidget(parent=self)
        self._plotRequired = False
        self.item = PlotDataItem(clipToView=False)

        
    def process(self, df):
        df  = returnPandasDf(df)

        colname = [col for col in df.columns if not isNumpyDatetime(df[col].dtype)]
        self._ctrlWidget.p.param('Y:signal').setLimits(colname)
        colname = [None]+[col for col in df.columns if isNumpyDatetime(df[col].dtype)]
        self._ctrlWidget.p.param('X:datetime').setLimits(colname)


        kwargs = self._ctrlWidget.evaluateState()


        with BusyCursor():
            kwargs = self.ctrlWidget().evaluateState()
            t = df[kwargs['X:datetime']].values
            # part 1
            timeSeries = pd.DataFrame(data=df[kwargs['Y:signal']].values, index=t, columns=[kwargs['Y:signal']])

            # part 2
            #   convert time
            b = t.astype(np.dtype('datetime64[s]'))
            timeStamps = b.astype(np.int64)-kwargs['tz correct']*60*60
            #   now create curve
            self.item.setData(timeStamps, df[kwargs['Y:signal']].values, pen=kwargs['color'], name=kwargs['Y:signal'])
            
            return{'Curve': self.item, 'pd.Series': Package(timeSeries) }






class makeTimeseriesCurveNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(makeTimeseriesCurveNodeCtrlWidget, self).__init__()
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
        self.p.child('Help').sigActivated.connect(self.on_help_clicked)

        self.p.child('tz correct').sigValueChanged.connect(self._parent.update)
        self.p.child('Y:signal').sigValueChanged.connect(self._parent.update)
        self.p.child('X:datetime').sigValueChanged.connect(self._parent.update)
        self.p.child('color').sigValueChanged.connect(self._parent.update)





    @QtCore.pyqtSlot()  #default signal
    def on_help_clicked(self):
        webbrowser.open('https://github.com/cdd1969/pygwa/blob/gh-pages/node_match_peaks.md')

    
    def params(self):
        params = [
            {'name': 'Help', 'type': 'action'},

            {'name': 'Y:signal', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Signal Data-Values (Y-axis)'},
            {'name': 'X:datetime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Datetime Values (X-axis)'},
            {'name': 'tz correct', 'type': 'float', 'value': 0, 'default': 0, 'suffix': ' hours', 'tip': '<float>\nONLY FOR CURVE!!!\nTimezone correction\nNumber of hours to add/substract from result. Due to missing\ntimezone settings it may be nessesary to use this parameter.\nCheck the results manually with *TimeseriesPlot* Node'},
            {'name': 'color', 'type': 'color', 'tip': 'Curve color'},

        
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
        listWithDicts = evaluateDict(state['children'], functionToDicts=evaluationFunction, log=False, validArgumnets=['Y:signal', 'X:datetime', 'tz correct', 'color'])
        kwargs = dict()
        for d in listWithDicts:
            # {'a': None}.items() >>> [('a', None)] => two times indexing
            kwargs[d.items()[0][0]] = d.items()[0][1]

        return kwargs
