# -*- coding: utf-8 -*-
from pyqtgraph.flowchart.Flowchart import Flowchart
from pyqtgraph.Qt import QtGui
from pyqtgraph import configfile as configfile
import traceback
import os


class customFlowchart(Flowchart):
    """Custom Flowchart
        - save/load now blocks mainwindow
        - input/output nodes are hidden
    """
    def __init__(self, parent=None, **kwargs):
        Flowchart.__init__(self, **kwargs)
        self.parent = parent
        self.inputNode.graphicsItem().hide()
        self.outputNode.graphicsItem().hide()

    def loadFile(self, fileName=None, startDir=None):
        print( 'loadFile called with fname:', fileName)
        if fileName is None:
            if startDir is None:
                startDir = self.filePath
            if startDir is None:
                startDir = '.'
            fname = QtGui.QFileDialog.getOpenFileName(self.parent, caption="Load Flowchart", directory=startDir, filter="Flowchart (*.fc)")[0]
            if fname:
                fileName = fname
            else:
                return
        fileName = unicode(fileName)
        try:
            state = configfile.readConfigFile(fileName)
            self.restoreState(state, clear=True)
            self.viewBox.autoRange()
            #self.emit(QtCore.SIGNAL('fileLoaded'), fileName)
            self.sigFileLoaded.emit(fileName)

            self.inputNode.graphicsItem().hide()
            self.outputNode.graphicsItem().hide()
        except Exception, err:
            traceback.print_exc()
            self.clear()
            QtGui.QMessageBox.warning(self.parent, "Load Flowchart", "Cannot load flowchart from file <i>{0}</i>".format(fileName))
            return
    
    def saveFile(self, fileName=None, startDir=None, suggestedFileName='flowchart.fc'):
        if fileName is None:
            if startDir is None:
                startDir = self.filePath
            if startDir is None:
                startDir = '.'
            fname = QtGui.QFileDialog.getSaveFileName(self.parent, caption="Save Flowchart As...", directory=startDir, filter="Flowchart (*.fc)")[0]
            if fname:
                fileName = fname
            else:
                return

        fileName = unicode(fileName)
        if os.path.splitext(fileName)[1] != '.fc':
            fileName += u'.fc'
        configfile.writeConfigFile(self.saveState(), fileName)
        self.sigFileSaved.emit(fileName)

    def addNode(self, node, name, pos=None):
        super(customFlowchart, self).addNode(node, name, pos=pos)
        if hasattr(node, 'sigUIStateChanged'):  #only my custom nodes do have this signal
            node.sigUIStateChanged.connect(lambda: self.sigChartChanged.emit(self, 'uiChanged', node))
