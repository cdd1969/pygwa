# -*- coding: utf-8 -*-
"""
This block is the reimplementation of FlowChart module from pyqtgraph,
tuned for my custom needs

Source: pyqtgraph, branch <devel>, commit <0976991efda1825d8f92b2462ded613bcadef188>
Original author: Luke Campagnola
Original file: pyqtgraph/flowchart/Flowchart.py
"""

import os
from pyqtgraph.Qt import QtCore, QtGui, USE_PYSIDE, USE_PYQT5
from pyqtgraph.flowchart.Node import Node, GraphicsObject
from pyqtgraph.pgcollections import OrderedDict
from pyqtgraph.widgets.TreeWidget import TreeWidget
from pyqtgraph import FileDialog, DataTreeWidget



from pyqtgraph.flowchart.Terminal import Terminal
from numpy import ndarray
import numpy as np
from pyqtgraph.flowchart.library import LIBRARY
from pyqtgraph.debug import printExc
from pyqtgraph import configfile as configfile
from pyqtgraph import dockarea as dockarea
from pyqtgraph.flowchart import FlowchartGraphicsView
from pyqtgraph import functions as fn

        

class Flowchart(object):
    sigFileLoaded = QtCore.Signal(object)
    sigFileSaved = QtCore.Signal(object)
    #sigOutputChanged = QtCore.Signal() ## inherited from Node
    sigChartLoaded = QtCore.Signal()
    sigStateChanged = QtCore.Signal()  # called when output is expected to have changed
    sigChartChanged = QtCore.Signal(object, object, object) # called when nodes are added, removed, or renamed.
                                                            # (self, action, node)
    
    def __init__(self, name=None, filePath=None, library=None):
        self.library = library or LIBRARY
        if name is None:
            name = "Flowchart"

        self.filePath = filePath
               
        self._nodes     = {}
        self.nextZVal   = 10
        self.processing = False  ## flag that prevents recursive node updates
        self._gui       = None
        self.gui()  # Initialize gui
    
    def setLibrary(self, lib):
        self.library = lib


    def createNode(self, nodeType, name=None, pos=None):
        if name is None:
            n = 0
            while True:
                name = "%s.%d" % (nodeType, n)
                if name not in self._nodes:
                    break
                n += 1
        node = self.library.getNodeType(nodeType)(name)
        self.addNode(node, name, pos)
        return node
        
    def addNode(self, node, name, pos=None):
        if pos is None:
            pos = [0, 0]
        if type(pos) in [QtCore.QPoint, QtCore.QPointF]:
            pos = [pos.x(), pos.y()]
        
        # create graphical item of a node in FlowChart
        item = node.graphicsItem()
        item.setZValue(self.nextZVal*2)
        self.nextZVal += 1
        self.gui().viewBox.addItem(item)
        item.moveBy(*pos)

        self._nodes[name] = node
        self.gui().addNode(node)
        
        # connect new node to signals
        node.sigClosed.connect(self.nodeClosed)
        node.sigRenamed.connect(self.nodeRenamed)
        node.sigOutputChanged.connect(self.nodeOutputChanged)
        self.sigChartChanged.emit(self, 'add', node)
        
    def removeNode(self, node):
        node.close()
        
    def nodeClosed(self, node):
        del self._nodes[node.name()]
        self.gui().removeNode(node)
        for signal in ['sigClosed', 'sigRenamed', 'sigOutputChanged']:
            try:
                getattr(node, signal).disconnect(self.nodeClosed)
            except (TypeError, RuntimeError):
                pass
        self.sigChartChanged.emit(self, 'remove', node)
        
    def nodeRenamed(self, node, oldName):
        del self._nodes[oldName]
        self._nodes[node.name()] = node
        self.gui().nodeRenamed(node, oldName)
        self.sigChartChanged.emit(self, 'rename', node)

        
    def connectTerminals(self, term1, term2):
        """Connect two terminals together within this flowchart."""
        term1 = self.internalTerminal(term1)
        term2 = self.internalTerminal(term2)
        term1.connectTo(term2)

    def clear(self):
        for n in list(self._nodes.values()):
            if n is self.inputNode or n is self.outputNode:
                continue
            n.close()  ## calls self.nodeClosed(n) by signal
        self.gui().clear()

    # ------------------------------------------------------------------------------------------
    # ------------------------------  GETTERS  -------------------------------------------------
    # ------------------------------------------------------------------------------------------

    def nodes(self):
        return self._nodes

    def chartGraphicsItem(self):
        """Return the graphicsItem which displays the internals of this flowchart.
        (graphicsItem() still returns the external-view item)"""
        #return self._chartGraphicsItem
        return self._gui.viewBox()

    def gui(self):
        if self._gui is None:
            # initialize gui widget
            self._gui = FlowchartCtrlWidget(self)
            self._gui.viewBox.autoRange(padding=0.04)
        return self._gui
        
















