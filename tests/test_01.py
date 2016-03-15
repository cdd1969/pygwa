from __future__ import print_function
import sys
import os
# hack our sys argv path to match BASEDIRECTORY
sys.argv[0] = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), os.pardir, 'pygwa.py'))

import unittest

from PyQt5 import QtGui, QtCore
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt


import numpy as np
import matplotlib.pyplot as plt

from lib.mainWindow import MainWindow
from lib import projectPath

"""
to run this test

    $ git clone https://github.com/cdd1969/pygwa.git pygwa
    $ cd pygwa
    $ python -m tests.test_01 -v

"""

app = QtGui.QApplication(sys.argv)
plt.ion()  #enable matplotlib interactive mode

if '-v' in sys.argv:
    log = True
else:
    log = False


class FlowchartNodesTest(unittest.TestCase):
    '''Test different nodes in PyGWA GUI'''

    def setUp(self):
        '''Create the GUI'''
        self.form = MainWindow()
        self.form._unittestmode = True
        self.fc = self.form.fc
        self.nodeTypes = self.form.uiData.fclib().getNodeList()
        
    def tearDown(self):
        plt.close('all')
        self.form.close()
        del self.form
        if log: print('')

    def readXLS(self, path=None):
        ''' Read XLS and return the node'''
        if path is None:
            # now set test_data file
            path = projectPath('../TUTORIALS/test_data.xlsx')

        n = self.fc.createNode('readXLS', pos=(0, 0))
        p = n.ctrlWidget().param  #alias to method
        p('Select File').setValue(path)
        #set some params...
        p('Parameters', 'skiprows').setValue(0)
        p('Parameters', 'skip_footer').setValue(0)
        p('Parameters', 'na_values').setValue(u'---')
        #load data
        p('Load File').activate()
        return n

    def test_01_init(self):
        '''Test the GUI in its default state by initializing it'''
        print ('sys.argv = ', sys.argv)
    
    def test_02_add_nodes(self):
        ''' Test GUI by adding number of nodes'''
        for nodeType in self.nodeTypes:
            if log: print ('\tadding node `{0}`...'.format(nodeType), end='')
            self.fc.createNode(nodeType, pos=(0, 0))
            if log: print ('ok')

    def test_03_node_readXLS(self):
        ''' Add Node `readXLS`, load data'''
        self.readXLS()

    def test_04_node_QuickView(self):
        ''' Connect node QuickView to readXLS and view data'''
        readXLS = self.readXLS()
        QuickView = self.fc.createNode('QuickView', pos=(0, 0))
        self.fc.connectTerminals(readXLS['output'], QuickView['In'])
        
        QTest.mouseClick(QuickView.ctrlWidget().pushButton_viewTable, Qt.LeftButton)
        #QuickView.ctrlWidget().twWindow.close()

        QTest.mouseClick(QuickView.ctrlWidget().pushButton_viewPlot, Qt.LeftButton)
        


    def test_05_node_TimeseriesPlot(self):
        ''' Load data, create two curves with node `makeTimeseriesCurve` and plot them with node `TimeseriesPlot`'''
        readXLS = self.readXLS()
        curve1 = self.fc.createNode('makeTimeseriesCurve', pos=(0, 0))
        curve2 = self.fc.createNode('makeTimeseriesCurve', pos=(0, 0))
        plotNode = self.fc.createNode('TimeseriesPlot', pos=(0, 0))
        self.fc.connectTerminals(readXLS['output'], curve1['df'])
        self.fc.connectTerminals(readXLS['output'], curve2['df'])

        curve1.ctrlWidget().p.param('Y:signal').setValue(u'River')
        curve1.ctrlWidget().p.param('tz correct').setValue(1.2)

        self.fc.connectTerminals(curve1['Curve'], plotNode['Curves'])
        self.fc.connectTerminals(curve2['Curve'], plotNode['Curves'])

        plotNode.ctrlWidget().p.param('Y:Label').setValue('test label')
        plotNode.ctrlWidget().p.param('Y:Units').setValue('test units')
        plotNode.ctrlWidget().p.param('Crosshair').setValue(True)
        plotNode.ctrlWidget().p.param('Data Points').setValue(True)
        plotNode.ctrlWidget().p.param('Plot').activate()


    def test_06_node_StatisticalAnalysis(self):
        ''' Load data, perform stat analysis'''
        readXLS = self.readXLS()
        statAnalysis = self.fc.createNode('Plot Histogram', pos=(0, 0))

        self.fc.connectTerminals(readXLS['output'], statAnalysis['In'])

        statAnalysis.ctrlWidget().p.param('Signal').setValue('GW_2')
        statAnalysis.ctrlWidget().p.param('Signal Units').setValue('test units')
        statAnalysis.ctrlWidget().p.param('Histogram Type').setValue('Normalized')
        statAnalysis.ctrlWidget().p.param('Bins').setValue(15)
        statAnalysis.ctrlWidget().p.param('Plot').activate()



if __name__ == "__main__":
    unittest.main()
