# -*- coding: utf-8 -*-
"""
This example demonstrates writing a custom Node subclass for use with flowcharts.

We implement a couple of simple image processing nodes.
"""

from pyqtgraph.flowchart import Flowchart
import pyqtgraph.flowchart.library as fclib
import numpy as np
import pyqtgraph.metaarray as metaarray
import pyqtgraph as pg
from PyQt5 import QtWidgets



class flowchartWidgetDefault(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self)
        ## Create flowchart, define input/output terminals
        

        fc = Flowchart(terminals={
            'dataIn': {'io': 'in'},
            'dataOut': {'io': 'out'}
        })
        
        ## Add two plot widgets
        pw1 = pg.PlotWidget()
        pw2 = pg.PlotWidget()

        ## generate signal data to pass through the flowchart
        data = np.random.normal(size=1000)
        data[200:300] += 1
        data += np.sin(np.linspace(0, 100, 1000))
        data = metaarray.MetaArray(data, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data))}, {}])

        ## Feed data into the input terminal of the flowchart
        fc.setInput(dataIn=data)

        ## populate the flowchart with a basic set of processing nodes. 
        ## (usually we let the user do this)
        plotList = {'Top Plot': pw1, 'Bottom Plot': pw2}

        pw1Node = fc.createNode('PlotWidget', pos=(0, -150))
        pw1Node.setPlotList(plotList)
        pw1Node.setPlot(pw1)

        pw2Node = fc.createNode('PlotWidget', pos=(150, -150))
        pw2Node.setPlot(pw2)
        pw2Node.setPlotList(plotList)

        fNode = fc.createNode('GaussianFilter', pos=(0, 0))
        fNode.ctrls['sigma'].setValue(5)
        fc.connectTerminals(fc['dataIn'], fNode['In'])
        fc.connectTerminals(fc['dataIn'], pw1Node['In'])
        fc.connectTerminals(fNode['Out'], pw2Node['In'])
        fc.connectTerminals(fNode['Out'], fc['dataOut'])
        self.fc = fc
        self.widget = fc.widget()



"""
class flowchartWidgetDefault(flowchartWidgetDefault1.widget()):
    def __init__(self, parent=None):
        flowchartWidgetDefault.__init__(self)
"""
