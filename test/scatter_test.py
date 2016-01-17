# -*- coding: utf-8 -*-
"""
Example demonstrating a variety of scatter plot features.
"""


from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

app = QtGui.QApplication([])
mw = QtGui.QMainWindow()
mw.resize(800,800)
view = pg.GraphicsLayoutWidget()  ## GraphicsView with GraphicsLayout inserted by default
mw.setCentralWidget(view)
mw.show()
mw.setWindowTitle('pyqtgraph example: ScatterPlot')

w4 = view.addPlot()
print("Generating data, this takes a few seconds...")

## Make all plots clickable
import timeit

lastClicked = []
def clicked(plot, points):
    start = timeit.default_timer()
    global lastClicked
    for p in lastClicked:
        p.resetPen()
#     print("clicked points", points)
    for p in points:
        p.setPen('b', width=2)
    lastClicked = points
    stop = timeit.default_timer()
    print(stop - start)
    
## Test performance of large scatterplots

s4 = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 20))
pos = np.random.normal(size=(2,10000), scale=1e-9)
s4.addPoints(x=pos[0], y=pos[1])
w4.addItem(s4)


s4.sigClicked.connect(clicked)

## Start Qt event loop unless running in interactive mode.

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()