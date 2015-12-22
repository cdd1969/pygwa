#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph import BusyCursor
from lib.flowchart.package import Package
import os, sys
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.flowchart.Node import Node
from pyqtgraph.parametertree import Parameter, ParameterTree
from ..functions.general import isNumpyDatetime
import webbrowser
from ..functions.general import returnPandasDf
import gc
import numpy as np
from ..common.NodeWithCtrlWidget import NodeWithCtrlWidget


class datetime2secondsNode(NodeWithCtrlWidget):
    """Convert array of datetime objects to Timestamp (integer, seconds since 1970-01-01)"""
    nodeName = "datetime2sec"


    def __init__(self, name, parent=None):
        super(datetime2secondsNode, self).__init__(name, parent=parent, terminals={'In': {'io': 'in'}, 'Out': {'io': 'out'}})
        self._ctrlWidget = datetime2secondsNodeCtrlWidget(self)

        
    def process(self, In):
        gc.collect()
        if isNumpyDatetime(In.dtype):
            with BusyCursor():
                self._ctrlWidget.p.param('dtype').setValue(str(In.dtype))
                kwargs = self.ctrlWidget().evaluateState()
                b = In.astype(np.dtype('datetime64[s]'))
                return{'Out': b.astype(np.int64)-kwargs['tz correct']*60*60 }
    
    def restoreState(self, state):
        """overriding standard Node method to extend it with restoring ctrlWidget state"""
        NodeWithCtrlWidget.restoreState(self, state, update=True)



class datetime2secondsNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(datetime2secondsNodeCtrlWidget, self).__init__()
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

    @QtCore.pyqtSlot()  #default signal
    def on_help_clicked(self):
        webbrowser.open('https://github.com/cdd1969/pygwa/blob/gh-pages/node_datetime2seconds.md')

    def params(self):
        params = [
            {'name': 'Help', 'type': 'action'},
            {'name': 'dtype', 'type': 'str', 'value': None, 'default': None, 'readonly': True, 'tip': 'data-type of the received object'},
            {'name': 'tz correct', 'type': 'float', 'value': 0, 'default': 0, 'suffix': ' hours', 'tip': '<float>\nTimezone correction\nNumber of hours to add/substract from result. Due to missing\ntimezone settings it may be nessesary to use this parameter. Check the results manually on plot'},

        ]
        return params

    def saveState(self):
        return self.p.saveState()
    
    def restoreState(self, state):
        self.p.restoreState(state)

    def evaluateState(self, state=None):
        """ function evaluates passed state , reading only necessary parameters,
            those that can be passed to pandas.read_csv() as **kwargs (see function4arguments)

            user should reimplement this function for each Node"""

        kwargs = {
            'tz correct': self.p.param('tz correct').value(),
        }

        return kwargs