class FlowchartCtrlWidget(QtGui.QWidget):
    """The widget that contains the list of all the nodes in a flowchart and their controls, as well as buttons for loading/saving flowcharts."""
    
    def __init__(self, chart):
        self.items = {}
        #self.loadDir = loadDir  ## where to look initially for chart files
        self.currentFileName = None
        QtGui.QWidget.__init__(self)
        self.chart = chart

        self.chartWidget = FlowchartWidget(chart, self)

        self.cwWin = QtGui.QMainWindow()
        self.cwWin.setWindowTitle('Flowchart')
        self.cwWin.setCentralWidget(self.chartWidget)
        self.cwWin.resize(1000, 800)
        self.cwWin.show()

    def scene(self):
        return self.chartWidget.scene()  ## returns the GraphicsScene object
    
    def viewBox(self):
        return self.chartWidget.viewBox()

    def chartWidget(self):
        return self.chartWidget

    def clear(self):
        self.chartWidget.clear()



















class FlowchartWidget(dockarea.DockArea):
    """Includes the actual graphical flowchart and debugging interface"""
    def __init__(self, chart, ctrl):
        #QtGui.QWidget.__init__(self)
        dockarea.DockArea.__init__(self)
        self.chart = chart
        self.ctrl = ctrl
        self.hoverItem = None

        ## build user interface (it was easier to do it here than via developer)
        self._view = FlowchartGraphicsView.FlowchartGraphicsView(self)

        self.viewDock = dockarea.Dock('view', size=(1000, 600))
        self.viewDock.addWidget(self._view)
        self.viewDock.hideTitleBar()
        self.addDock(self.viewDock)
    

        self.hoverText = QtGui.QTextEdit()
        self.hoverText.setReadOnly(True)
        self.hoverDock = dockarea.Dock('Hover Info', size=(1000, 20))
        self.hoverDock.addWidget(self.hoverText)
        self.addDock(self.hoverDock, 'bottom')

        self.selInfo = QtGui.QWidget()
        self.selInfoLayout = QtGui.QGridLayout()
        self.selInfo.setLayout(self.selInfoLayout)
        self.selDescLabel = QtGui.QLabel()
        self.selNameLabel = QtGui.QLabel()
        self.selDescLabel.setWordWrap(True)
        self.selectedTree = DataTreeWidget()

        self.selInfoLayout.addWidget(self.selDescLabel)
        self.selInfoLayout.addWidget(self.selectedTree)
        self.selDock = dockarea.Dock('Selected Node', size=(1000, 200))
        self.selDock.addWidget(self.selInfo)
        self.addDock(self.selDock, 'bottom')

        self.buildMenu()
    
        self.scene().selectionChanged.connect(self.selectionChanged)
        self.scene().sigMouseHover.connect(self.hoverOver)

        
    def buildMenu(self, pos=None):
        def buildSubMenu(node, rootMenu, pos=None):
            for section, node in node.items():
                menu = QtGui.QMenu(section)
                
                rootMenu.addMenu(menu)
                
                if isinstance(node, OrderedDict):
                    buildSubMenu(node, menu, pos=pos)
                else:
                    act = rootMenu.addAction(section)
                    act.nodeType = section
                    act.pos = pos
        self.nodeMenu = QtGui.QMenu()
        buildSubMenu(self.chart.library.getNodeTree(), self.nodeMenu, pos=pos)
        self.nodeMenu.triggered.connect(self.nodeMenuTriggered)
        return self.nodeMenu
    
    def menuPosChanged(self, pos):
        self.menuPos = pos
    
    def showViewMenu(self, ev):
        self.buildMenu(ev.scenePos())
        self.nodeMenu.popup(ev.screenPos())
        
    def scene(self):
        return self._view.scene()  ## the GraphicsScene item

    def viewBox(self):
        return self._view.viewBox()  ## the viewBox that items should be added to

    def nodeMenuTriggered(self, action):
        nodeType = action.nodeType
        if action.pos is not None:
            pos = action.pos
        else:
            pos = self.menuPos
        pos = self.viewBox().mapSceneToView(pos)

        self.chart.createNode(nodeType, pos=pos)


    def selectionChanged(self):
        #print "FlowchartWidget.selectionChanged called."
        items = self._scene.selectedItems()
        #print "     scene.selectedItems: ", items
        if len(items) == 0:
            data = None
        else:
            item = items[0]
            if hasattr(item, 'node') and isinstance(item.node, Node):
                n = item.node
                self.ctrl.select(n)
                data = {'outputs': n.outputValues(), 'inputs': n.inputValues()}
                self.selNameLabel.setText(n.name())
                if hasattr(n, 'nodeName'):
                    self.selDescLabel.setText("<b>%s</b>: %s" % (n.nodeName, n.__class__.__doc__))
                else:
                    self.selDescLabel.setText("")
                if n.exception is not None:
                    data['exception'] = n.exception
            else:
                data = None
        self.selectedTree.setData(data, hideRoot=True)

    def hoverOver(self, items):
        #print "FlowchartWidget.hoverOver called."
        term = None
        for item in items:
            if item is self.hoverItem:
                return
            self.hoverItem = item
            if hasattr(item, 'term') and isinstance(item.term, Terminal):
                term = item.term
                break
        if term is None:
            self.hoverText.setPlainText("")
        else:
            val = term.value()
            if isinstance(val, ndarray):
                val = "%s %s %s" % (type(val).__name__, str(val.shape), str(val.dtype))
            else:
                val = str(val)
                if len(val) > 400:
                    val = val[:400] + "..."
            self.hoverText.setPlainText("%s.%s = %s" % (term.node().name(), term.name(), val))
            #self.hoverLabel.setCursorPosition(0)

    

    def clear(self):
        #self.outputTree.setData(None)
        self.selectedTree.setData(None)
        self.hoverText.setPlainText('')
        self.selNameLabel.setText('')
        self.selDescLabel.setText('')





