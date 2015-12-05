#!/usr/bin python
# -*- coding: utf-8 -*-

import pyqtgraph as pg

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt, qDebug
from pyqtgraph.flowchart.Node import Node
from pyqtgraph.functions import mkPen
import pyqtgraph as pg
from package import Package
import sys
from ..common.onedimarrayitem import OneDimArrayItem
from ..common.DateAxisItem import DateAxisItem



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


    def disconnected(self, localTerm, remoteTerm):
        if localTerm is self['Array'] and remoteTerm in self._items.keys():
            self.removeItem(remoteTerm)

    def connected(self, localTerm, remoteTerm):
        """Called whenever one of this node's terminals is connected elsewhere."""
        print 'TERMS CONNECTED'



    def process(self, Array):
        for term, vals in Array.items():
            print "???>>>", term
            print "???>>>", vals
            if vals is None:
                continue
            if type(vals) is not list:
                vals = [vals]
            
            for val in vals:
                if term in self._items.keys():
                    # if the data transmitted is different from the one saved...
                    if id(val) == id(self._items[term]['arrayItem'].array()):
                        continue
                    else:
                        self._items[term]['arrayItem'].update(array=val)
                        self.redraw()
                    print '>>>on_process(): removing ', term
                    #self.removeItem(term.name())
                self.sigItemReceived.emit(term, val)
                

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



    def removeItem(self, id):
        if id not in self._items.keys():
            return
        # first remove the widget from QListWidget
        self._ctrlWidget.removeListWidgetItem(id)

        # remove plotItems from canvas
        self._ctrlWidget.p1.removeItem(self._items[id]['plotItems'][0])
        self._ctrlWidget.p2.removeItem(self._items[id]['plotItems'][1])
        
        # delete plotItems
        del self._items[id]['plotItems']

        # Now disconnect signals
        ctrlWidget = self._items[id]['arrayItem'].ctrlWidget()
        ctrlWidget.pushButton_color.sigColorChanged.disconnect()
        ctrlWidget.lineEdit_name.textChanged.disconnect()
        ctrlWidget.spinBox_size.valueChanged.disconnect()

        # delete arrayItem
        del self._items[id]['arrayItem']

        # delete the whole entry
        del self._items[id]

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
    def on_sigItemReceived(self, id, array):
        """ <id> is not <id(array)>, but it should be passed from parent widget
        """
        self._items[id] = dict()
        if isinstance(array, (pg.PlotDataItem, pg.ScatterPlotItem)):
            l1 = self._ctrlWidget.p1.addItem(array)
            l2 = self._ctrlWidget.p2.addItem(array)
            self._items[id]['plotItems'] = [l1, l2]
            return
        # create arrayItem...
        arrayItem   = OneDimArrayItem(id=id, array=array)
        self._items[id]['arrayItem'] = arrayItem
        
        # create QListWidget...
        ctrlWidget  = arrayItem.ctrlWidget()
        QListWidget = arrayItem.QListWidget()
        
        # register signals to redraw graphical items on ui-changes
        ctrlWidget.pushButton_color.sigColorChanged.connect(self.redraw)
        ctrlWidget.lineEdit_name.textChanged.connect(self.redraw)
        ctrlWidget.spinBox_size.valueChanged.connect(self.redraw)

        self._ctrlWidget.listWidget.addItem(QListWidget)
        self._ctrlWidget.listWidget.setItemWidget(QListWidget, ctrlWidget)

        # now create graphic objects
        state = arrayItem.saveState()
        pen = mkPen(color=state['color'], width=state['size'])
        
        l1 = self._ctrlWidget.p1.plot(array, pen=pen)
        l2 = self._ctrlWidget.p2.plot(array, pen=pen)
        self._items[id]['plotItems'] = [l1, l2]


    def redraw(self):
        for iId in self._items.keys():
            state = self._items[iId]['arrayItem'].saveState()
            pen = mkPen(color=state['color'], width=state['size'])
            for plotItem in self._items[iId]['plotItems']:
                plotItem.setPen(pen)





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
        self.win = pg.GraphicsWindow(title=u"Node: "+unicode(self.parent().nodeName))
        self.win.resize(1000, 600)
        self.win.show()
        self.win.hide()
        #self.win.setWindowTitle(self.parent().nodeName)

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
        self.coordLabel = pg.LabelItem(justify='right')
        self.win.addItem(self.coordLabel)
        
        #add custom datetime axis
        axis1 = DateAxisItem(orientation='bottom')
        axis2 = DateAxisItem(orientation='bottom')

        self.p1 = self.win.addPlot(row=1, col=0, axisItems={'bottom': axis1})
        self.vb = self.p1.vb  # ViewBox
        self.p2 = self.win.addPlot(row=2, col=0, axisItems={'bottom': axis2})
        
        self.zoomRegion = pg.LinearRegionItem()
        self.zoomRegion.setZValue(10)
        self.zoomRegion.setRegion([1000, 2000])
        
        self.p2.addItem(self.zoomRegion, ignoreBounds=True)
        self.p1.setAutoVisible(y=True)

        self.initCrosshair()
        self.toggleCrosshair()

    def connectSignals(self):
        #self.parent().sigItemReceived.connect(self.createListWidgetItem)

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


    def removeListWidgetItem(self, id):
        # remove item with given ID from the QListWidget
        QListWidgetItem = self.parent().items()[id]['arrayItem'].QListWidget()
        row = self.listWidget.row(QListWidgetItem)
        self.listWidget.takeItem(row)


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
