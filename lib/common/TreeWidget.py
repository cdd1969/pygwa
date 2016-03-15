from pyqtgraph.Qt import QtGui, QtCore


class TreeWidget(QtGui.QTreeWidget):

    def __init__(self, parent=None):
        self._parent = parent
        super(TreeWidget, self).__init__(parent)
        self.itemActivated.connect(self.on_itemActivated)

    def on_itemActivated(self, item, column):
        self._parent.lineEdit_nodeSelect.setText(item.text(0))
        self._parent.lineEdit_nodeSelect.selectAll()


    @QtCore.pyqtSlot(QtGui.QTreeWidgetItem, int)
    def on_nodeLibTreeWidget_itemActivated(self, item, column):
        self.lineEdit_nodeSelect.setText(item.text(0))
        self.lineEdit_nodeSelect.selectAll()
        


        # connect on select QTreeWidgetItem > se text in QLineEdit
        self.treeWidget.itemActivated.connect(self.on_nodeLibTreeWidget_itemActivated)