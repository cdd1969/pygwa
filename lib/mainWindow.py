#!/usr/bin python
# -*- coding: utf-8 -*-
import os, sys
import traceback
import getpass
from PyQt5 import QtWidgets, QtGui, uic, QtCore
from PyQt5.QtCore import Qt
from pyqtgraph.flowchart import Node

from functions.dictionary2qtreewidgetitem import fill_widget
from flowchart.NodeLibrary import readNodeFile
from flowchart.Flowchart import customFlowchart as Flowchart
from common.CustomQCompleter import CustomQCompleter
import PROJECTMETA
from lib import projectPath, version_info
from pyqtgraph import configfile
from lib.common.basic import ErrorPopupMessagBox
import pygwa_logger
import logging
logger = logging.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, app=None):
        super(MainWindow, self).__init__()
        self._unittestmode = False  #set this to True if running a unittest
        self._application = app
        uic.loadUi(projectPath('resources/mainwindow.ui'), self)
        self.uiData = uiData(self)
        self.connectActions()
        self.initUI()
        self.initGlobalShortcuts()

        # everything has been inited. Now do some actions
        # 1) check crash status
        self.uiData.on_crash_LoadBakFile()


    def initGlobalShortcuts(self):
        # for some reason action shotcuts are not always working... change them to global shortcuts
        QtGui.QShortcut(QtGui.QKeySequence("F1"), self, self.on_actionDocumentation)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Alt+C"), self, self.on_actionCopy_Selected_Node)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Alt+V"), self, self.on_actionPaste_Node)

        

    def initUI(self):
        self.setWindowTitle(PROJECTMETA.__label__)
        #self.center()  # center window position
        
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
        # set tree view of node library
        fill_widget(self.treeWidget, self.uiData.nodeNamesTree())

        # create EMPTY Open Recent Actions
        self.recentFileActs = []
        for i in xrange(GlobalOptions.n_recent_files):
            action = QtGui.QAction(self, visible=False, triggered=self.openRecentFile)
            self.menuOpen_Recent.addAction(action)
            self.recentFileActs.append(action)
        self.menuOpen_Recent.addSeparator()
        self.actionClearRecent = QtGui.QAction('Clear', self, visible=True, triggered=self.on_actionClearRecent)
        self.menuOpen_Recent.addAction(self.actionClearRecent)

        # create a tool bar menu button to open recent files and connect it to proper QMenu
        for widget in self.actionLoad_fc.associatedWidgets():
            # loop over assosiated widgets and search for QToolButton, assuming that only one is connected.
            if isinstance(widget, QtWidgets.QToolButton):
                widget.setMenu(self.menuOpen_Recent)
                widget.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)

        # now populate recent files QMenu
        self.uiData.updateRecentFileActions()


    def resetNodeLibraryWidgets(self):
        #init node selector tab, set autocompletion etc
        self.uiData.nodeNamesModel().setStringList(self.uiData.nodeNamesList())
        # set tree view of node library
        fill_widget(self.treeWidget, self.uiData.nodeNamesTree())

    def connectActions(self):
        self.actionNew_fc.triggered.connect(self.on_actionNew_fc)
        self.actionSave_fc.triggered.connect(self.on_actionSave_fc)
        self.actionSave_As_fc.triggered.connect(self.on_actionSave_As_fc)
        self.actionLoad_fc.triggered.connect(self.on_actionLoad_fc)
        
        self.actionAdd_item_to_library.triggered.connect(self.on_actionAdd_item_to_library)
        self.actionLoadLibrary.triggered.connect(self.on_actionLoadLibrary)
        self.actionReloadDefaultLib.triggered.connect(self.on_actionReloadDefaultLib)
        

        self.actionCopy_Selected_Node.triggered.connect(self.on_actionCopy_Selected_Node)
        self.actionPaste_Node.triggered.connect(self.on_actionPaste_Node)
        self.actionDelete_Node.triggered.connect(self.on_actionDelete_Node)

        self.actionAbout.triggered.connect(self.on_actionAbout)
        self.actionDocumentation.triggered.connect(self.on_actionDocumentation)

        self.actionQuit.triggered.connect(self.closeEvent)


    def connectFCSignals(self):
        '''
        self.fc.sigFileLoaded - file is loaded
        self.fc.sigFileSaved - file saved
        self.fc.sigChartChanged - flowchart is changed
        self.fc.sigChartLoaded - flowchart is loaded (restoreState finished with OK)
        '''
        self.fc.sigFileLoaded.connect(self.uiData.setCurrentFileName)
        self.fc.sigFileLoaded.connect(self.on_sigFileLoaded)

        self.fc.sigFileSaved.connect(self.uiData.setCurrentFileName)
        self.fc.sigFileSaved.connect(self.on_sigFileSaved)

        self.fc.sigChartChanged.connect(self.on_sigChartChanged)  # when the flowchart is loaded
        self.fc.sigChartLoaded.connect(self.on_sigChartLoaded)
        
        self.fc.scene.selectionChanged.connect(self.selectionChanged)

        self.lineEdit_nodeSelect.editingFinished.connect(self.on_lineEditNodeSelect_editingFinished)
 
        self.uiData.sigCurrentFilenameChanged.connect(self.renameFlowchartTab)


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
                self.fc.createNode(nodeType, pos=mappedPos)

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
        self.fc.loadFile(fileName=self.uiData.defaultFlowchartFileName())
        #fn = self.fc.ctrlWidget().currentFileName
        self.uiData.setCurrentFileName(None)
        self.uiData.setChangesUnsaved(False)

    @QtCore.pyqtSlot()
    def on_actionSave_fc(self):
        self.fc.saveFile(fileName=self.uiData.currentFileName())
        return True

    @QtCore.pyqtSlot()
    def on_actionSave_As_fc(self, fileName=None):
        try:
            startDir = os.path.dirname(self.uiData.currentFileName())
        except:
            startDir = None
        self.fc.saveFile(fileName=fileName, startDir=startDir)
        return True

    @QtCore.pyqtSlot()
    def on_actionDelete_Node(self):
        ''' simulate Delete Key Press event'''
        it = self.fc.getSelectedItem()


        if it[1] == 'connection':
            it[0].source.disconnect(it[0].target)
        elif it[1] == 'node':
            it[0].node.close()

    
    def on_sigFileSaved(self):
        '''
            Executed after the Flowchart() has sended signal sigFileSaved
        '''
        fn = self.fc.widget().currentFileName
        if fn != self.uiData.defaultFlowchartFileName():
            self.uiData.setCurrentFileName(fn)
            self.uiData.setChangesUnsaved(False)
            self.uiData.addRecentFile(fn)
            self.statusBar().showMessage("File saved: "+fn, 5000)

    @QtCore.pyqtSlot()
    def on_actionLoad_fc(self, fileName=None):
        if self.doActionIfUnsavedChanges(message='Are you sure to load another Flowchart without saving this one?'):
            #directory = os.path.join(os.getcwd(), 'examples')
            try:
                startDir = os.path.dirname(self.uiData.currentFileName())
            except:
                startDir = None
            self.fc.loadFile(startDir=startDir, fileName=fileName)
            
    
    def on_sigFileLoaded(self):
        '''
            Executed after the Flowchart() has sended signal sigFileLoaded
        '''
        fn = self.fc.widget().currentFileName
        if fn != self.uiData.defaultFlowchartFileName():
            self.uiData.setCurrentFileName(fn)
            self.uiData.setChangesUnsaved(False)
            self.uiData.addRecentFile(fn)
            self.statusBar().showMessage("File loaded: "+fn, 5000)

    def openRecentFile(self):
        action = self.sender()
        if action:
            self.on_actionLoad_fc(fileName=action.data())

    @QtCore.pyqtSlot()
    def on_actionAdd_item_to_library(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, caption="Load Node Registration File", filter="(*.node)")[0]
        if not fname:
            return
        try:
            data = readNodeFile(fname)
        except Exception, err:
            ErrorPopupMessagBox(self, 'Add Item to Node Library', 'Cannot load information from file <i>{0}</i>'.format(fname))
            return
        try:
            self.uiData.fclib().registerExternalNode(fname)
            self.resetNodeLibraryWidgets()
            QtWidgets.QMessageBox.information(self, "Add Item to Node Library", "Node <b>`{0}`</b> has been successflly added to the Library. Node information has been loaded from file <i>{1}</i>".format(data['classname'], fname))
        except Exception, err:
            ErrorPopupMessagBox(self, 'Add Item to Node Library', 'Cannot load Node <b>`{0}`</b> from file <i>{1}</i>'.format(data['classname'], data['filename']))
    
    @QtCore.pyqtSlot()
    def on_actionReloadDefaultLib(self):
        self.uiData.initLibrary()
        self.resetNodeLibraryWidgets()
        QtWidgets.QMessageBox.information(self, "Reload Default Library", 'Default library has been loaded from file <i>{0}</i>'.format(self.uiData.defaultLibFileName()))

    @QtCore.pyqtSlot()
    def on_actionLoadLibrary(self):
        QtWidgets.QMessageBox.warning(self, "Load Node Library", "Not implemented yet")

    
    @QtCore.pyqtSlot()
    def on_actionCopy_Selected_Node(self):
        self.fc.copySelectedNodeToBuffer()
        if self.fc.nodeCopyPasteBuffer() is not None:
            self.actionPaste_Node.setEnabled(True)
        else:
            self.actionPaste_Node.setEnabled(False)

    @QtCore.pyqtSlot()
    def on_actionPaste_Node(self):
        self.fc.pasteNodeFromBuffer()

    @QtCore.pyqtSlot()
    def on_actionAbout(self):
        versions_str = ''
        for n, v in version_info().iteritems():
            versions_str += '<br>{0} == {1}'.format(n, v)
        QtWidgets.QMessageBox.about(self, "About...", "{0}<br><br>Version: {1}<br>Author: {2}<br>Contact: {3}<br><hr>Configuration<br>{4}".format(
            PROJECTMETA.about, PROJECTMETA.__version__, PROJECTMETA.__author__, PROJECTMETA.__contact__, versions_str) )

    @QtCore.pyqtSlot()
    def on_actionDocumentation(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('https://github.com/cdd1969/pygwa/wiki'))

    @QtCore.pyqtSlot()
    def on_actionClearRecent(self):
        self.uiData.clearRecentFiles()
    
    @QtCore.pyqtSlot()
    def selectionChanged(self):
        self.actionCopy_Selected_Node.setEnabled(self.fc.nodeIsSelected())  # enable action only when node is selected
        self.actionDelete_Node.setEnabled(self.fc.nodeIsSelected() or self.fc.getSelectedItem()[1] == 'connection')  # enable action only when node is selected
        
        item = self.fc.getSelectedItem()  #return tuple [item, 'description']
        if item[1] == 'node':
            self.on_selectedNodeChanged(item[0].node)
                
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
        self.uiData.deleteBakFile()


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
                if hasattr(node, 'nodeName'):
                    self.label_nodeCtrlName.setText("Node Type:{0}<br>Node Name:{1}".format(node.nodeName, node.name()))
                else:
                    self.label_nodeCtrlName.setText("Node Name:{0}".format(node.name()))
        
        elif action == 'uiChanged':
            pass
        else:
            msg = 'on_sigChartChanged(): Undefined action recieved <{0}>'.format(action)
            raise KeyError(msg)


        # save backup flowchart
        if action in ['add', 'remove', 'rename']:
            self.uiData.saveBakFile()


    @QtCore.pyqtSlot(Node)
    def on_selectedNodeChanged(self, node):
        if node.ctrlWidget() is not None:
            self.stackNodeCtrlStackedWidget.setCurrentWidget(node.ctrlWidget())
        else:
            self.stackNodeCtrlStackedWidget.setCurrentWidget(self._dummyWidget)

        if hasattr(node, 'nodeName'):
            self.label_nodeCtrlName.setText("Node Type:{0}<br>Node Name:{1}".format(node.nodeName, node.name()))
        else:
            self.label_nodeCtrlName.setText("Node Name:{0}".format(node.name()))


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
                    return True
            else:
                return False
        else:
            return True

    def closeEvent(self, event):
        if self._unittestmode:  # set this variable in your unittest
            # if we are running tests...
            self.uiData.deleteBakFile()
            QtWidgets.qApp.quit()

        if self.doActionIfUnsavedChanges(message='Are you sure to quit?'):
            self.uiData.deleteBakFile()
            self.uiData.writeSettingsOnQuit()

            logger.info('Quit application')
            QtWidgets.qApp.quit()  #quit application
        else:
            event.ignore()


















