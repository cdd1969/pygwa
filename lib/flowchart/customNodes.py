# -*- coding: utf-8 -*-
from pyqtgraph.flowchart import Node
from ..process2pandas.process2pandas import read_hydrographs_into_pandas


#read_hydrographs_into_pandas(fname, datetime_indexes=False, log=False, decimal='.', delimiter=';', usecols=[0, 1, 2, 3, 4, 5, 6, 7], skiprows=1)

class ColumnSelectNode(Node):
    """Read ASCI column-based data file and convert values to [numpy-array]/[pandas dataframe]"""
    nodeName = "readTextData"
    

    def __init__(self, name):
        Node.__init__(self, name, terminals={'In': {'io': 'in'}})
        self.columns = set()
        self.columnList = QtGui.QListWidget()
        self.axis = 0
        self.columnList.itemChanged.connect(self.itemChanged)
        
    def process(self, In, display=True):
        if display:
            self.updateList(In)
                
        out = {}
        if hasattr(In, 'implements') and In.implements('MetaArray'):
            for c in self.columns:
                out[c] = In[self.axis:c]
        elif isinstance(In, np.ndarray) and In.dtype.fields is not None:
            for c in self.columns:
                out[c] = In[c]
        else:
            self.In.setValueAcceptable(False)
            raise Exception("Input must be MetaArray or ndarray with named fields")
            
        return out
        
    def ctrlWidget(self):
        return self.columnList

    def updateList(self, data):
        if hasattr(data, 'implements') and data.implements('MetaArray'):
            cols = data.listColumns()
            for ax in cols:  ## find first axis with columns
                if len(cols[ax]) > 0:
                    self.axis = ax
                    cols = set(cols[ax])
                    break
        else:
            cols = list(data.dtype.fields.keys())
                
        rem = set()
        for c in self.columns:
            if c not in cols:
                self.removeTerminal(c)
                rem.add(c)
        self.columns -= rem
                
        self.columnList.blockSignals(True)
        self.columnList.clear()
        for c in cols:
            item = QtGui.QListWidgetItem(c)
            item.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsUserCheckable)
            if c in self.columns:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
            self.columnList.addItem(item)
        self.columnList.blockSignals(False)
        

    def itemChanged(self, item):
        col = str(item.text())
        if item.checkState() == QtCore.Qt.Checked:
            if col not in self.columns:
                self.columns.add(col)
                self.addOutput(col)
        else:
            if col in self.columns:
                self.columns.remove(col)
                self.removeTerminal(col)
        self.update()
        
    def saveState(self):
        state = Node.saveState(self)
        state['columns'] = list(self.columns)
        return state
    
    def restoreState(self, state):
        Node.restoreState(self, state)
        self.columns = set(state.get('columns', []))
        for c in self.columns:
            self.addOutput(c)