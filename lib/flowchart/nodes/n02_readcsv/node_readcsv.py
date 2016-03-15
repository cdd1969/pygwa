#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import BusyCursor
import pandas as pd
import os

from lib.functions.general import getCallableArgumentList
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget


class readCSVNode(NodeWithCtrlWidget):
    """Load column-based data from ASCII file"""
    nodeName = "Read CSV"
    uiTemplate = [
            {'name': 'Select File', 'type': 'action', 'value': None},
            {'name': 'Load CSV parameters', 'type': 'group', 'children': [
                {'name': 'decimal', 'type': 'str', 'value': '.', 'default': '.', 'tip': '<str>\nCharacter to recognize as decimal point. E.g. use ","" for European data'},
                {'name': 'delimiter', 'type': 'str', 'value': ';', 'default': None, 'tip': '<str>\nDelimiter to use. If sep is None, will try to automatically determine this. Regular expressions are accepted'},
                {'name': 'header', 'type': 'str', 'value': 0, 'default': 0, 'tip': '< int, list of ints, default ‘infer’>\nRow number(s) to use as the column names, and the start of the data.\nREAD HELP'},  #dependent on <names>
                {'name': 'skiprows', 'type': 'str', 'value': 0, 'default': None, 'tip': '<list-like or integer, default None>\nLine numbers to skip (0-indexed) or number of lines to skip (int) at the start of the file'},
                {'name': 'parse_dates', 'type': 'str', 'value': False, 'default': False, 'tip': '<boolean, list of ints or names, list of lists, or dict, default False>\nIf True -> try parsing the index. If [1, 2, 3] -> try parsing columns 1, 2, 3 each as a\nseparate date column. If [[1, 3]] -> combine columns 1 and 3 and parse as a single\ndate column. {‘foo’ : [1, 3]} -> parse columns 1, 3 as date and call result ‘foo’ A fast-\npath exists for iso8601-formatted dates.'},
                {'name': 'date_parser', 'type': 'str', 'value': 'lambda x: datetime.strptime(x, "%d.%m.%Y %H:%M")', 'default': 'lambda x: datetime.strptime(x, "%d.%m.%Y %H:%M")', 'tip': '<str>\nDatetime format of the data in CSV file.\nREAD HELP'},
                {'name': 'nrows', 'type': 'str', 'value': None, 'default': None, 'tip': '<int, default None>\nNumber of rows of file to read. Useful for reading pieces of large files'},

                {'name': 'Advanced parameters', 'type': 'group', 'expanded': False, 'children': [
                    {'name': 'prefix', 'type': 'str', 'value': None, 'default': None},
                    {'name': 'converters', 'type': 'str', 'value': None, 'default': None},
                    {'name': 'thousands', 'type': 'str', 'value': None, 'default': None},
                    {'name': 'skipfooter', 'type': 'int', 'value': 0, 'default': 0, 'limits': (0, int(10e6))},
                    {'name': 'comment', 'type': 'str', 'value': None, 'default': None},
                    {'name': 'na_values', 'type': 'str', 'value': None, 'default': None},
                    {'name': 'keep_default_na', 'type': 'bool', 'value': True, 'default': True},
                    {'name': 'names', 'type': 'str', 'value': None, 'default': None},
                    {'name': 'index_col', 'type': 'str', 'value': None, 'default': None},
                    {'name': 'usecols', 'type': 'str', 'value': None, 'default': None, 'enabled': False},
                    {'name': 'skipinitialspace', 'type': 'bool', 'value': False, 'tip': "My tooltip"},
                    {'name': 'Manually set parameters', 'type': 'bool', 'value': False, 'tip': "Ignore all setting before (except File selection) and read\nparameter dictionary from the text-field below.\nREAD HELP", 'expanded': False, 'children': [
                        {'name': 'Manuall parameters', 'type': 'text', 'value': '#Pass here manually params. For Example:\n#{"decimal": ".", "skiprows": 2, "skip_blank_lines": True}', 'default': '#Pass here manually params. For Example:\n#{"decimal": ".", "skiprows": 2, "skip_blank_lines": True}'}]
                    },
                ]}
            ]},
            {'name': 'Load File', 'type': 'action'},
        ]

    def __init__(self, name, parent=None):
        super(readCSVNode, self).__init__(name, terminals={'Out': {'io': 'out'}}, color=(100, 250, 100, 150), parent=parent)
    
    def _createCtrlWidget(self, **kwargs):
        return readCSVNodeCtrlWidget(**kwargs)
 
    def process(self, display=True):
        kwargs = self.ctrlWidget().prepareInputArguments()
        with BusyCursor():
            df = pd.read_csv(**kwargs)
        return {'Out': df}



