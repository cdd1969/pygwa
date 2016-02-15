# -*- coding: utf-8 -*-
from pyqtgraph.python2_3 import asUnicode
from pyqtgraph.Qt import QtCore, QtGui


class TableView(QtGui.QTableView):
    """ Extends QTableView with some useful functions for automatic data handling
    and copy / export context menu.

    Modified from <pyqtgraph.TableWidget.setData>
    """
    
    def __init__(self, *args, **kwds):
        """
        All positional arguments are passed to QTableWidget.__init__().
        
        ===================== =================================================
        **Keyword Arguments**
        editable              (bool) If True, cells in the table can be edited
                              by the user. Default is False.
        sortable              (bool) If True, the table may be soted by
                              clicking on column headers. Note that this also
                              causes rows to appear initially shuffled until
                              a sort column is selected. Default is True.
                              *(added in version 0.9.9)*
        ===================== =================================================
        """
        
        QtGui.QTableView.__init__(self, *args)
        self._parent = kwds['parent']

        self.setSelectionMode(QtGui.QAbstractItemView.ContiguousSelection)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        
        
        self.contextMenu = QtGui.QMenu()
        self.contextMenu.addAction('Copy Selection').triggered.connect(self.copySel)
        self.contextMenu.addAction('Copy All').triggered.connect(self.copyAll)
        self.contextMenu.addAction('Save Selection').triggered.connect(self.saveSel)
        self.contextMenu.addAction('Save All').triggered.connect(self.saveAll)
        

         
    def serialize(self, useSelection=False):
        """Convert entire table (or just selected area) into tab-separated text values"""
        if useSelection:
            selection = self.selectionModel().selection().indexes()
            topLeft = selection[0]
            bottomRight = selection[-1]

            rows = list(range(topLeft.row(),
                              bottomRight.row() + 1))
            columns = list(range(topLeft.column(),
                                 bottomRight.column() + 1))
        else:
            rows = list(range(self.rowCount()))
            columns = list(range(self.columnCount()))

        data = []
        if self.horizontalHeadersSet:
            row = []
            if self.verticalHeadersSet:
                row.append(u'')
            
            for c in columns:
                row.append(asUnicode(self.horizontalHeaderItem(c)))
            data.append(row)
        
        for r in rows:
            row = []
            if self.verticalHeadersSet:
                row.append(asUnicode(self.verticalHeaderItem(r)))
            for c in columns:
                item = self.item(r, c)
                if item is not None:
                    row.append(asUnicode(item))
                else:
                    row.append(u'')
            data.append(row)
            
        s = ''
        for row in data:
            s += ('\t'.join(row) + '\n')
        return s

    def item(self, row, col):
        return self.model().index(row, col).data()
    
    def rowCount(self):
        return self.model().rowCount()

    def columnCount(self):
        return self.model().columnCount()

    def horizontalHeadersSet(self):
        return self.model().horizontalHeadersSet()

    def verticalHeadersSet(self):
        return self.model().verticalHeadersSet()

    def horizontalHeaderItem(self, *args):
        return self.model().headerData(*args, orientation=QtCore.Qt.Horizontal)

    def verticalHeaderItem(self, *args):
        return self.model().headerData(*args, orientation=QtCore.Qt.Vertical)

    def copySel(self):
        """Copy selected data to clipboard."""
        QtGui.QApplication.clipboard().setText(self.serialize(useSelection=True))

    def copyAll(self):
        """Copy all data to clipboard."""
        QtGui.QApplication.clipboard().setText(self.serialize(useSelection=False))

    def saveSel(self):
        """Save selected data to file."""
        self.save(self.serialize(useSelection=True))

    def saveAll(self):
        """Save all data to file."""
        self.save(self.serialize(useSelection=False))

    def save(self, data):
        fileName = QtGui.QFileDialog.getSaveFileName(self, "Save As..", "tableview_export.tsv", "Tab-separated values (*.tsv)")[0]
        if fileName:
            try:
                open(fileName, 'w').write(data)
            except Exception, err:
                print( "File is not created...")
                print( Exception, err)
        return

    def contextMenuEvent(self, ev):
        self.contextMenu.popup(ev.globalPos())
        
    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_C and ev.modifiers() == QtCore.Qt.ControlModifier:
            ev.accept()
            self.copySel()
        if ev.key() == QtCore.Qt.Key_A and ev.modifiers() == QtCore.Qt.ControlModifier:
            ev.accept()
            self.selectAll()
        else:
            ev.ignore()




