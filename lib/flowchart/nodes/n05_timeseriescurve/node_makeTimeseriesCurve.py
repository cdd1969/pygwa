#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph import BusyCursor, PlotDataItem
from pyqtgraph import functions as fn
from pyqtgraph.Qt import QtCore
import numpy as np
import pandas as pd

from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.general import isNumpyDatetime, isNumpyNumeric
import time


class makeTimeseriesCurveNode(NodeWithCtrlWidget):
    """Prepare Timeseries for plotting. Generate curve that can be viewed with node *TimeseriesPlot*
    and pd.Series with datetime stored in Index
    """
    nodeName = "Make Curve"
    uiTemplate = [
        {'name': 'Y:signal', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Signal Data-Values (Y-axis)'},
        {'name': 'X:datetime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Datetime Values (X-axis)'},
        {'name': 'tz correct', 'type': 'float', 'value': 0, 'default': 0, 'suffix': ' hours', 'tip': '<float>\nONLY FOR CURVE!!!\nTimezone correction\nNumber of hours to add/substract from result. Due to missing\ntimezone settings it may be nessesary to use this parameter.\nCheck the results manually with *TimeseriesPlot* Node'},
        {'name': 'color', 'type': 'color', 'tip': 'Curve color'},
        {'name': 'Display Line', 'type': 'bool', 'value': True, 'tip': 'display line-curve between data points', 'children': [
            {'name': 'Style', 'type': 'list', 'tip': 'Style', 'values':
                {'solid': QtCore.Qt.SolidLine,
                 'dash': QtCore.Qt.DashLine,
                 'dash-dot': QtCore.Qt.DashDotLine,
                 'dot-dot': QtCore.Qt.DotLine,
                 'dash-dot-dot': QtCore.Qt.DashDotDotLine }},
            {'name': 'Linewidth', 'type': 'float', 'value': 1., 'limits': (0., 20.), 'step': 0.1,  'tip': 'Linewidth'},
        ]},
        {'name': 'Display Data Points', 'type': 'bool', 'value': False, 'tip': 'display data points as scatter', 'children': [
            {'name': 'Symbol', 'type': 'list', 'tip': 'Symbol for data points', 'value': 'o', 'values':
                {'circle': 'o',
                 'triangle': 't',
                 'square': 's',
                 'pentagon': 'p',
                 'hexagon': 'h',
                 'star': 'star',
                 'cross': '+',
                 'diamond': 'd'}},
            {'name': 'Size', 'type': 'int', 'value': 5, 'limits': (0, 1000), 'tip': 'Symbol size'},
        ]},
        ]

    def __init__(self, name, parent=None):
        super(makeTimeseriesCurveNode, self).__init__(name, parent=parent, terminals={'df': {'io': 'in'}, 'pd.Series': {'io': 'out'}, 'Curve': {'io': 'out'}}, color=(150, 150, 250, 150))
        self._plotRequired = False
        self.item = PlotDataItem(clipToView=False)
    
    def _createCtrlWidget(self, **kwargs):
        return makeTimeseriesCurveNodeCtrlWidget(**kwargs)
        
    def process(self, df):
        if df is None:
            del self.item
            self.item = None
            return {'Curve': None, 'pd.Series': None }
        if self.item is None:
            self.item = PlotDataItem(clipToView=False)

        colname = [col for col in df.columns if isNumpyNumeric(df[col].dtype)]
        self._ctrlWidget.param('Y:signal').setLimits(colname)
        colname = [col for col in df.columns if isNumpyDatetime(df[col].dtype)]
        self._ctrlWidget.param('X:datetime').setLimits(colname)

        with BusyCursor():
            kwargs = self.ctrlWidget().prepareInputArguments()
            
            #self.item = PlotDataItem(clipToView=False)
            t = df[kwargs['X:datetime']].values
            # part 1
            timeSeries = pd.DataFrame(data=df[kwargs['Y:signal']].values, index=t, columns=[kwargs['Y:signal']])

            # part 2
            #   convert time
            b = t.astype(np.dtype('datetime64[s]'))
            timeStamps = b.astype(np.int64)-kwargs['tz correct']*60*60+time.timezone
            #   now create curve
            pen = fn.mkPen(color=kwargs['color'], width=kwargs['width'], style=kwargs['style'])
            self.item.setData(timeStamps, df[kwargs['Y:signal']].values, pen=pen, name=kwargs['Y:signal'])
            
            self.item.setSymbol(kwargs['symbol'])
            if kwargs['symbol'] is not None:
                self.item.setSymbolPen(kwargs['color'])
                self.item.setSymbolBrush(kwargs['color'])
                self.item.setSymbolSize(kwargs['symbolSize'])
        return {'Curve': self.item, 'pd.Series': timeSeries }



class makeTimeseriesCurveNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(makeTimeseriesCurveNodeCtrlWidget, self).__init__(**kwargs)

    def prepareInputArguments(self):
        kwargs = dict()
        kwargs['Y:signal'] = self.paramValue('Y:signal', datatype=(str, unicode))
        kwargs['X:datetime'] = self.paramValue('X:datetime', datatype=(str, unicode))
        kwargs['tz correct'] = self.paramValue('tz correct', datatype=(int, float))
        kwargs['color'] = self.p['color']
        kwargs['width'] = self.p['Display Line', 'Linewidth']
        kwargs['style'] = self.p['Display Line', 'Style'] if self.p['Display Line'] else QtCore.Qt.NoPen
        kwargs['symbol'] = self.p['Display Data Points', 'Symbol'] if self.p['Display Data Points'] else None
        kwargs['symbolSize'] = self.p['Display Data Points', 'Size']

        return kwargs
