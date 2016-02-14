#!/usr/bin python
# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import BusyCursor
import pandas as pd

from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.general import returnPandasDf, getCallableArgumentList



class toXLSNode(NodeWithCtrlWidget):
    """Write data to spreadsheet or copy to clipboard"""
    nodeName = "writeXLS"
    uiTemplate = [
            {'name': 'Parameters', 'type': 'group', 'children': [
                {'name': 'sheet_name', 'type': 'str', 'value': 'Sheet1', 'default': 'Sheet1', 'tip': '<string, default "Sheet1">\nName of sheet which will contain DataFrame'},
                {'name': 'na_rep', 'type': 'str', 'value': "", 'default': "", 'tip': '<string, default "">\nMissing data representation'},
                {'name': 'Additional parameters', 'type': 'text', 'value': '#Pass here manually params. For Example:\n#{"float_format": None, "columns": None, "header": True, etc...}\n{}', 'expanded': False}
            ]},
            {'name': 'Copy to\nclipboard', 'type': 'action', 'tip': 'Copy current DataFrame to clipboard, so it can be pasted\nwith CTRL+V into Excel or text-editor'},
            {'name': 'Save file', 'type': 'action', 'tip': 'Generate Excel file'},
        ]

    def __init__(self, name, parent=None):
        super(toXLSNode, self).__init__(name, parent=parent, terminals={'In': {'io': 'in'}}, color=(100, 250, 100, 150))
    
    def _createCtrlWidget(self, **kwargs):
        return toXLSNodeCtrlWidget(**kwargs)
        
    def process(self, In):
        if self._ctrlWidget.saveAllowed():
            kwargs = self.ctrlWidget().prepareInputArguments()
            df = returnPandasDf(In)
            fileName = QtGui.QFileDialog.getSaveFileName(None, "Save As..", "export.xlsx", "Excel files (*.xls *.xlsx)")[0]
            if fileName:
                with BusyCursor():
                    df.to_excel(fileName, **kwargs)
                
        if self._ctrlWidget.toClipbord():
            with BusyCursor():
                df = returnPandasDf(In)
                df.to_clipboard(excel=True)
        return



class toXLSNodeCtrlWidget(NodeCtrlWidget):
    
    def __init__(self, **kwargs):
        super(toXLSNodeCtrlWidget, self).__init__(update_on_statechange=False, **kwargs)
        self._save = False
        self._toClipbord = False

    def initUserSignalConnections(self):
        self.param('Save file').sigActivated.connect(self.on_save_clicked)
        self.param('Copy to\nclipboard').sigActivated.connect(self.on_copy2clipboard_clicked)

    @QtCore.pyqtSlot()  #default signal
    def on_save_clicked(self):
        self._save = True
        self._parent.update()  #we want to update only with this flag enabled, not when terminal is connected
        self._save = False

    @QtCore.pyqtSlot()  #default signal
    def on_copy2clipboard_clicked(self):
        self._toClipbord = True
        self._parent.update()  #we want to update only with this flag enabled, not when terminal is connected
        self._toClipbord = False

    def toClipbord(self):
        return self.toClipbord

    def saveAllowed(self):
        return self._save
    
    def prepareInputArguments(self):
        valid_arg_list = getCallableArgumentList(pd.DataFrame.to_excel, get='args')
        kwargs = dict()

        for param in self.params():
            if param.name() in valid_arg_list and self.p.evaluateValue(param.value()) != '':
                kwargs[param.name()] = self.p.evaluateValue(param.value())
        try:
            Additional_kwargs = self.paramValue('Parameters', 'Additional parameters', datatype=dict)
            if isinstance(Additional_kwargs, dict):
                kwargs.update(Additional_kwargs)
        except:
            pass
        return kwargs