class readCSVNodeCtrlWidget(NodeCtrlWidget):
    
    def __init__(self, **kwargs):
        super(readCSVNodeCtrlWidget, self).__init__(update_on_statechange=False, **kwargs)
    

    def initUserSignalConnections(self):
        self.param('Load File').sigActivated.connect(self._parent.update)
        self.param('Select File').sigActivated.connect(self.on_selectFile_clicked)
        self.param('Select File').sigValueChanged.connect(self.on_selectFile_valueChanged)
        self.param('Load CSV parameters', 'Advanced parameters', 'Manually set parameters').sigValueChanged.connect(self.on_manuallySetParams_checked)

    @QtCore.pyqtSlot()  #default signal
    def on_selectFile_clicked(self):
        fname = None
        filters = "ASCII files (*.txt *.csv *.all *.dat);;All files (*.*)"
        fname = unicode(QtGui.QFileDialog.getOpenFileName(self, 'Open ASCII data file', filter=filters)[0])
        if fname:
            self.param('Select File').setValue(fname)
    
    @QtCore.pyqtSlot(object)  #default signal
    def on_selectFile_valueChanged(self, value):
        button  = self.param('Select File').items.items()[0][0].button
        fname = self.param('Select File').value()
        self._parent.sigUIStateChanged.emit(self)

        if fname is not None and os.path.isfile(fname):
            button.setToolTip('File is selected: {0}'.format(fname))
            button.setStatusTip('File is selected: {0}'.format(fname))
        else:
            button.setToolTip('Select File')
            button.setStatusTip('Select File')

    @QtCore.pyqtSlot(bool)  #default signal
    def on_manuallySetParams_checked(self, state):
        """ will disable all other widgets on this checkbox checked """
        state = state.value()
        emmiterName = ['Manually set parameters']
        changeName = ['Manuall parameters']
        for child in self.param('Load CSV parameters').children():
            if child.name() not in emmiterName+changeName:
                #print( child, child.name(), '>>>setting ipts', not state)
                try:
                    ctrlWidget = child.items.items()[0][0].widget  # dont ask why,but this is the link to the widget
                    ctrlWidget.setEnabled(not state)
                except AttributeError:  #AttributeError: 'GroupParameterItem' object has no attribute 'widget'
                    pass

    def prepareInputArguments(self):
        if self.paramValue('Load CSV parameters', 'Advanced parameters', 'Manually set parameters') is True:
            # if we will use manually set params... then simply evaluate text-field
            kwargs = self.paramValue('Load CSV parameters', 'Advanced parameters', 'Manually set parameters', 'Manuall parameters', datatype=dict)
        else:
            valid_arg_list = getCallableArgumentList(pd.read_csv, get='args')
            kwargs = dict()

            for param in self.params():
                if param.name() in valid_arg_list and self.p.evaluateValue(param.value()) != '':
                    kwargs[param.name()] = self.p.evaluateValue(param.value())

            #if kwargs['date_parser'] is not None:
                # convert our STR to lambda FUNCTION
                #dateParserStr = kwargs['date_parser']
                #kwargs['date_parser'] = lambda x: datetime.strptime(x, dateParserStr)
        kwargs['filepath_or_buffer'] = self.paramValue('Select File')
        return kwargs
