#!/usr/bin python
# -*- coding: utf-8 -*-

import pyqtgraph as pg

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt, qDebug
from pyqtgraph.flowchart.Node import Node
from pyqtgraph.functions import mkPen
import pyqtgraph as pg
import sys
from ..common.onedimarrayitem import OneDimArrayItem
from ..common.DateAxisItem import DateAxisItem
from copy import copy, deepcopy
import datetime
import time
from pyqtgraph import BusyCursor


class plotArrayNode(Node):
    """Plot number of 1D arrays as timeseries"""
    nodeName = "PlotArray"

    sigItemReceived    = QtCore.Signal(object, object)  #(id(item), item)
    sigRegItemReceived = QtCore.Signal(object)  #allready registered item received (id(item))

    def __init__(self, name, parent=None):
        super(plotArrayNode, self).__init__(name, terminals={'Array': {'io': 'in', 'multi': True}})
        self._ctrlWidget = plotArrayNodeCtrlWidget(self)
        #self.items = set()   #set to save incoming items
        self._items = dict()
        self.sigItemReceived.connect(self.on_sigItemReceived)

    def items(self):
        return self._items

    def disconnected(self, localTerm, remoteTerm):
        if localTerm is self['Array'] and remoteTerm in self._items.keys():
            print "localTerm <{0}> is diconnected from remoteTerm <{1}>".format(localTerm, remoteTerm)
            if 'plotItems' in self._items[remoteTerm].keys():
                item1, item2 = self._items[remoteTerm]['plotItems']
                self.removeItem(item1)
                self.removeItem(item2)
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
                # gui-based handling of exeptions (will result in crash)
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
        """overriding stadart Node method to extend it with saving ctrlWidget state"""
        state = Node.saveState(self)
        # sacing additionaly state of the control widget
        #state['crtlWidget'] = self.ctrlWidget().saveState()
        return state
        
    def restoreState(self, state):
        """overriding stadart Node method to extend it with restoring ctrlWidget state"""
        Node.restoreState(self, state)
        # additionally restore state of the control widget
        #self.ctrlWidget().restoreState(state['crtlWidget'])
        self.update()


    def clear(self):
        for iId in self._items.keys():
            self.removeItem(iId)

    def close(self):
        self.clear()
        print '---->>> CLOSE'
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
                    #print '>>> on_sigItemReceived(): {0}: item is the same'.format(term)
                    return
        if isinstance(item, (pg.PlotDataItem, pg.ScatterPlotItem)):
            self._items[term] = dict()
            # init symbol pen and size
            item.setSymbolPen(item.opts['pen'])
            item.setSymbolSize(5)

            self.canvas()[0].addItem(item)

            # for some reason it is impossible to add same item to two subplots...
            opts = item.opts
            opts['clipToView'] = False  #  we need to change it to False, because for some reason it fails....
            item2 = pg.PlotDataItem(item.xData, item.yData, **opts)
            
            self.canvas()[1].addItem(item2)

            self._items[term]['plotItems'] = [item, item2]
            #print 'adding items: (1) {0} {1} >>> (2) {2} {3}'.format(item, type(item), item2, type(item2))
            return


    def redraw(self):
        for iId in self._items.keys():
            state = self._items[iId]['arrayItem'].saveState()
            pen = mkPen(color=state['color'], width=state['size'])
            for plotItem in self._items[iId]['plotItems']:
                plotItem.setPen(pen)


    def removeItem(self, item):
        try:
            self.canvas()[0].removeItem(item)
            self.canvas()[1].removeItem(item)
        except RuntimeError:  # somtimes happens by loading new chart (RuntimeError: wrapped C/C++ object of type PlotDataItem has been deleted)
            pass
        del item


class plotArrayNodeCtrlWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(plotArrayNodeCtrlWidget, self).__init__()
        uic.loadUi('/home/nck/prj/master_thesis/code/lib/flowchart/customnode_plotarray.ui', self)
        self._parent = parent
        self._listWidgetItems = set()  # registered items in ListWidget
        self.initUI()
        self.connectSignals()
        self.items = dict()


    def initUI(self):
        win = pg.GraphicsLayoutWidget()
        win.resize(1000, 600)
        win.setWindowTitle(u"Node: "+unicode(self.parent().name()))

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
        # Add Label where coords of current bouse position will be printed
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
            index = int(mousePoint.x())
            #if index > 0 and index < len(data1):
            #    self.coordLabel.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), data1[index], data2[index]))
            t = datetime.datetime.utcfromtimestamp(mousePoint.x()+60*60).strftime('%Y-%m-%d %H:%M')  # we add 1hour manually. This is probably due to the bug in DateTimeAxis
            data_y = {}  # should be y-coordinates of the data lines
            self.setCoordLabelText(t, **data_y)
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

    def setCoordLabelText(self, x_coord, **kwargs):
        text = "<span style='font-size: 12pt'>t={0}".format(x_coord)
        self.coordLabel.setText(text)



def test():
    app = QtWidgets.QApplication()
    ex = plotArrayNodeCtrlWidget()
    ex.show()


    sys.exit(app.exec_())


if __name__ == '__main__':
    test()
