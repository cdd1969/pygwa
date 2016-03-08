#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import gc

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import functions as fn
from pyqtgraph import BusyCursor
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.common.DateAxisItem import DateAxisItem


class plotTimeseriesNode(NodeWithCtrlWidget):
    """Convinient widget for visualizing timeseries"""
    nodeName = "TimeseriesPlot"
    uiTemplate = [
        {'name': 'Y:Label', 'type': 'str', 'value': 'Water level', 'default': 'Water level'},
        {'name': 'Y:Units', 'type': 'str', 'value': 'm AMSL', 'default': 'm AMSL'},
        {'name': 'Crosshair', 'type': 'bool', 'value': False, 'default': False},
        {'name': 'Legend', 'type': 'bool', 'value': True, 'default': True, 'visible': False},
        {'name': 'Data Points', 'type': 'bool', 'value': False, 'default': False, 'visible': False},
        
        {'name': 'Plot', 'type': 'action'},
        ]
    sigItemReceived    = QtCore.Signal(object, object)  #(id(item), item)
    #sigRegItemReceived = QtCore.Signal(object)  #already registered item received (id(item))

    def __init__(self, name, parent=None, **kwargs):
        super(plotTimeseriesNode, self).__init__(name, terminals={'Curves': {'io': 'in', 'multi': True}}, color=(150, 150, 250, 200), **kwargs)
        self.sigItemReceived.connect(self.on_sigItemReceived)

    def _init_at_first(self):
        self._graphicsWidget = plotTimeseriesGraphicsWidget(self)
        self._TSitems = dict()

    def _createCtrlWidget(self, **kwargs):
        return plotTimeseriesNodeCtrlWidget(**kwargs)
    
    def graphicsWidget(self):
        return self._graphicsWidget
    
    def TSitems(self):
        return self._TSitems

    def disconnected(self, localTerm, remoteTerm):
        if localTerm is self['Curves'] and remoteTerm in self._TSitems.keys():
            self.removeTSItem(remoteTerm)

    def process(self, Curves):
        for term, vals in Curves.items():
            if vals is None:
                continue
            if not hasattr(vals, '__iter__'):
                vals = [vals]
            
            for val in vals:
                # do not emit here a signal, because if that is done,
                # <process> function is executed with OK status, and then
                # the execution of <on_signal_received> takes place, WITHOUT
                # GUI-based handling of exceptions (will result in crash)
                #
                # Therefore we directly call <on_signal_received> here
                #self.on_sigItemReceived(term, val)
                self.addTSItem(val, term)
        self._graphicsWidget.redrawLegend()
    
    def canvas(self):
        c1 = self._graphicsWidget.p1
        c2 = self._graphicsWidget.p2
        return [c1, c2]

    def clear(self):
        for remoteTerm in self._TSitems.keys():
            self.removeTSItem(remoteTerm)

    def close(self):
        self.clear()
        self._graphicsWidget.win.clear()
        self._graphicsWidget.win.hide()
        self._graphicsWidget.win.close()
        super(plotTimeseriesNode, self).close()

    @QtCore.pyqtSlot(object, object)
    def on_sigItemReceived(self, term, item):
        self.addTSItem(item, term)

    def copyItem(self, sampleItem):
        opts = sampleItem.opts
        opts['clipToView'] = False  #  we need to change it to False, because for some reason it fails....
        opts['symbol'] = None
        return pg.PlotDataItem(sampleItem.xData, sampleItem.yData, **opts)

    def redraw(self):
        for termName in self._TSitems.keys():
            state = self._TSitems[termName]['arrayItem'].saveState()
            pen = fn.mkPen(color=state['color'], width=state['size'])
            for plotItem in self._TSitems[termName]['GraphItems']:
                plotItem.setPen(pen)


    def addTSItem(self, GraphItem, terminal_name):
        if isinstance(GraphItem, (pg.PlotDataItem, pg.ScatterPlotItem)):
            if terminal_name in self._TSitems.keys():
                # if we have already something from this terminal
                if id(GraphItem) == id(self._TSitems[terminal_name]['GraphItems'][0]):
                    # only update item at bottom subplot
                    self.updateBottomGraphItem(self._TSitems[terminal_name])
                    return
                else:
                    self.removeTSItem(terminal_name)
            #print ('adding item from term: {0}'.format(terminal_name))
            self._TSitems[terminal_name] = dict()

            #print( '>>> on_sigItemReceived(): adding item to upper subplot')
            self.canvas()[0].addItem(GraphItem)
            #self._graphicsWidget.legend.addItem(GraphItem, name=GraphItem.name())

            # for some reason it is impossible to add same item to two subplots...
            #print( '>>> on_sigItemReceived(): creating item-copy for bottom subplot')
            GraphItem2 = self.copyItem(GraphItem)
            
            #print( '>>> on_sigItemReceived(): adding item-copy to bottom subplot')
            self.canvas()[1].addItem(GraphItem2)

            self._TSitems[terminal_name]['GraphItems'] = [GraphItem, GraphItem2]
            #print( 'adding items: (1) {0} {1} >>> (2) {2} {3}'.format(item, type(item), item2, type(item2)))

    def removeTSItem(self, terminal_name):
        #print ('removing item from term: {0}'.format(terminal_name))
        if terminal_name in self._TSitems.keys():
            TSitem = self._TSitems[terminal_name]
            self.canvas()[0].removeItem(TSitem['GraphItems'][0])
            self._graphicsWidget.legend.removeItem(TSitem['GraphItems'][0].name())
            self.canvas()[1].removeItem(TSitem['GraphItems'][1])
            del TSitem['GraphItems'][0]
            del TSitem['GraphItems'][0]
            del self._TSitems[terminal_name]
            gc.collect()

    def updateBottomGraphItem(self, TSitem):
        ''' update bottom GraphItem taking params from the upper one'''
        opts = TSitem['GraphItems'][0].opts

        TSitem['GraphItems'][1].setAlpha(opts['alphaHint'], opts['alphaMode'])
        TSitem['GraphItems'][1].setFftMode(opts['fftMode'])
        TSitem['GraphItems'][1].setLogMode(opts['logMode'][0], opts['logMode'][1])
        TSitem['GraphItems'][1].setPointMode(opts['pointMode'])
        TSitem['GraphItems'][1].setPen(opts['pen'])
        TSitem['GraphItems'][1].setShadowPen(opts['shadowPen'])
        TSitem['GraphItems'][1].setFillBrush(opts['fillBrush'])
        TSitem['GraphItems'][1].setFillLevel(opts['fillLevel'])
        TSitem['GraphItems'][1].setSymbol(opts['symbol'])
        TSitem['GraphItems'][1].setSymbolPen(opts['symbolPen'])
        TSitem['GraphItems'][1].setSymbolBrush(opts['symbolBrush'])
        TSitem['GraphItems'][1].setSymbolSize(opts['symbolSize'])
        TSitem['GraphItems'][1].setDownsampling(opts['downsample'], opts['autoDownsample'], opts['autoDownsampleFactor'])
        TSitem['GraphItems'][1].setClipToView(opts['clipToView'])

        x, y = TSitem['GraphItems'][0].getData()
        TSitem['GraphItems'][1].setData(x, y)
        del x, y





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
        self.p2 = win.addPlot(row=2, col=0, axisItems={'bottom': x_axis2, 'left': self.y_axis2}, enableMenu=False, title=' ')
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
        #print('toggleLegend', enable)
        if enable:
            #self.p1.addItem(self.legend)
            # dont know how to restore legend...
            pass
        else:
            self.legend.scene().removeItem(self.legend)

    @QtCore.pyqtSlot(bool)
    def toggleCrosshair(self, enable):
        #print('toggleCrosshair', enable)
        if enable:
            #cross hair
            self.p1.addItem(self.vLine, ignoreBounds=True)
            self.p1.addItem(self.hLine, ignoreBounds=True)
        else:
            self.p1.removeItem(self.vLine)
            self.p1.removeItem(self.hLine)

    @QtCore.pyqtSlot(bool)
    def togglePoints(self, enable):
        #print('togglePoints', enable)
        with BusyCursor():
            for TSitem in self.parent().TSitems().values():
                if enable:
                    symbol = 'x'
                else:
                    symbol = None
                # we want to toggle points only on upper subplot => index [0]
                ##print ('toggle points:', enable)
                ##TSitem['GraphItems'][0].setSymbol(symbol)
                ### we want to keep no points on lower subplot => index [1]
                ##TSitem['GraphItems'][1].setSymbol(None)


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


    def redrawLegend(self):
        # remove old names
        graph_item_names = [TSitem['GraphItems'][0].name() for TSitem in self.parent().TSitems().values()]
        for sample, label in self.legend.items:
            if label.text not in graph_item_names:
                self.legend.removeItem(label.text)

        # now remove all items
        for term_name, TSitem in self.parent().TSitems().iteritems():
            self.legend.removeItem(TSitem['GraphItems'][0].name())
        # add all items
        for term_name, TSitem in self.parent().TSitems().iteritems():
            self.legend.addItem(TSitem['GraphItems'][0], TSitem['GraphItems'][0].name())

        #for sample, label in self.legend.items:
        #    #self.legend.items.remove( (sample, label) )    # remove from itemlist
        #    self.legend.layout.removeItem(sample)          # remove from layout
        #    #sample.close()                          # remove from drawing
        #    self.legend.layout.removeItem(label)
        #    #label.close()
        #    row = self.legend.layout.rowCount()
        #    self.legend.layout.addItem(sample, row, 0)
        #    self.legend.layout.addItem(label, row, 1)
        #self.legend.updateSize()                       # redraq box


class plotTimeseriesNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(plotTimeseriesNodeCtrlWidget, self).__init__(update_on_statechange=False, **kwargs)
        self._gr = self._parent.graphicsWidget()
        self.on_yAxisLabelUnitsChanged()  #on init, it is important that WINDOW is already inited

        self.param('Plot').sigActivated.connect(self._gr.win.show)
        #self.param('Label').sigValueChanged.connect(self._gr.setLabel)
        self.param('Y:Label').sigValueChanged.connect(self.on_yAxisLabelUnitsChanged)
        self.param('Y:Units').sigValueChanged.connect(self.on_yAxisLabelUnitsChanged)
        self.param('Crosshair').sigValueChanged.connect(self.on_crosshairChanged)

    def on_yAxisLabelUnitsChanged(self):
        text  = self.param('Y:Label').value()
        units = self.param('Y:Units').value()
        self._gr.setYAxisTextAndUnits(text, units)
    
    def on_crosshairChanged(self):
        self._gr.toggleCrosshair(self.param('Crosshair').value())

    def prepareInputArguments(self):
        kwargs = dict()
        for p in self.params():
            kwargs[p.name()] = p.value()
        return kwargs
