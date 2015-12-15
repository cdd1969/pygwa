#!/usr/bin python
# -*- coding: utf-8 -*-

import os, sys
from PyQt5 import QtWidgets, QtGui, uic, QtCore
from pyqtgraph.flowchart import Flowchart, Node
from lib.functions.dictionary2qtreewidgetitem import fill_widget


class MainWindow(QtWidgets.QMainWindow):
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

        self.splitter.setSizes([300, 500])  #set horizontal sizes between splitter

        font = QtGui.QFont("Times", 11, QtGui.QFont.Bold, True)
        font.setUnderline(True)
        self.label_nodeCtrlName.setFont(font)


        self.initFlowchart()

        #init node selector tab, set autocompletion etc
        self._nodeNameCompleter = QtWidgets.QCompleter(self)
        self._nodeNameCompleter.setModel(self.uiData.nodeNamesModel())
        self._nodeNameCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.lineEdit_nodeSelect.setCompleter(self._nodeNameCompleter)

        # set tree view of node library
        fill_widget(self.treeWidget, self.uiData.nodeNamesTree())
    
    def connectActions(self):
        self.actionNew_fc.triggered.connect(self.on_actionNew_fc)
        self.actionSave_fc.triggered.connect(self.on_actionSave_fc)
        self.actionSave_As_fc.triggered.connect(self.on_actionSave_As_fc)
        self.actionLoad_fc.triggered.connect(self.on_actionLoad_fc)
        self.actionQuit.triggered.connect(self.closeEvent)

        self.uiData.sigCurrentFilenameChanged.connect(self.renameFlowchartTab)

    def connectFCSignals(self):
        self.fc.sigFileLoaded.connect(self.uiData.setCurrentFileName)
        self.fc.sigFileSaved.connect(self.uiData.setCurrentFileName)
        self.fc.sigChartChanged.connect(self.on_sigChartChanged)
        self.fc.sigChartLoaded.connect(self.on_sigChartLoaded)
        self.fc.scene.selectionChanged.connect(self.selectionChanged)

        self.lineEdit_nodeSelect.editingFinished.connect(self.on_lineEditNodeSelect_editingFinished)
 
    def closeEvent(self, event):
        QtWidgets.qApp.quit()  #quit application

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
        #self.flowChartWidget = self.fc.widget_.chartWidget
        self.layoutTab1.addWidget(self.flowChartWidget)


        # now set flowchart canvas able to accept drops from QTreeWidget and create nodes. To do that
        # we will overwrite default drag and drop events
        def dragEnterEvent(ev):
            ev.accept()

        def dropEvent(event):
            pos = event.pos()
            nodeType = event.source().currentItem().text(0)
            #print "Got drop at fcWidget.view:", nodeType, '. At coords:', pos
            #print self.flowChartWidget.view.viewBox().mapFromView(pos)
            #print self.flowChartWidget.view.viewBox().mapSceneToView(pos)
            #print self.flowChartWidget.view.viewBox().mapToView(pos)
            #print self.flowChartWidget.view.viewBox().mapViewToScene(pos)
            mappedPos = self.flowChartWidget.view.viewBox().mapSceneToView(pos)
            self.flowChartWidget.chart.createNode(nodeType, pos=mappedPos)


        self.flowChartWidget.view.dragEnterEvent = dragEnterEvent
        self.flowChartWidget.view.viewBox().setAcceptDrops(True)
        self.flowChartWidget.view.viewBox().dropEvent = dropEvent
    
    def clearStackedWidget(self):
        """ function deletes all items from QStackWidget"""
        nItems = self.stackNodeCtrlStackedWidget.count()
        for i in xrange(nItems):
            widget = self.stackNodeCtrlStackedWidget.widget(i)
            self.stackNodeCtrlStackedWidget.removeWidget(widget)
            del widget


    @QtCore.pyqtSlot()
    def on_actionNew_fc(self):
        self.clearStackedWidget()
        self.fc.loadFile(fileName=self.uiData.standardFileName())
        #fn = self.fc.ctrlWidget().currentFileName
        self.uiData.setCurrentFileName(None)

    @QtCore.pyqtSlot()
    def on_actionSave_fc(self,):
        self.fc.saveFile(fileName=self.uiData.currentFileName())
        fn = self.fc.widget().currentFileName
        if fn != self.uiData.standardFileName():
            self.uiData.setCurrentFileName(fn)

    @QtCore.pyqtSlot()
    def on_actionSave_As_fc(self):
        self.fc.saveFile()
        fn = self.fc.widget().currentFileName
        if fn != self.uiData.standardFileName():
            self.uiData.setCurrentFileName(fn)
    
    @QtCore.pyqtSlot()
    def on_actionLoad_fc(self):
        self.fc.loadFile()
        fn = self.fc.widget().currentFileName
        if fn != self.uiData.standardFileName():
            self.uiData.setCurrentFileName(fn)


    
    @QtCore.pyqtSlot()
    def selectionChanged(self):
        items = self.fc.scene.selectedItems()
        if len(items) != 0:
            item = items[0]
            if hasattr(item, 'node') and isinstance(item.node, Node):
                self.on_selectedNodeChanged(item.node)
                
    @QtCore.pyqtSlot()
    def on_sigChartLoaded(self):
        print "on_sigChartLoaded() is called"
        # since during the fc.loadFile() all the sigChartChanged() is blocked, our method @on_sigChartChanged()
        # will not be called, and thus the ctrlWidgets wont be added into the QStackWidget. Lets do it explicitly.
        # We know, that after the File with flow chart has been loaded in pyqtgraph.flowchart class, it emits
        # signal sigChartLoaded, we are using this feature
        self.clearStackedWidget()
        for name, node in self.fc.nodes().iteritems():
            if node.ctrlWidget() is not None:
                self.stackNodeCtrlStackedWidget.addWidget(node.ctrlWidget())
            self.on_selectedNodeChanged(node)


    @QtCore.pyqtSlot(object, str, object)
    def on_sigChartChanged(self, emitter, action, node):
        print "on_sigChartChanged() is called"
        print self, emitter, action, node
        if action == 'add':
            print 'on_sigChartChanged(): adding', node.ctrlWidget(), type(node.ctrlWidget())
            if node.ctrlWidget() is not None:
                self.stackNodeCtrlStackedWidget.addWidget(node.ctrlWidget())
            self.on_selectedNodeChanged(node)


        elif action == 'remove':
            print 'on_sigChartChanged(): remove'
            # widget is not removed but hidden! find a way to safely remove it
            self.stackNodeCtrlStackedWidget.removeWidget(node.ctrlWidget())
            #print self.stackNodeCtrlStackedWidget.currentWidget().parent()
            #self.on_selectedNodeChanged(self.stackNodeCtrlStackedWidget.currentWidget().parent())
            #self.label_nodeCtrlName.setText("Node: <"+node.name()+">")
            node.close()
            del node


        elif action == 'rename':
            print 'on_sigChartChanged(): rename'
            if self.stackNodeCtrlStackedWidget.currentWidget() is node.ctrlWidget():
                self.label_nodeCtrlName.setText("Node: <"+node.name()+">")
        else:
            msg = 'on_sigChartChanged(): Undefined action recieved <{0}>'.format(action)
            raise KeyError(msg)


    @QtCore.pyqtSlot(Node)
    def on_selectedNodeChanged(self, node):
        self.stackNodeCtrlStackedWidget.setCurrentWidget(node.ctrlWidget())
        self.label_nodeCtrlName.setText("Node: <"+node.name()+">")


    @QtCore.pyqtSlot(unicode, unicode)
    def renameFlowchartTab(self, oldName, newName):
        currentTab = self.tabWidget.currentIndex()
        #print '>>> renameFlowchartTab()', newName, type(newName)
        if newName in [None, u'']:
            newName = 'new_flowchart'
        else:
            newName = os.path.basename(newName)
            #if newName in ['default.fc', u'default.fc']:
            #    newName = 'new_flowchart'

        self.tabWidget.setTabText(currentTab, newName)


    @QtCore.pyqtSlot()
    def on_lineEditNodeSelect_editingFinished(self):
        currentText = self.lineEdit_nodeSelect.text()
        listFoundWidget = self.treeWidget.findItems(currentText, QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive)
        if len(listFoundWidget) == 1:
            self.treeWidget.setCurrentItem(listFoundWidget[0])

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())




