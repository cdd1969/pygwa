# -*- coding: utf-8 -*-
"""
This example demonstrates the use of pyqtgraph's parametertree system. This provides
a simple way to generate user interfaces that control sets of parameters. The example
demonstrates a variety of different parameter types (int, float, list, etc.)
as well as some customized parameter types

"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import os


from pyqtgraph.parametertree import Parameter, ParameterTree


class loadPandas_parameterTree(ParameterTree):
    

    def __init__(self, parent=None):
        super(loadPandas_parameterTree, self).__init__()
        self._parent = parent

        params = self.params()
        ## Create tree of Parameter objects
        self.p = Parameter.create(name='params', type='group', children=params)

        ## set parameter tree to <self> (parameterTreeWidget)
        self.setParameters(self.p, showTop=False)
        self.initConnections()

    def initConnections(self):
        pass
        self.p.child('Open help').sigActivated.connect(self.on_openHelp_clicked)
        self.p.child('Select File').sigActivated.connect(self.on_selectFile_clicked)
        self.p.child('Select File').sigValueChanged.connect(self.on_selectFile_valueChanged)
        self.p.child('Load CSV parameters').child('Advanced parameters').child('Manually set parameters').sigValueChanged.connect(self.on_manuallySetParams_checked)



    @QtCore.pyqtSlot()  #default signal
    def on_openHelp_clicked(self):
        self.performFunctionToChildren(self._printChild)


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

        if os.path.isfile(fname):
            button.setFlat(True)
            button.setToolTip('File is selected: {0}'.format(fname))
            button.setStatusTip('File is selected: {0}'.format(fname))
        else:
            button.setFlat(False)
            button.setToolTip('Select File')
            button.setStatusTip('Select File')

    @QtCore.pyqtSlot(bool)  #default signal
    def on_manuallySetParams_checked(self, state):
        state = state.value()
        print 'STATE IS', state
        emmiterName = ['Manually set parameters']
        changeName = ['Manuall parameters']
        for child in self.p.child('Load CSV parameters').children():
            if child.name() not in emmiterName+changeName:
                print child, child.name(), '>>>setting ipts', not state
                try:
                    child.items.items()[0][0].widget.setEnabled(not state)  # dont ask why,but this is the link to the widget
                except AttributeError:  #AttributeError: 'GroupParameterItem' object has no attribute 'widget'
                    pass
                print '-----'
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
    
    def visitTreeDoAction(self, tree, do_something, **kwargs):
        """ this is a recursion function to visit all children of passed QTreeWidget"""
        for i in xrange(tree.topLevelItemCount()):
            self.visitAllChildrenDoAction(do_something, tree.topLevelItem(i), **kwargs)

    def visitAllChildrenDoAction(self, do_something, item, ignoreNames=[]):
        try:
            n = item.param.name()
            if n not in ignoreNames:
                do_something(item)
        except AttributeError, err:  #AttributeError: 'GroupParameterItem' object has no attribute 'name'
            print 'ERROR:', err, item
            print '_______',
        for i in xrange(item.childCount()):
            self.visitAllChildrenDoAction(do_something, item.child(i), ignoreNames)

    def performFunctionToChildren(self, function, paramNames=[], treatNamesAsIgnoreNames=True):
        """ now perform <function> to all children (some children can be ignored by passing <paramNames>)

            if treatNamesAsIgnoreNames=True, the list <ignoreNames> = <paramNames>
            
            but if it was set to False, it will be treated as the names of the parameters, to which we
            will perform out <function>, i.e. in this case <ignoreNames> = <allNames> - <paramNames>
        

        """
        
        if treatNamesAsIgnoreNames is True:
            ignoreNames = paramNames
            if 'params' not in ignoreNames:
                ignoreNames.append('params')  #pop root item
        else:
            allNames = self.visitTree(self)
            ignoreNames = [n for n in allNames if n not in paramNames]

        self.visitTreeDoAction(self, function, ignoreNames=ignoreNames)

    def _printChild(self, item):
        print item.param.name(), '>>>', item
        print item.widget
        print '_________________'



    def params(self):
        params = [
            {'name': 'Open help', 'type': 'action', 'tip': 'Open documentation in browser'},
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




if __name__ == '__main__':
    app = QtGui.QApplication([])
    win = QtGui.QWidget()
    layout = QtGui.QGridLayout()
    win.setLayout(layout)
    layout.addWidget(QtGui.QLabel("These are two views of the same data. They should always display the same values."), 0,  0, 1, 2)
    t = loadPandas_parameterTree()
    layout.addWidget(t, 1, 0, 1, 1)
    win.show()
    win.resize(800, 800)

    # Too lazy for recursion:
    for child in t.p.children():
        print child, 'is child of ', t
        #for ch2 in child.children():
        #    print '\t', ch2, 'is child of ', child
        #    for ch3 in ch2.children():
        #        print '\t\t', ch3, 'is child of ', ch2


    s =  t.p.saveState()
    t.p.restoreState(s)
    print isinstance(t, QtGui.QTreeWidget)
    print t.visitTree(t)

    QtGui.QApplication.instance().exec_()
