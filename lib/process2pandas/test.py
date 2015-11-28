from PyQt5 import QtWidgets
from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant, QModelIndex, qDebug, pyqtSlot, pyqtSignal
import sys
import numpy as np
import process2pandas
import cPickle as pickle
import gc
import pandas as pd



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(QtWidgets.QMainWindow, self).__init__()
        tableView = QtWidgets.QTableView()
        self.setCentralWidget(tableView)

        d = process2pandas.read_hydrographs_into_pandas('../../../Farge-ALL_10min.all', datetime_indexes=False)
        myModel = PandasModel(d)
        #myModel = PandasModel("dataAveraged")
        tableView.setModel(myModel)



        #myModel.setData(filter_wl_71h_serfes1991(myModel.getData()))

        #myModel.saveData("save_test")
        #myModel.loadData("dataAveraged")



class PandasModel(QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        if isinstance(data, pd.DataFrame):
            # set explicitly passed pandas dataframe
            self._dataPandas = data
            self.update()
        elif isinstance(data, (str, unicode)):
            # try to load data from file
            self.loadData(data)
        else:
            raise TypeError("Invalid type of argument <data> detected. Received: {0}. Must be [str, unicode, pd.DataFrame]".format(type(data)))

    def setData(self, data):
        try:
            del self._dataPandas
            # no need to call garbage collector, since it will be executed via <update()>
        except:
            pass
        self._dataPandas = data
        self.update()

    def getData(self):
        return self._dataPandas

    def update(self):
        try:
            del self._data
            gc.collect()
        except:  # no instance <self._data> yet
            pass
        self._data = self.createNumpyData()
        self.r, self.c = self._data.shape
        self.endResetModel()

    def createNumpyData(self):
        # we will use Numpy cause of its blazing speed
        # in contrast, the direct usage of pandas dataframe <df[i][j]> in method <data()> is extremely slow
        return np.array(self._dataPandas)




    def rowCount(self, parent=None):
        return self.r

    def columnCount(self, parent=None):
        return self.c

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data[index.row(), index.column()])
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._dataPandas.columns[section]
            elif orientation == Qt.Vertical:
                return section
        return QVariant()

    def saveData(self, fname):
        sys.stdout.write('Saving data to file <{0}>...'.format(fname))
        try:
            with open(fname, 'w') as f:
                pickle.dump(self._dataPandas, f)
                f.close()
            sys.stdout.write('OK\n'.format(fname))
        except:
            sys.stdout.write('FAILED\n'.format(fname))

    def loadData(self, fname):
        sys.stdout.write('Loading data from file <{0}>...'.format(fname))
        try:
            with open(fname, 'r') as f:
                self.setData(pickle.load(f))
                f.close()
            sys.stdout.write('OK\n'.format(fname))
        except:
            sys.stdout.write('FAILED\n'.format(fname))




def filter_wl_71h_serfes1991(data):
    '''
    data - is pandas dataframe, where indexes are Datetime objects,
           see 'parse_dates' parameters
    '''
    print "Passed data has shape:", data.shape
    #print number of items per day
    #print(data.groupby(data.index.date).count())

    # ok, we see, that we have 144 measurements per day....
    entriesPerDay = data.groupby(data.index.date).count()
    print entriesPerDay
    N = entriesPerDay.ix[1, 0]
    print 'i will use following number of entries per day: ', N

    #N = 144
    for col_name in data.columns:  # cycle through each column...
        print "working with column:", col_name
        data[col_name+'_averaging1'] = np.nan
        data[col_name+'_averaging2'] = np.nan
        data[col_name+'_timeAverage'] = np.nan
        
        print "\t Calculating first mean:", col_name
        for i in xrange(N/2, len(data.index)-N/2):  # cycle trough correct indexes
            data.ix[i, col_name+'_averaging1'] = data.ix[i-N/2:i+N/2, col_name].mean()
        
        print "\t Calculating second mean:", col_name
        for i in xrange(N, len(data.index)-N):  # cycle trough correct indexes
            data.ix[i, col_name+'_averaging2'] = data.ix[i-N/2:i+N/2, col_name+'_averaging1'].mean()
        
        print "\t Calculating third mean:", col_name
        for i in xrange(N+N/2, len(data.index)-N-N/2):  # cycle trough correct indexes
            data.ix[i, col_name+'_timeAverage'] = data.ix[i-N/2:i+N/2, col_name+'_averaging2'].mean()
        
        del data[col_name+'_averaging1']
        del data[col_name+'_averaging2']

    return data



def main():
    app = QtWidgets.QApplication(sys.argv)

    w = MainWindow()
    w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    #main()


    class aaa (object):
        def __init__(self):
            self._a = 5
            print 'self._a: id=', id(self._a)
        def get(self):
            return self._a

    a = aaa()
    b = a.get()
    print 'return self._a: id=', id(b) 

