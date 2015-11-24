#!/usr/bin python
# -*- coding: utf-8 -*-

import os, sys
from PyQt5 import QtWidgets, QtGui, uic
from flowchart_default import flowchart_default_widget
import ui_mainwindow as ui

#pyfile = open('ui_mainwindow.py', 'w')
#uic.compileUi('mainwindow.ui', pyfile)
#pyfile.close()

#class MainWindow(QtWidgets.QMainWindow):
class MainWindow(QtWidgets.QMainWindow, ui.Ui_MainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        #uic.loadUi('mainwindow.ui', self)
        self.initUI()
        

    def initUI(self):
        #self.main_widget = selectdata_dlg(path=os.path.dirname(os.path.abspath(sys.argv[0])))
        #self.setCentralWidget(self.main_widget)
        self.center()

        #fc_d = flowchart_default_widget()
        #self.flowChartWidget = fc_d.widget()
        pass
    
    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    ex.show()


    print type(ex.flowChartWidget)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()