from lib.flowchart.NodeLibrary import customNodeLibrary



class uiData(QtCore.QObject):
    """ class to collect all our user-interface settings,
        and to separate these params from MainWindow class"""
    
    sigCurrentFilenameChanged = QtCore.Signal(unicode, unicode)


    def __init__(self, parent=None):
        super(QtCore.QObject, self).__init__(parent=parent)
        self.settings = QtCore.QSettings()
        #self.settings.clear()

        self.win = parent
        GlobalOptions.n_recent_files = 10
        self._defaultFlowchartFileName = projectPath('resources/defaultFlowchart.dfc')
        self._defaultLibFileName = projectPath('resources/defaultLibrary.json')
        
        self.initLibrary()
        self.readSettingsOnStart()

    def initLibrary(self, fname=None):
        #if self._flowchartLib:
        #    del self._flowchartLib
        #    del self._nodeNamesModel

        if fname is None:
            fname = self.defaultLibFileName()
        self._flowchartLib = customNodeLibrary()
        self._flowchartLib.buildDefault(fname, include_pyqtgraph=False)

        # create a StringListModel of registered node names, it will be used for auto completion
        self._nodeNamesModel = QtCore.QStringListModel(self)
        self._nodeNamesModel.setStringList(self._flowchartLib.getNodeList())

    def nodeNamesList(self):
        return self._flowchartLib.getNodeList()

    def nodeNamesModel(self):
        return self._nodeNamesModel

    def nodeNamesTree(self):
        return self._flowchartLib.getNodeTree()

    def currentFileName(self):
        return self.settings.value('currentSession/fileName')

    def currentBakFileName(self):
        return self.settings.value('currentSession/bakFileName')
    
    def setCurrentBakFileName(self, name):
        self.settings.setValue("currentSession/bakFileName", name)

    def changesUnsaved(self):
        return self.settings.value('currentSession/changesUnsaved')
        
    def addRecentFile(self, fname):
        if fname is None or fname.endswith('.bak'):
            return
        recentFiles = self.settings.value('RecentFiles', [])
        if not recentFiles:
            recentFiles = []
        
        fname = unicode(fname)
        if fname not in recentFiles:
            # fname is not here
            recentFiles.insert(0, fname)

        elif recentFiles.index(fname) != 0:
            # fname is here and is not on top of the list
            oldindex = recentFiles.index(fname)
            newindex = 0
            recentFiles.insert(newindex, recentFiles.pop(oldindex))

        # cut it to 10 files
        recentFiles = recentFiles[0:GlobalOptions.n_recent_files] if len(recentFiles) >= GlobalOptions.n_recent_files else recentFiles
        
        self.settings.setValue("RecentFiles", recentFiles)
        self.updateRecentFileActions()

    def removeRecentFile(self, fname):
        recentFiles = self.settings.value('RecentFiles', [])
        if fname not in recentFiles:
            return
        recentFiles.remove(fname)
        self.settings.setValue("RecentFiles", recentFiles)
        self.updateRecentFileActions()

    def clearRecentFiles(self):
        recentFiles = self.settings.value('RecentFiles', [])
        if not recentFiles:
            return
        for fname in recentFiles:
            self.removeRecentFile(fname)
        self.settings.setValue("RecentFiles", [])

    
    
    def updateRecentFileActions(self):
        files = self.settings.value('RecentFiles', [])
        if files is None:
            return

        numRecentFiles = min(len(files), GlobalOptions.n_recent_files)

        for i in xrange(numRecentFiles):
            if not os.path.isfile(files[i]):
                self.win.recentFileActs[i].setVisible(False)
                continue
            text = self.strippedName(files[i])
            self.win.recentFileActs[i].setText(text)
            self.win.recentFileActs[i].setData(files[i])
            self.win.recentFileActs[i].setVisible(True)

        for j in xrange(numRecentFiles, GlobalOptions.n_recent_files):
            self.win.recentFileActs[j].setVisible(False)

    def setChangesUnsaved(self, state):
        if isinstance(state, bool):
            self.settings.setValue('currentSession/changesUnsaved', state)
            fn = self.settings.value('currentSession/fileName')
            if fn is not None:
                # we are only emitting sigal simutaing the rename operation, without actually renaming
                # the flowchart. This will cause TabWidget label to be renamed
                if state is True:  # changes are unsaved >>> add asterix
                    self.sigCurrentFilenameChanged.emit(fn, unicode(fn+'*'))
                else:  # changes are saved, remove asterix
                    self.sigCurrentFilenameChanged.emit(fn, unicode(fn))


    def setCurrentFileName(self, name):
        oldName = self.settings.value('currentSession/fileName')
        self.settings.setValue('currentSession/fileName', name)
        self.sigCurrentFilenameChanged.emit(oldName, name)

    def defaultFlowchartFileName(self):
        return self._defaultFlowchartFileName
    
    def defaultLibFileName(self):
        return self._defaultLibFileName

    def fclib(self):
        return self._flowchartLib

    def writeSettingsOnQuit(self):
        settings = QtCore.QSettings()  # do not know why i have to Initialize it once again
        #settings = self.settings
        
        # user session
        settings.setValue('currentSession/exitStatus', u'ok')
      
        # MainWindow state
        settings.setValue('mainwindow/size', self.win.size())
        settings.setValue('mainwindow/pos',  self.win.pos())
        settings.setValue('mainwindow/fullScreen',  self.win.isFullScreen())
        settings.setValue('mainwindow/state',  self.win.saveState())
        settings.setValue('mainwindow/splitter_sizes',  self.win.splitter.sizes())
        #settings.setValue('mainwindow/geometry_nodelibrary_dockwidget',  self.win.dockWidget.geometry())
        #settings.setValue('mainwindow/geometry_nodecontrol_dockwidget',  self.win.dockWidget_2.geometry())
        logger.info('Settings file saved [{0}]'.format(settings.fileName()))



    def readSettingsOnStart(self):
        settings = self.settings

        settings.setValue('lastSession/exitStatus', settings.value('currentSession/exitStatus', u'ok'))
        settings.setValue('lastSession/fileName', settings.value('currentSession/fileName', None))
        settings.setValue('lastSession/bakFileName', settings.value('currentSession/bakFileName', None))
        settings.setValue('lastSession/user', settings.value('currentSession/user', getpass.getuser()))

        settings.setValue('currentSession/exitStatus', u'crash')
        settings.setValue('currentSession/fileName', None)
        settings.setValue('currentSession/bakFileName', None)
        settings.setValue('currentSession/changesUnsaved', False)
        settings.setValue('currentSession/user', getpass.getuser())


        # restore GUI settings if the config file was previously generated by the same user
        if settings.value('currentSession/user') != settings.value('lastSession/user') and settings.value('lastSession/user') is not None:
            return

        self.win.resize(settings.value('mainwindow/size', QtCore.QSize(800, 800)))
        self.win.move(settings.value('mainwindow/pos', QtCore.QPoint(400, 400)))
        self.win.splitter.setSizes(settings.value('mainwindow/splitter_sizes', [150, 500]))

        if settings.value('mainwindow/state') is not None:
            self.win.restoreState(settings.value('mainwindow/state'))
        #if settings.value('mainwindow/geometry_nodelibrary_dockwidget') is not None:
        #    self.win.dockWidget.setGeometry(settings.value('mainwindow/geometry_nodelibrary_dockwidget'))
        #if settings.value('mainwindow/geometry_nodecontrol_dockwidget') is not None:
        #    self.win.dockWidget_2.setGeometry(settings.value('mainwindow/geometry_nodecontrol_dockwidget'))
        
        if settings.value('mainwindow/fullScreen', False) is True:
            self.win.showFullScreen()

        #self.updateRecentFileActions()  #>>> is moved to INIT of MainWindow since actions are not inited yet
        logger.info('Settings file loaded [{0}]'.format(settings.fileName()))

    def saveBakFile(self):
        if not GlobalOptions.save_bak:
            return
        fname = self.currentFileName()
        if fname is None:
            # save in pygwa root folder
            bakname = os.path.join(os.path.dirname(__file__), '../', 'unsaved_flowchart.fc.bak')
        else:
            #save to current file folder
            bakname = fname+'.bak'

        bakname = os.path.abspath(bakname)
        try:
            configfile.writeConfigFile(self.win.fc.saveState(), bakname)
        except Exception, e:
            if GlobalOptions.notify_on_savebak_error:
                ErrorPopupMessagBox(self.win, 'Save Backup File', 'Cannot save backup file at <i>{0}</i>'.format(bakname))
                return

        self.setCurrentBakFileName(bakname)
        # delay dsiplaying because status bar shows other messages as well. Too lazy to make queue
        QtCore.QTimer.singleShot(5000, lambda: self.win.statusBar().showMessage("Bak file saved: "+bakname, 5000))

    def deleteBakFile(self):
        if self.currentBakFileName() is not None:
            if os.path.isfile(self.currentBakFileName()) and self.currentBakFileName().endswith('.bak'):
                os.remove(self.currentBakFileName())
            self.setCurrentBakFileName(None)

    def on_crash_LoadBakFile(self):
        ''' Checks crash status of last session and offers to load BAK file
        Warning: use after the MainWindow has been already initialized
        '''
        if self.settings.value('lastSession/exitStatus') != 'crash':
            return
        bak = self.settings.value('lastSession/bakFileName', None)
        if bak is None:
            return
        reply = QtWidgets.QMessageBox.question(self.win, "Load Backup File", 'Previous session was not closed properly. Would you like to load backup file? \br <i>{0}</i>'.format(bak), QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)

        if reply == QtWidgets.QMessageBox.Ok:
            self.win.on_actionLoad_fc(bak)
            self.win.on_actionSave_As_fc(fileName=os.path.splitext(bak)[0])
            self.deleteBakFile()
            self.win.statusBar().showMessage("Restored after crash from BAK file: {0}".format(bak), 5000)

        

    def strippedName(self, fullFileName):
        return QtCore.QFileInfo(fullFileName).canonicalFilePath()

    def print_settings(self, symbol):
        settings = self.settings
        print '-'*20
        for k in settings.allKeys():
            print '{0} {2} {1}'.format(k, settings.value(k), symbol)
        print '-'*20



class GlobalOptions(object):
    '''
        global options (may be implemented in future into Options Menu)
    '''
    n_recent_files = 10  # number of recent files
    save_bak = True  # try to save backup file
    notify_on_savebak_error = True  # notify, when bak cannot be saved

    # to do....
    logger_on = True  #toggle logger
    logfile_location = 'path/to/log/file'



def main():

    # load logging configuration
    pygwa_logger.setup_logging()
    logger.info('\n|\n|\n|\n|\n|\n...Starting the application...\n')


    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(projectPath('resources/icon.gif')))
    
    # is needed for QSettings
    app.setOrganizationName("pygwa")
    app.setApplicationName("pygwa")

    ex = MainWindow(app=app)
    ex.show()

    sys.exit(app.exec_())
