#!/usr/bin python
# -*- coding: utf-8 -*-

import os
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import BusyCursor
import pandas as pd

from lib.flowchart.package import Package
from lib.functions.general import getCallableArgumentList
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget



class readXLSNode(NodeWithCtrlWidget):
    """Read data from spreadsheet"""
    nodeName = "readXLS"
    uiTemplate = [
            {'name': 'Select File', 'type': 'action', 'value': None},
            {'name': 'Parameters', 'type': 'group', 'children': [
                {'name': 'sheetname', 'type': 'str', 'value': 0, 'default': 0, 'tip': '<string, int, mixed list of strings/ints, or None, default 0>\nStrings are used for sheet names, Integers are used in zero-indexed sheet positions.\nLists of strings/integers are used to request multiple sheets.\nSpecify `None` to get all sheets.\nstr|int -> DataFrame is returned. list|None -> Dict of DataFrames is returned, with \nkeys representing sheets.\nAvailable Cases\n - Defaults to 0 -> 1st sheet as a DataFrame\n - 1 -> 2nd sheet as a DataFrame\n - "Sheet1" -> 1st sheet as a DataFrame\n - [0,1,"Sheet5"] -> 1st, 2nd & 5th sheet as a dictionary of DataFrames\n - None -> All sheets as a dictionary of DataFrames'},
                {'name': 'header', 'type': 'str', 'value': 0, 'default': 0, 'tip': '<int, list of ints, default 0>\nRow (0-indexed) to use for the column labels of the parsed DataFrame. If a list of \nintegers is passed those row positions will be combined into a MultiIndex'},
                {'name': 'skiprows', 'type': 'str', 'value': None, 'default': None, 'tip': '<list-like or integer, default None>\nRows to skip at the beginning (0-indexed)'},
                {'name': 'skip_footer', 'type': 'str', 'value': 0, 'default': 0, 'tip': '< int, default 0>\nRows at the end to skip (0-indexed)'},
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

    def __init__(self, name, parent=None):
        super(readXLSNode, self).__init__(name, parent=parent, terminals={'output': {'io': 'out'}}, color=(100, 250, 100, 150))
    
    def _createCtrlWidget(self, **kwargs):
        return readXLSNodeCtrlWidget(**kwargs)
        
    def process(self, display=True):
        kwargs = self.ctrlWidget().prepareInputArguments()
        with BusyCursor():
            df = pd.read_excel(**kwargs)
        return {'output': Package(df)}





class readXLSNodeCtrlWidget(NodeCtrlWidget):
    
    def __init__(self, **kwargs):
        super(readXLSNodeCtrlWidget, self).__init__(update_on_statechange=False, **kwargs)

    def initUserSignalConnections(self):
        self.param('Load File').sigActivated.connect(self._parent.update)
        self.param('Select File').sigActivated.connect(self.on_selectFile_clicked)
        self.param('Select File').sigValueChanged.connect(self.on_selectFile_valueChanged)

    @QtCore.pyqtSlot()  #default signal
    def on_selectFile_clicked(self):
        fname = None
        filters = "Excel Spreadsheet (*.xls *.xlsx *.xlrd);; All files (*.*)"
        fname = unicode(QtGui.QFileDialog.getOpenFileName(self, 'Open Spreadsheet Data File', filter=filters)[0])
        if fname:
            self.param('Select File').setValue(fname)

    
    @QtCore.pyqtSlot(object)  #default signal
    def on_selectFile_valueChanged(self, value):
        button  = self.param('Select File').items.items()[0][0].button
        fname = self.param('Select File').value()

        if fname is not None and os.path.isfile(fname):
            button.setToolTip('File is selected: {0}'.format(fname))
            button.setStatusTip('File is selected: {0}'.format(fname))
        else:
            button.setToolTip('Select File')
            button.setStatusTip('Select File')
    
    def prepareInputArguments(self):
        valid_arg_list = getCallableArgumentList(pd.read_excel, get='args')
        kwargs = dict()

        for param in self.params():
            if param.name() in valid_arg_list and self.p.evaluateValue(param.value()) != '':
                kwargs[param.name()] = self.p.evaluateValue(param.value())

        kwargs['io'] = self.paramValue('Select File')
        return kwargs
