#!/usr/bin python
# -*- coding: utf-8 -*-

import os, sys
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.flowchart.Node import Node
import pandas as pd
from package import Package

from pyqtgraph.parametertree import Parameter, ParameterTree
from ..functions.evaluatedictionary import evaluateDict, evaluationFunction
import webbrowser
from pyqtgraph import BusyCursor


class toXLSNode(Node):
    """Write pandas.DataFrame to a excel sheet """
    nodeName = "export to Excel"


    def __init__(self, name, parent=None):
        super(toXLSNode, self).__init__(name, terminals={'In': {'io': 'in'}})
        self._ctrlWidget = toXLSNodeCtrlWidget(self)

        
    def process(self, In):
        print 'process is called'
        if self._ctrlWidget.saveAllowed():
            print 'processing!'
            kwargs = self.ctrlWidget().evaluateState()
            with BusyCursor():
                if isinstance(In, (pd.DataFrame, pd.Series)):
                    In.to_excel(**kwargs)
                elif isinstance(In, Package):
                    In.unpack().to_excel(**kwargs)

                else:
                    raise TypeError('Unsupported data received. Expected pandas.DataFrame or Package, received:', type(In))
            #show message box...
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Information)
            msg.setText('file saved at:\n'+os.path.abspath(kwargs['excel_writer']))
            msg.setWindowTitle("File saved successfully!")
            msg.setStandardButtons(QtGui.QMessageBox.Ok)
            msg.exec_()
        return

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

    def initConnections(self):
        self.p.child('Help').sigActivated.connect(self.on_help_clicked)
        self.p.child('Save file').sigActivated.connect(self.on_save_clicked)

    @QtCore.pyqtSlot()  #default signal
    def on_help_clicked(self):
        webbrowser.open('https://github.com/cdd1969/pygwa/blob/gh-pages/node_toXLS.md')

    @QtCore.pyqtSlot()  #default signal
    def on_save_clicked(self):
        self._save = True
        self._parent.update()  #we want to update only with this flag enabled, not when terminal is connected
        self._save = False

    def saveAllowed(self):
        return self._save

    def params(self):
        params = [
            {'name': 'Help', 'type': 'action'},
            {'name': 'Parameters', 'type': 'group', 'children': [
                {'name': 'file path', 'type': 'str', 'value': 'export.xlsx', 'default': 'export.xlsx', 'tip': '<string>\nFile path of file to be created'},
                {'name': 'sheet_name', 'type': 'str', 'value': 'Sheet1', 'default': 'Sheet1', 'tip': '<string, default "Sheet1">\nName of sheet which will contain DataFrame'},
                {'name': 'na_rep', 'type': 'str', 'value': "", 'default': "", 'tip': '<string, default "">\nMissing data representation'},
                
                {'name': 'Additional parameters', 'type': 'text', 'value': '#Pass here manually params. For Example:\n#{"float_format": None, "columns": None, "header": True, etc...}\n{}', 'expanded': False}
            ]},
            {'name': 'Save file', 'type': 'action'},
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
        kwargs['excel_writer'] = state['children']['Parameters']['children']['file path']['value']

        try:
            Additional_kwargs = eval(state['children']['Parameters']['children']['Additional parameters']['value'])
            if isinstance(Additional_kwargs, dict):
                for key, val in Additional_kwargs.iteritems():
                    kwargs[key] = val
        except:
            pass

        return kwargs
