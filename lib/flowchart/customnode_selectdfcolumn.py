#!/usr/bin python
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt, qDebug
from pyqtgraph.flowchart.Node import Node


import numpy as np






class selectDfColumnNode(Node):
    """Select single column from Pandas Dataframe and return as 1d anumpy array"""
    nodeName = "TakeColumn"


    def __init__(self, name, parent=None):
        super(selectDfColumnNode, self).__init__(name, terminals={'Df': {'io': 'in'}, 'Column': {'io': 'out'}})
        self._ctrlWidget = selectDfColumnCtrlWidget(self)
        self._dataHeader = None

        
    def process(self, Df):
        pandasData = Df.unpack()  # type pd dataframe

        dataHeader = pandasData.columns.values.tolist()
        if self._dataHeader != dataHeader:
            self._dataHeader = dataHeader
            self.ctrlWidget().updateComboBox(itemList=dataHeader)
        columnName = self.ctrlWidget().getColumnName()
        return {'Column': np.squeeze(pandasData[columnName].values)}

        
    def ctrlWidget(self):
        return self._ctrlWidget

    def saveState(self):
        """overriding stadart Node method to extend it with saving ctrlWidget state"""
        state = Node.saveState(self)
        # sacing additionaly state of the control widget
        #state['crtlWidget'] = self.ctrlWidget().saveState()
        return state
        
    def restoreState(self, state):
        """overriding stadart Node method to extend it with restoring ctrlWidget state"""
        Node.restoreState(self, state)
        # additionally restore state of the control widget
        #self.ctrlWidget().restoreState(state['crtlWidget'])







class selectDfColumnCtrlWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(selectDfColumnCtrlWidget, self).__init__()
        self._parent = parent
        self.initUI()

    def initUI(self):
        self.layout = QtWidgets.QVBoxLayout()
        
        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.setToolTip("Choose column name to extract data")
        self.comboBox.currentIndexChanged.connect(self.on_currentIndexChanged)


        self.layout.addWidget(self.comboBox)
        self.setLayout(self.layout)

        self.updateComboBox()

    def updateComboBox(self, itemList=None):
        self._requiredUpdateCombobox = True
        
        self.comboBox.clear()
        if itemList is not None:
            for columnName in itemList:
                self.comboBox.addItem(columnName)
            self._requiredUpdateCombobox = False

    def requiredUpdateCombobox(self):
        return self._requiredUpdateCombobox
    
    def getColumnName(self):
        return self.comboBox.currentText()

    def parent(self):
        return self._parent

    @QtCore.pyqtSlot()
    def on_currentIndexChanged(self):
        self.parent().update()


