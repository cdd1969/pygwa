#!/usr/bin python
# -*- coding: utf-8 -*-
import numpy as np
from pyqtgraph.Qt import QtCore
import pyqtgraph.parametertree.parameterTypes as pTypes

from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.common.ScatterPlotWidget import ScatterPlotWidget
from lib.functions.general import returnPandasDf


class scatterPlotWidgetNode(NodeWithCtrlWidget):
    """Explore data with a scatter plot widget"""
    nodeName = "ScatterPlot"
    uiTemplate = [ {'name': 'Plot', 'type': 'action'}]

    def __init__(self, name, parent=None):
        super(scatterPlotWidgetNode, self).__init__(name, parent=parent, terminals={'In': {'io': 'in'}}, color=(150, 150, 250, 200))
    
    def _createCtrlWidget(self, **kwargs):
        return scatterPlotWidgetNodeCtrlWidget(**kwargs)
        
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
            self._ctrlWidget.param(colName, 'name').setValue(colName)

        self._ctrlWidget.spw().setData(In)
        self._ctrlWidget.setFields()
        return

    def restoreState(self, state):
        """overriding standard Node method to extend it with restoring ctrlWidget state"""
        super(scatterPlotWidgetNode, self).restoreState(state, update=True)

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
        currentColumns.remove('Plot')  # we have this Extra button
        for colName in currentColumns:
            self._ctrlWidget.removeDfColumn(colName)

    def close(self):
        self._ctrlWidget.spw().hide()
        self._ctrlWidget.spw().close()
        NodeWithCtrlWidget.close(self)


class scatterPlotWidgetNodeCtrlWidget(NodeCtrlWidget):
    
    def __init__(self, **kwargs):
        super(scatterPlotWidgetNodeCtrlWidget, self).__init__(update_on_statechange=False, **kwargs)
        self._spw = ScatterPlotWidget(self)

    def initUserSignalConnections(self):
        self.param('Plot').sigActivated.connect(self.on_plot_clicked)

    def spw(self):
        return self._spw

    @QtCore.pyqtSlot()  #default signal
    def on_plot_clicked(self):
        if self._spw.isHidden():
            self.setFields()
            self._spw.show()
        else:
            self._spw.hide()

    @QtCore.pyqtSlot(object)  #default signal
    def on_param_valueChanged(self, sender):
        self.setFields()

    def addDfColumn(self, columnName):
        columnParam = columnScatterPlotWidgetGroupParameter(name=columnName)
        self.p.addChild(columnParam)
        
        self.param(columnName, 'name').sigValueChanged.connect(self.on_param_valueChanged)
        self.param(columnName, 'units').sigValueChanged.connect(self.on_param_valueChanged)

    def removeDfColumn(self, columnName):
        self.param(columnName, 'name').sigValueChanged.disconnect()
        self.param(columnName, 'units').sigValueChanged.disconnect()
        self.p.removeChild(self.param(columnName))
    
    def restoreState(self, state):
        # here i wold have to probably add constructor of the missing params
        #self.restoreState(state)
        pass

    def evaluateState(self):
        fields = list()
        for child in self.params(recursive=False):
            if child.name() != 'Plot':
                field = (child.name(), {'units': child.child('units').value()})
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
