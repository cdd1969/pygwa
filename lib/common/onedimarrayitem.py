import pyqtgraph as pg


#!/usr/bin python
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt, qDebug
from pyqtgraph.flowchart.Node import Node
import sys





class OneDimArrayItem(object):
    def __init__(self, array=None, name='unknown', parent=None, **kwargs):
        self._parent = parent
        self._array = array
        self._name = name

        color = kwargs.get('color', 'r')
        self.initUI(color=color)
    
    def initUI(self, **kwargs):
        self._ctrlWidget = OneDimArrayItemCtrlWidget(self, **kwargs)


    def array(self):
        return self._array

    def _setArray(self, array):
        self._array = array

    def setArrayCellData(self, ind, data):
        if self._array is not None:
            if 0 <= ind < len(self._array) and type(ind) is int:
                oldData = self._array[ind]
                try:
                    self._array[ind] = float(data)
                except:
                    self._array[ind] = oldData


    def originalName(self):
        return self._name
    
    def currentName(self):
        return self._ctrlWidget.lineEdit_name.currentText()


    def color(self, mode='qcolor'):
        return self._ctrlWidget.pushButton_color.color(mode=mode)

    def size(self):
        return self._ctrlWidget.spinBox_size.value()

    def _setOriginalName(self, name):
        self._name = name

    def update(self, name=None, array=None):
        if name is not None:
            self._setOriginalName(name)
        if array is not None:
            self._setArray(array)

    def isEnabled(self):
        return self._ctrlWidget.checkBox_enabled.isChecked()

    
    def parent(self):
        return self._parent
    
    def ctrlWidget(self):
        return self._ctrlWidget

    def saveState(self):
        state = {
            'originalName': self._name,
            'enabled': self.isEnabled(),
            'currentName': self.currentName(),
            'color': self.color(mode='byte'),
            'size': self.size()
        }
        return state

    def restoreState(self, state):
        self._name = state['originalName']
        self._ctrlWidget.checkBox_enabled.setChecked(state['enabled'])
        self._ctrlWidget.lineEdit_name.setText(state['currentName'])
        self._ctrlWidget.pushButton_color.setColor(state['color'])
        self._ctrlWidget.spinBox_size.setValue(state['size'])


    def __del__(self):
        del self._ctrlWidget
        object.__del__(self)




class OneDimArrayItemCtrlWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, color='r'):
        super(OneDimArrayItemCtrlWidget, self).__init__()
        uic.loadUi('/home/nck/prj/master_thesis/code/lib/common/onedimarrayhorizontalwidget.ui', self)
        self._parent = parent
        self.initUI(color=color)

    def initUI(self, **kwargs):
        self.checkBox_enabled.stateChanged.connect(self.on_checkBoxStateChanged)
        self.pushButton_color = pg.ColorButton(**kwargs)
        self.layout_colorButton.addWidget(self.pushButton_color)
        self.pushButton_resetName.clicked.emit()  # setting default name

    @QtCore.pyqtSlot()
    def on_pushButton_resetName_clicked(self):
        self.lineEdit_name.setText(self._parent.originalName())

    @QtCore.pyqtSlot(int)
    def on_checkBoxStateChanged(self, state):
        self.lineEdit_name.setEnabled(state)
        self.pushButton_resetName.setEnabled(state)
        self.pushButton_color.setEnabled(state)
        self.spinBox_size.setEnabled(state)




def test():
    app = QtWidgets.QApplication(sys.argv)
    array = [1,2,3]
    ex = OneDimArrayItem(array, name="name", color='m')
    ex.ctrlWidget().show()

    array = [2, 3, 4,]
    print id(array)
    print id(ex.array())

    sys.exit(app.exec_())


if __name__ == '__main__':
    test()
