from pyqtgraph.Qt import QtGui
import pyqtgraph as pg
import numpy as np
import sys

class SubWindow(QtGui.QDialog): 

    def __init__(self, parent=None):
        super(SubWindow, self).__init__(parent)

        self.dataHistory = []

        self.plotItem()

        self.button_undo = QtGui.QPushButton()
        self.button_undo.setText('Undo')

        self.button_changedata = QtGui.QPushButton()
        self.button_changedata.setText('change_data')

        layout = QtGui.QGridLayout()
        layout.addWidget(self.button_changedata , 1, 1)
        layout.addWidget(self.button_undo, 2, 1)              
        layout.addWidget(self.pw         , 3, 1)        

        self.setLayout(layout)

        self.button_changedata.clicked.connect(self.changedata)
        self.button_undo      .clicked.connect(self.undo)

    def plotItem(self):

        self.x = np.linspace(0.0, 10.0, num=10)
        self.y = np.linspace(0.0, 10.0, num=10)

        self.plt    = pg.PlotDataItem(self.x, self.y)  
        self.vb     = pg.ViewBox()
        self.vb.addItem(self.plt) 
        self.pw     = pg.PlotWidget(viewBox = self.vb)          

        ###############################################
        self.history(self.y)
        ###############################################

    def changedata(self):

        self.newData()
        self.plt.setData(self.x, self.y_new)

    def undo(self):

        self.history(None)
        self.plt.setData(self.x, self.y_old)

    def newData(self):

        self.y_new = self.dataHistory[-1]
        self.y_new[0:3] = -999
        self.history(self.y_new)

    def history(self, new):

        if new is not None:
            self.dataHistory.append(new[:])  # copy of new
        else:
            if len(self.dataHistory) == 1:
                self.y_old = self.dataHistory[-1]
            else:
                del self.dataHistory[-1]
                self.y_old = self.dataHistory[-1]

        ###############################################
        print self.dataHistory
        ###############################################

if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    main = SubWindow()
    main.resize(500,500)
    main.move(app.desktop().screen().rect().center() - main.rect().center())
    main.show()
    sys.exit(app.exec_())