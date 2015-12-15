from pyqtgraph import QtCore, QtGui
import sys

class GraphicsScene(QtGui.QGraphicsScene):

    def __init__(self, parent = None):
        super(GraphicsScene, self).__init__(parent)

    #def dragEnterEvent(self, event):
    #    event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    #def dragLeaveEvent(self, event):
    #    event.accept()

    def dropEvent(self, event):
        text = QtGui.QGraphicsTextItem(event.mimeData().text())
        text.setPos(event.scenePos())
        self.addItem(text)
        event.accept()

class ListView(QtGui.QListView):

    def __init__(self, parent = None):
        super(ListView, self).__init__(parent)
        self.setDragEnabled(True)

    def dragEnterEvent(self, event):
        #event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()
    
    def startDrag(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return

        selected = self.model().data(index, QtCore.Qt.DisplayRole)

        mimeData = QtCore.QMimeData()
        mimeData.setText(unicode(selected))

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)

        result = drag.exec_(QtCore.Qt.MoveAction)
        if result: # == QtCore.Qt.MoveAction:
            pass

    def mouseMoveEvent(self, event):
        self.startDrag(event)
    
class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)

        self.setGeometry(100, 100, 400, 400)

        self.widget = QtGui.QWidget()
        self.setCentralWidget(self.widget)
        layout = QtGui.QGridLayout(self.widget)

        self.ListView = ListView()

        data = list()
        data = ['one', 'two', 'three']
        self.model = QtCore.QStringListModel(data)

        self.ListView.setModel(self.model)

        self.GraphicsView = QtGui.QGraphicsView()
        self.scene = GraphicsScene()
        self.GraphicsView.setScene(self.scene)
        self.GraphicsView.setSceneRect(0, 0, self.GraphicsView.width(), self.GraphicsView.height())


        layout.addWidget(self.ListView, 0, 0, 5, 5)
        layout.addWidget(self.GraphicsView, 0, 1, 5, 5)

        self.show()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())