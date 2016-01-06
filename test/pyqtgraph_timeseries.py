# -*- coding: utf-8 -*-
"""
Description of example
"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from DateAxisItem import DateAxisItem
from datetime import datetime

print datetime.now()


pg.mkQApp()


axis = DateAxisItem(orientation='bottom')
pw = pg.PlotWidget(axisItems={'bottom': axis})
pw.setWindowTitle('pyqtgraph example: DateTimeAxis')
pw.show()
pw.setXRange(1383960000, 1384020000)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
