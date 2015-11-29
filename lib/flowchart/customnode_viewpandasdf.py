#!/usr/bin python
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt, qDebug
from pyqtgraph.flowchart.Node import Node


import numpy as np
import cPickle as pickle
import gc
import pandas as pd

import os, sys
import traceback






class viewPandasDfNode(Node):
    """View Pandas dataframe in QTable-view"""
    nodeName = "viewPandasDf"


    def __init__(self, name, parent=None):
        super(viewPandasDfNode, self).__init__(name, terminals={'In': {'io': 'in'}})
        self._ctrlWidget = viewPandasDfCtrlWidget(self)

        
    def process(self, In):
        print 'process() received In of ', type(In)
        self._pandasModel = PandasModel(In.unpack())
        self.ctrlWidget().update()
        print 'process() returning...'

    def getPandasModel(self):
        return self._pandasModel
        
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







class viewPandasDfCtrlWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(viewPandasDfCtrlWidget, self).__init__()
        uic.loadUi('/home/nck/prj/master_thesis/code/lib/flowchart/customnode_viewpandasdf.ui', self)
        self._parent = parent
        self.initUI()


    def initUI(self):
        self.tableView = QtWidgets.QTableView()
        self.update()

    def setModels(self):
        print "setModels()"
        modelsAreSet = True
        try:
            self.listView.setModel(self.parent().getPandasModel().headerModel())
        except Exception, err:
            modelsAreSet = False
            traceback.print_exc()
            print "viewPandasDfCtrlWidget: Unnable to set listView model"
        try:
            self.tableView.setModel(self.parent().getPandasModel())
        except Exception, err:
            modelsAreSet = False
            traceback.print_exc()
            print "viewPandasDfCtrlWidget: Unnable to set tableView model"
        self.pushButton_viewTable.setEnabled(modelsAreSet)
        self.pushButton_viewPlot.setEnabled(modelsAreSet)

            
            



    def update(self):
        try:
            del self.twWindow
        except:
            pass
        self.twWindow = None
        self.setModels()  # we enable and disable buttons also in this method

    @QtCore.pyqtSlot()  #default signal
    def on_pushButton_viewTable_clicked(self):
        """ open our data in a tableView"""
        print "on_pushButton_viewTable_clicked() is called"
        if self.twWindow is None:
            self.twWindow = QtWidgets.QMainWindow()
            self.twWindow.setWindowTitle(self.parent().nodeName+': Table View')
            self.twWindow.setCentralWidget(self.tableView)
            self.twWindow.resize(1000, 800)


            self.parent().getPandasModel().update()
            self.twWindow.show()
            
            self.pushButton_viewTable.setChecked(True)
        else:
            if not self.pushButton_viewTable.isChecked():  # This is obviously a bug! Returns 
                self.twWindow.hide()
                self.pushButton_viewTable.setChecked(False)
            else:
                self.parent().getPandasModel().update()
                self.twWindow.show()
                self.pushButton_viewTable.setChecked(True)


    @QtCore.pyqtSlot()  #default signal
    def on_pushButton_viewPlot_clicked(self):
        """ open nice graphic representation of our data"""
        pass
    
    @QtCore.pyqtSlot(bool)  #default signal
    def on_radioButton_columnIndex_toggled(self, isChecked):
        self.spinBox_columnIndex.setEnabled(isChecked)
        self.lineEdit_combineColumn.setDisabled(isChecked)

    def parent(self):
        return self._parent





class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._headerModel = QtGui.QStandardItemModel()  # this model will be used with QListView to display Dataframe header (and check them)
        self._headerModel.itemChanged.connect(self.on_tv_itemChanged)


        if isinstance(data, pd.DataFrame):
            # set explicitly passed pandas dataframe
            self.setPandasDataframe(data)
        else:
            raise TypeError("Invalid type of argument <data> detected. Received: {0}. Must be [pd.DataFrame]".format(type(data)))

    def setPandasDataframe(self, data):
        try:
            del self._dataPandas
            # no need to call garbage collector, since it will be executed via <update()>
        except:
            pass
        self._dataPandas = data
        
        # append header of the newly set data to our HeaderModel
        self._headerModel.clear()  #flush previous model
        for name in self.getDataHeader():
            item = QtGui.QStandardItem(name)
            item.setCheckable(True)
            item.setEditable(False)
            item.setCheckState(Qt.Checked)
            self._headerModel.appendRow(item)
        
        #finally call update method
        self.update()

        # since we reimplement function @setPandasDataframe() we need to re-emit the dataChanged signal
        #topLeft = self.createIndex(0, 0)
        #bottomRight = self.createIndex(data.shape[0], data.shape[1])
        #self.dataChanged.emit(topLeft, bottomRight, ())

    def setData(self, index, value=QtCore.QVariant(), role=Qt.EditRole):
        """ make user able to edit cells, limited to float"""
        if role == Qt.EditRole:
            oldVal = self._data[index.row(), index.column()]
            try:
                newVal = float(value)
                self._data[index.row(), index.column()] = newVal
            except:
                self._data[index.row(), index.column()] = oldVal
        return True
    
    def flags(self, index=QtCore.QModelIndex()):
        """define flags for all items of current model"""
        return (Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)


    def getData(self):
        return self._dataPandas

    def getSelectedData(self):
        pass

    def getDataHeader(self):
        return self._dataPandas.columns.values.tolist()

    def headerModel(self):
        return self._headerModel

    def update(self):
        try:
            del self._data
            gc.collect()
        except:  # no instance <self._data> yet
            pass
        self._data = self.createNumpyData()
        self.r, self.c = self._data.shape
        self.endResetModel()


    def selectColumns(self):
        ''' This method can be used to pass specific column names in method @createNumpyData
            Selected column is the clumn which name IS CHECKED

            <columns> is a list of strings (i.e. ['datetime', 'col1', 'col2']) or None'''
        columns = list()
        for i in xrange(self._headerModel.rowCount()):
            item = self._headerModel.item(i)
            if item.checkState() == Qt.Checked:
                columns.append(item.text())
        
        # if all has been checked => return None
        if len(columns) == self._headerModel.rowCount():
            columns = None

        print "selectColumns() returning", columns
        return columns

    def createNumpyData(self):
        # we will use Numpy cause of its blazing speed
        # in contrast, the direct usage of pandas dataframe <df[i][j]> in method <data()> is extremely slow
        selectedColumns = self.selectColumns()
        if selectedColumns is None:  #return all columns
            return np.array(self._dataPandas)
        else:
            # return only desired columns
            # note <selectedColumns> should be a list of strings (i.e. ['datetime', 'col1', 'col2'])
            return np.array(self._dataPandas[selectedColumns])

    @QtCore.pyqtSlot(object)
    def on_tv_itemChanged(self, item):
        self.update()


    def rowCount(self, parent=None):
        return self.r

    def columnCount(self, parent=None):
        return self.c

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return unicode(self._data[index.row(), index.column()])
        return QtCore.QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                selectedHeader = self.selectColumns()
                if selectedHeader is not None:  # if not all columns
                    return selectedHeader[section]
                else:                           # if all columns
                    return self._dataPandas.columns[section]
            elif orientation == Qt.Vertical:
                return section
        return QtCore.QVariant()
