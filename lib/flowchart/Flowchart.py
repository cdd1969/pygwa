# -*- coding: utf-8 -*-
from pyqtgraph.flowchart.Flowchart import Flowchart
from pyqtgraph.flowchart.Node import Node
from pyqtgraph.Qt import QtGui
from pyqtgraph import configfile as configfile
import traceback
import os


class customFlowchart(Flowchart):
    """Custom Flowchart
        - save/load now blocks mainwindow
        - input/output nodes are hidden
        - additional signal `sigUIStateChanged` is emmited when Nodes params are changed
    """
    def __init__(self, parent=None, **kwargs):
        Flowchart.__init__(self, **kwargs)
        self.parent = parent
        self.inputNode.graphicsItem().hide()
        self.outputNode.graphicsItem().hide()
        self._nodeCopyPasteBuffer = None

    def loadFile(self, fileName=None, startDir=None):
        #print( 'loadFile called with fname:', fileName)
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

    def copySelectedNodeToBuffer(self):
        if not self.nodeIsSelected():
            return
        del self._nodeCopyPasteBuffer
        self._nodeCopyPasteBuffer = None
        items = self.scene.selectedItems()
        if len(items) == 0:
            return
        item = items[0]
        if not hasattr(item, 'node') or not isinstance(item.node, Node):
            return
        SELECTED_NODE = {}
        state = item.node.saveState()
        state['pos'] = (state['pos'][0]+30, state['pos'][1]+30)  #move position a bit
        SELECTED_NODE['nodeType'] = item.node.nodeName
        SELECTED_NODE['state'] = state
        self._nodeCopyPasteBuffer = SELECTED_NODE

    def pasteNodeFromBuffer(self, pos=None):
        if self._nodeCopyPasteBuffer is None:
            return

        n = self.createNode(self._nodeCopyPasteBuffer['nodeType'])

        state = self._nodeCopyPasteBuffer['state']
        if pos:
            state['pos'] = pos
        n.restoreState(state)

    def nodeCopyPasteBuffer(self):
        return self._nodeCopyPasteBuffer

    def nodeIsSelected(self):
        items = self.scene.selectedItems()
        if len(items) == 0:
            return False
        item = items[0]
        if not hasattr(item, 'node') or not isinstance(item.node, Node):
            return False
        return True
