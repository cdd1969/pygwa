#!/usr/bin python
# -*- coding: utf-8 -*-

import os, sys
import traceback
from PyQt5 import QtWidgets, QtGui, uic, QtCore
from pyqtgraph.flowchart import Node

from functions.dictionary2qtreewidgetitem import fill_widget
from flowchart.NodeLibrary import readNodeFile
from flowchart.Flowchart import customFlowchart as Flowchart
from common.CustomQCompleter import CustomQCompleter
import PROJECTMETA
from lib import projectPath


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        #self.setupUi(self)
        uic.loadUi(projectPath('resources/mainwindow.ui'), self)
        self.uiData = uiData(self)
        self.connectActions()
        #self.connectSignals()
        self.initUI()
        
        

    def initUI(self):
        self.setWindowTitle(PROJECTMETA.__label__)
        self.center()  # center window position

        self.splitter.setSizes([300, 500])  #set horizontal sizes between splitter

        font = QtGui.QFont("Times", 11, QtGui.QFont.Bold, True)
        font.setUnderline(True)
        self.label_nodeCtrlName.setFont(font)
        
        # create dummy widget (it will be selected if our node doesnot has ctrlWidget)
        self._dummyWidget = QtWidgets.QWidget(self)

        # init FlowChart
        self.initFlowchart()



        # connect on select QTreeWidgetItem > se text in QLineEdit
        self.treeWidget.itemActivated.connect(self.on_nodeLibTreeWidget_itemActivated)

        # init dock widgets
        css = "color: white; font-size: 12pt; font-weight: bold; background: rgb(102, 102, 204);  qproperty-alignment: 'AlignVCenter | AlignHCenter';"
        label_1 = QtWidgets.QLabel("Node Library")
        label_1.setStyleSheet(css)
        self.dockWidget.setTitleBarWidget(label_1)
        
        label_2 = QtWidgets.QLabel("Node Controls")
        label_2.setStyleSheet(css)
        self.dockWidget_2.setTitleBarWidget(label_2)

        #init node selector tab, set autocompletion etc
        #self._nodeNameCompleter = QtWidgets.QCompleter(self)
        self._nodeNameCompleter = CustomQCompleter(self)
        self._nodeNameCompleter.setModel(self.uiData.nodeNamesModel())
        self._nodeNameCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.lineEdit_nodeSelect.setCompleter(self._nodeNameCompleter)
        self.lineEdit_nodeSelect.setPlaceholderText('Type Node Name Here')
        # set tree view of node library
        fill_widget(self.treeWidget, self.uiData.nodeNamesTree())

    def resetNodeLibraryWidgets(self):
        #init node selector tab, set autocompletion etc
        #self._nodeNameCompleter = QtWidgets.QCompleter(self)
        self.uiData.nodeNamesModel().setStringList(self.uiData.nodeNamesList())
        # set tree view of node library
        fill_widget(self.treeWidget, self.uiData.nodeNamesTree())

    def connectActions(self):
        self.actionNew_fc.triggered.connect(self.on_actionNew_fc)
        self.actionSave_fc.triggered.connect(self.on_actionSave_fc)
        self.actionSave_As_fc.triggered.connect(self.on_actionSave_As_fc)
        self.actionLoad_fc.triggered.connect(self.on_actionLoad_fc)
        self.actionAdd_item_to_library.triggered.connect(self.on_actionAdd_item_to_library)

        self.actionAbout.triggered.connect(self.on_actionAbout)
        self.actionDocumentation.triggered.connect(self.on_actionDocumentation)

        self.actionQuit.triggered.connect(self.closeEvent)

        self.uiData.sigCurrentFilenameChanged.connect(self.renameFlowchartTab)

    def connectFCSignals(self):
        self.fc.sigFileLoaded.connect(self.uiData.setCurrentFileName)
        self.fc.sigFileSaved.connect(self.uiData.setCurrentFileName)
        self.fc.sigChartChanged.connect(self.on_sigChartChanged)
        self.fc.sigChartLoaded.connect(self.on_sigChartLoaded)
        self.fc.scene.selectionChanged.connect(self.selectionChanged)

        self.lineEdit_nodeSelect.editingFinished.connect(self.on_lineEditNodeSelect_editingFinished)
 


    def initFlowchart(self):
        # removing dummyWidget created with QtDesigner
        self.layoutTab1.removeWidget(self.flowChartWidget)
        del self.flowChartWidget

        # generating flowchart instance. Further we will work only with this instance,
        # simply saving/loading it's state.
        self.fc = Flowchart(parent=self,
                            terminals={
                              'dataIn': {'io': 'in'},
                              'dataOut': {'io': 'out'}},
                            library=self.uiData.fclib())
        
        # connecting standard signals of the flowchart
        self.connectFCSignals()

        # load default scheme
        self.on_actionNew_fc(init=True)

        # placing the real widget on the place of a dummy
        self.flowChartWidget = self.fc.widget().chartWidget
        #self.flowChartWidget = self.fc.widget_.chartWidget
        self.layoutTab1.addWidget(self.flowChartWidget)


        # now set flowchart canvas able to accept drops from QTreeWidget and create nodes. To do that
        # we will overwrite default dragEnterEvent and dropEvent with custom methods
        def dragEnterEvent(ev):
            ev.accept()

        def dropEvent(event):
            pos = event.pos()
            try:
                nodeType = event.source().currentItem().text(0)
            except AttributeError:
                try:
                    nodeType = event.source().text()
                except:
                    event.ignore()
                    return
            #print( "Got drop at fcWidget.view:", nodeType, '. At coords:', pos)
            #print( self.flowChartWidget.view.viewBox().mapFromView(pos))
            #print( self.flowChartWidget.view.viewBox().mapSceneToView(pos))
            #print( self.flowChartWidget.view.viewBox().mapToView(pos))
            #print( self.flowChartWidget.view.viewBox().mapViewToScene(pos))
            mappedPos = self.flowChartWidget.view.viewBox().mapSceneToView(pos)
            if nodeType in self.uiData.nodeNamesList():  # to avoid drag'n'dropping Group-names
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
        # finally add dummy widget - to be selected with nodes that does not have any ctrlWidget()
        self.stackNodeCtrlStackedWidget.addWidget(self._dummyWidget)
    
    @QtCore.pyqtSlot(object, int)
    def on_nodeLibTreeWidget_itemActivated(self, item, column):
        self.lineEdit_nodeSelect.setText(item.text(0))
        self.lineEdit_nodeSelect.selectAll()

    @QtCore.pyqtSlot()
    def on_actionNew_fc(self, init=False):
        if not init:  #if we are not initing
            if not self.doActionIfUnsavedChanges(message='Are you sure to start new Flowchart from scratch without saving this one?'):
                return
        self.clearStackedWidget()
        self.fc.loadFile(fileName=self.uiData.standardFileName())
        #fn = self.fc.ctrlWidget().currentFileName
        self.uiData.setCurrentFileName(None)
        self.uiData.setChangesUnsaved(False)

    @QtCore.pyqtSlot()
    def on_actionSave_fc(self):
        self.fc.saveFile(fileName=self.uiData.currentFileName())
        fn = self.fc.widget().currentFileName
        if fn != self.uiData.standardFileName():
            self.uiData.setCurrentFileName(fn)
            self.uiData.setChangesUnsaved(False)
            #self.statusBar().showMessage("File saved: "+fn, 10000)
        return True


    @QtCore.pyqtSlot()
    def on_actionSave_As_fc(self):
        self.fc.saveFile()
        fn = self.fc.widget().currentFileName
        if fn != self.uiData.standardFileName():
            self.uiData.setCurrentFileName(fn)
            self.uiData.setChangesUnsaved(False)
            #self.statusBar().showMessage("File saved: "+fn, 10000)
        return True
    
    @QtCore.pyqtSlot()
    def on_actionLoad_fc(self):
        if self.doActionIfUnsavedChanges(message='Are you sure to load another Flowchart without saving this one?'):
            directory = os.path.join(os.getcwd(), 'examples')
            self.fc.loadFile(startDir=directory)
            fn = self.fc.widget().currentFileName
            if fn != self.uiData.standardFileName():
                self.uiData.setCurrentFileName(fn)
                self.uiData.setChangesUnsaved(False)
                #self.statusBar().showMessage("File loaded: "+fn)

    @QtCore.pyqtSlot()
    def on_actionAdd_item_to_library(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, caption="Load Node Registration File", filter="(*.node)")[0]
        if not fname:
            return
        try:
            data = readNodeFile(fname)
        except Exception, err:
            QtWidgets.QMessageBox.warning(self, "Add Item to Node Library", "Cannot load information from file <i>{0}</i> <br><br> {1}".format(fname, traceback.print_exc()))
            return
        try:
            self.uiData.fclib().registerExternalNode(fname)
            self.resetNodeLibraryWidgets()
            QtWidgets.QMessageBox.information(self, "Add Item to Node Library", "Node <b>`{0}`</b> has been successflly added to the Library. Node information has been loaded from file <i>{1}</i>".format(data['classname'], fname))
        except Exception, err:
            QtWidgets.QMessageBox.warning(self, "Add Item to Node Library", "Cannot load Node <b>`{0}`</b> from file <i>{1}</i> <br><br> {2}".format(data['classname'], data['filename'], traceback.print_exc()))
            

    @QtCore.pyqtSlot()
    def on_actionAbout(self):
        QtWidgets.QMessageBox.about(self, "About...", "{0}\n\nVersion: {1}\nAuthor: {2}\nContact: {3}".format(
            PROJECTMETA.about, PROJECTMETA.__version__, PROJECTMETA.__author__, PROJECTMETA.__contact__))

    @QtCore.pyqtSlot()
    def on_actionDocumentation(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('https://github.com/cdd1969/pygwa/wiki'))


    
    @QtCore.pyqtSlot()
    def selectionChanged(self):
        items = self.fc.scene.selectedItems()
        if len(items) != 0:
            item = items[0]
            if hasattr(item, 'node') and isinstance(item.node, Node):
                self.on_selectedNodeChanged(item.node)
                
    @QtCore.pyqtSlot()
    def on_sigChartLoaded(self):
        #print("on_sigChartLoaded() is called")
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
        #print( "on_sigChartChanged() is called")
        #print( self, emitter, action, node)
        self.uiData.setChangesUnsaved(True)

        if action == 'add':
            #print( 'on_sigChartChanged(): adding', node.ctrlWidget(), type(node.ctrlWidget()))
            if node.ctrlWidget() is not None:
                self.stackNodeCtrlStackedWidget.addWidget(node.ctrlWidget())
            self.on_selectedNodeChanged(node)


        elif action == 'remove':
            #print( 'on_sigChartChanged(): remove')
            # widget is not removed but hidden! find a way to safely remove it
            self.stackNodeCtrlStackedWidget.removeWidget(node.ctrlWidget())
            #self.on_selectedNodeChanged(self.stackNodeCtrlStackedWidget.currentWidget().parent())
            #self.label_nodeCtrlName.setText("Node: <"+node.name()+">")
            node.close()
            del node


        elif action == 'rename':
            #print( 'on_sigChartChanged(): rename')
            if self.stackNodeCtrlStackedWidget.currentWidget() is node.ctrlWidget():
                self.label_nodeCtrlName.setText("Node: <"+node.name()+">")
        else:
            msg = 'on_sigChartChanged(): Undefined action recieved <{0}>'.format(action)
            raise KeyError(msg)


    @QtCore.pyqtSlot(Node)
    def on_selectedNodeChanged(self, node):
        if node.ctrlWidget() is not None:
            self.stackNodeCtrlStackedWidget.setCurrentWidget(node.ctrlWidget())
        else:
            self.stackNodeCtrlStackedWidget.setCurrentWidget(self._dummyWidget)

        self.label_nodeCtrlName.setText("Node: <"+node.name()+">")


    @QtCore.pyqtSlot(unicode, unicode)
    def renameFlowchartTab(self, oldName, newName):
        currentTab = self.tabWidget.currentIndex()
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
        self.lineEdit_nodeSelect.selectAll()
        

    def center(self):
        """ Center MainWindow position"""
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def doActionIfUnsavedChanges(self, message=''):
        if self.uiData.changesUnsaved():
            reply = QtWidgets.QMessageBox.question(self, 'Message',
                "You have unsaved changes in current Flowchart. " + message,
                QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Save, QtWidgets.QMessageBox.Cancel)

            if reply == QtWidgets.QMessageBox.Discard:
                return True
            elif reply == QtWidgets.QMessageBox.Save:
                if self.on_actionSave_fc():
                    pass
            else:
                return False
        else:
            return True

    def closeEvent(self, event):
        if self.doActionIfUnsavedChanges(message='Are you sure to quit?'):
            QtWidgets.qApp.quit()  #quit application
        else:
            event.ignore()




