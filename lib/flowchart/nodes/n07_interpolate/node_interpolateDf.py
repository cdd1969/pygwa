#!/usr/bin python
# -*- coding: utf-8 -*-
import gc
import copy
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.Qt import QtCore
from pyqtgraph import BusyCursor
import numpy as np
import matplotlib.pyplot as plt

from lib.flowchart.package import Package
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.interpolate import applyInterpolationBasedOnRanges, createInterpolationRanges
from lib.functions.general import returnPandasDf


class interpolateDfNode(NodeWithCtrlWidget):
    """Interpolate missing data in given DataFrame"""
    nodeName = "interpolate"


    def __init__(self, name, parent=None, **kwargs):
        super(interpolateDfNode, self).__init__(name, parent=parent, terminals={'In': {'io': 'in'}, 'Out': {'io': 'out'}}, color=(250, 250, 150, 150), **kwargs)
        self._columnsToUpdate = list()

    def _createCtrlWidget(self, **kwargs):
        return interpolateDfNodeCtrlWidget(**kwargs)
        
    def process(self, In):
        df = returnPandasDf(In)
        if df is None:
            self._ctrlWidget.p.clearChildren()
            return

        receivedColumns = df.columns
        currentColumns = [item.name() for item in self._ctrlWidget.p.children()]
        
        # First take care of ParameterTree Widget.Remove missing and add new ParameterGroups
        for colName in receivedColumns:
            if colName not in currentColumns:
                self._ctrlWidget.addDfColumn(colName)

        for colName in currentColumns:
            if colName not in receivedColumns:
                self._ctrlWidget.removeDfColumn(colName)

        #Now perform some of evaluation
        if len(self._columnsToUpdate) == 0:  # update all columns
            #print ('UPDATING ALL COLUMNS')
            self._columnsToUpdate = receivedColumns
        else:  # update only some of the columns
            #print( 'UPDATING PARTLY COLUMNS')
            if self.outputs()['Out'].value() is not None:
                #print( 'UPDATING FROM OUTPUT')
                df = self.outputs()['Out'].value().unpack()
        

        nN = len(df.index)
        with BusyCursor():
            df_out = copy.deepcopy(df)
            # evaluation we will do column by column
            for colName in self._columnsToUpdate:
                validN = df_out[colName].count()
                nanN = (nN-validN)
                self._ctrlWidget.param(colName).nEntries.setValue(nN)
                self._ctrlWidget.param(colName).nNansBefore.setValue(nanN)
                
                if nanN > 0:
                    #print( 'Updating ...', colName)
                    params = self._ctrlWidget.prepareInputArguments(columnName=colName)
                    realKwargs = {
                                    'method': params['method'],
                    }
                    if realKwargs['method'] in ['spline', 'polynomial']:
                        realKwargs['order'] = params['order']
                    if isinstance(params['**kwargs'], dict):
                        for key, val in params['**kwargs'].iteritems():
                            realKwargs[key] = val
                    #print( '>>>', colName, 'Real KWARGS >>>', realKwargs)
                    ranges2treat = createInterpolationRanges(df_out, colName, interpolateMargin=params['interpolateMargin'])
                    
                    #print( '>>>', colName, 'ranges >>>', ranges2treat)
                    applyInterpolationBasedOnRanges(df_out, colName, ranges2treat, **realKwargs)
                    nNansAfter = nN-df_out[colName+'_interpolated'].count()

                    self._ctrlWidget.p.child(colName).child('Plot').show()  #show plotButton for parameter with NaNs
                else:
                    #print( 'Skipping ...', colName, '(no NaNs)')
                    self._ctrlWidget.p.child(colName).child('Plot').hide()  #hide plotButton for parameter without NaNs
                    nNansAfter = 0
                self._ctrlWidget.p.child(colName).nNansAfter.setValue(nNansAfter)

        self._columnsToUpdate = list()
        gc.collect()
        return {'Out': Package(df_out)}
        
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
            print ("Error: Cannot plot.", Exception, err)







class interpolateDfNodeCtrlWidget(NodeCtrlWidget):
    
    def __init__(self, **kwargs):
        super(interpolateDfNodeCtrlWidget, self).__init__(**kwargs)

    def addDfColumn(self, columnName):
        columnParam = columnInterpolateGroupParameter(name=columnName)
        self.p.addChild(columnParam)
        
        self.param(columnName, 'interpolateMargin').sigValueChanged.connect(self._parent.updateColumns)
        self.param(columnName, 'method').sigValueChanged.connect(self._parent.updateColumns)
        self.param(columnName, 'order').sigValueChanged.connect(self._parent.updateColumns)
        self.param(columnName, '**kwargs').sigValueChanged.connect(self._parent.updateColumns)
        self.param(columnName, 'Plot').sigActivated.connect(self._parent.plot)


    def removeDfColumn(self, columnName):
        self.param(columnName, 'interpolateMargin').sigValueChanged.disconnect()
        self.param(columnName, 'method').sigValueChanged.disconnect()
        self.param(columnName, 'order').sigValueChanged.disconnect()
        self.param(columnName, '**kwargs').sigValueChanged.disconnect()
        #self.param(columnName, 'Plot').sigActivated.disconnect(self._parent.plot)
        self.p.removeChild(self.param(columnName))
        #del self.param(columnName)
    
    #def restoreState(self, state): #
    #    # here i wold have to probably add constructor of the missing params
    #    #print ('-----------------------')
    #    #print ('restroing state:', state['name'])
    #    #print ('-----------------------') #
    #    #self.restoreState(state)
    #    pass

    def prepareInputArguments(self, columnName=''):
        kwargs = {
            'interpolateMargin': self.p.child(columnName, 'interpolateMargin').value(),
            'method':            self.p.child(columnName, 'method').value(),
            'order':             self.p.child(columnName, 'order').value(),
            '**kwargs':          self.p.evaluateValue(self.p.child(columnName, '**kwargs').value(), datatype=dict)}
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

