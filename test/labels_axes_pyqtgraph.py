from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

app = QtGui.QApplication([])
view = pg.GraphicsView()
l = pg.GraphicsLayout(border=(100,100,100))
view.setCentralItem(l)
view.show()
view.setWindowTitle('pyqtgraph example: GraphicsLayout')
view.resize(800,600)


l2 = l.addLayout(colspan=3, border=(50,0,0))
l2.setContentsMargins(10, 10, 10, 10)
l2.addLabel("Sub-layout: this layout demonstrates the use of shared    axes and axis labels", colspan=3)
l2.nextRow()
l2.addLabel('Vertical Axis Label', angle=-90, rowspan=2)
p21 = l2.addPlot()
p21.setYRange(0,1000)
l2.nextRow()
p23 = l2.addPlot()
p23.setYRange(0,50)
l2.nextRow()
l2.addLabel("HorizontalAxisLabel", col=1, colspan=1)

## hide axes on some plots
p21.hideAxis('bottom')
p21.hideButtons()
p23.hideButtons()

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore,   'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