# these imports are for creating custom Node-Library
import pyqtgraph.flowchart.library as fclib
from lib.flowchart.customnode_readcsv import readCSVNode
from lib.flowchart.customnode_viewpandasdf import viewPandasDfNode
from lib.flowchart.customnode_selectdfcolumn import selectDfColumnNode
from lib.flowchart.customnode_plotarray import plotArrayNode
from lib.flowchart.customnode_df2recarray import df2recArrayNode
from lib.flowchart.customnode_detectpeaks import detectPeaksNode



class uiData(QtCore.QObject):
    """ class to collect all our user-interface settings,
        and to seperate these params from MainWindow class"""
    
    sigCurrentFilenameChanged = QtCore.Signal(unicode, unicode)


    def __init__(self, parent=None):
        super(QtCore.QObject, self).__init__(parent=parent)
        self.parent = parent
        self.initLibrary()
        self._currentFileName  = None
        self._standardFileName = os.path.join(os.getcwd(), 'resources/defaultFlowchart.dfc')



    def initLibrary(self):
        self._flowchartLib = fclib.LIBRARY.copy()  # start with the default node set
        self._flowchartLib.addNodeType(readCSVNode, [('My',)])
        self._flowchartLib.addNodeType(viewPandasDfNode, [('My',)])
        self._flowchartLib.addNodeType(selectDfColumnNode, [('My',)])
        self._flowchartLib.addNodeType(plotArrayNode, [('My',)])
        self._flowchartLib.addNodeType(df2recArrayNode, [('My',)])
        self._flowchartLib.addNodeType(detectPeaksNode, [('My',)])

        # create a StringListModel of registered node names, it will be used for auto completion
        self._nodeNamesModel = QtCore.QStringListModel(self)
        self._nodeNamesModel.setStringList(self._flowchartLib.nodeList.keys())
        
        # create a TreeModel of registered node names, it will be used for auto completion
        self._nodeNamesTree = self._flowchartLib.nodeTree


    def nodeNamesModel(self):
        return self._nodeNamesModel

    def nodeNamesTree(self):
        return self._nodeNamesTree

    def currentFileName(self):
        return self._currentFileName

    @QtCore.pyqtSlot(str)
    def setCurrentFileName(self, name):
        oldName = self._currentFileName
        self._currentFileName = name
        self.sigCurrentFilenameChanged.emit(oldName, name)

    def standardFileName(self):
        return self._standardFileName

    def flowchartLib(self):
        return self._flowchartLib


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('resources/theme_oceans_90.gif'))
    ex = MainWindow()
    ex.show()


    print type(ex.flowChartWidget)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()