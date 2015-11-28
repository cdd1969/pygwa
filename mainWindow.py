#!/usr/bin python
# -*- coding: utf-8 -*-

import os, sys
from PyQt5 import QtWidgets, QtGui, uic, QtCore
from pyqtgraph.flowchart import Flowchart


#pyfile = open('ui_mainwindow.py', 'w')
#uic.compileUi('mainwindow.ui', pyfile)
#pyfile.close()

class MainWindow(QtWidgets.QMainWindow):
#class MainWindow(QtWidgets.QMainWindow, ui.Ui_MainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        #self.setupUi(self)
        uic.loadUi('mainwindow.ui', self)
        self.uiData = uiData(self)
        self.connectActions()
        #self.connectSignals()
        self.initUI()
        
        

    def initUI(self):
        self.center()
        self.initFlowchart()
        pass
    
    def connectActions(self):
        self.actionNew_fc.triggered.connect(self.on_actionNew_fc)
        self.actionSave_fc.triggered.connect(self.on_actionSave_fc)
        self.actionSave_As_fc.triggered.connect(self.on_actionSave_As_fc)
        self.actionLoad_fc.triggered.connect(self.on_actionLoad_fc)
        self.actionQuit.triggered.connect(QtWidgets.qApp.quit)

    def connectFCSignals(self):
        self.fc.sigFileLoaded.connect(self.uiData.setCurrentFileName)
        self.fc.sigFileSaved.connect(self.uiData.setCurrentFileName)


    def initFlowchart(self):
        # removing dummyWidget created with QtDesigner
        self.layoutTab1.removeWidget(self.flowChartWidget)
        del self.flowChartWidget

        # generating flowchart instance. Further we will work only with this instance,
        # simply saving/loading it's state.
        self.fc = Flowchart(terminals={
        'dataIn': {'io': 'in'},
        'dataOut': {'io': 'out'}}, library=self.uiData.flowchartLib())
        
        # connecting standard signals of the flowchart
        self.connectFCSignals()

        # load default scheme
        self.on_actionNew_fc()

        # placing the real widget on the place of a dummy
        self.flowChartWidget = self.fc.widget().chartWidget
        self.layoutTab1.addWidget(self.flowChartWidget)
    

    @QtCore.pyqtSlot()
    def on_actionNew_fc(self):
        self.fc.loadFile(fileName=self.uiData.standardFileName())
        self.uiData.setCurrentFileName(None)

    @QtCore.pyqtSlot()
    def on_actionSave_fc(self,):
        self.fc.saveFile(fileName=self.uiData.currentFileName())

    @QtCore.pyqtSlot()
    def on_actionSave_As_fc(self):
        self.fc.saveFile()
    
    @QtCore.pyqtSlot()
    def on_actionLoad_fc(self):
        self.fc.loadFile()
    
    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())





import pyqtgraph.flowchart.library as fclib
from lib.flowchart.customnode_readtextdata import readTextDataNode
from lib.flowchart.customnode_viewpandasdf import viewPandasDfNode
from lib.flowchart.customnode_selectdfcolumn import selectDfColumnNode

class uiData(object):
    """ class to collect all our user-interface settings,
        and to seperate these params from MainWindow class"""
    def __init__(self, parent=None):
        self.parent = parent
        self.initLibrary()
        self._currentFileName  = None
        self._standardFileName = 'lib/common/default.fc'


    def initLibrary(self):
        self._flowchartLib = fclib.LIBRARY.copy()  # start with the default node set
        self._flowchartLib.addNodeType(readTextDataNode, [('My',)])
        self._flowchartLib.addNodeType(viewPandasDfNode, [('My',)])
        self._flowchartLib.addNodeType(selectDfColumnNode, [('My',)])


    def currentFileName(self):
        return self._currentFileName

    @QtCore.pyqtSlot(str)
    def setCurrentFileName(self, name):
        self._currentFileName = name

    def standardFileName(self):
        return self._standardFileName

    def flowchartLib(self):
        return self._flowchartLib

def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    ex.show()


    print type(ex.flowChartWidget)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()