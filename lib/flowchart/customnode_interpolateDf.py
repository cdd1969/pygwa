#!/usr/bin python
# -*- coding: utf-8 -*-

import os, sys
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.flowchart.Node import Node
import numpy as np
from package import Package
import inspect
from pyqtgraph.parametertree import Parameter, ParameterTree
from ..functions.interpolate import applyInterpolationBasedOnRanges, createInterpolationRanges
from ..functions.evaluatedictionary import evaluateDict, evaluationFunction
import webbrowser
import pyqtgraph.parametertree.parameterTypes as pTypes
import pandas as pd
import gc
import copy
import matplotlib.pyplot as plt
from pyqtgraph import BusyCursor
from ..common.NodeWithCtrlWidget import NodeWithCtrlWidget


class interpolateDfNode(NodeWithCtrlWidget):
    """Interpolate missing data in given pandas.DataFrame"""
    nodeName = "interpolateDf"


    def __init__(self, name, parent=None):
        super(interpolateDfNode, self).__init__(name, parent=parent, terminals={'In': {'io': 'in'}, 'Out': {'io': 'out'}})
        self._ctrlWidget = interpolateDfNodeCtrlWidget(parent=self)
        self._columnsToUpdate = list()

        
    def process(self, In):
        if not isinstance(In, Package) or not isinstance(In.unpack(), pd.DataFrame):
            self.In.setValueAcceptable(False)
            if In is None:
                self.deleteAllColumns()
                return {'Out': None}
            raise Exception("Input must be a <Package> with <pandas.DataDrame>. Received: {0}".format(type(In)))


        df = In.unpack()
        #kwargs = self._ctrlWidget.evaluateState()
        #vals, indices = detectPeaks(In, **kwargs)

        receivedColumns = df.columns
        currentColumns = [item.name() for item in self._ctrlWidget.p.children()]
        currentColumns.remove('Help')  # we have this Extra button
        
        # First take care of ParameterTree Widget.Remove missing and add new ParameterGroups
        for colName in receivedColumns:
            if colName not in currentColumns:
                self._ctrlWidget.addDfColumn(colName)

        for colName in currentColumns:
            if colName not in receivedColumns:
                self._ctrlWidget.removeDfColumn(colName)

        #Now perform some of evaluation
        if len(self._columnsToUpdate) == 0:  # update all columns
            #print 'UPDATING ALL COLUMNS'
            self._columnsToUpdate = receivedColumns
        else:  # update only some of the columns
            #print 'UPDATING PARTLY COLUMNS'
            if self.outputs()['Out'].value() is not None:
                #print 'UPDATING FROM OUTPUT'
                df = self.outputs()['Out'].value().unpack()
        

        nN = len(df.index)
        with BusyCursor():
            df_out = copy.deepcopy(df)
            # evaluation we will do column by column
            for colName in self._columnsToUpdate:
                validN = df_out[colName].count()
                nanN = (nN-validN)
                self._ctrlWidget.p.child(colName).nEntries.setValue(nN)
                self._ctrlWidget.p.child(colName).nNansBefore.setValue(nanN)
                
                if nanN > 0:
                    #print 'Updating ...', colName
                    params = self._ctrlWidget.evaluateState(columnName=colName)
                    realKwargs = {
                                    'method': params['method'],
                    }
                    if realKwargs['method'] in ['spline', 'polynomial']:
                        realKwargs['order'] = params['order']
                    if isinstance(params['**kwargs'], dict):
                        for key, val in params['**kwargs'].iteritems():
                            realKwargs[key] = val
                    #print '>>>', colName, 'Real KWARGS >>>', realKwargs


                    ranges2treat = createInterpolationRanges(df_out, colName, interpolateMargin=params['interpolateMargin'])
                    
                    #print '>>>', colName, 'ranges >>>', ranges2treat
                    applyInterpolationBasedOnRanges(df_out, colName, ranges2treat, **realKwargs)
                    nNansAfter = nN-df_out[colName+'_interpolated'].count()

                    self._ctrlWidget.p.child(colName).child('Plot').show()  #show plotButton for parameter with NaNs
                else:
                    #print 'Skipping ...', colName, '(no NaNs)'
                    self._ctrlWidget.p.child(colName).child('Plot').hide()  #hide plotButton for parameter without NaNs
                    nNansAfter = 0
                self._ctrlWidget.p.child(colName).nNansAfter.setValue(nNansAfter)


            

        self._columnsToUpdate = list()
        gc.collect()
        return {'Out': Package(df_out)}

    def ctrlWidget(self):
        return self._ctrlWidget

    def saveState(self):
        """overriding standard Node method to extend it with saving ctrlWidget state"""
        state = Node.saveState(self)
        # saving additional state of the control widget
        state['crtlWidget'] = self.ctrlWidget().saveState()
        return state
        
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
        for colName in currentColumns:
            self._ctrlWidget.removeDfColumn(colName)

    @QtCore.pyqtSlot(object)
    def plot(self, sender):
        #sender name is... sender.name() (this is the name of the PushButton >>> "Plot"),
        # so the name of the column is the name of the parent parameter group
        try:
            cn  = sender.parent().name()
            cni = cn+'_interpolated'
            df = self.outputs()['Out'].value().unpack()

            #plot
            ax = plt.subplot(211)

            df[cn].plot(ax=ax, marker='x', color='b')

            criterion = df.index.isin(np.where(df[cn].isnull())[0])  # where values are not NaN
            x = df[criterion].index
            y = df[cni][criterion].values
            plt.scatter(x=x, y=y, marker='o', color='r', label='interpolated', s=100)
            plt.legend(loc='best')


            ax2 = plt.subplot(212)
            df[cni].plot(ax=ax2, marker='x', color='g')
            plt.legend(loc='best')

            plt.show()
        except Exception, err:
            print "Error: Cannot plot.", Exception, err







class interpolateDfNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(interpolateDfNodeCtrlWidget, self).__init__()
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
        #self.p.sigValueChanged.connect(self._parent.updateColumns)
        self.p.child('Help').sigActivated.connect(self.on_help_clicked)
        #self.p.child('split').sigValueChanged.connect(self._parent.updateWithoutArgs)



    @QtCore.pyqtSlot()  #default signal
    def on_help_clicked(self):
        webbrowser.open('https://github.com/cdd1969/pygwa/blob/gh-pages/node_interpolateDf.md')

    
    def params(self):
        params = [
            {'name': 'Help', 'type': 'action'}
            ]

        return params

    def addDfColumn(self, columnName):
        columnParam = columnInterpolateGroupParameter(name=columnName)
        self.p.addChild(columnParam)
        
        self.p.child(columnName).child('interpolateMargin').sigValueChanged.connect(self._parent.updateColumns)
        self.p.child(columnName).child('method').sigValueChanged.connect(self._parent.updateColumns)
        self.p.child(columnName).child('order').sigValueChanged.connect(self._parent.updateColumns)
        self.p.child(columnName).child('**kwargs').sigValueChanged.connect(self._parent.updateColumns)
        self.p.child(columnName).child('Plot').sigActivated.connect(self._parent.plot)


    def removeDfColumn(self, columnName):
        self.p.child(columnName).child('interpolateMargin').sigValueChanged.disconnect()
        self.p.child(columnName).child('method').sigValueChanged.disconnect()
        self.p.child(columnName).child('order').sigValueChanged.disconnect()
        self.p.child(columnName).child('**kwargs').sigValueChanged.disconnect()
        #self.p.child(columnName).child('Plot').sigActivated.disconnect(self._parent.plot)
        self.p.removeChild(self.p.child(columnName))
        #del self.p.child(columnName)



    def saveState(self):
        return self.p.saveState()
    
    def restoreState(self, state):

        # here i wold have to probably add constructor of the missing params
        #print '-----------------------'
        #print 'restroing state:', state['name']
        #print '-----------------------'

        #self.restoreState(state)
        pass

    def evaluateState(self, state=None, columnName=''):
        """ function evaluates passed state , reading only necessary parameters,
            those that can be passed to pandas.read_csv() as **kwargs

            user should re-implement this function for each Node"""

        if state is None:
            state = self.saveState()
        listWithDicts = evaluateDict(state['children'][columnName], functionToDicts=evaluationFunction, log=False)
        print 'returning listWithDicts for column', columnName
        print listWithDicts
        kwargs = dict()
        for d in listWithDicts:
            # {'a': None}.items() >>> [('a', None)] => two times indexing
            kwargs[d.items()[0][0]] = d.items()[0][1]
        print 'returning kwargs for column', columnName
        print kwargs
        return kwargs





class columnInterpolateGroupParameter(pTypes.GroupParameter):
    """ this parameter will be added for each column of the received
        DataDrame, so we can set different interpolation options for each
        column separately
    """
    def __init__(self, **opts):
        opts['type'] = 'bool'
        opts['value'] = True
        opts['expanded'] = False
        pTypes.GroupParameter.__init__(self, **opts)
        self.addChild({'name': 'Entries', 'type': 'int', 'value': -1, 'readonly': True, 'tip': 'number of entries in current column'})
        self.addChild({'name': 'NaNs before', 'type': 'int', 'value': -1, 'readonly': True, 'tip': 'number of NaNs in current column before interpolation'})
        self.addChild({'name': 'NaNs after', 'type': 'int', 'value': -1, 'readonly': True, 'tip': 'number of NaNs in current column after interpolation'})
        
        self.addChild({'name': 'interpolateMargin', 'type': 'int', 'value': 100, 'step': 1, 'limits': (1, int(1000)), 'default': 100, 'tip': 'number of data-points to consider left and\nright from NaN value during interpolation'})
        self.addChild({'name': 'method', 'type': 'list', 'value': 'linear', 'values': ['linear', 'time', 'index', 'values', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'barycentric', 'krogh', 'polynomial', 'spline', 'piecewise_polynomial', 'pchip'], 'default': 'polynomial', 'tip': 'Method of interpolation. See docs'})
        self.addChild({'name': 'order', 'type': 'int', 'value': 15, 'default': 15, 'step': 1, 'limits': (1, int(1000)), 'tip': 'Both ‘polynomial’ and ‘spline’ require that you\n also specify an order (int), e.g. df.interpolate \n(method=’polynomial’, order=4). See docs'})
        self.addChild({'name': '**kwargs', 'type': 'text', 'value': '#Example:\n#{"axis": 1, "limit": 20, "limit_direction": "both"}', 'tip': 'these <**kwargs> will be passed to DataFrame.interpolate()\nin addition to defined above "method" and "order".\nLines may be commented with "#"', 'default': '#Example:\n#{"axis": 1, "limit": 20, "limit_direction": "both"}', "expanded": False})
        self.addChild({'name': 'Plot', 'type': 'action', 'tip': 'Visualize performed interpolation with matplotlib'})

        self.nEntries = self.param('Entries')
        self.nNansBefore = self.param('NaNs before')
        self.nNansAfter = self.param('NaNs after')

