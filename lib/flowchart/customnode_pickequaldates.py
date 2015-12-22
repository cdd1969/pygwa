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


class pickEqualDatesNode(Node):
    """Pick values which correspond to datetimes in other DataFame"""
    nodeName = "pickEqualDates"


    def __init__(self, name, parent=None):
        super(pickEqualDatesNode, self).__init__(name, terminals={'datePattern': {'io': 'in'}, 'toPick': {'io': 'in'}, 'Out': {'io': 'out'}})
        self._ctrlWidget = pickEqualDatesNodeCtrlWidget(self)

        
    def process(self, datePattern, toPick):
        gc.collect()
        with BusyCursor():
            df1 = returnPandasDf(toPick)
            df2 = returnPandasDf(datePattern)

            colname = [None]+[col for col in df1.columns if isNumpyDatetime(df1[col].dtype)]
            self._ctrlWidget.p.param('datetime <datePattern>').setLimits(colname)
            colname = [None]+[col for col in df2.columns if isNumpyDatetime(df2[col].dtype)]
            self._ctrlWidget.p.param('datetime <toPick>').setLimits(colname)
            
            kwargs = self.ctrlWidget().evaluateState()

            print kwargs
            if kwargs['datetime <datePattern>'] is None and kwargs['datetime <toPick>'] is None:
                selector = df1.index.isin(df2.index)
            elif kwargs['datetime <datePattern>'] is not None and kwargs['datetime <toPick>'] is None:
                selector = df1[kwargs['datetime <datePattern>']].isin(df2.index)
            elif kwargs['datetime <datePattern>'] is None and kwargs['datetime <toPick>'] is not None:
                selector = df1.index.isin(df2[kwargs['datetime <toPick>']])
            elif kwargs['datetime <datePattern>'] is not None and kwargs['datetime <toPick>'] is not None:
                selector = df1[kwargs['datetime <datePattern>']].isin(df2[kwargs['datetime <toPick>']])
            selectedDf = df1[selector]
            return {'Out': Package(selectedDf)}


    def ctrlWidget(self):
        return self._ctrlWidget

    def saveState(self):
        """overriding stadart Node method to extend it with saving ctrlWidget state"""
        state = Node.saveState(self)
        # sacing additionaly state of the control widget
        state['crtlWidget'] = self.ctrlWidget().saveState()
        return state
        
    def restoreState(self, state):
        """overriding stadart Node method to extend it with restoring ctrlWidget state"""
        Node.restoreState(self, state)
        # additionally restore state of the control widget
        self.ctrlWidget().restoreState(state['crtlWidget'])
        #self.update()  # we do not call update() since we want to process only on LoadButton clicked



class pickEqualDatesNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(pickEqualDatesNodeCtrlWidget, self).__init__()
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
        self.p.child('datetime <datePattern>').sigValueChanged.connect(self._parent.update)
        self.p.child('datetime <toPick>').sigValueChanged.connect(self._parent.update)

    @QtCore.pyqtSlot()  #default signal
    def on_help_clicked(self):
        webbrowser.open('https://github.com/cdd1969/pygwa/blob/gh-pages/node_pickequaldates.md')

    def params(self):
        params = [
            {'name': 'Help', 'type': 'action'},
            {'name': 'datetime <datePattern>', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects.\nBy default is `None`, meaning that datetime objects are\nlocated within `pd.DataFrame.index`. If not `None` - pass the\ncolumn-name of dataframe where datetime objects are located.'},
            {'name': 'datetime <toPick>', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects.\nBy default is `None`, meaning that datetime objects are\nlocated within `pd.DataFrame.index`. If not `None` - pass the\ncolumn-name of dataframe where datetime objects are located.'},

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
            'datetime <datePattern>': self.p.param('datetime <datePattern>').value(),
            'datetime <toPick>': self.p.param('datetime <toPick>').value()
        }

        for k, v in kwargs.iteritems():
            if v == 'None':
                kwargs[k] = None
        return kwargs
