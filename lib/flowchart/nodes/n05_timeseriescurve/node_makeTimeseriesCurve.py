#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph import BusyCursor, PlotDataItem
import numpy as np
import pandas as pd

from lib.flowchart.package import Package
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.general import returnPandasDf, isNumpyDatetime, isNumpyNumeric


class makeTimeseriesCurveNode(NodeWithCtrlWidget):
    """Prepare Timeseries for plotting. Generate curve that can be viewed with node *TimeseriesPlot*
    and pd.Series with datetime stored in Index
    """
    nodeName = "makeTimeseriesCurve"
    uiTemplate = [
        {'name': 'Y:signal', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Signal Data-Values (Y-axis)'},
        {'name': 'X:datetime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Datetime Values (X-axis)'},
        {'name': 'tz correct', 'type': 'float', 'value': 0, 'default': 0, 'suffix': ' hours', 'tip': '<float>\nONLY FOR CURVE!!!\nTimezone correction\nNumber of hours to add/substract from result. Due to missing\ntimezone settings it may be nessesary to use this parameter.\nCheck the results manually with *TimeseriesPlot* Node'},
        {'name': 'color', 'type': 'color', 'tip': 'Curve color'},
        ]

    def __init__(self, name, parent=None):
        super(makeTimeseriesCurveNode, self).__init__(name, parent=parent, terminals={'df': {'io': 'in'}, 'pd.Series': {'io': 'out'}, 'Curve': {'io': 'out'}}, color=(150, 150, 250, 150))
        self._plotRequired = False
        self.item = PlotDataItem(clipToView=False)
    
    def _createCtrlWidget(self, **kwargs):
        return makeTimeseriesCurveNodeCtrlWidget(**kwargs)
        
    def process(self, df):
        df  = returnPandasDf(df)

        colname = [col for col in df.columns if isNumpyNumeric(df[col].dtype)]
        self._ctrlWidget.param('Y:signal').setLimits(colname)
        colname = [col for col in df.columns if isNumpyDatetime(df[col].dtype)]
        self._ctrlWidget.param('X:datetime').setLimits(colname)

        with BusyCursor():
            kwargs = self.ctrlWidget().prepareInputArguments()
            t = df[kwargs['X:datetime']].values
            # part 1
            timeSeries = pd.DataFrame(data=df[kwargs['Y:signal']].values, index=t, columns=[kwargs['Y:signal']])

            # part 2
            #   convert time
            b = t.astype(np.dtype('datetime64[s]'))
            timeStamps = b.astype(np.int64)-kwargs['tz correct']*60*60
            #   now create curve
            self.item.setData(timeStamps, df[kwargs['Y:signal']].values, pen=kwargs['color'], name=kwargs['Y:signal'])
        return{'Curve': self.item, 'pd.Series': Package(timeSeries) }



class makeTimeseriesCurveNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(makeTimeseriesCurveNodeCtrlWidget, self).__init__(**kwargs)

    def prepareInputArguments(self):
        kwargs = dict()
        kwargs['Y:signal'] = self.paramValue('Y:signal', datatype=(str, unicode))
        kwargs['X:datetime'] = self.paramValue('X:datetime', datatype=(str, unicode))
        kwargs['tz correct'] = self.paramValue('tz correct', datatype=(int, float))
        kwargs['color'] = self.param('color').value()
        return kwargs
