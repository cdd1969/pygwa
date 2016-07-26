#!/usr/bin python
# -*- coding: utf-8 -*-
import os
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt
from pyqtgraph.flowchart.Node import Node
from pyqtgraph import BusyCursor
from pyqtgraph import functions as fn
from pyqtgraph.python2_3 import asUnicode

import gc
import traceback
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)

from lib.common.TableView import TableView
from lib.functions.general import isNumpyDatetime, isNumpyNumeric

RED_FONT = QtGui.QBrush(Qt.red)


class QuickViewNode(Node):
    """View dataframe in TableView/Matplotlib-plot"""
    nodeName = "Quick View"

    def __init__(self, name, parent=None):
        super(QuickViewNode, self).__init__(name, terminals={'In': {'io': 'in'}})
        self.graphicsItem().setBrush(fn.mkBrush(150, 150, 250, 200))
        self._pandasModel = None
        self._ctrlWidget = QuickViewCtrlWidget(self)
        self._id = None
        
    def process(self, In):
        df = In
        if id(df) != self._id and self._pandasModel is not None:
            self._id = None
            self._pandasModel.destroy()
            self._pandasModel = None
        if df is not None:
            self._pandasModel = PandasModel(df, parent=self)
            self._id = id(df)
        self.ctrlWidget().update()

    def getPandasModel(self):
        return self._pandasModel
        
    def ctrlWidget(self):
        return self._ctrlWidget

    def saveState(self):
        """overwriting stadart Node method to extend it with saving ctrlWidget state"""
        state = Node.saveState(self)
        # sacing additionaly state of the control widget
        #state['crtlWidget'] = self.ctrlWidget().saveState()
        return state
        
    def restoreState(self, state):
        """overwriting stadart Node method to extend it with restoring ctrlWidget state"""
        Node.restoreState(self, state)
        # additionally restore state of the control widget
        #self.ctrlWidget().restoreState(state['crtlWidget'])



class QuickViewCtrlWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(QuickViewCtrlWidget, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'node_quickview.ui'), self)
        self._parent = parent
        self.initUI()
        self.pushButton_viewPlot.setEnabled(False)


    def initUI(self):
        #self.tableView = QtWidgets.QTableView()
        self.tableView = TableView(parent=self)
        self.twWindow = None
        self.update()

    def setModels(self):
        """ Set already created models to node's widgets:
                (1) - set header model to `self.tableView_header` (MENU)
                (2) - set data table model to `self.tableView` (DATA)
        """
        #logger.debug( "setModels()")
        modelsAreSet = False
        if self.parent().getPandasModel() is not None:
            try:
                self.tableView_header.setModel(self.parent().getPandasModel().headerModel())
                modelOneIsSet = True
            except Exception, err:
                modelOneIsSet = False
                traceback.print_exc()
                logger.info("QuickViewCtrlWidget: Unnable to set listView model")
            try:
                self.tableView.setModel(self.parent().getPandasModel())
                modelTwoIsSet = True
            except Exception, err:
                modelTwoIsSet = False
                traceback.print_exc()
                logger.info("QuickViewCtrlWidget: Unnable to set tableView model")
            if modelOneIsSet and modelTwoIsSet:
                modelsAreSet = True
        self.updateButtons(modelsAreSet)

    def updateButtons(self, modelsAreSet=False):
        ''' enable buttons only if the models are set '''
        self.pushButton_deselectAll.setEnabled(modelsAreSet)
        self.pushButton_selectAll.setEnabled(modelsAreSet)
        self.pushButton_viewTable.setEnabled(modelsAreSet)
        self.pushButton_viewPlot.setEnabled(modelsAreSet)

    def update(self):
        #try:
        #    self.twWindow.hide()
        #except:
        #    self.twWindow = None
        self.setModels()  # we enable and disable buttons also in this method
        self.tableView.resizeColumnsToContents()

    @QtCore.pyqtSlot()  #default signal
    def on_pushButton_selectAll_clicked(self):
        """ Select all data-rows in a tableView_header"""
        if True:
            model = self.parent().getPandasModel().headerModel()
            # now loop over all items at column (0)
            for i in xrange(model.rowCount()):
                model.item(i, 0).setCheckState(Qt.Checked)

    @QtCore.pyqtSlot()  #default signal
    def on_pushButton_deselectAll_clicked(self):
        """ Select all data-rows in a tableView_header"""
        if True:
            model = self.parent().getPandasModel().headerModel()
            # now loop over all items at column (0)
            for i in xrange(model.rowCount()):
                model.item(i, 0).setCheckState(Qt.Unchecked)


    @QtCore.pyqtSlot()  #default signal
    def on_pushButton_viewTable_clicked(self):
        """ open our data in a tableView"""
        if self.twWindow is None:
            self.twWindow = QtWidgets.QMainWindow()
            self.twWindow.setWindowTitle(self.parent().nodeName+': Table View')
            self.twWindow.setCentralWidget(self.tableView)
            self.twWindow.resize(1000, 800)
        self.twWindow.show()
        self.twWindow.activateWindow()

    @QtCore.pyqtSlot()  #default signal
    def on_pushButton_viewPlot_clicked(self):
        """ open nice graphic representation of our data"""
        with BusyCursor():
            try:
                self.matplotlibWindow = plt.figure()
                ax = plt.subplot(111)
                columns = self.parent().getPandasModel().selectColumns()
                df = self.parent().getPandasModel().getData()[columns]  #slice of the input dataframe with selected columns

                datetime_cols = [col for col in df.columns if isNumpyDatetime(df[col].dtype)]
                numeric_cols  = [col for col in df.columns if isNumpyNumeric (df[col].dtype)]

                datetime_col = datetime_cols[0] if len(datetime_cols) > 0 else None   #plot with x=datetime if possible

                for numeric_col in numeric_cols:
                    df.plot(x=datetime_col, y=numeric_col, ax=ax)
                self.matplotlibWindow.show()
            except Exception as exp:
                self._parent.setException(exp)
                return

    def parent(self):
        return self._parent







