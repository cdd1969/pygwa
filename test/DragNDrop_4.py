import pyqtgraph as pg
import sys
app = pg.QtGui.QApplication([])

l = pg.QtGui.QListWidget()
l.addItem('Drag me')
l.setDragDropMode(l.DragOnly)
l.show()

win = pg.GraphicsWindow()
win.show()

def dragEnterEvent(ev):
    ev.accept()

win.dragEnterEvent = dragEnterEvent

plot = pg.PlotItem()
plot.setAcceptDrops(True)
#win.addItem(plot)

def dropEvent(event):
    print "Got drop!"

plot.dropEvent = dropEvent

win.setAcceptDrops(True)
win.ci.setAcceptDrops(True)
win.ci.dropEvent = dropEvent




sys.exit(app.exec_())