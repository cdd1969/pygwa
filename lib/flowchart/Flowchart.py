# -*- coding: utf-8 -*-
from pyqtgraph.flowchart.Flowchart import Flowchart
from pyqtgraph.flowchart.Terminal import ConnectionItem
from pyqtgraph.flowchart.Node import Node
from pyqtgraph.Qt import QtGui
from pyqtgraph import configfile as configfile
import traceback
import os
from pyqtgraph.flowchart.Terminal import Terminal
from numpy import ndarray
from lib.common.basic import ErrorPopupMessagBox
import logging
logger = logging.getLogger(__name__)


class customFlowchart(Flowchart):
    """Custom Flowchart with following addons:

        - save/load now blocks mainwindow
        - input/output nodes are hidden
        - additional signal `sigUIStateChanged` is emmited when Nodes params are changed
            (this works only for my custom nodes see `lib.flowchart.nodes.generalNode.NodeWithCtrlWidget`)
        - added node COPY/PASTE functionality
                * copySelectedNodeToBuffer()
                * pasteNodeFromBuffer()
                * nodeCopyPasteBuffer()
                * nodeIsSelected()
    """
    def __init__(self, parent=None, **kwargs):
        Flowchart.__init__(self, **kwargs)
        self.parent = parent
        self.inputNode.graphicsItem().hide()
        self.outputNode.graphicsItem().hide()
        self._nodeCopyPasteBuffer = None

        self.widget().chartWidget.hoverOver = self.hoverOver  # this thing is not working....

    def loadFile(self, fileName=None, startDir=None):
        logger.info('loading file [{0}]'.format(fileName))
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
        except Exception, err:
            logger.error('Failed to Load file [{0}]'.format(fileName), exc_info=True)
            self.clear()
            ErrorPopupMessagBox(self.parent, "Load Flowchart", 'Cannot load flowchart from file <i>{0}</i>'.format(fileName))
            return

        self.viewBox.autoRange()
        self.sigFileLoaded.emit(fileName)
        self.inputNode.graphicsItem().hide()
        self.outputNode.graphicsItem().hide()
        logger.info('file loaded [{0}]'.format(fileName))
    
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

        logger.info('saving file [{0}]'.format(fileName))

        fileName = unicode(fileName)
        if os.path.splitext(fileName)[1] != '.fc':
            fileName += u'.fc'
        try:
            configfile.writeConfigFile(self.saveState(), fileName)
        except Exception, err:
            logger.error('Failed to Save file [{0}]'.format(fileName), exc_info=True)
            ErrorPopupMessagBox(self.parent, "Save Flowchart", 'Cannot save flowchart to file <i>{0}</i>'.format(fileName))
            return
        self.sigFileSaved.emit(fileName)
        logger.info('file saved [{0}]'.format(fileName))

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
        '''
            return True if currently a Node is selected
        '''
        it = self.getSelectedItem()
        if it[1] == 'node':
            return True
        else:
            return False
    
    def getSelectedItem(self):
        '''
            Return a tuple of two objects:
                (first selected item, description=str)
        '''
        items = self.scene.selectedItems()
        if len(items) == 0:
            return (None, None)  # nothing is selected
        else:
            item = items[0]
            if hasattr(item, 'node') and isinstance(item.node, Node):
                return (item, 'node')  # returning Node
            elif isinstance(item, ConnectionItem):
                return (item, 'connection')  # returning ConnectionItem
            else:
                return (item, 'unknown')  # returning HZ chto

    def hoverOver(self, items):
        ''' overriding default method of 
            self.widget().chartWidget.hoverOver()
         due to decoding problem'''
        #print "FlowchartWidget.hoverOver called."
        wdg = self.widget().chartWidget
        term = None
        for item in items:
            if item is wdg.hoverItem:
                return
            wdg.hoverItem = item
            if hasattr(item, 'term') and isinstance(item.term, Terminal):
                term = item.term
                break
        if term is None:
            wdg.hoverText.setPlainText("")
        else:
            val = term.value()
            if isinstance(val, ndarray):
                val = "{0} {1} {2}".format(type(val).__name__, str(val.shape), str(val.dtype))
            else:
                val = str(val)
                if len(val) > 400:
                    val = val[:400] + "..."
            wdg.hoverText.setPlainText("{0}.{1} = {2}".format(term.node().name(), term.name(), val).decode('utf-8'))
            #wdg.hoverLabel.setCursorPosition(0)