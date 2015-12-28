#!/usr/bin python
# -*- coding: utf-8 -*-

import pyqtgraph as pg

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt, qDebug
from pyqtgraph.flowchart.Node import Node
from pyqtgraph import functions as fn

import pyqtgraph as pg
import sys
from ..common.onedimarrayitem import OneDimArrayItem
from ..common.DateAxisItem import DateAxisItem
from copy import copy, deepcopy
import datetime
import time
from pyqtgraph import BusyCursor
import gc



class plotTimeseriesNode(Node):
    """Plot number of 1D arrays as timeseries"""
    nodeName = "PlotTimeseries"

    sigItemReceived    = QtCore.Signal(object, object)  #(id(item), item)
    sigRegItemReceived = QtCore.Signal(object)  #already registered item received (id(item))

    def __init__(self, name, parent=None):
        super(plotTimeseriesNode, self).__init__(name, terminals={'Array': {'io': 'in', 'multi': True}})
        self.graphicsItem().setBrush(fn.mkBrush(150, 150, 250, 150))
        self._ctrlWidget = plotTimeseriesNodeCtrlWidget(self)
        #self.items = set()   #set to save incoming items
        self._items = dict()
        self.sigItemReceived.connect(self.on_sigItemReceived)

    def items(self):
        return self._items

    def disconnected(self, localTerm, remoteTerm):
        if localTerm is self['Array'] and remoteTerm in self._items.keys():
            print "localTerm <{0}> is disconnected from remoteTerm <{1}>".format(localTerm, remoteTerm)
            if 'plotItems' in self._items[remoteTerm].keys():
                self.removeItem(self._items[remoteTerm])
                del self._items[remoteTerm]


    #def connected(self, localTerm, remoteTerm):
    #    """Called whenever one of this node's terminals is connected elsewhere."""
    #    print 'TERMS CONNECTED'



    def process(self, Array):
        print '>>> plotArray: process() is called'
        for term, vals in Array.items():
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
        c1 = self._ctrlWidget.p1
        c2 = self._ctrlWidget.p2
        return [c1, c2]

    def items(self):
        return self._items
        
    def ctrlWidget(self):
        return self._ctrlWidget

    def saveState(self):
        """overriding standard Node method to extend it with saving ctrlWidget state"""
        state = Node.saveState(self)
        # saving additionally state of the control widget
        #state['crtlWidget'] = self.ctrlWidget().saveState()
        return state
        
    def restoreState(self, state):
        """overriding standard Node method to extend it with restoring ctrlWidget state"""
        Node.restoreState(self, state)
        # additionally restore state of the control widget
        #self.ctrlWidget().restoreState(state['crtlWidget'])
        self.update()


    def clear(self):
        for item in self._items.values():
            self.removeItem(item)

    def close(self):
        self.clear()
        #print '---->>> CLOSE'
        self._ctrlWidget.win.hide()
        self._ctrlWidget.win.close()

        Node.close(self)

    @QtCore.pyqtSlot(object, object)
    def on_sigItemReceived(self, term, item):
        """ <term> is not <id(array)>, but it should be passed from parent widget
        """
        # check if this item exists
        if term in self._items.keys():  # if we have already something from this terminal
            if 'plotItems' in self._items[term].keys():
                if self._items[term]['plotItems'][0] is item:  # if the item is absolutely same
                    #print '>>> on_sigItemReceived(): already have something from term <{0}>: item <{1}> is the same'.format(term, item)
                    
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
                    #print '>>> on_sigItemReceived(): already have something from term <{0}>: item <{1}> is different'.format(term, item)
                    self.removeItems(self._items[term])

        if isinstance(item, (pg.PlotDataItem, pg.ScatterPlotItem)):
            #print '>>> on_sigItemReceived(): registering incoming item'
            self._items[term] = dict()
            # init symbol pen and size
            item.setSymbolPen(item.opts['pen'])
            item.setSymbolSize(5)

            #print '>>> on_sigItemReceived(): adding item to upper subplot'
            self.canvas()[0].addItem(item)

            # for some reason it is impossible to add same item to two subplots...
            #print '>>> on_sigItemReceived(): creating item-copy for bottom subplot'
            item2 = self.copyItem(item)
            
            #print '>>> on_sigItemReceived(): adding item-copy to bottom subplot'
            self.canvas()[1].addItem(item2)

            self._items[term]['plotItems'] = [item, item2]
            #print 'adding items: (1) {0} {1} >>> (2) {2} {3}'.format(item, type(item), item2, type(item2))
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


    def removeGraphicItem(self, item):
        try:
            self.canvas()[0].removeItem(item)
            self.canvas()[1].removeItem(item)
        except RuntimeError:  # sometimes happens by loading new chart (RuntimeError: wrapped C/C++ object of type PlotDataItem has been deleted)
            pass
        del item

    def removeItem(self, item):
        #print '>>> plotArray: removeItem is called'
        try:
            if 'plotItems' in item.keys() and isinstance(item['plotItems'], list) and len(item['plotItems']) == 2:
                #print '>>> plotArray: actually removing items'
                self.canvas()[0].removeItem(item['plotItems'][0])
                self.canvas()[1].removeItem(item['plotItems'][1])
        except RuntimeError:  # sometimes happens by loading new chart (RuntimeError: wrapped C/C++ object of type PlotDataItem has been deleted)
            #print '>>> plotArray: item not deleted'
            pass
        del item
        gc.collect()


class plotTimeseriesNodeCtrlWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(plotTimeseriesNodeCtrlWidget, self).__init__()
        uic.loadUi('/home/nck/prj/master_thesis/code/lib/flowchart/customnode_plottimeseries.ui', self)
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
        axis1 = DateAxisItem(orientation='bottom')
        axis2 = DateAxisItem(orientation='bottom')

        self.p1 = win.addPlot(row=1, col=0, axisItems={'bottom': axis1})
        #self.p1 = win.addPlot(row=1, col=0)
        self.p1.setClipToView(False)
        self.p2 = win.addPlot(row=2, col=0, axisItems={'bottom': axis2})
        #self.p2 = win.addPlot(row=2, col=0)
        self.p1.setClipToView(False)
        self.vb = self.p1.vb  # ViewBox
        
        self.zoomRegion = pg.LinearRegionItem()
        self.zoomRegion.setZValue(-10)
        self.zoomRegion.setRegion([1000, 2000])
        self.p2.addItem(self.zoomRegion, ignoreBounds=True)
        #self.p2.addItem(self.zoomRegion)
        
        self.p1.setAutoVisible(y=True)

        self.initCrosshair()
        self.toggleCrosshair()


        self.win = win


    def connectSignals(self):
        #self.parent().sigItemReceived.connect(self.createListWidgetItem)

        self.zoomRegion.sigRegionChanged.connect(self.on_zoomRegion_changed)
        self.p1.sigRangeChanged.connect(self.updateZoomRegion)

        self.proxy = pg.SignalProxy(self.p1.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

        self.checkBox_toggleCrosshair.stateChanged.connect(self.toggleCrosshair)
        self.checkBox_togglePoints.stateChanged.connect(self.togglePoints)


    def parent(self):
        return self._parent

    def initCrosshair(self):
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)

    def toggleCrosshair(self):
        if self.checkBox_toggleCrosshair.isChecked():
            #cross hair
            self.p1.addItem(self.vLine, ignoreBounds=True)
            self.p1.addItem(self.hLine, ignoreBounds=True)
        else:
            self.p1.removeItem(self.vLine)
            self.p1.removeItem(self.hLine)

    def togglePoints(self):
        with BusyCursor():
            for item in self.parent().items().values():
                # we want to toggle points only on upper subplot => index [0]
                if self.checkBox_togglePoints.isChecked():
                    symbol = 'x'
                else:
                    symbol = None
                item['plotItems'][0].setSymbol(symbol)



    def removeListWidgetItem(self, id):
        # remove item with given ID from the QListWidget
        QListWidgetItem = self.parent().items()[id]['arrayItem'].QListWidget()
        row = self.listWidget.row(QListWidgetItem)
        self.listWidget.takeItem(row)


    @QtCore.pyqtSlot()
    def on_zoomRegion_changed(self):
        #self.zoomRegion.setZValue(-10)
        minX, maxX = self.zoomRegion.getRegion()
        self.p1.setXRange(minX, maxX, padding=0)

    def updateZoomRegion(self, window, viewRange):
        rgn = viewRange[0]
        self.zoomRegion.setRegion(rgn)



    @QtCore.pyqtSlot()  #default signal
    def on_pushButton_plot_clicked(self):
        if not self.pushButton_plot.isChecked():
            self.win.hide()
        else:
            self.win.show()

    @QtCore.pyqtSlot(object)
    def mouseMoved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.p1.sceneBoundingRect().contains(pos):
            mousePoint = self.vb.mapSceneToView(pos)
            #index = int(mousePoint.x())
            #if index > 0 and index < len(data1):
            #    self.coordLabel.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), data1[index], data2[index]))
            
            # we add 1-hour manually (mouse.x+60*60). This is probably due to the TimeZone definition(???) in DateTimeAxis
            t = datetime.datetime.utcfromtimestamp(mousePoint.x()+60*60).strftime('%Y-%m-%d %H:%M')
            
            data_y = {}  # should be y-coordinates of the data lines
            self.setCoordLabelText(t, mousePoint.y(), **data_y)
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

    def setCoordLabelText(self, x_coord, y_coord, **kwargs):
        text = "<span style='font-size: 12pt'>t={0} | y={1:2.2f}".format(x_coord, y_coord)
        self.coordLabel.setText(text)



def test():
    app = QtWidgets.QApplication()
    ex = plotTimeseriesNodeCtrlWidget()
    ex.show()


    sys.exit(app.exec_())


if __name__ == '__main__':
    test()
