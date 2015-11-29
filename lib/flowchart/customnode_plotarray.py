#!/usr/bin python
# -*- coding: utf-8 -*-

import pyqtgraph as pg

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt, qDebug
from pyqtgraph.flowchart.Node import Node
from package import Package
import sys
from ..common.onedimarrayitem import OneDimArrayItem




class plotArrayNode(Node):
    """Plot number of 1D arrays as timeseries"""
    nodeName = "PlotArray"


    def __init__(self, name, parent=None):
        super(plotArrayNode, self).__init__(name, terminals={'Array': {'io': 'in', 'multi': True}})
        self._ctrlWidget = plotArrayNodeCtrlWidget(self)
            
    def process(self, Array):
        print 'process() received Array of ', type(Array)
        items = set()
        for name, vals in Array.items():
            if vals is None:
                continue
            if isinstance(vals, Package):
                vals = vals.unpack()
            if type(vals) is not list:
                vals = [vals]
            
            for val in vals:
                vid = id(val)
                if vid in self.items:
                    items.add(vid)
                else:
                    self.canvas.addItem(val)
                    item = val
                    self.items[vid] = item
                    items.add(vid)
        for vid in list(self.items.keys()):
            if vid not in items:
                #print "remove", self.items[vid]
                self.canvas.removeItem(self.items[vid])
                del self.items[vid]

        
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









class plotArrayNodeCtrlWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(plotArrayNodeCtrlWidget, self).__init__()
        uic.loadUi('/home/nck/prj/master_thesis/code/lib/flowchart/customnode_plotarray.ui', self)
        self._parent = parent
        self._listWidgetItems = set()  # registered items in ListWidget
        self.initUI()
        self.connectSignals()


    def initUI(self):
        self.win = pg.GraphicsWindow()
        self.win.resize(1000, 600)
        self.win.hide()
        #self.win.setWindowTitle(self.parent().nodeName)

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
        self.coordLabel = pg.LabelItem(justify='right')
        self.win.addItem(self.coordLabel)

        self.p1 = self.win.addPlot(row=1, col=0)
        self.vb = self.p1.vb  # ViewBox
        self.p2 = self.win.addPlot(row=2, col=0)
        
        self.zoomRegion = pg.LinearRegionItem()
        self.zoomRegion.setZValue(10)
        self.zoomRegion.setRegion([1000, 2000])
        
        self.p2.addItem(self.zoomRegion, ignoreBounds=True)
        self.p1.setAutoVisible(y=True)

        self.initCrosshair()
        self.toggleCrosshair()

    def connectSignals(self):
        self.zoomRegion.sigRegionChanged.connect(self.on_zoomRegion_changed)
        self.p1.sigRangeChanged.connect(self.updateZoomRegion)
        self.proxy = pg.SignalProxy(self.p1.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

        self.checkBox_toggleCrosshair.stateChanged.connect(self.toggleCrosshair)


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

    def addListWidgetItem(self, name=None, array=None, state=None):
        item = OneDimArrayItem(name=name, array=array)
        if state is not None and name == state['originalName']:
            item.restoreState(state)
            self.listWidget.appendRow(item)
            self._listWidgetItems.add(id(item))        


    @QtCore.pyqtSlot()
    def on_zoomRegion_changed(self):
        self.zoomRegion.setZValue(10)
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
            self.setCoordLabelText(mousePoint.x())
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

    def setCoordLabelText(self, x_coord):
        self.coordLabel.setText("<span style='font-size: 12pt'>x=%0.1f" % x_coord)



def test():
    app = QtWidgets.QApplication()
    ex = plotArrayNodeCtrlWidget()
    ex.show()


    sys.exit(app.exec_())


if __name__ == '__main__':
    test()