from lib.flowchart.NodeLibrary import customNodeLibrary



class uiData(QtCore.QObject):
    """ class to collect all our user-interface settings,
        and to seperate these params from MainWindow class"""
    
    sigCurrentFilenameChanged = QtCore.Signal(unicode, unicode)


    def __init__(self, parent=None):
        super(QtCore.QObject, self).__init__(parent=parent)
        self.parent = parent
        self.initLibrary()
        self._currentFileName  = None
        self._changesUnsaved  = True
        self._standardFileName = projectPath('resources/defaultFlowchart.dfc')



    def initLibrary(self):
        self._flowchartLib = customNodeLibrary()
        self._flowchartLib.buildDefault(projectPath('resources/defaultLibrary.json'), include_pyqtgraph=False)

        # create a StringListModel of registered node names, it will be used for auto completion
        #self._nodeNamesList  = self._flowchartLib.nodeList.keys()
        self._nodeNamesModel = QtCore.QStringListModel(self)
        self._nodeNamesModel.setStringList(self._flowchartLib.getNodeList())

    def nodeNamesList(self):
        return self._flowchartLib.getNodeList()

    def nodeNamesModel(self):
        return self._nodeNamesModel

    def nodeNamesTree(self):
        return self._flowchartLib.getNodeTree()

    def currentFileName(self):
        return self._currentFileName

    def changesUnsaved(self):
        return self._changesUnsaved

    def setChangesUnsaved(self, state):
        if isinstance(state, bool):
            self._changesUnsaved = state
            fn = self._currentFileName
            if fn is not None:
                # we are only emitting sigal simutaing the rename operation, without actually renaming
                # the flowchart. This will cause TabWidget label to be renamed
                if state is True:  # changes are unsaved >>> add asterix
                    self.sigCurrentFilenameChanged.emit(fn, unicode(fn+'*'))
                else:  # changes are saved, remove asterix
                    self.sigCurrentFilenameChanged.emit(fn, unicode(fn))


    @QtCore.pyqtSlot(str)
    def setCurrentFileName(self, name):
        oldName = self._currentFileName
        self._currentFileName = name
        self.sigCurrentFilenameChanged.emit(oldName, name)

    def standardFileName(self):
        return self._standardFileName

    def fclib(self):
        return self._flowchartLib


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(projectPath('resources/icon.gif')))
    ex = MainWindow()
    ex.show()


    print(type(ex.flowChartWidget))
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
