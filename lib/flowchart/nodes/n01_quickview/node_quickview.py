#!/usr/bin python
# -*- coding: utf-8 -*-
import os
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt
from pyqtgraph.flowchart.Node import Node
from pyqtgraph import BusyCursor
from pyqtgraph import functions as fn

import traceback
import pandas as pd
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)

from lib.common.TableView import TableView
from lib.common.PandasQModels import PandasDataModel, PandasHeaderModel
from lib.functions.general import isNumpyDatetime, isNumpyNumeric


class QuickViewNode(Node):
    """View dataframe in TableView/Matplotlib-plot"""
    nodeName = "Quick View"

    def __init__(self, name, parent=None):
        super(QuickViewNode, self).__init__(name, terminals={'In': {'io': 'in'}})
        self.graphicsItem().setBrush(fn.mkBrush(150, 150, 250, 200))
        self._pandasDataModel   = PandasDataModel(parent=self)
        self._pandasHeaderModel = PandasHeaderModel(parent=self)
        self._ctrlWidget = QuickViewCtrlWidget(self)

        # connect show/hide signals
        self._pandasHeaderModel.row_hidden.connect(self._ctrlWidget.tableView.horizontalHeader().hideSection)  #argumnent [int]
        self._pandasHeaderModel.row_showed.connect(self._ctrlWidget.tableView.horizontalHeader().showSection)  #argumnent [int]
        self._pandasDataModel.modelReset.connect(self._ctrlWidget.update)  #no argument


        self._id = None
        
    def process(self, In):
        '''
            Take the dataframe from the terminal `In` and process it
        '''

        if id(In) != self._id and self._pandasDataModel is not None:
            logger.debug('clearing QuickView on_process()')
            self.clearModels()
        if In is not None:
            if isinstance(In, pd.Series):
                In = In.to_frame(name='SERIES')

            self._pandasDataModel.setPandasDataframe(In)
            self._pandasHeaderModel.setPandasDataframe(In)
            self._id = id(In)
        self.ctrlWidget().update()

    def getPandasDataModel(self):
        return self._pandasDataModel
    
    def getPandasHeaderModel(self):
        return self._pandasHeaderModel
        
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

    def clearModels(self):
        self._id = None
        self._pandasDataModel.clear()
        self._pandasHeaderModel.destroy()



class QuickViewCtrlWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(QuickViewCtrlWidget, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'node_quickview.ui'), self)
        self._parent = parent
        self.initUI()
        self.pushButton_viewPlot.setEnabled(False)


    def initUI(self):
        #self.tableView_header = QtWidgets.QTableView()  # already set in the *.ui file
        self.tableView = TableView(parent=self)
        self.twWindow  = None
        self.update()

    def setModels(self):
        """ Set already created models to node's widgets:
                (1) - set header model to `self.tableView_header` (MENU)
                (2) - set data table model to `self.tableView` (DATA)
        """
        #logger.debug( "setModels()")
        modelsAreSet = True
        if self.parent().getPandasDataModel() is not None:
            try:
                self.tableView_header.setModel(self.parent().getPandasHeaderModel())
                if self.parent().getPandasHeaderModel().df.empty:
                    modelsAreSet &= False
            except Exception, err:
                modelsAreSet &= False
                traceback.print_exc()
                logger.info("QuickViewCtrlWidget: Unnable to set QlistView model (Selection-Menu)")
            try:
                self.tableView.setModel(self.parent().getPandasDataModel())
                if self.parent().getPandasDataModel().df.empty:
                    modelsAreSet &= False
            except Exception, err:
                modelsAreSet &= False
                traceback.print_exc()
                logger.info("QuickViewCtrlWidget: Unnable to set QtableView model (Data-Table-View")

        self.updateUI(modelsAreSet)

    def updateUI(self, modelsAreSet=False):
        ''' enable buttons only if the models are set '''

        self.pushButton_deselectAll.setEnabled(modelsAreSet)
        self.pushButton_selectAll.setEnabled(modelsAreSet)
        self.pushButton_viewTable.setEnabled(modelsAreSet)
        self.pushButton_viewPlot.setEnabled(modelsAreSet)
        self.checkBox_separateSubplots.setEnabled(modelsAreSet)


        df = self.parent().getPandasDataModel().df
        table_size_str = ' {0} x {1}'.format(len(df.columns), len(df.index))
        memory_usg_str = ' {0:.0f} '.format(float(sum(df.memory_usage(index=True)))/1024.)
        self.label_tableSize.setText(table_size_str)
        self.label_memoryUsage.setText(memory_usg_str)

    def update(self):
        #try:
        #    self.twWindow.hide()
        #except:
        #    self.twWindow = None
        self.setModels()  # we enable and disable buttons also in this method
        self.tableView.horizontalHeader().reset()
        self.tableView.resizeColumnsToContents()
        self.tableView_header.resizeColumnsToContents()

    @QtCore.pyqtSlot()  #default signal
    def on_pushButton_selectAll_clicked(self):
        """ Select all data-rows in a tableView_header"""
        if True:
            model = self.parent().getPandasHeaderModel()
            # now loop over all items at column (0)
            for i in xrange(model.rowCount()):
                model.item(i, 0).setCheckState(Qt.Checked)

    @QtCore.pyqtSlot()  #default signal
    def on_pushButton_deselectAll_clicked(self):
        """ Select all data-rows in a tableView_header"""
        if True:
            model = self.parent().getPandasHeaderModel()
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
                df = self.parent().getPandasDataModel().df
                
                columns = self.parent().getPandasHeaderModel().selectedColumns()  #consider only the selected columns
                datetime_cols = [col for col in columns if isNumpyDatetime(df[col].dtype)]
                numeric_cols  = [col for col in columns if isNumpyNumeric (df[col].dtype)]
                datetime_col = datetime_cols[0] if len(datetime_cols) > 0 else None   #plot with x=datetime if possible
                
                if self.checkBox_separateSubplots.isChecked() and len(numeric_cols) > 1:
                    '''
                        Do the plotting of each selected numerical column on an individual subplot
                    '''
                    f, axes = plt.subplots(len(numeric_cols), sharex=True)
                    for ax, numeric_col in zip(axes, numeric_cols):
                        df.plot(x=datetime_col, y=numeric_col, ax=ax)
                        legend = ax.legend(shadow=True)
                    # Fine-tune figure; make subplots close to each other and hide x ticks for all but bottom plot.
                    #f.subplots_adjust(hspace=0)
                    plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
                else:
                    '''
                        Plot all selected numerical columns together on a single subplot
                    '''
                    f, ax = plt.subplots(1)
                    for numeric_col in numeric_cols:
                        df.plot(x=datetime_col, y=numeric_col, ax=ax)
                    legend = ax.legend(shadow=True)

                f.show()
            except Exception as exp:
                self._parent.setException(exp)
                return

    def parent(self):
        return self._parent
