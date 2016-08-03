#!/usr/bin python
# -*- coding: utf-8 -*-
#
#
#  This files containt two classes
#   - PandasDataModel
#   - PandasHeaderModel
#   that are both used with the `QuickView` node.
#   These classes describe a QModels that are used for displaying the data from a pandas.DataFrame
#
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from pyqtgraph.python2_3 import asUnicode

import gc
import pandas as pd

import logging
logger = logging.getLogger(__name__)

RED_FONT = QtGui.QBrush(Qt.red)
GREEN_FONT = QtGui.QBrush(Qt.green)


class PandasDataModel(QtCore.QAbstractTableModel):
    """
    This class contains a model to set the data into our QTableView
        - QAbstractTableModel for the data (DATA-TABLE)

    Set the DataFrame with `self.setPandasDataframe()` method
    """
    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._parent = parent
        self._df = pd.DataFrame()
    
    @property
    def df(self):
        return self._df
    @property
    def rawdata(self):
        return self._rawdata

    def setPandasDataframe(self, df):
        '''
            Actually set the data

        Args:
        -----
            df (pd.DataFrame):
                data of interest
        '''
        if not isinstance(df, (pd.DataFrame)):
            msg = "Invalid type of argument <df> detected. Received: {0}. Must be [pd.DataFrame]".format(type(df))
            logger.error(msg)
            raise TypeError(msg)

        self._df = df  # actually set the dataframe
        self._rawdata = df.values
        self.r, self.c = self.df.shape
        # ------------------------------------------------------
        self.endResetModel()
        gc.collect()
    
    def flags(self, index=QtCore.QModelIndex()):
        """define flags for all items of current model"""
        #return (Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        return (Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    def rowCount(self, parent=None):
        return len(self.df)

    def columnCount(self, parent=None):
        return len(self.df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return asUnicode(self.rawdata[index.row(), index.column()])
        return QtCore.QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.df.columns[section]
            elif orientation == Qt.Vertical:
                return asUnicode(self.df.index.tolist()[section])
        return QtCore.QVariant()

    def clear(self):
        self.setPandasDataframe(pd.DataFrame())










class PandasHeaderModel(QtGui.QStandardItemModel):
    """
    This class contains model to view Menu for column selection:
        - QStandardItemModel for the headers (MENU)
    # this model will be used with QListView to display Dataframe header (and check them)
    """

    row_hidden = QtCore.pyqtSignal(int)  #hide/show row, where `int` is the index of the row
    row_showed = QtCore.pyqtSignal(int)  #hide/show row, where `int` is the index of the row

    def __init__(self, parent=None):
        QtGui.QStandardItemModel.__init__(self, parent)
        self._parent = parent
        self._df = pd.DataFrame()
    
        self.itemChanged.connect(self.on_menuItemChanged)  #argument [QtGui.QStandardItem]


    @property
    def df(self):
        return self._df

    def setPandasDataframe(self, df):
        '''
            Actually set the data

        Args:
        -----
            df (pd.DataFrame):
                data of interest
        '''
        if not isinstance(df, (pd.DataFrame)):
            msg = "Invalid type of argument <df> detected. Received: {0}. Must be [pd.DataFrame]".format(type(df))
            logger.error(msg)
            raise TypeError(msg)

        self._df = df  # actually set the dataframe
        # ------------------------------------------------------
        self.update()
    
    def update(self):
        ''' uodate the model of the MENU (header)'''
        N_index = len(self.df.index)
        
        for name in self.df.columns:
            # append a table with three columns (Name, Data-Type and N_NaNs). Each row represents
            # a data-column in the input dataframe object

            item_name = QtGui.QStandardItem(asUnicode('{0}'.format(name.encode('UTF-8'))))
            item_name.setCheckable(True)
            item_name.setEditable(False)
            item_name.setCheckState(Qt.Checked)

            dt = self.df[name].dtype if isinstance(self.df, pd.DataFrame) else self.df.dtype
            item_type = QtGui.QStandardItem(asUnicode('{0}'.format(dt)))
            item_type.setEditable(False)
            if dt == type(object):
                # if the data-type of the column is not numeric or datetime, then it's propabply has not been
                # loaded successfully. Therefore, explicitly change the font color to red, to inform the user.
                item_type.setForeground(RED_FONT)
            
            n_nans = N_index - (self.df[name].count() if isinstance(self.df, pd.DataFrame) else self.df.count())
            item_nans = QtGui.QStandardItem(asUnicode('{0}'.format(n_nans)))
            item_nans.setEditable(False)
            if n_nans > 0:
                item_nans.setForeground(RED_FONT)

            self.appendRow([item_name, item_type, item_nans])

        self.setHorizontalHeaderLabels(['Name', 'Data-type', 'Number of NaNs'])
        self.endResetModel()


    def selectedColumns(self):
        '''  Loop over the first column of the current Model and 
            return the names of the items that are CHECKED.

            <columns> is a list of strings (i.e. ['datetime', 'col1', 'col2']) or None
        '''
        columns = list()
        for i in xrange(self.rowCount()):
            item = self.item(i)
            if item.checkState() == Qt.Checked:
                column_name = self.getItemName(item)
                columns.append(column_name)
        return columns

    def getItemName(self, tw_item):
        ''' Return the name of the columns in pandas dataframe `self.df`
            based on the selected item . The selected item is `tw_item`.
        '''
        colNameStr = tw_item.text()

        if colNameStr not in self.df.columns:
            raise ValueError('Column name `{0}` not found in DataFtame.columns'.format(colNameStr))
        return colNameStr

    @QtCore.pyqtSlot(object)
    def on_menuItemChanged(self, item):
        """ Does something when the item in Table-View (MENU) model is changed
            item -- item of the MENU table (row)
        """
        if item.checkState() == Qt.Checked:
            for i in xrange(self.rowCount()):
                if item is self.item(i):
                    self.row_showed.emit(i)
                    break
        else:
            for i in xrange(self.rowCount()):
                if item is self.item(i):
                    self.row_hidden.emit(i)
                    break
    
    def destroy(self):
        self.clear()
        #self.endResetModel()
        gc.collect()
