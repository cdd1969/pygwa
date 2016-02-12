import numpy as np
import pyqtgraph as pg
from pyqtgraph import functions as fn
from pyqtgraph import getConfigOption

from ..functions.general import returnPandasDf, isNumpyDatetime



class ScatterPlotWidget(pg.ScatterPlotWidget):
    """ This is a high-level widget for exploring relationships in tabular data.

        This plot widget is an extended version of pyqtgraph default widget.

        - data dtype check
            (column that are of <datetime64> are not displayed)
            Data check conditions are wrapped within method *toIgnore*
            You my want to override this method to change your data-input
            conditions

        - input data now may be pandas.DataFrame

        - close/show event change the stauts *self._hidden*, which may be
            acesses through *isHidden()* and *isShown()* methods
        
    
    """
    def __init__(self, parent=None):
        super(ScatterPlotWidget, self).__init__(self)
        self._hidden = True

        bg = fn.mkColor(getConfigOption('background'))
        bg.setAlpha(255)  # we need to do that, since in default widget alpha is set to 50, but we want it BLACK!
    
    def toIgnore(self, obj):
        """ consider overriding this method for your custom criteria"""
        if isNumpyDatetime(obj):  # datetime column
            return True
        return False
        
    def setFields(self, fields, mouseOverField=None):
        """
        Set the list of field names/units to be processed.
        
        The format of *fields* is the same as used by
        :func:`ColorMapWidget.setFields <pyqtgraph.widgets.ColorMapWidget.ColorMapParameter.setFields>`

        ============== ============================================================
        Field Options:
        mode           Either 'range' or 'enum' (default is range). For 'range',
                       The user may specify a gradient of colors to be applied
                       linearly across a specific range of values. For 'enum',
                       the user specifies a single color for each unique value
                       (see *values* option).
        units          String indicating the units of the data for this field.
        values         List of unique values for which the user may assign a
                       color when mode=='enum'. Optionally may specify a dict
                       instead {value: name}.
        ============== ============================================================
        """

        COLNAMES = [field[0] for field in fields]
        if self.data is not None:
            for columnName in self.data.dtype.fields.keys():  #go through dtype fields
                if columnName in COLNAMES:  #if we want to set up this opt (in our inputs)
                    if self.toIgnore(self.data.dtype.fields[columnName][0]):  # if condition met
                        for f in fields:  #now find it in our list
                            if f[0] == columnName:
                                fields.remove(f)
        pg.ScatterPlotWidget.setFields(self, fields, mouseOverField=mouseOverField)
        
    def setData(self, data):
        """ Extendind defult method to accept pandas.DataFrame
            and exit on unpropriate dtype
        """
        df = returnPandasDf(data, raiseException=False)
        if df is not None:
            pg.ScatterPlotWidget.setData(self, df.to_records())
            return

        elif isinstance(data, np.recarray):
            pg.ScatterPlotWidget.setData(self, data)
            return
        else:
            return

    def updatePlot(self):
        try:
            pg.ScatterPlotWidget.updatePlot(self)
        except Exception, err:
            print( 'Unable to update plot')
            print( Exception, err)
            

    
    def hideEvent(self, event):
        super(ScatterPlotWidget, self).hideEvent(event)
        self.hide()
        self._hidden = True

    def showEvent(self, event):
        super(ScatterPlotWidget, self).showEvent(event)
        self.show()
        self._hidden = False

    def closeEvent(self, event):
        #super(ScatterPlotWidget, self).closeEvent(event)
        self._hidden = True
        self.destroy()

    def isShown(self):
        return not self._hidden

    def isHidden(self):
        return self._hidden
