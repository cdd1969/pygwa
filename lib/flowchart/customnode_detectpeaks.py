#!/usr/bin python
# -*- coding: utf-8 -*-

import os, sys
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.flowchart.Node import Node
import numpy as np
from package import Package
import inspect
from pyqtgraph.parametertree import Parameter, ParameterTree
from ..functions.detectpeaks import detectPeaks
from ..functions.evaluatedictionary import evaluateDict, evaluationFunction
import webbrowser
from ..common.NodeWithCtrlWidget import NodeWithCtrlWidget


class detectPeaksNode(NodeWithCtrlWidget):
    """Detect peaks (minima/maxima) from passed signal"""
    nodeName = "detectPeaks"


    def __init__(self, name, parent=None):
        super(detectPeaksNode, self).__init__(name, parent=parent, terminals={'In': {'io': 'in'}})
        self._ctrlWidget = detectPeaksNodeCtrlWidget(parent=self)
        self._outputTerminalNames_MinMax = ['val:min', 'ind:min', 'val:max', 'ind:max']
        self._outputTerminalNames_All    = ['val', 'ind']
        self._mode = 'all'
        self.changeOutTerminals(split=False)

        
    def process(self, In):
        if not isinstance(In, np.ndarray):
            self.In.setValueAcceptable(False)
            raise Exception("Input must be ndarray. Received: {0}".format(type(In)))

        kwargs = self._ctrlWidget.evaluateState()
        vals, indices = detectPeaks(In, **kwargs)

        out = dict()
        if self._mode == 'all':
            out['val'] = vals[0]
            out['ind'] = indices[0]
        elif self._mode == 'minmax':
            out['val:min'] = vals[0]
            out['ind:min'] = indices[0]
            out['val:max'] = vals[1]
            out['ind:max'] = indices[1]
        else:
            raise KeyError('Invalid mode Received {0}'.format(self._mode))

        return out
        
    def restoreState(self, state):
        """overriding stadart Node method to extend it with restoring ctrlWidget state"""
        NodeWithCtrlWidget.restoreState(self, state)
        self.updateWithoutArgs()

    @QtCore.pyqtSlot(bool)
    def changeOutTerminals(self, split=None):
        # split - split output into two categories min/max. If False - do not split and use all peaks together
        for termName in self.outputs():
            self.removeTerminal(termName)

        if split is None:
            split = self._ctrlWidget.p.child('split').value()
        
        if split is False:
            self._mode = 'all'
            termNames = self._outputTerminalNames_All
        else:
            self._mode = 'minmax'
            termNames = self._outputTerminalNames_MinMax

        for termName in termNames:
                self.addOutput(termName)


    def updateWithoutArgs(self):
        print 'update without args'
        self.changeOutTerminals()
        self.update()






class detectPeaksNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(detectPeaksNodeCtrlWidget, self).__init__()
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

        self.p.sigValueChanged.connect(self._parent.updateWithoutArgs)
        self.p.child('Help').sigActivated.connect(self.on_help_clicked)
        self.p.child('split').sigValueChanged.connect(self._parent.updateWithoutArgs)
        self.p.child('order').sigValueChanged.connect(self._parent.update)
        self.p.child('removeRegions').sigValueChanged.connect(self._parent.update)
        self.p.child('mode').sigValueChanged.connect(self._parent.update)


    @QtCore.pyqtSlot()  #default signal
    def on_help_clicked(self):
        webbrowser.open('https://github.com/cdd1969/pygwa/blob/gh-pages/node_detectPeaks.md')

    
    def params(self):
        params = [
            {'name': 'Help', 'type': 'action'},
            {'name': 'order', 'type': 'int', 'value': 100, 'default': 100, 'limits': (0, int(10e6)), 'tip': 'How many points on each side to use for the comparison'},
            {'name': 'mode', 'type': 'list', 'values': ['clip', 'wrap'], 'value': 'clip', 'default': 'clip', 'tip': 'How the edges of the vector are treated. ‘wrap’ (wrap around)\nor ‘clip’ (treat overflow as the same as the last (or first) element)'},
            {'name': 'split', 'type': 'bool', 'value': False, 'default': False, 'tip': "If checked -> treat minima/maxima peaks separately\nif not -> together"},
            {'name': 'removeRegions', 'type': 'bool', 'value': True, 'default': True, 'tip': "remove possible multiple peaks that go one-by-one"}
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
        listWithDicts = evaluateDict(state['children'], functionToDicts=evaluationFunction, log=False, function4arguments=detectPeaks)
        kwargs = dict()
        for d in listWithDicts:
            # {'a': None}.items() >>> [('a', None)] => two times indexing
            kwargs[d.items()[0][0]] = d.items()[0][1]
        return kwargs