class PandasModel(QtCore.QAbstractTableModel):
    """
    This class contains two models:
        - QAbstractTableModel for the data (DATA-TABLE)
        - QStandardItemModel for the headers (MENU)
    """
    def __init__(self, data, parent=None, enable_index=False):
        '''
        Args:
        -----
            data (pd.DataFrame|pd.Series):
                pandas dataframe or series with data of interest
        '''
        self.ENABLE_INDEX = enable_index  # enable or disable showing the index of the pd.Series or pd.DataFrame in `data`
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._headerModel = QtGui.QStandardItemModel(parent=self)  # this model will be used with QListView to display Dataframe header (and check them)
        self._headerModel.itemChanged.connect(self.on_tv_itemChanged)
        self._parent = parent
        

        self.setPandasDataframe(data)

    def setPandasDataframe(self, df):
        '''
            Update the QAbstractTableModel (self) and QStandardItemModel (self._headerModel)
            with the data from a given pandas DataFrame (df)

        Args:
        -----
            df (pd.DataFrame, pd.Series):
                data of interest
        '''
        if not isinstance(df, (pd.DataFrame, pd.Series)):
            msg = "Invalid type of argument <df> detected. Received: {0}. Must be [pd.DataFrame, pd.Series]".format(type(df))
            logger.error(msg)
            raise TypeError(msg)

        try:
            del self._df
            # no need to call garbage collector, since it will be executed via <update()>
        except:
            pass
        self._df = df
        
        # ------------------------------------------------------
        # append header of the new dataframe to our HeaderModel
        # ------------------------------------------------------
        self._headerModel.clear()  #flush previous model

        N_index = len(self._df.index)
        
        for name in self.getDataHeader():
            # append a table with three columns (Name, Data-Type and N_NaNs). Each row represents
            # a data-column in the input dataframe object

            # Case 1 Treat separately `_INDEX_` case, meaning the index of the pd.DataFrame or pd.Series
            if name == '_INDEX_':
                item_name = QtGui.QStandardItem(asUnicode('{0}'.format(name.encode('UTF-8'))))
                item_name.setCheckable(True)
                item_name.setEditable(False)
                item_name.setCheckState(Qt.Checked)
                item_name.setEnabled(False)

                dt = self._df.index.dtype
                item_type = QtGui.QStandardItem(asUnicode('{0}'.format(dt)))
                item_type.setEditable(False)
                
                item_nans = QtGui.QStandardItem(asUnicode('{0}'.format(0)))
                item_nans.setEditable(False)
                
                self._headerModel.appendRow([item_name, item_type, item_nans])

            # Case 2 Treat columns...
            else:
                item_name = QtGui.QStandardItem(asUnicode('{0}'.format(name.encode('UTF-8'))))
                item_name.setCheckable(True)
                item_name.setEditable(False)
                item_name.setCheckState(Qt.Checked)

                dt = self._df[name].dtype if isinstance(df, pd.DataFrame) else self._df.dtype
                item_type = QtGui.QStandardItem(asUnicode('{0}'.format(dt)))
                item_type.setEditable(False)
                if dt == type(object):
                    # if the data-type of the column is not numeric or datetime, then it's propabply has not been
                    # loaded successfully. Therefore, explicitly change the font color to red, to inform the user.
                    item_type.setForeground(RED_FONT)
                
                n_nans = N_index - (self._df[name].count() if isinstance(df, pd.DataFrame) else self._df.count())
                item_nans = QtGui.QStandardItem(asUnicode('{0}'.format(n_nans)))
                item_nans.setEditable(False)
                if n_nans > 0:
                    item_nans.setForeground(RED_FONT)
                
                self._headerModel.appendRow([item_name, item_type, item_nans])

        self._headerModel.setHorizontalHeaderLabels(['Name', 'Data-type', 'Number of NaNs'])
        
        self._headerModel.endResetModel()
        # ------------------------------------------------------
        
        #finally call update method
        self.update()

        # make sure previously hidden rows will appear
        for i in xrange(self._headerModel.rowCount()):
            self._parent.ctrlWidget().tableView.horizontalHeader().showSection(i)

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
        #return (Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        return (Qt.ItemIsSelectable | Qt.ItemIsEnabled)


    def getData(self):
        return self._df

    def getSelectedData(self):
        pass

    def getDataHeader(self):
        '''
            return the list of the column names from the dataframe
            stored in self._df. Optionally include the name `_INDEX_`
        '''
        if isinstance(self._df, (pd.Series)):
            columns = ['SERIES']
        elif isinstance(self._df, (pd.DataFrame)):
            columns = self._df.columns.values.tolist()
        else:
            raise NotImplementedError('Received invalid dtype: {0}'.format(type(self._df)))

        if self.ENABLE_INDEX:
            return ['_INDEX_'] + columns
        else:
            return columns

    def headerModel(self):
        return self._headerModel

    def update(self):
        print 'update'
        try:
            del self._data
            gc.collect()
        except:  # no instance <self._data> yet
            pass
        self._data = self.createNumpyData()
        self.r, self.c = self._data.shape
        #if self.ENABLE_INDEX:
        #    self.c += 1
        #print 'rows, cols', self.r, self.c
        self.endResetModel()
        self._parent.ctrlWidget().update()


    def selectColumns(self):
        ''' This method can be used to pass specific column names in method @createNumpyData
            "Selected column" is the column, which name IS CHECKED

            <columns> is a list of strings (i.e. ['datetime', 'col1', 'col2']) or None
        '''
        columns = list()
        for i in xrange(self._headerModel.rowCount()):
            item = self._headerModel.item(i)
            if item.checkState() == Qt.Checked:
                column_name = self.getItemName(item)
                if column_name == '_INDEX_' and not self.ENABLE_INDEX:
                    continue
                columns.append(column_name)
        return columns

    def getItemName(self, tw_item):
        ''' Return the name of the columns in pandas dataframe `self._df`
            based on the selected item in `self.headerModel` (MENU). The
            selected item is `tw_item`. Optionally return '_INDEX_' string
        '''
        colNameStr = tw_item.text()

        if isinstance(self._df, pd.Series):
            if colNameStr == 'SERIES' or (colNameStr == '_INDEX_' and self.ENABLE_INDEX):
                return colNameStr
            else:
                raise ValueError('Column name `{0}` not found in DataFtame.columns'.format(colNameStr))
                
        elif isinstance(self._df, pd.DataFrame):
            if colNameStr not in self._df.columns:
                if not ( colNameStr == '_INDEX_' and self.ENABLE_INDEX):
                    raise ValueError('Column name `{0}` not found in DataFtame.columns'.format(colNameStr))
            return colNameStr
        else:
            raise NotImplementedError('Received invalid dtype: {0}'.format(type(self._df)))




    def createNumpyData(self):
        ''' Return a Numpa 2D array with data copied from `self._df` pandas
            dataframe. Optionally also copy `self._df.index` values to the numpy
            array into the first position
        '''
        # we will use Numpy cause of its blazing speed
        # in contrast, the direct usage of pandas dataframe <df[i][j]> in method <data()> is extremely slow

        selectedColumns = self.selectColumns()
        if self.ENABLE_INDEX:
            selectedColumns.remove('_INDEX_')

        # return only desired columns
        # note <selectedColumns> should be a list of strings (i.e. ['datetime', 'col1', 'col2'])
        if isinstance(self._df, pd.Series):
            data = self._df.values[:, np.newaxis]
        elif isinstance(self._df, pd.DataFrame):
            data = self._df[[col for col in selectedColumns]].values
        else:
            raise NotImplementedError('Received invalid dtype: {0}'.format(type(self._df)))

        if self.ENABLE_INDEX:
            index = self._df.index.values
            # append `index` as the first column to the 2D array `data`
            print 'TYPE:', index[:, np.newaxis].astype(object, copy=False).dtype, data.astype(object, copy=False).dtype
            return np.hstack((index[:, np.newaxis].astype(object, copy=False), data.astype(object, copy=False)))
        else:
            return data

    @QtCore.pyqtSlot(object)
    def on_tv_itemChanged(self, item):
        """ Does something when the item in Table-View (MENU) model is changed
            item -- item of the MENU table
        """
        if item.checkState() == Qt.Checked:
            for i in xrange(self._headerModel.rowCount()):
                if item is self._headerModel.item(i):
                    #print( '>>> index found', i)
                    self._parent.ctrlWidget().tableView.horizontalHeader().showSection(i)
                    break
        else:
            for i in xrange(self._headerModel.rowCount()):
                if item is self._headerModel.item(i):
                    #print( '>>> index found', i)
                    self._parent.ctrlWidget().tableView.horizontalHeader().hideSection(i)
                    break
                
        


    def rowCount(self, parent=None):
        return self.r

    def columnCount(self, parent=None):
        return self.c

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return asUnicode(self._data[index.row(), index.column()])
        return QtCore.QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.getDataHeader()[section]
            elif orientation == Qt.Vertical:
                return section
        return QtCore.QVariant()

    def clearAll(self):
        self.clear()

    def destroy(self):
        self._headerModel.clear()
        self.endResetModel()
        gc.collect()
