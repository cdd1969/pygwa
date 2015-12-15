import sys
from pyqtgraph import QtCore, QtGui

class QCustomTreeWidget (QtGui.QTreeWidget):
    itemMoveOutActivated = QtCore.pyqtSignal(object)
    itemNewMoveActivated = QtCore.pyqtSignal(object)

    def __init__ (self, parent = None):
        super(QCustomTreeWidget, self).__init__(parent)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)

    def dragEnterEvent (self, eventQDragEnterEvent):
        sourceQCustomTreeWidget = eventQDragEnterEvent.source()
        if isinstance(sourceQCustomTreeWidget, QCustomTreeWidget) and (self is not sourceQCustomTreeWidget):
            eventQDragEnterEvent.accept()
        else:
            QtGui.QTreeWidget.dragEnterEvent(self, eventQDragEnterEvent)

    def dropEvent (self, eventQDropEvent):
        sourceQCustomTreeWidget = eventQDropEvent.source()
        if isinstance(sourceQCustomTreeWidget, QCustomTreeWidget) and (self is not sourceQCustomTreeWidget):
            sourceQTreeWidgetItem      = sourceQCustomTreeWidget.currentItem()
            destinationQTreeWidgetItem = sourceQTreeWidgetItem.clone()
            self.addTopLevelItem(destinationQTreeWidgetItem)
            sourceQCustomTreeWidget.itemMoveOutActivated.emit(destinationQTreeWidgetItem)
            self.itemNewMoveActivated.emit(destinationQTreeWidgetItem)
        else:
            QtGui.QTreeWidget.dropEvent(self, eventQDropEvent)

class QCustomQWidget (QtGui.QWidget):
    def __init__ (self, parent = None):
        super(QCustomQWidget, self).__init__(parent)
        self.my1QCustomTreeWidget = QCustomTreeWidget(self)
        self.my2QCustomTreeWidget = QCustomTreeWidget(self)
        self.my1QCustomTreeWidget.itemMoveOutActivated.connect(self.itemMoveOutActivatedCallBack1)
        self.my2QCustomTreeWidget.itemMoveOutActivated.connect(self.itemMoveOutActivatedCallBack2)
        self.my1QCustomTreeWidget.itemNewMoveActivated.connect(self.itemNewMoveActivatedCallBack1)
        self.my2QCustomTreeWidget.itemNewMoveActivated.connect(self.itemNewMoveActivatedCallBack2)
        listsExampleQTreeWidgetItem = [QtGui.QTreeWidgetItem([name]) for name in ['Part A', 'Part B', 'Part C']]
        self.my1QCustomTreeWidget.addTopLevelItems(listsExampleQTreeWidgetItem)
        self.allQHBoxLayout = QtGui.QHBoxLayout()
        self.allQHBoxLayout.addWidget(self.my1QCustomTreeWidget)
        self.allQHBoxLayout.addWidget(self.my2QCustomTreeWidget)
        self.setLayout(self.allQHBoxLayout)

    @QtCore.pyqtSlot(QtGui.QTreeWidgetItem)
    def itemMoveOutActivatedCallBack1 (self, goneQTreeWidgetItem):
        print 'QTreeWidget 1 has move QTreeWidgetItem to Another QTreeWidget'

    @QtCore.pyqtSlot(QtGui.QTreeWidgetItem)
    def itemMoveOutActivatedCallBack2 (self, goneQTreeWidgetItem):
        print 'QTreeWidget 2 has move QTreeWidgetItem to Another QTreeWidget'

    @QtCore.pyqtSlot(QtGui.QTreeWidgetItem)
    def itemNewMoveActivatedCallBack1 (self, newQTreeWidgetItem):
        print 'Another QTreeWidget has move QTreeWidgetItem in QTreeWidget 1'

    @QtCore.pyqtSlot(QtGui.QTreeWidgetItem)
    def itemNewMoveActivatedCallBack2 (self, newQTreeWidgetItem):
        print 'Another QTreeWidget has move QTreeWidgetItem in QTreeWidget 2'

app = QtGui.QApplication(sys.argv)
myQCustomQWidget = QCustomQWidget()
myQCustomQWidget.show()
sys.exit(app.exec_())