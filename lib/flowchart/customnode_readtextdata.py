#!/usr/bin python
# -*- coding: utf-8 -*-

import os, sys
from PyQt5 import QtWidgets, QtGui, uic, QtCore
from collections import OrderedDict




class readTextDataCtrlWidget(QtWidgets.QWidget):
    sigFileSelected = QtCore.pyqtSignal(unicode)
    

    def __init__(self):
        super(readTextDataCtrlWidget, self).__init__()
        uic.loadUi('customnode_readtextdata.ui', self)

        self._fileIsSelected = False
        self._fname = None
        self._labelPallete = QtGui.QPalette()

        self.connectSignals()
        self.initUI()

    def connectSignals(self):
        self.sigFileSelected.connect(self.fileIsSelected)
    

    def initUI(self):
        self._labelPallete.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        self.label_selectFile.setPalette(self._labelPallete)

        for item in ['%d.%m.%Y %H:%M',
                      '%d.%m.%Y %H:%M:%S',
                      '%c',
                      '%x',
                      '%X',
                      '--userdefined--'
                    ]:
            self.comboBox_datetimeParser.addItem(item)

        self.lineEdit_decimal.setText('.')
        self.lineEdit_delimiter.setText(';')


    @QtCore.pyqtSlot()  #default signal
    def on_pushButton_selectFile_clicked(self):
        fname = None
        filters = "ASCII files (*.txt *.csv *.all *.dat);;All files (*.*)"
        fname = unicode(QtWidgets.QFileDialog.getOpenFileName(self, 'Open ASCII data file', filter=filters)[0])
        if fname:
            self.sigFileSelected.emit(fname)
    
    @QtCore.pyqtSlot(bool)  #default signal
    def on_radioButton_columnIndex_toggled(self, isChecked):
        self.spinBox_columnIndex.setEnabled(isChecked)
        self.lineEdit_combineColumn.setDisabled(isChecked)

    @QtCore.pyqtSlot(unicode)
    def fileIsSelected(self, filename):
        if os.path.isfile(filename):
            self._fileIsSelected = True
            self._fname = filename


            # now change QLabel
            self._labelPallete.setColor(QtGui.QPalette.Foreground, QtCore.Qt.green)
            self.label_selectFile.setPalette(self._labelPallete)

            self.label_selectFile.setText('File is selected')
            self.label_selectFile.setToolTip('File is selected: {0}'.format(filename))
            self.label_selectFile.setStatusTip('File is selected: {0}'.format(filename))
        else:
            self._fileIsSelected = False
            self._fname = None
            # now change QLabel
            self._labelPallete.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
            self.label_selectFile.setPalette(self._labelPallete)

            self.label_selectFile.setText('Select File')
            self.label_selectFile.setToolTip('')
            self.label_selectFile.setStatusTip('')


    def saveState(self):
        """Return a dictionary representing the current state of this Widget"""

        state = {'fname': self._fname,
                 'datetime': self.groupBox_dateTime.isChecked(),
                 'radioButton_columnIndex_isToggled': self.radioButton_columnIndex.isChecked(),
                 'columnIndex': self.spinBox_columnIndex.value(),
                 'combineCols': self.lineEdit_combineColumn.text().strip(),
                 'dateParser': self.comboBox_datetimeParser.currentText().strip(),
                 'decimal': self.lineEdit_decimal.text().strip(),
                 'delimiter': self.lineEdit_delimiter.text().strip(),
                 'skipRows': self.spinBox_skiprows.value(),
                 'useCols': self.lineEdit_useCols.text().strip()
                 }
        return state
    
    def loadState(self, state):
        """Load widget state from a dictionary"""
        self.sigFileSelected.emit(state['fname'])
        
        if state['radioButton_columnIndex_isToggled'] is True:
            self.radioButton_columnIndex.toggle()
        else:
            self.radioButton_combineColumn.toggle()
        #self.on_radioButton_columnIndex_toggled(True if state['datetimeMode'] == u'columnIndex' else False)  # this will trigger the signal
        self.groupBox_dateTime.setChecked(state['datetime'])  # it is important to check this groupBox one after radio buttons
        self.spinBox_columnIndex.setValue(state['columnIndex'])
        self.lineEdit_combineColumn.setText(state['combineCols'])
        self.comboBox_datetimeParser.insertItem(0, state['dateParser'])
        self.comboBox_datetimeParser.setCurrentIndex(0)
        self.lineEdit_decimal.setText(state['decimal'])
        self.lineEdit_delimiter.setText(state['delimiter'])
        self.spinBox_skiprows.setValue(state['columnIndex'])
        self.lineEdit_useCols.setText(state['useCols'])

    def evaluateState(self, state):
        """ Some of the parameters read from widget are not of desired type,
            i.e. in combineCols lineEdit we can have <u'[1,2,3]'> but we want
            to have a python-list instead of a unicode string. Thats why we will
            evaluate some of the state-parameters.

            This function also maps dictionary of savedState() to the real
            parameter names of function pandas.read_csv() that will be used
            for processing

            OUTPUT:
                The dictionary <evParams> can be used in a following way:
                    pandas.read_csv(**evParams)
        """
        evParams = {}

        # ---!---
        evParams['parse_dates'] = False
        evParams['index_col']   = None
        evParams['date_parser'] = None

        if state['datetime'] is True:
            evParams['date_parser'] = state['dateParser']
            
            if state['radioButton_columnIndex_isToggled']:
                evParams['parse_dates'] = True
                evParams['index_col'] = state['columnIndex']
            else:
                if state['combineCols'] is not u'':
                    evParams['parse_dates'] = eval(state['combineCols'])
                else:  # if we have emty lineEdit
                    evParams['parse_dates'] = False
        # ---!---
        if state['useCols'] is not u'':
            evParams['usecols'] = eval(state['useCols'])
        else:  # if we have emty lineEdit
            evParams['usecols'] = None
        # ---!---
        evParams['decimal']  = state['decimal']
        evParams['sep']      = state['delimiter']
        evParams['skiprows'] = state['skipRows']
        evParams['filepath_or_buffer'] = state['fname']
        
        return evParams



def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = readTextDataCtrlWidget()
    ex.show()

    #raw_input('save')
    state = ex.saveState()
    #raw_input('load')

    ex.loadState(state)
    print ex.saveState()

    print ex.evaluateState(state)


    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
