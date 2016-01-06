#!/usr/bin python
# -*- coding: utf-8 -*-

import os, sys
from pyqtgraph.Qt import QtCore, QtGui
from package import Package
from pyqtgraph.parametertree import Parameter, ParameterTree
from ..functions.detectpeaks import detectPeaks_ts, plot_signal_peaks_and_errors
from ..functions.evaluatedictionary import evaluateDict, evaluationFunction
import webbrowser
from ..common.NodeWithCtrlWidget import NodeWithCtrlWidget
from ..functions.general import returnPandasDf, isNumpyDatetime
from pyqtgraph import BusyCursor


class detectPeaksTSNode(NodeWithCtrlWidget):
    """Detect peaks (minima/maxima) from passed TimeSeries, check period"""
    nodeName = "detectPeaks_ts"


    def __init__(self, name, parent=None):
        super(detectPeaksTSNode, self).__init__(name, parent=parent, terminals={'In': {'io': 'in'}, 'peaks': {'io': 'out'}}, color=(250, 250, 150, 150))
        self._ctrlWidget = detectPeaksTSNodeCtrlWidget(parent=self)
        self._plotRequired = False

        
    def process(self, In):
        self._ctrlWidget.p.child('Period Check Params').child('Errors').setValue('?')
        df = returnPandasDf(In)
        colname = [col for col in df.columns if not isNumpyDatetime(df[col].dtype)]
        self._ctrlWidget.p.param('column').setLimits(colname)
        colname = [None]+[col for col in df.columns if isNumpyDatetime(df[col].dtype)]
        self._ctrlWidget.p.param('datetime').setLimits(colname)

        kwargs = self._ctrlWidget.evaluateState()
        with BusyCursor():
            peaks = detectPeaks_ts(df, kwargs.pop('column'), plot=self._plotRequired, **kwargs)
            self._ctrlWidget.p.child('Period Check Params').child('Errors').setValue(len(peaks[peaks['check'] == False]))
            
        return {'peaks': Package(peaks)}

    def plot(self):
        self._plotRequired = True
        self.update()
        self._plotRequired = False





class detectPeaksTSNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(detectPeaksTSNodeCtrlWidget, self).__init__()
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
        self.p.child('Plot').sigActivated.connect(self._parent.plot)
        self.p.child('column').sigValueChanged.connect(self._parent.update)
        self.p.child('datetime').sigValueChanged.connect(self._parent.update)
        self.p.child('Peak Detection Params').child('order').sigValueChanged.connect(self._parent.update)
        self.p.child('Peak Detection Params').child('mode').sigValueChanged.connect(self._parent.update)
        self.p.child('Peak Detection Params').child('removeRegions').sigValueChanged.connect(self._parent.update)
        self.p.child('Period Check Params').child('T').sigValueChanged.connect(self._parent.update)
        self.p.child('Period Check Params').child('hMargin').sigValueChanged.connect(self._parent.update)




    @QtCore.pyqtSlot()  #default signal
    def on_help_clicked(self):
        webbrowser.open('https://github.com/cdd1969/pygwa/blob/gh-pages/node_detectPeaks_ts.md')

    
    def params(self):
        params = [
            {'name': 'Help', 'type': 'action'},
            {'name': 'column', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Column name with hydrograph data'},
            {'name': 'datetime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects.'},
            {'name': 'Peak Detection Params', 'type': 'group', 'children': [
                {'name': 'order', 'type': 'int', 'value': 100, 'default': 100, 'limits': (0, int(10e6)), 'tip': 'How many points on each side to use for the comparison'},
                {'name': 'mode', 'type': 'list', 'values': ['clip', 'wrap'], 'value': 'clip', 'default': 'clip', 'tip': 'How the edges of the vector are treated. ‘wrap’ (wrap around)\nor ‘clip’ (treat overflow as the same as the last (or first) element)'},
                {'name': 'removeRegions', 'type': 'bool', 'value': True, 'readonly': True, 'default': True, 'tip': "remove possible multiple peaks that go one-by-one"}
            ]},
            {'name': 'Period Check Params', 'type': 'group', 'children': [
                {'name': 'T', 'type': 'str', 'value': 12.42, 'default': None, 'tip': 'Awaited period of the signal in hours. If `None`, will calculate\nthe Period `T` as the mean of difference between peaks, multiplied\nby two (i.e. T = peaks["time"].diff().mean()*2)'},
                {'name': 'hMargin', 'type': 'int', 'value': 1, 'default': 1, 'limits': (0, int(10e6)), 'tip': 'Number of hours, safety margin when comparing period length.\nSee formula below:\nT/2 - hMargin < T_i/2 < T/2 + hMargin'},
                {'name': 'Errors', 'type': 'str', 'value': '?', 'default': '?', 'tip': 'Number of errors detected after detecting peaks.\nErrors are raised where period condition is not met.\tHit `Plot` button to visualize errors', 'readonly': True},
            ]},
            {'name': 'Plot', 'type': 'action'},
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
        listWithDicts = evaluateDict(state['children'], functionToDicts=evaluationFunction, log=False, validArgumnets=['column', 'T', 'datetime', 'hMargin', 'mode', 'order', 'removeRegions'])
        kwargs = dict()
        for d in listWithDicts:
            # {'a': None}.items() >>> [('a', None)] => two times indexing
            kwargs[d.items()[0][0]] = d.items()[0][1]
        return kwargs
