#!/usr/bin python
# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtWidgets, uic, QtCore, QtGui

from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt
from pyqtgraph.flowchart.Node import Node
from pyqtgraph import BusyCursor
from pyqtgraph import functions as fn
import pyqtgraph as pg


import traceback
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import logging
logger = logging.getLogger(__name__)

from lib.common.graphics import myArrow
from lib.functions.general import isNumpyDatetime, isNumpyNumeric
from lib.functions.devlin2003 import devlin2003pandas, devlin2003, angle2bearing


class hydraulicGradientNode(Node):
    """Estimate hydraulic gradient using head data of multiple wells (method of Devlin 2003) for a given timestep"""
    nodeName = "Hydraulic Gradient (v2)"

    sigSingleGradientChanged = QtCore.Signal(float, float)  # magnitude, direction; is used to update QGraphicsView

    def __init__(self, name, parent=None):
        terms = {'coord': {'io': 'in'},
                 'data': {'io': 'in'},
                 'this': {'io': 'out'},
                 'All': {'io': 'out'}}
        super(hydraulicGradientNode, self).__init__(name, terminals=terms)
        self.graphicsItem().setBrush(fn.mkBrush(250, 250, 150, 150))

        self._ctrlWidget = hydraulicGradientNodeCtrlWidget(self)

        self._coords_id = None
        
    def process(self, coord, data):
        self._checkInputs()

        if id(coord) != self._coords_id:
            logger.debug('clearing HydrGradientNode (coord table) on_process()')
            self._coords_id = id(coord)
            self.ctrlWidget().clear()

        self.ctrlWidget().on_coords_recieved(coord)
        self.ctrlWidget().on_data_recieved(data)
        self.ctrlWidget().updateUI()

        return None

    def on_calcSingle_requested(self):
        '''
            Calculation of gradient for a single timestep has been requested
        '''
        try:
            df = self.inputValues()['data']  #pd.DataFrame in the input terminal `data`

            info = self.ctrlWidget().selectedWellsInfo()
            if len(info.keys()) < 3:
                raise ValueError('Select at least 3 wells to calculate gradient')


            # first select the timestep
            datetimeColName = self.ctrlWidget().comboBox_Datetime.currentText()
            if not datetimeColName:
                return
            row = df.loc[df[datetimeColName] == self.ctrlWidget().selectedTimestep()]  # select row whith user-specified datetime `timestep`
            if row.empty:
                raise IndexError('Invalid timestep. Selected timestep `{0}` not found in `data`s column {1}.'.format(self.ctrlWidget().selectedTimestep(), datetimeColName))

            # then get the information
            dictForDf = {'well': [], 'x': [], 'y': [], 'z': []}  # dictionary that will be used for a convinient creation of the DataFrame that is requered for calculations
            for wellName, wellInfo in info.iteritems():
                if wellInfo['z'] not in row:
                    raise IndexError('Z-value (head) for well `{2}` is missing. Cannot find column `{0}` at timestep {1} in DataFrame `data`'.format(wellInfo['z'], self.ctrlWidget().selectedTimestep(), wellName))

                dictForDf['well'].append(wellName)
                dictForDf['x'].append(wellInfo['x'])
                dictForDf['y'].append(wellInfo['y'])
                dictForDf['z'].append(float(row[wellInfo['z']]))

            df_this = pd.DataFrame(dictForDf)
            gradient, direction = devlin2003pandas(df_this, 'x', 'y', 'z')

            single_magnitude_str = ' {0:.3e}'.format(gradient)
            single_direction_str = ' {0:.1f} degrees N'.format(direction)
            
            self.ctrlWidget().label_singleMagVal.setText(single_magnitude_str)
            self.ctrlWidget().label_singleDirVal.setText(single_direction_str)

            self.setOutput(this=df_this)

            self.sigSingleGradientChanged.emit(gradient, direction)
            self.clearException()
        except:
            self.setOutput(this=None)
            self.ctrlWidget().clear(clearTable=False)
            self.setException(sys.exc_info())
            
            self.sigOutputChanged.emit(self)  ## triggers flowchart to propagate new data

    def on_calcAll_requested(self):
        '''
            Calculation of gradient for all timesteps has been requested
        '''
        try:
            info = self.ctrlWidget().selectedWellsInfo()
            if len(info.keys()) < 3:
                raise ValueError('Select at least 3 wells to calculate gradient')
            
            datetimeColName = self.ctrlWidget().comboBox_Datetime.currentText()
            if not datetimeColName:
                return
            
            # now generate long dataframe
            df    = self.inputValues()['data']  #pd.DataFrame in the input terminal `data`
            All_df = pd.DataFrame({datetimeColName: df[datetimeColName], 'gradient': np.zeros(len(df.index)), 'direction(degrees North)': np.zeros(len(df.index))}  )
            

            # then get the information
            dictForDf = {'well': [], 'x': [], 'y': []}  # dictionary that will be used for a convinient creation of the DataFrame that is requered for calculations
            for wellName, wellInfo in info.iteritems():
                dictForDf['well'].append(wellName)
                dictForDf['x'].append(wellInfo['x'])
                dictForDf['y'].append(wellInfo['y'])


            with pg.ProgressDialog("Calculating gradient for All timesteps {0}".format(len(All_df.index)), 0, len(All_df.index)) as dlg:
                for row_i in df.index:
                    row = df.loc[row_i]
                    z = np.zeros(len(dictForDf['well']))
                    for i, well_n in enumerate(dictForDf['well']):
                        z[i] = float(row[info[well_n]['z']])
                    x = np.array(dictForDf['x'])
                    y = np.array(dictForDf['y'])
                    _, gradient, angle = devlin2003(np.matrix([x, y, z]).T)
                    All_df.loc[row_i, 'gradient'] = gradient
                    All_df.loc[row_i, 'direction(degrees North)'] = angle2bearing(angle, origin='N')[0]
                    dlg += 1
                    del z
                    
                    if dlg.wasCanceled():
                        del All_df
                        All_df = None
                        break
                dlg += 1
            self.setOutput(All=All_df)
            self.clearException()
        except:
            self.setOutput(All=None)
            self.ctrlWidget().clear(clearTable=False)
            self.setException(sys.exc_info())
            
            self.sigOutputChanged.emit(self)  ## triggers flowchart to propagate new data


    def _checkInputs(self):
        ''' Check datatypes in the input terminals
        '''
        for inputTermName, inputTermVal in self.inputValues().items():  # returns dictionary where [key=input terminal name, value=data inside terminal]
            if not (isinstance(inputTermVal, pd.DataFrame) or inputTermVal is None ):
                raise TypeError('Invalid datatype {1} received in Terminal <{0}>. Expected datatype [pd.DataFrame|None]'.format(inputTermName, type(inputTermVal)))

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

    def getMinMaxDatetime(self, colname=None):
        '''
            Get Min and Max datetime values from the given column `colname`
            from table if terminal `data`
        '''
        df = self.inputValues()['data']
        if isinstance(df, pd.DataFrame) and colname in df.columns:
            tMin = df[colname].min()
            tMax = df[colname].max()
            return (tMin, tMax)
        else:
            return (None, None)





class hydraulicGradientNodeCtrlWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(hydraulicGradientNodeCtrlWidget, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'node_hydrgrad.ui'), self)
        self._parent = parent


        # init graphicsView for direction visualization
        self.initDirectionGraphicsView()
        self.update()

        #init signals
        self.tableWidget_menu.itemChanged.connect(self.on_itemAtColumn0_changed)
        self._parent.sigSingleGradientChanged.connect(self.on_singleGradientChanged)
    
    def initDirectionGraphicsView(self):
        '''
            Draw the coordinate-axes in the QGraphicsView that is responsible
            for visualization of the gradient direction for a single selected
            timestep
        '''
        view = self.graphicsView_direction
        scene = QtGui.QGraphicsScene()
        scene.setSceneRect(-40, -40, 80, 80)  #set scene to be 100x100 with 0, 0 beeing the center point
        view.setScene(scene)
        view.scale(1, -1)  #reverse positive directions to match those in a common mathematical x/y plane
        
        xAxes = myArrow(QtCore.QPointF(0, -40), QtCore.QPointF(0, 40), arrowHeadSize=5, lineWidth=0.5)
        yAxes = myArrow(QtCore.QPointF(-40, 0), QtCore.QPointF(40, 0), arrowHeadSize=5, lineWidth=0.5)
        scene.addItem(xAxes)
        scene.addItem(yAxes)

        self._arrow = None  #pointer to the arrow object that will be created later

    def on_coords_recieved(self, df):
        """
            Modify the TableWidget when the data is recieved in the `coords` terminal
        """
        if df is None:
            # if DataFrame withh coords is emty
            self.clear()
        else:
            #if everything is Ok, create rows and populate them
            for i, wellName in enumerate(df.index.values):
                # first check if a row with this name already exists
                if wellName in self._tableWidget_wellNames():
                    continue

                # no dupticated entry > continue adding the row

                self.tableWidget_menu.insertRow(i)  #create row

                # now create 4 items for this row
                #   - well Name [Checkbox]
                #   - X coord [label]
                #   - Y coord [label]
                #   - Head [combobox]


                wellNameItem = QTableWidgetItem(wellName)
                wellNameItem.setFlags(wellNameItem.flags() ^ Qt.ItemIsEditable)
                wellNameItem.setCheckState(Qt.Checked)
                #wellNameItem.currentIndexChanged.connect(self._parent.on_calcSingle_requested)

                xCoordItem = QTableWidgetItem('{0:.2f}'.format( float(df.iloc[[i]]['x']) ) )
                xCoordItem.setFlags(xCoordItem.flags() ^ Qt.ItemIsEditable)
                yCoordItem = QTableWidgetItem('{0:.2f}'.format( float(df.iloc[[i]]['y']) ) )
                yCoordItem.setFlags(yCoordItem.flags() ^ Qt.ItemIsEditable)

                headItem = QtWidgets.QComboBox()
                headItem.currentIndexChanged.connect(self._parent.on_calcSingle_requested)

                # finally add items to the table (populate the row)
                self.tableWidget_menu.setItem(i, 0, wellNameItem)
                self.tableWidget_menu.setItem(i, 1, xCoordItem)
                self.tableWidget_menu.setItem(i, 2, yCoordItem)
                self.tableWidget_menu.setCellWidget(i, 3, headItem)
        
        self.updateUI()
    
    def on_data_recieved(self, df):
        """
            Modify the TableWidget when the data is recieved in the `data` terminal
        """
        self._clear_comboboxes()
        self.clear(clearTable=False)
        if df is not None:
            colnamesNumeric  = [col for col in df.columns if isNumpyNumeric (df[col].dtype)]
            colnamesDatetime = [col for col in df.columns if isNumpyDatetime(df[col].dtype)]
            self._addItems_to_comboboxes(colnamesNumeric, colnamesDatetime)
        self.updateUI()

    def on_itemAtColumn0_changed(self, item):
        if item.column() == 0:  # correct item at column 0, e.g. name column
            self.parent().on_calcSingle_requested()


    def updateUI(self):
        ''' enable buttons only if the data is here '''

        self.groupBox_singleTS.setEnabled(False)
        self.groupBox_allTS.setEnabled(False)
        
        self.comboBox_Datetime.setEnabled(False)
        self.label_3.setEnabled(False)

        if isinstance(self.parent().inputValues()['coord'], pd.DataFrame):
            if isinstance(self.parent().inputValues()['data'], pd.DataFrame) and self.comboBox_Datetime.currentText():
                self.groupBox_singleTS.setEnabled(True)
                self.groupBox_allTS.setEnabled(True)
                self.comboBox_Datetime.setEnabled(True)
                self.label_3.setEnabled(True)

        self.tableWidget_menu.resizeColumnsToContents()
    
    def clearSingleGradientDirectionArrow(self):
        '''
            Removes the QGraphicsLineItem that represents
            the gradient direction arrow from the visalization area
        '''
        view = self.graphicsView_direction
        if self._arrow is not None:
            view.scene().removeItem(self._arrow)
            self._arrow = None

    @QtCore.pyqtSlot(float, float)
    def on_singleGradientChanged(self, magnitude, direction):
        """  Update QGraphicsView with the gradient data"""
        self.clearSingleGradientDirectionArrow()
        
        angle = angle2bearing(direction)[0]
        self._arrow = myArrow(QtCore.QPointF(0, 0), None, angle=angle, length=40, lineWidth=1.5, arrowHeadSize=8, color=QtCore.Qt.blue)
        #print 'adding item', self._arrow, '  >>> ',
        self.graphicsView_direction.scene().addItem(self._arrow)
        #print 'ok'

    @QtCore.pyqtSlot()
    def on_pushButton_calculateAll_clicked(self):
        """ Button `calculate All` has been clicked."""
        self.parent().on_calcAll_requested()

    @QtCore.pyqtSlot()
    def on_dateTimeEdit_editingFinished(self):
        """
            Is executed, when the user finishes editing of the Datetime
            selection combobox. In practice, this happens, when a different
            timestep is selected.
        """
        #print 'editingFinished'
        self.parent().on_calcSingle_requested()
    
    @QtCore.pyqtSlot(unicode)
    def on_comboBox_Datetime_currentTextChanged(self, text):
        '''
            Update DateTimeEdit selection widget, based on the selected
            data in the `comboBox_Datetime`
        '''
        if not text:
            return
        tMin, tMax = self.parent().getMinMaxDatetime(colname=text)
        if tMin is not None and tMax is not None:
            QtMin = self.dateTimeEdit.dateTimeFromText(tMin.strftime('%Y-%m-%d %H:%M:%S'))
            QtMax = self.dateTimeEdit.dateTimeFromText(tMax.strftime('%Y-%m-%d %H:%M:%S'))


            self.dateTimeEdit.setMinimumDateTime(QtMin)
            self.dateTimeEdit.setMaximumDateTime(QtMax)

    def parent(self):
        return self._parent

    def selectedRows(self):
        '''
            Return the indexes of selected rows.

            Loop over rows in TableWidget and return the list of indexes
            of those rows in which the first item (column 0) is checked
        '''
        lst = []
        for i in xrange(self.tableWidget_menu.rowCount()):
            if self.tableWidget_menu.item(i, 0).checkState() == Qt.Checked:
                lst.append(i)
        return lst

    def selectedWellsInfo(self):
        '''
            Return the information of the selected wells.
            Dictionary where key is the well name, value - another dictionary with:
                'x' - x coord [float]
                'y' - y coord [float]
                'z' - name of the column with Z (head) values for this well in table in terminal `data` [str]
        '''
        INFO = dict()
        for i in self.selectedRows():
            sInfo = dict()
            sInfo['x'] = float(self.tableWidget_menu.item(i, 1).text())
            sInfo['y'] = float(self.tableWidget_menu.item(i, 2).text())
            sInfo['z'] = self.tableWidget_menu.cellWidget(i, 3).currentText()
            INFO[self.tableWidget_menu.item(i, 0).text()] = sInfo
        return INFO

    def selectedTimestep(self):
        '''
            Return the datetime in QDateTimeEdit widget
            converted to the requred python-datetime format
        '''
        t = self.dateTimeEdit.dateTime().toString('yyyy-MM-dd hh:mm:ss')
        return np.datetime64(t+'Z')  # zulu time

    def _tableWidget_wellNames(self):
        '''
            Get the list with names of the rows of the
            current table. Returns the list with names of
            the cells of the first column (`Well`)

        Return:
            list[str]
        '''
        return [self.tableWidget_menu.item(i, 0).text() for i in xrange(self.tableWidget_menu.rowCount())]

    def _clearQTableWidget(self):
        '''
            Method is used to flush all rows in the
            QTableWidget menu and disconnect the signals of
            the items
        '''
        #self.tableWidget_menu.disconnect()
        self.tableWidget_menu.setRowCount(0)
        self.tableWidget_menu.resizeColumnsToContents()

    def clear(self, clearTable=True):
        '''
            Clear table widget,
            Clear graphical arrow,
            set output to None,
            clear the strings in informative labels
        '''
        if clearTable:
            self._clearQTableWidget()
        self.clearSingleGradientDirectionArrow()
        self.parent().setOutput(this=None, All=None)
        self.label_singleMagVal.setText('')
        self.label_singleDirVal.setText('')

    def _clear_comboboxes(self):
        '''
            Method clears the content of the QComboBoxes in the menu table,
            which is represented with QTableWidget. The comboboxes are the
            column `Head` and separate ComboBox Datetime

        '''
        self.comboBox_Datetime.clear()

        for i in xrange(self.tableWidget_menu.rowCount()):
            self.tableWidget_menu.cellWidget(i, 3).clear()  #clear Head Combobox

    def _addItems_to_comboboxes(self, itemListHead, itemListDatetime):
        '''
            Method adds items to the QComboBoxes in the menu table,
            which is represented with QTableWidget. The comboboxes are the
            columns `Head` and `Datetime`. The `Head` box is created for each well,
            where the `Datetime` box is one for all wells.

            Automatically set the `currentItem` of the comboboxes based on the
            well name (for the HEAD-combobox) and on the datetime-dtype (for the
            datetime-Combobox)

        Args:
            itemListHead (list|tuple [str]):
                iterable with strings, names will be added to `Head`-combobox
            itemListDatetime (list|tuple [str]):
            iterable with strings, names will be added to `Datetime`-combobox

        '''
        self.comboBox_Datetime.addItems(itemListDatetime)

        
        for i in xrange(self.tableWidget_menu.rowCount()):
            name = self.tableWidget_menu.item(i, 0).text()  #string, name of the current well
            cb_head = self.tableWidget_menu.cellWidget(i, 3)
            cb_head.addItems(itemListHead)  # add to Head Combobox
           

            #now guess the correct currentItem in Head-Combobox
            if name in itemListHead:
                # if a complete-match , take this index
                cb_head.setCurrentIndex(itemListHead.index(name))
            else:
                for i in xrange(cb_head.count()):
                    #loop over different items (column names) in head-ComboBox
                    if cb_head.itemText(i) == name:
                        # text of this item (column name) matches the name of the well absolutely
                        cb_head.setCurrentIndex(i)
                        break
                    elif cb_head.itemText(i) in name or name in cb_head.itemText(i):
                        # text of this item (column name) matches the name of the well
                        cb_head.setCurrentIndex(i)
                        break
