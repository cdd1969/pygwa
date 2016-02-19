# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import BusyCursor
import csv


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
        #self.contextMenu.addAction('Copy All').triggered.connect(self.copyAll)
        self.contextMenu.addAction('Save Selection').triggered.connect(self.saveSel)
        self.contextMenu.addAction('Save All').triggered.connect(self.saveAll)
        

         
    def serialize(self, useSelection=False, sep='\t', fv=u''):
        """Convert entire table (or just selected area) into tab-separated text values

        Args:
        -----
            useSelection (bool):
                flag to read selected data
            
            sep (str):
                string-separator between cells

            fv (str):
                string to represent fill-values
        """
        sep = unicode(sep)
        fv = unicode(fv)
        model = self.model()
        if useSelection:
            selection = self.selectionModel().selection().indexes()
            if selection:
                topLeft = selection[0]
                bottomRight = selection[-1]

                rows = xrange(topLeft.row(), bottomRight.row() + 1)
                columns = xrange(topLeft.column(), bottomRight.column() + 1)
            else:
                return None
        else:
            rows = xrange(model.rowCount())
            columns = xrange(model.columnCount())

        data = []
        if self.horizontalHeadersSet:
            row = []
            if self.verticalHeadersSet:
                row.append(u'')
            
            for c in columns:
                row.append(unicode(self.horizontalHeaderItem(c)))
            data.append(row)
        
        for r in rows:
            row = []
            if self.verticalHeadersSet:
                row.append(unicode(self.verticalHeaderItem(r)))
            for c in columns:
                index = model.index(r, c)
                item = model.data(index)
                if item is not None:
                    row.append(unicode(item))
                else:
                    row.append(fv)
            data.append(row)
            
        s = u''
        for row in data:
            s += sep.join(row) + '\n'
        return unicode(s)


    def handleSave(self, useSelection=False, missing_value=u''):
        missing_value = unicode(missing_value)
        
        model = self.model()
        if useSelection:
            selection = self.selectionModel().selection().indexes()
            if selection:
                topLeft = selection[0]
                bottomRight = selection[-1]

                rows = xrange(topLeft.row(), bottomRight.row() + 1)
                columns = xrange(topLeft.column(), bottomRight.column() + 1)
            else:
                return None
        else:
            rows = xrange(model.rowCount())
            columns = xrange(model.columnCount())


        fn = self.fileSaveAs()
        if fn:
            try:
                with BusyCursor(), open(unicode(fn), 'wb') as stream:
                    if fn.endswith('.tsv'):
                        dialect = 'excel-tab'
                    else:
                        dialect = 'excel'
                    writer = csv.writer(stream, dialect=dialect)

                    # Write header
                    if self.horizontalHeadersSet:
                        header_row = []
                        if self.verticalHeadersSet:
                            header_row.append(u'')
                        for c in columns:
                            header_row.append(unicode(self.horizontalHeaderItem(c)))
                        writer.writerow(header_row)

                    # Write data
                    for row in rows:
                        rowdata = []
                        if self.verticalHeadersSet:
                            rowdata.append(unicode(self.verticalHeaderItem(row)))
                        for column in columns:
                            index = model.index(row, column)
                            item  = model.data(index)
                            if item:
                                rowdata.append(unicode(item))
                            else:
                                rowdata.append(missing_value)
                        writer.writerow(rowdata)
                QtGui.QMessageBox.information(None, 'Export table to file', 'File `{0}` saved successfully'.format(fn))
            except Exception, err:
                QtGui.QMessageBox.critical(None, 'Export table to file', 'File `{2}` cannot be saved:\n{0}\n{1}'.format(Exception, err, fn))


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
        with BusyCursor():
            data = self.serialize(useSelection=True)
        if data:
            QtGui.QApplication.clipboard().setText(data)

    def copyAll(self):
        """Copy all data to clipboard."""
        with BusyCursor():
            self.serialize(useSelection=False)

    def saveSel(self):
        """Save selected data to file."""
        self.handleSave(useSelection=True)

    def saveAll(self):
        """Save all data to file."""
        #with BusyCursor():
        #    data = self.serialize(useSelection=False)
        #self.save(data)
        self.handleSave(useSelection=False)

    def save(self, data):
        fileName = self.fileSaveAs()
        if fileName:
            try:
                open(fileName, 'w').write(data)
            except Exception, err:
                QtGui.QMessageBox.critical(None, 'Export table to file', 'File `{2}` cannot be saved:\n{0}\n{1}'.format(Exception, err, fileName))
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


    def fileSaveAs(self):
        fn, _ = QtGui.QFileDialog.getSaveFileName(self, "Export table to file", "export.csv", "CSV files (*.csv);; TAB separated files (*.tsv)")
        if not fn:
            return False
        #fn = fn.lower()
        if not fn.endswith(('.csv', '.tsv')):
            # The default.
            fn += '.csv'
        return fn

