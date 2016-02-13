#!/usr/bin python
# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph import BusyCursor
import pandas as pd

from lib.flowchart.nodes.NodeWithCtrlWidget import NodeWithCtrlWidget
from lib.functions.general import returnPandasDf
from lib.functions.evaluatedictionary import evaluateDict, evaluationFunction



class toXLSNode(NodeWithCtrlWidget):
    """Write data to spreadsheet """
    nodeName = "toXLS"


    def __init__(self, name, parent=None):
        super(toXLSNode, self).__init__(name, parent=parent, terminals={'In': {'io': 'in'}}, color=(100, 250, 100, 150))
        self._ctrlWidget = toXLSNodeCtrlWidget(self)

        
    def process(self, In):
        if self._ctrlWidget.saveAllowed():
            kwargs = self.ctrlWidget().evaluateState()
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






class toXLSNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(toXLSNodeCtrlWidget, self).__init__()
        self._parent = parent

        params = self.params()
        ## Create tree of Parameter objects
        self.p = Parameter.create(name='params', type='group', children=params)

        ## set parameter tree to <self> (parameterTreeWidget)
        self.setParameters(self.p, showTop=False)
        self.initConnections()
        # save default state
        self._savedState = self.saveState()
        self._save = False
        self._toClipbord = False

    def initConnections(self):
        self.p.child('Save file').sigActivated.connect(self.on_save_clicked)
        self.p.child('Copy to\nclipboard').sigActivated.connect(self.on_copy2clipboard_clicked)


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

    def params(self):
        params = [
            {'name': 'Parameters', 'type': 'group', 'children': [
                #{'name': 'file path', 'type': 'str', 'value': 'export.xls', 'default': 'export.xls', 'tip': '<string>\nFile path of file to be created'},
                {'name': 'sheet_name', 'type': 'str', 'value': 'Sheet1', 'default': 'Sheet1', 'tip': '<string, default "Sheet1">\nName of sheet which will contain DataFrame'},
                {'name': 'na_rep', 'type': 'str', 'value': "", 'default': "", 'tip': '<string, default "">\nMissing data representation'},
                
                {'name': 'Additional parameters', 'type': 'text', 'value': '#Pass here manually params. For Example:\n#{"float_format": None, "columns": None, "header": True, etc...}\n{}', 'expanded': False}
            ]},
            {'name': 'Copy to\nclipboard', 'type': 'action', 'tip': 'Copy current DataFrame to clipboard, so it can be pasted\nwith CTRL+V into Excel or text-editor'},
            {'name': 'Save file', 'type': 'action', 'tip': 'Generate Excel file'},
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

        if state is None:
            state = self.saveState()

        # ------------------------------------------------------
        # if we wont use manually set params, then collect all params values
        listWithDicts = evaluateDict(state['children'], functionToDicts=evaluationFunction, log=False,
            function4arguments=pd.DataFrame.to_excel)
        kwargs = dict()
        for d in listWithDicts:
            # {'a': None}.items() = [('a', None)] => two times indexing
            kwargs[d.items()[0][0]] = d.items()[0][1]

        # this one has not been included, since the name "file path" will not be recognized with <function4arguments=pd.to_excel> (see above)
        #kwargs['excel_writer'] = state['children']['Parameters']['children']['file path']['value']

        try:
            Additional_kwargs = eval(state['children']['Parameters']['children']['Additional parameters']['value'])
            if isinstance(Additional_kwargs, dict):
                for key, val in Additional_kwargs.iteritems():
                    kwargs[key] = val
        except:
            pass

        return kwargs