if __name__ == '__main__':
    import pyqtgraph as pg
    import pyqtgraph.flowchart.library as fclib
    from pyqtgraph.flowchart.library.common import CtrlNode
    app = QtGui.QApplication([])

    ## Create main window with a grid layout inside
    win = QtGui.QMainWindow()
    win.setWindowTitle('pyqtgraph example: FlowchartCustomNode')
    cw = QtGui.QWidget()
    win.setCentralWidget(cw)


    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    ## Create an empty flowchart with a single input and output
    fc = Flowchart(terminals={
        'dataIn': {'io': 'in'},
        'dataOut': {'io': 'out'}    
    })
    w = fc.widget()

    layout.addWidget(fc.widget(), 0, 0, 2, 1)

    ## Create two ImageView widgets to display the raw and processed data with contrast
    ## and color control.
    v1 = pg.ImageView()
    v2 = pg.ImageView()
    layout.addWidget(v1, 0, 1)
    layout.addWidget(v2, 1, 1)

    win.show()

    ## generate random input data
    data = np.random.normal(size=(100, 100))
    data = 25 * pg.gaussianFilter(data, (5, 5))
    data += np.random.normal(size=(100, 100))
    data[40:60, 40:60] += 15.0
    data[30:50, 30:50] += 15.0

    ## Set the raw data as the input value to the flowchart
    fc.setInput(dataIn=data)


    ## At this point, we need some custom Node classes since those provided in the library
    ## are not sufficient. Each node will define a set of input/output terminals, a
    ## processing function, and optionally a control widget (to be displayed in the
    ## flowchart control panel)

    class ImageViewNode(Node):
        """Node that displays image data in an ImageView widget"""
        nodeName = 'ImageView'
        
        def __init__(self, name):
            self.view = None
            ## Initialize node with only a single input terminal
            Node.__init__(self, name, terminals={'data': {'io': 'in'}})
            
        def setView(self, view):  ## setView must be called by the program
            self.view = view
            
        def process(self, data, display=True):
            ## if process is called with display=False, then the flowchart is being operated
            ## in batch processing mode, so we should skip displaying to improve performance.
            
            if display and self.view is not None:
                ## the 'data' argument is the value given to the 'data' terminal
                if data is None:
                    self.view.setImage(np.zeros((1, 1)))  # give a blank array to clear the view
                else:
                    self.view.setImage(data)

        
    class UnsharpMaskNode(CtrlNode):
        """Return the input data passed through an unsharp mask."""
        nodeName = "UnsharpMask"
        uiTemplate = [
            ('sigma',  'spin', {'value': 1.0, 'step': 1.0, 'bounds': [0.0, None]}),
            ('strength', 'spin', {'value': 1.0, 'dec': True, 'step': 0.5, 'minStep': 0.01, 'bounds': [0.0, None]}),
        ]
        
        def __init__(self, name):
            ## Define the input / output terminals available on this node
            terminals = {
                'dataIn': dict(io='in'),    # each terminal needs at least a name and
                'dataOut': dict(io='out'),  # to specify whether it is input or output
            }                               # other more advanced options are available
                                            # as well..
            
            CtrlNode.__init__(self, name, terminals=terminals)
            
        def process(self, dataIn, display=True):
            # CtrlNode has created self.ctrls, which is a dict containing {ctrlName: widget}
            sigma = self.ctrls['sigma'].value()
            strength = self.ctrls['strength'].value()
            output = dataIn - (strength * pg.gaussianFilter(dataIn, (sigma, sigma)))
            return {'dataOut': output}


    library = fclib.LIBRARY.copy()  # start with the default node set
    library.addNodeType(ImageViewNode, [('Display',)])
    library.addNodeType(UnsharpMaskNode, [('Image',),
                                          ('Submenu_test', 'submenu2', 'submenu3')])
    fc.setLibrary(library)

    v1Node = fc.createNode('ImageView', pos=(0, -150))
    v1Node.setView(v1)

    v2Node = fc.createNode('ImageView', pos=(150, -150))
    v2Node.setView(v2)

    fNode = fc.createNode('UnsharpMask', pos=(0, 0))
    fc.connectTerminals(fc['dataIn'], fNode['dataIn'])
    fc.connectTerminals(fc['dataIn'], v1Node['data'])
    fc.connectTerminals(fNode['dataOut'], v2Node['data'])
    fc.connectTerminals(fNode['dataOut'], fc['dataOut'])



    QtGui.QApplication.instance().exec_()
