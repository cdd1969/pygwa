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
from ..functions import evaluateDict
import webbrowser


"""
df1 = pd.Dataframe(...)
df2 = pd.Dataframe(...)

BOTH df1, df2 have index as datetime!!!


OPTION1
(select all data in df1 that has same datetime as in df2)

selector = df1.index.isin(df2.index)
selectedDf = df1[selector]


OPTION2
(select all data in df1 that has minutes = 10, 20, 30)

minutes = df1.index.minutes
selector = (minutes == 10) | (minutes == 20) | (minutes == 30)
selectedDf = df1[selector]

"""








class readCSVNode(Node):
    """Load column-based data from ASCII file"""
    nodeName = "readCSV"


    def __init__(self, name, parent=None):
        super(readCSVNode, self).__init__(name, terminals={'output': {'io': 'out'}})
        self._ctrlWidget = readCSVNodeCtrlWidget(self)

        
    def process(self, display=True):
        print 'process() is called'
        kwargs = self.ctrlWidget().evaluateState()
        try:
            df = pd.read_csv(**kwargs)
            print 'process() returning...'
            return {'output': Package(df)}
        except Exception, err:
            print Exception, err
            print 'Passed **kwargs = ', kwargs
            print 'ERROR: file not loaded'

        
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
















class readCSVNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(readCSVNodeCtrlWidget, self).__init__()
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
        pass
        self.p.child('Help').sigActivated.connect(self.on_help_clicked)
        self.p.child('Load state').sigActivated.connect(self.on_loadstate_clicked)
        self.p.child('Load File').sigActivated.connect(self.on_loadfile_clicked)
        self.p.child('Select File').sigActivated.connect(self.on_selectFile_clicked)
        self.p.child('Select File').sigValueChanged.connect(self.on_selectFile_valueChanged)
        self.p.child('Load CSV parameters').child('Advanced parameters').child('Manually set parameters').sigValueChanged.connect(self.on_manuallySetParams_checked)

    @QtCore.pyqtSlot()  #default signal
    def on_loadfile_clicked(self):
        self._parent.update()

    @QtCore.pyqtSlot()  #default signal
    def on_help_clicked(self):
        webbrowser.open('https://github.com/cdd1969/pygwa/blob/gh-pages/node_readCSV.md')

    @QtCore.pyqtSlot()  #default signal
    def on_loadstate_clicked(self):
        self.restoreState(self._savedState)

    @QtCore.pyqtSlot()  #default signal
    def on_selectFile_clicked(self):
        fname = None
        filters = "ASCII files (*.txt *.csv *.all *.dat);;All files (*.*)"
        fname = unicode(QtGui.QFileDialog.getOpenFileName(self, 'Open ASCII data file', filter=filters)[0])
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

    @QtCore.pyqtSlot(bool)  #default signal
    def on_manuallySetParams_checked(self, state):
        """ will disable all other widgets on this checkbox checked """
        state = state.value()
        emmiterName = ['Manually set parameters']
        changeName = ['Manuall parameters']
        for child in self.p.child('Load CSV parameters').children():
            if child.name() not in emmiterName+changeName:
                print child, child.name(), '>>>setting ipts', not state
                try:
                    ctrlWidget = child.items.items()[0][0].widget  # dont ask why,but this is the link to the widget
                    ctrlWidget.setEnabled(not state)
                except AttributeError:  #AttributeError: 'GroupParameterItem' object has no attribute 'widget'
                    pass
                #child.setOpts(visible=not state)
        #self.p.child('Load CSV parameters').child('Advanced parameters').child(emmiterName).child(changeName).setOpts(visible=state)

        
    def visitTree(self, tree):
        """ this is a recursion function to visit all children of passed QTreeWidget"""
        lst = []
        for i in xrange(tree.topLevelItemCount()):
            self.visitAllChildren(lst, tree.topLevelItem(i))
        return lst

    def visitAllChildren(self, lst, item):
        try:
            lst.append(item.param.name())
        except AttributeError, err:  #AttributeError: 'GroupParameterItem' object has no attribute 'name'
            pass
        for i in xrange(item.childCount()):
            self.visitAllChildren(lst, item.child(i))
    

    def performFunctionToChildren(self, function, paramNames=[], treatNamesAsIgnoreNames=True):
        """ now perform <function> to all children (some children can be ignored by passing <paramNames>)

            if treatNamesAsIgnoreNames=True, the list <ignoreNames> = <paramNames>
            
            but if it was set to False, it will be treated as the names of the parameters, to which we
            will perform out <function>, i.e. in this case <ignoreNames> = <allNames> - <paramNames>
        

        """
        def visitTreeDoAction(tree, do_something, **kwargs):
            """ this is a recursion function to visit all children of passed QTreeWidget"""
            for i in xrange(tree.topLevelItemCount()):
                visitAllChildrenDoAction(do_something, tree.topLevelItem(i), **kwargs)

        def visitAllChildrenDoAction(do_something, item, ignoreNames=[]):
            try:
                n = item.param.name()
                if n not in ignoreNames:
                    do_something(item)
            except AttributeError, err:  #AttributeError: 'GroupParameterItem' object has no attribute 'name'
                print 'ERROR:', err, item
                print '_______',
            for i in xrange(item.childCount()):
                visitAllChildrenDoAction(do_something, item.child(i), ignoreNames)
        
        if treatNamesAsIgnoreNames is True:
            ignoreNames = paramNames
            if 'params' not in ignoreNames:
                ignoreNames.append('params')  #pop root item
        else:
            allNames = self.visitTree(self)
            ignoreNames = [n for n in allNames if n not in paramNames]

        visitTreeDoAction(self, function, ignoreNames=ignoreNames)

    def _printChild(self, item):
        print item.param.name(), '>>>', item
        print item.widget
        print '_________________'



    def params(self):
        params = [
            {'name': 'Help', 'type': 'action'},
            {'name': 'Load state', 'type': 'action'},
            {'name': 'Select File', 'type': 'action', 'value': None},
            {'name': 'Load CSV parameters', 'type': 'group', 'children': [
                {'name': 'decimal', 'type': 'str', 'value': '.', 'default': '.', 'tip': '<str>\nCharacter to recognize as decimal point. E.g. use ","" for European data'},
                {'name': 'delimiter', 'type': 'str', 'value': ';', 'default': None, 'tip': '<str>\nDelimiter to use. If sep is None, will try to automatically determine this. Regular expressions are accepted'},
                {'name': 'header', 'type': 'str', 'value': 0, 'default': 0, 'tip': '< int, list of ints, default ‘infer’>\nRow number(s) to use as the column names, and the start of the data.\nREAD HELP'},  #dependent on <names>
                {'name': 'skiprows', 'type': 'str', 'value': 0, 'default': None, 'tip': '<list-like or integer, default None>\nLine numbers to skip (0-indexed) or number of lines to skip (int) at the start of the file'},
                {'name': 'parse_dates', 'type': 'str', 'value': False, 'default': False, 'tip': '<boolean, list of ints or names, list of lists, or dict, default False>\nIf True -> try parsing the index. If [1, 2, 3] -> try parsing columns 1, 2, 3 each as a\nseparate date column. If [[1, 3]] -> combine columns 1 and 3 and parse as a single\ndate column. {‘foo’ : [1, 3]} -> parse columns 1, 3 as date and call result ‘foo’ A fast-\npath exists for iso8601-formatted dates.'},
                {'name': 'date_parser', 'type': 'str', 'value': '%d.%m.%Y %H:%M', 'default': '%d.%m.%Y %H:%M:%S', 'tip': '<str>\nDatetime format of the data in CSV file.\nREAD HELP'},
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
                        {'name': 'Manuall parameters', 'type': 'text', 'value': '#Pass here manually params. For Example:\n#{"decimal": ".", "skiprows": 2, skip_blank_lines": True}', 'default': '#Pass here manually params. For Example:\n#{"decimal": ".", "skiprows": 2, skip_blank_lines": True}'}]
                    },
                ]}
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
            those that can be passed to pandas.read_csv() as **kwargs

            user should reimplement this function for each Node"""

        function = pd.read_csv
        # -------------------------------------------------------------
        if not inspect.isfunction(function):
            raise ValueError('Argument passed is not a function. Received type: {0}'.format(type(function)))
        
        if state is None:
            state = self.saveState()

        def evaluationFunction(dictionary):
            nameArgFound = False
            for name in ['name', u'name']:
                if name in dictionary.keys():
                    nameArgFound = True
            if not nameArgFound:
                return None

            defaultArgNames = inspect.getargspec(function).args
            stateArgs = None
            # if passed argument name is in defauklt argument names
            if dictionary['name'] in defaultArgNames:
                stateArgs = dict()
                # save value from passed state...
                if dictionary['value'] in ['', u'']:  #if emty line
                    val = dictionary['default']
                else:
                    try:
                        val = eval(dictionary['value'])
                    except Exception, err:
                        print Exception, err, '. Received:', dictionary['name'], '=', dictionary['value'],  '>>> I will set value without evaluation'
                        val = dictionary['value']


                stateArgs[dictionary['name']] = val
            return stateArgs
        # ------------------------------------------------------
        if state['children']['Load CSV parameters']['children']['Advanced parameters']['children']['Manually set parameters']['value'] is True:
            # if we will use manually set params... then simply evaluate text-field
            kwargs = eval(state['children']['Load CSV parameters']['children']['Advanced parameters']['children']['Manually set parameters']['children']['Manuall parameters']['value'])
        else:
            # if we wont use manually set params, then collect all params values
            listWithDicts = evaluateDict(state['children'], functionToDicts=evaluationFunction, log=False)
            kwargs = dict()
            for d in listWithDicts:
                # {'a': None}.items() => [('a', None)] => two times indexing
                kwargs[d.items()[0][0]] = d.items()[0][1]
            if kwargs['date_parser'] is not None:
                # convert our STR to lambda FUNCTION
                dateParserStr = kwargs['date_parser']
                kwargs['date_parser'] = lambda x: datetime.strptime(x, dateParserStr)
        kwargs['filepath_or_buffer'] = state['children']['Select File']['value']

        return kwargs



def test():
    app = QtGui.QApplication([])
    win = QtGui.QWidget()
    layout = QtGui.QGridLayout()
    win.setLayout(layout)
    layout.addWidget(QtGui.QLabel("These are two views of the same data. They should always display the same values."), 0,  0, 1, 2)
    t = readTextDataNodeCtrlWidget()
    layout.addWidget(t, 1, 0, 1, 1)
    win.show()
    win.resize(800, 800)
    print t.evaluateState()
    QtGui.QApplication.instance().exec_()