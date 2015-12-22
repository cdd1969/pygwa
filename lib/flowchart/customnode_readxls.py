#!/usr/bin python
# -*- coding: utf-8 -*-

import os, sys
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.flowchart.Node import Node
import pandas as pd
from package import Package
from datetime import datetime
import inspect
from pyqtgraph.parametertree import Parameter, ParameterTree
from ..functions.evaluatedictionary import evaluateDict, evaluationFunction
import webbrowser
from pyqtgraph import BusyCursor
from ..common.NodeWithCtrlWidget import NodeWithCtrlWidget



class readXLSNode(NodeWithCtrlWidget):
    """Load EXCEL file into pandas.DataFrame"""
    nodeName = "readXLS"


    def __init__(self, name, parent=None):
        super(readXLSNode, self).__init__(name, parent=parent, terminals={'output': {'io': 'out'}})
        self._ctrlWidget = readXLSNodeCtrlWidget(self)

        
    def process(self, display=True):
        kwargs = self.ctrlWidget().evaluateState()
        with BusyCursor():
            df = pd.read_excel(**kwargs)
        return {'output': Package(df)}
















class readXLSNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(readXLSNodeCtrlWidget, self).__init__()
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
        self.p.child('Load File').sigActivated.connect(self.on_loadfile_clicked)
        self.p.child('Select File').sigActivated.connect(self.on_selectFile_clicked)
        self.p.child('Select File').sigValueChanged.connect(self.on_selectFile_valueChanged)

    @QtCore.pyqtSlot()  #default signal
    def on_loadfile_clicked(self):
        self._parent.update()

    @QtCore.pyqtSlot()  #default signal
    def on_help_clicked(self):
        webbrowser.open('https://github.com/cdd1969/pygwa/blob/gh-pages/node_readXLX.md')

    @QtCore.pyqtSlot()  #default signal
    def on_selectFile_clicked(self):
        fname = None
        filters = "Excel files (*.xls *.xlsx *.xlrd);;All files (*.*)"
        fname = unicode(QtGui.QFileDialog.getOpenFileName(self, 'Open Excel data file', filter=filters)[0])
        if fname:
            self.p.child('Select File').setValue(fname)
            #self.itemWidget(self.p.child('Select File'), 0).setTooltip(fname)
            print self.p.child('Select File').value()
    
    @QtCore.pyqtSlot(object)  #default signal
    def on_selectFile_valueChanged(self, value):
        button  = self.p.child('Select File').items.items()[0][0].button
        fname = self.p.child('Select File').value()

        if fname is not None and os.path.isfile(fname):
            button.setFlat(True)
            button.setToolTip('File is selected: {0}'.format(fname))
            button.setStatusTip('File is selected: {0}'.format(fname))
        else:
            button.setFlat(False)
            button.setToolTip('Select File')
            button.setStatusTip('Select File')



    def params(self):
        params = [
            {'name': 'Help', 'type': 'action'},
            {'name': 'Select File', 'type': 'action', 'value': None},
            {'name': 'Parameters', 'type': 'group', 'children': [
                {'name': 'sheetname', 'type': 'str', 'value': 0, 'default': 0, 'tip': '<string, int, mixed list of strings/ints, or None, default 0>\nStrings are used for sheet names, Integers are used in zero-indexed sheet positions.\nLists of strings/integers are used to request multiple sheets.\nSpecify `None` to get all sheets.\nstr|int -> DataFrame is returned. list|None -> Dict of DataFrames is returned, with \nkeys representing sheets.\nAvailable Cases\n - Defaults to 0 -> 1st sheet as a DataFrame\n - 1 -> 2nd sheet as a DataFrame\n - "Sheet1" -> 1st sheet as a DataFrame\n - [0,1,"Sheet5"] -> 1st, 2nd & 5th sheet as a dictionary of DataFrames\n - None -> All sheets as a dictionary of DataFrames'},
                {'name': 'header', 'type': 'str', 'value': 0, 'default': 0, 'tip': '<int, list of ints, default 0>\nRow (0-indexed) to use for the column labels of the parsed DataFrame. If a list of \nintegers is passed those row positions will be combined into a MultiIndex'},
                {'name': 'skiprows', 'type': 'str', 'value': None, 'default': None, 'tip': '<list-like or integer, default None>\nRows to skip at the beginning (0-indexed)'},
                {'name': 'index_col', 'type': 'str', 'value': None, 'default': None, 'tip': '<int, list of ints, default None>\nColumn (0-indexed) to use as the row labels of the DataFrame. Pass None if there is \nno such column. If a list is passed, those columns will be combined into a\nMultiIndex'},
                {'name': 'converters', 'type': 'text', 'value': None, 'default': None, 'tip': '<dict, default None>\nDict of functions for converting values in certain columns. Keys can either be \nintegers or column labels, values are functions that take one input argument, the \nExcel cell content, and return the transformed content.', 'expanded': False},
                {'name': 'parse_cols', 'type': 'str', 'value': None, 'default': None, 'tip': '< int or list, default None>\n - If None then parse all columns,\n - If int then indicates last column to be parsed\n - If list of ints then indicates list of column numbers to be parsed\n - If string then indicates comma separated list of column names and column ranges \n   (e.g. “A:E” or “A,C,E:F”)'},
                {'name': 'na_values', 'type': 'str', 'value': None, 'default': None, 'tip': '< list-like, default None>\n List of additional strings to recognize as NA/NaN'},
                {'name': 'keep_default_na', 'type': 'bool', 'value': True, 'default': True, 'tip': '<bool, default True>\nIf na_values are specified and keep_default_na is False the default NaN values are \noverridden, otherwise they’re appended to'},
                {'name': 'thousands', 'type': 'str', 'value': None, 'default': None, 'tip': '<str, default None>\nThousands separator for parsing string columns to numeric. Note that this parameter \nis only necessary for columns stored as TEXT in Excel, any numeric columns will \nautomatically be parsed, regardless of display format.'},
                {'name': 'Additional parameters', 'type': 'text', 'value': '#Pass here manually params. For Example:\n#{"verbose": False, "engine": None, "convert_float": True}\n{}', 'expanded': False}
            ]},
            {'name': 'Load File', 'type': 'action'},
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
            function4arguments=pd.read_excel)
        kwargs = dict()
        for d in listWithDicts:
            # {'a': None}.items() = [('a', None)] => two times indexing
            kwargs[d.items()[0][0]] = d.items()[0][1]

        try:
            Additional_kwargs = eval(state['children']['Parameters']['children']['Additional parameters']['value'])
            if isinstance(Additional_kwargs, dict):
                for key, val in Additional_kwargs.iteritems():
                    kwargs[key] = val
        except:
            pass
        kwargs['io'] = state['children']['Select File']['value']

        return kwargs
