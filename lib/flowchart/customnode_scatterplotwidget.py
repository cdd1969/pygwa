#!/usr/bin python
# -*- coding: utf-8 -*-

import os, sys
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from pyqtgraph.parametertree import Parameter, ParameterTree
import webbrowser
import pyqtgraph.parametertree.parameterTypes as pTypes

from ..common.NodeWithCtrlWidget import NodeWithCtrlWidget
from ..functions.general import returnPandasDf
from ..ScatterPlotWidget import ScatterPlotWidget


class scatterPlotWidgetNode(NodeWithCtrlWidget):
    """Explore data as scatter plot"""
    nodeName = "ScatterPlot"


    def __init__(self, name, parent=None):
        super(scatterPlotWidgetNode, self).__init__(name, parent=parent, terminals={'In': {'io': 'in'}}, color=(150, 150, 250, 200))
        self._ctrlWidget = scatterPlotWidgetNodeCtrlWidget(parent=self)

        
    def process(self, In):
        if isinstance(In, np.recarray):
            receivedColumns = In.dtype.names
        else:
            In = returnPandasDf(In, raiseException=False)
            if In is not None:
                receivedColumns = In.columns
            else:
                self.deleteAllColumns()
                self._ctrlWidget.setFields()
                return

        for colName in receivedColumns:
            self._ctrlWidget.addDfColumn(colName)
            self._ctrlWidget.p.child(colName).child('name').setValue(colName)

        self._ctrlWidget.spw().setData(In)
        self._ctrlWidget.setFields()
        return

        
    def restoreState(self, state):
        """overriding standard Node method to extend it with restoring ctrlWidget state"""
        NodeWithCtrlWidget.restoreState(self, state, update=True)

    @QtCore.pyqtSlot(object, object)
    def updateColumns(self, sender, value):
        """ update only one column..."""
        #sender name is... sender.name() (this is the name of the PushButton >>> "Plot"),
        # so the name of the column is the name of the parent parameter group
        cn  = sender.parent().name()
        self._columnsToUpdate.append(cn)

        self.update()

    def deleteAllColumns(self):
        currentColumns = [item.name() for item in self._ctrlWidget.p.children()]
        currentColumns.remove('Help')  # we have this Extra button
        currentColumns.remove('Plot')  # we have this Extra button
        for colName in currentColumns:
            self._ctrlWidget.removeDfColumn(colName)


    def close(self):
        self._ctrlWidget.spw().hide()
        self._ctrlWidget.spw().close()

        NodeWithCtrlWidget.close(self)
        






class scatterPlotWidgetNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(scatterPlotWidgetNodeCtrlWidget, self).__init__()
        self._parent = parent

        params = self.params()
        ## Create tree of Parameter objects
        self.p = Parameter.create(name='params', type='group', children=params)

        ## set parameter tree to <self> (parameterTreeWidget)
        self.setParameters(self.p, showTop=False)
        self.initConnections()
        # save default state
        self._savedState = self.saveState()

        self._spw = ScatterPlotWidget(self)


    def spw(self):
        return self._spw


    def initConnections(self):
        #self.p.sigValueChanged.connect(self._parent.updateColumns)
        self.p.child('Help').sigActivated.connect(self.on_help_clicked)
        self.p.child('Plot').sigActivated.connect(self.on_plot_clicked)

    

    @QtCore.pyqtSlot()  #default signal
    def on_plot_clicked(self):
        if self._spw.isHidden():
            self.setFields()
            self._spw.show()
        else:
            self._spw.hide()
        #self._spw.show()

    @QtCore.pyqtSlot()  #default signal
    def on_help_clicked(self):
        webbrowser.open('https://github.com/cdd1969/pygwa/blob/gh-pages/node_interpolateDf.md')
    
    @QtCore.pyqtSlot(object)  #default signal
    def on_param_valueChanged(self, sender):
        self.setFields()

    
    def params(self):
        params = [
            {'name': 'Help', 'type': 'action'},
            {'name': 'Plot', 'type': 'action'},
            ]

        return params

    def addDfColumn(self, columnName):
        columnParam = columnScatterPlotWidgetGroupParameter(name=columnName)
        self.p.addChild(columnParam)
        
        self.p.child(columnName).child('name').sigValueChanged.connect(self.on_param_valueChanged)
        self.p.child(columnName).child('units').sigValueChanged.connect(self.on_param_valueChanged)
 


    def removeDfColumn(self, columnName):
        self.p.child(columnName).child('name').sigValueChanged.disconnect()
        self.p.child(columnName).child('units').sigValueChanged.disconnect()
        self.p.removeChild(self.p.child(columnName))


    def saveState(self):
        return self.p.saveState()
    
    def restoreState(self, state):

        # here i wold have to probably add constructor of the missing params
        #self.restoreState(state)
        pass

    def evaluateState(self, state=None):
        """ function evaluates passed state , reading only necessary parameters,
            those that can be passed to pandas.read_csv() as **kwargs

            user should re-implement this function for each Node"""

        if state is None:
            state = self.saveState()
        fields = list()
        for child in self.p.children():
            if child.name() not in ['Help', 'Plot']:
                field = (child.name(), {'units': child.param('units').value()})
                fields.append(field)
        
        return fields

    def setFields(self, fields=None):
        if fields is None:
            fields = self.evaluateState()
        self._spw.setFields(fields)




class columnScatterPlotWidgetGroupParameter(pTypes.GroupParameter):
    """ this parameter will be added for each column of the received
        DataDrame

    """
    def __init__(self, shortType=True, **opts):
        opts['type'] = 'bool'
        opts['value'] = True
        opts['expanded'] = False
        self._shortType = shortType
        pTypes.GroupParameter.__init__(self, **opts)
        
        self.addChild({'name': 'name', 'type': 'str', 'value': None, 'default': None, 'readonly': True, 'tip': ''})  # it can be extended to be editable
        self.addChild({'name': 'units', 'type': 'str', 'value': None, 'default': None, 'tip': ''})
        
        if self._shortType is False:
            '''
            The parameters `units`, `mode`, `values` are same as *fields* used by
            :func:`ColorMapWidget.setFields <pyqtgraph.widgets.ColorMapWidget.ColorMapParameter.setFields>`
            '''
            self.addChild({'name': 'mode', 'type': 'list', 'value': 'range', 'values': ['range', 'enum'], 'tip': "Either 'range' or 'enum' (default is range). For 'range',The user may specify a gradient of colors to be applied\n(linearly across a specific range of values. For 'enum',\nthe user specifies a single color for each unique value\nsee *values* option)."})
            self.addChild({'name': 'values', 'type': 'str', 'value': None, 'default': None, 'tip': "String indicating the units of the data for this field.\nList of unique values for which the user may assign a\ncolor when mode=='enum'. Optionally may specify a dict\ninstead {value: name}."})
