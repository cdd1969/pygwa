#!/usr/bin python
# -*- coding: utf-8 -*-

import os, sys
import datetime
import gc



import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import functions as fn
from pyqtgraph import BusyCursor
from pyqtgraph.parametertree import Parameter, ParameterTree

from ....functions.evaluatedictionary import evaluateDict, evaluationFunction
from ....common.NodeWithCtrlWidget import NodeWithCtrlWidget
from ....common.DateAxisItem import DateAxisItem


class plotTimeseriesNode(NodeWithCtrlWidget):
    """Convinient widget for visualizing timeseries"""
    nodeName = "TimeseriesPlot"

    sigItemReceived    = QtCore.Signal(object, object)  #(id(item), item)
    #sigRegItemReceived = QtCore.Signal(object)  #already registered item received (id(item))

    def __init__(self, name, parent=None):
        super(plotTimeseriesNode, self).__init__(name, terminals={'Items': {'io': 'in', 'multi': True}})
        self.graphicsItem().setBrush(fn.mkBrush(150, 150, 250, 200))
        self._graphicsWidget = plotTimeseriesGraphicsWidget(self)
        self._ctrlWidget = plotTimeseriesNodeCtrlWidget(self)
        #self.items = set()   #set to save incoming items
        self._items = dict()
        self.sigItemReceived.connect(self.on_sigItemReceived)

    def ctrlWidget(self):
        return self._ctrlWidget
    
    def graphicsWidget(self):
        return self._graphicsWidget
    
    def items(self):
        return self._items

    def disconnected(self, localTerm, remoteTerm):
        if localTerm is self['Items'] and remoteTerm in self._items.keys():
            #print( "localTerm <{0}> is disconnected from remoteTerm <{1}>".format(localTerm, remoteTerm))
            if 'plotItems' in self._items[remoteTerm].keys():
                self.removeItem(self._items[remoteTerm])
                del self._items[remoteTerm]


    def process(self, Items):
        for term, vals in Items.items():
            if vals is None:
                continue
            if type(vals) is not list:
                vals = [vals]
            
            for val in vals:
                # do not emit here a signal, because if that is done,
                # <process> function is executed with OK status, and then
                # the execution of <on_signal_received> takes place, WITHOUT
                # GUI-based handling of exceptions (will result in crash)
                #
                # Therefore we directly call <on_signal_received> here
                self.on_sigItemReceived(term, val)
    
    def canvas(self):
        c1 = self._graphicsWidget.p1
        c2 = self._graphicsWidget.p2
        return [c1, c2]

    def clear(self):
        for item in self._items.values():
            self.removeItem(item)

    def close(self):
        self.clear()
        self._graphicsWidget.win.clear()
        self._graphicsWidget.win.hide()
        self._graphicsWidget.win.close()
        super(plotTimeseriesNode, self).close()

    @QtCore.pyqtSlot(object, object)
    def on_sigItemReceived(self, term, item):
        """ <term> is not <id(array)>, but it should be passed from parent widget
        """
        # check if this item exists
        if term in self._items.keys():  # if we have already something from this terminal
            if 'plotItems' in self._items[term].keys():
                if self._items[term]['plotItems'][0] is item:  # if the item is absolutely same
                    #print( '>>> on_sigItemReceived(): already have something from term <{0}>: item <{1}> is the same'.format(term, item))
                    
                    # in this case item on the upper subplot will be updated automatically, but the bottom subplot will stay same...
                    # When the item is receive, we are manually creating a COPY of incoming item and are adding this copy to the
                    # bottom subplot. Lets do same trick! Keep original item, but recreate the COPY
                    item2 = self.copyItem(item)
                    self.canvas()[1].removeItem(self._items[term]['plotItems'][1])
                    del self._items[term]['plotItems'][1]
                    
                    self.canvas()[1].addItem(item2)
                    self._items[term]['plotItems'].append(item2)
                    return
                else:
                    #print( '>>> on_sigItemReceived(): already have something from term <{0}>: item <{1}> is different'.format(term, item))
                    self.removeItems(self._items[term])

        if isinstance(item, (pg.PlotDataItem, pg.ScatterPlotItem)):
            #print( '>>> on_sigItemReceived(): registering incoming item')
            self._items[term] = dict()
            # init symbol pen and size
            item.setSymbolPen(item.opts['pen'])
            item.setSymbolSize(5)

            #print( '>>> on_sigItemReceived(): adding item to upper subplot')
            self.canvas()[0].addItem(item)

            # for some reason it is impossible to add same item to two subplots...
            #print( '>>> on_sigItemReceived(): creating item-copy for bottom subplot')
            item2 = self.copyItem(item)
            
            #print( '>>> on_sigItemReceived(): adding item-copy to bottom subplot')
            self.canvas()[1].addItem(item2)

            self._items[term]['plotItems'] = [item, item2]
            #print( 'adding items: (1) {0} {1} >>> (2) {2} {3}'.format(item, type(item), item2, type(item2)))
            return

    def copyItem(self, sampleItem):
        opts = sampleItem.opts
        opts['clipToView'] = False  #  we need to change it to False, because for some reason it fails....
        return pg.PlotDataItem(sampleItem.xData, sampleItem.yData, **opts)

    def redraw(self):
        for iId in self._items.keys():
            state = self._items[iId]['arrayItem'].saveState()
            pen = fn.mkPen(color=state['color'], width=state['size'])
            for plotItem in self._items[iId]['plotItems']:
                plotItem.setPen(pen)


    def removeItem(self, item):
        try:
            if 'plotItems' in item.keys() and isinstance(item['plotItems'], list) and len(item['plotItems']) == 2:
                self.canvas()[0].removeItem(item['plotItems'][0])
                self.canvas()[1].removeItem(item['plotItems'][1])
        except RuntimeError:  # sometimes happens by loading new chart (RuntimeError: wrapped C/C++ object of type PlotDataItem has been deleted)
            #print( '>>> plotArray: item not deleted')
            pass
        del item
        gc.collect()



class plotTimeseriesGraphicsWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(plotTimeseriesGraphicsWidget, self).__init__()
        self._parent = parent
        self._listWidgetItems = set()  # registered items in ListWidget
        self.initUI()
        self.connectSignals()
        self.items = dict()


    def initUI(self):
        win = pg.GraphicsLayoutWidget()
        win.resize(1000, 600)
        win.setWindowTitle(u"Node: "+unicode(self.parent().name()))

        # Enable anti-aliasing for prettier plots
        pg.setConfigOptions(antialias=True)
        # Add Label where coords of current mouse position will be printed
        self.coordLabel = pg.LabelItem(justify='right')
        win.addItem(self.coordLabel)
        
        #add custom datetime axis
        x_axis1 = DateAxisItem(orientation='bottom')
        x_axis2 = DateAxisItem(orientation='bottom')
        self.y_axis1  = pg.AxisItem(orientation='left')  # keep reference to itm since we want to modify its label
        self.y_axis2  = pg.AxisItem(orientation='left')  # keep reference to itm since we want to modify its label

        self.p1 = win.addPlot(row=1, col=0, axisItems={'bottom': x_axis1, 'left': self.y_axis1})
        #self.p1.setClipToView(True)
        self.p2 = win.addPlot(row=2, col=0, axisItems={'bottom': x_axis2, 'left': self.y_axis2})
        #self.p1.setClipToView(True)
        self.vb = self.p1.vb  # ViewBox
        
        self.zoomRegion = pg.LinearRegionItem()
        self.zoomRegion.setZValue(-10)
        self.zoomRegion.setRegion([1000, 2000])
        self.p2.addItem(self.zoomRegion, ignoreBounds=True)
        
        self.p1.setAutoVisible(y=True)
        self.legend = self.p1.addLegend()

        self.initCrosshair()
        self.win = win


    def connectSignals(self):
        self.zoomRegion.sigRegionChanged.connect(self.on_zoomRegion_changed)
        self.p1.sigRangeChanged.connect(self.updateZoomRegion)

        self.proxy = pg.SignalProxy(self.p1.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)


    def parent(self):
        return self._parent

    def initCrosshair(self):
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.toggleCrosshair(False)
    

    @QtCore.pyqtSlot(bool)
    def toggleLegend(self, enable):
        print('toggleLegend', enable)
        if enable:
            #self.p1.addItem(self.legend)
            # dont know how to restore legend...
            pass
        else:
            self.legend.scene().removeItem(self.legend)



    @QtCore.pyqtSlot(bool)
    def toggleCrosshair(self, enable):
        print('toggleCrosshair', enable)
        if enable:
            #cross hair
            self.p1.addItem(self.vLine, ignoreBounds=True)
            self.p1.addItem(self.hLine, ignoreBounds=True)
        else:
            self.p1.removeItem(self.vLine)
            self.p1.removeItem(self.hLine)

    @QtCore.pyqtSlot(bool)
    def togglePoints(self, enable):
        print('togglePoints', enable)
        with BusyCursor():
            for item in self.parent().items().values():
                # we want to toggle points only on upper subplot => index [0]
                if enable:
                    symbol = 'x'
                else:
                    symbol = None
                item['plotItems'][0].setSymbol(symbol)


    def on_zoomRegion_changed(self):
        minX, maxX = self.zoomRegion.getRegion()
        self.p1.setXRange(minX, maxX, padding=0)

    def updateZoomRegion(self, window, viewRange):
        rgn = viewRange[0]
        self.zoomRegion.setRegion(rgn)

    @QtCore.pyqtSlot(object)
    def mouseMoved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.p1.sceneBoundingRect().contains(pos):
            mousePoint = self.vb.mapSceneToView(pos)
            # we add 1-hour manually (mouse.x+60*60). This is probably due to the TimeZone definition(???) in DateTimeAxis
            t = datetime.datetime.utcfromtimestamp(mousePoint.x()+60*60).strftime('%Y-%m-%d %H:%M')
            
            data_y = {}  # should be y-coordinates of the data lines
            self.setCoordLabelText(t, mousePoint.y(), **data_y)
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

    def setCoordLabelText(self, x_coord, y_coord, **kwargs):
        text = "<span style='font-size: 12pt'>{0} | y={1:2.2f}".format(x_coord, y_coord)
        self.coordLabel.setText(text)

    def setYAxisTextAndUnits(self, text='', units=None):
        self.y_axis1.setLabel(text=text, units=units)
        self.y_axis2.setLabel(text=text, units=units)

    def setLabel(self, label):
        self.p1.setTitle(label)









class plotTimeseriesNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(plotTimeseriesNodeCtrlWidget, self).__init__()
        self._parent = parent

        self._gr = self._parent.graphicsWidget()
        params = self.params()
        ## Create tree of Parameter objects
        self.p = Parameter.create(name='params', type='group', children=params)

        ## set parameter tree to <self> (parameterTreeWidget)
        self.setParameters(self.p, showTop=False)
        self.initConnections()
        # save default state
        self._savedState = self.saveState()
        self.on_yAxisLabelUnitsChanged()  #on init, it is important that WINDOW is already inited

    def initConnections(self):
        self.p.child('Plot').sigActivated.connect(self._gr.win.show)
        #self.p.child('Label').sigValueChanged.connect(self._gr.setLabel)
        self.p.child('Y:Label').sigValueChanged.connect(self.on_yAxisLabelUnitsChanged)
        self.p.child('Y:Units').sigValueChanged.connect(self.on_yAxisLabelUnitsChanged)
        self.p.child('Legend').sigValueChanged.connect(self.on_legendChanged)
        self.p.child('Crosshair').sigValueChanged.connect(self.on_crosshairChanged)
        self.p.child('Data Points').sigValueChanged.connect(self.on_datapointsChanged)

    def on_yAxisLabelUnitsChanged(self):
        text = self.p.child('Y:Label').value()
        units = self.p.child('Y:Units').value()
        self._gr.setYAxisTextAndUnits(text, units)
    
    def on_legendChanged(self):
        self._gr.toggleLegend(self.p.child('Legend').value())
    
    def on_crosshairChanged(self):
        self._gr.toggleCrosshair(self.p.child('Crosshair').value())
    
    def on_datapointsChanged(self):
        self._gr.togglePoints(self.p.child('Data Points').value())

    def params(self):
        params = [
            #{'name': 'Label', 'type': 'str', 'value': 'Hydrographs', 'default': 'Hydrographs'},
            {'name': 'Y:Label', 'type': 'str', 'value': 'Water level', 'default': 'Water level'},
            {'name': 'Y:Units', 'type': 'str', 'value': 'm AMSL', 'default': 'm AMSL'},
            {'name': 'Legend', 'type': 'bool', 'value': True, 'default': True, 'readonly': True},
            {'name': 'Crosshair', 'type': 'bool', 'value': False, 'default': False},
            {'name': 'Data Points', 'type': 'bool', 'value': False, 'default': False},
            
            {'name': 'Plot', 'type': 'action'},
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


        if state is None:
            state = self.saveState()
        validArgs = [d['name'] for d in self.params()]
        listWithDicts = evaluateDict(state['children'], functionToDicts=evaluationFunction, log=False, validArgumnets=validArgs)
        kwargs = dict()
        for d in listWithDicts:
            # {'a': None}.items() >>> [('a', None)] => two times indexing
            kwargs[d.items()[0][0]] = d.items()[0][1]
        return kwargs
