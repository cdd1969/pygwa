from pyqtgraph import QtGui, QtCore
import time

class MyCustomWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(MyCustomWidget, self).__init__(parent)
        layout = QtGui.QVBoxLayout(self)       

        self.progressBar = QtGui.QProgressBar(self)
        self.progressBar.setRange(0,100)
        button = QtGui.QPushButton("Start", self)
        button2 = QtGui.QPushButton("Cancel", self)
        layout.addWidget(self.progressBar)
        layout.addWidget(button)
        layout.addWidget(button2)


        self.myLongTask = TaskThread()
        self.myLongTask.notifyProgress.connect(self.onProgress)

        button.clicked.connect(self.onStart)
        button2.clicked.connect(self.onCancel)

    def onStart(self):
        self.myLongTask.resume()
        self.myLongTask.start()

    def onCancel(self):
        self.myLongTask.finished.emit()
        self.progressBar.setValue(0)

    def onProgress(self, i):
        self.progressBar.setValue(i)


class TaskThread(QtCore.QThread):
    notifyProgress = QtCore.pyqtSignal(int)
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.finished.connect(self.onFinished)
        self._pause = False

    def run(self):
        for i in xrange(101):
            if self._pause:
                while 1:
                    if self._pause:
                        continue
            else:
                self.result = i
                self.notifyProgress.emit(i)
                time.sleep(0.01)

    def pause(self):
        self._pause = True
    def resume(self):
        self._pause = False

        #self.finished.emit()  # already called
    
    def onFinished(self):
        print 'onFinished is called'
        self.pause()
        reply = QtGui.QMessageBox.question(None, 'Message',
            "Result is: {0}".format(self.result), QtGui.QMessageBox.Ok)

        if reply == QtGui.QMessageBox.Ok:
            self.terminate()


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    mw = MyCustomWidget()
    mw.show()
    sys.exit(app.exec_())
