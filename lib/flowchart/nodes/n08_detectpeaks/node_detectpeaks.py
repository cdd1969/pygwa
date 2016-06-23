#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph import BusyCursor

from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.general import isNumpyDatetime, isNumpyNumeric
from lib.functions.detectpeaks import detectPeaks_ts


class detectPeaksTSNode(NodeWithCtrlWidget):
    """Detect peaks (minima/maxima) from passed TimeSeries, check period"""
    nodeName = "Detect Peaks"
    uiTemplate = [
        {'title': 'data', 'name': 'column', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Column name with hydrograph data'},
        {'name': 'datetime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects.'},
        {'name': 'Peak Detection Params', 'type': 'group', 'children': [
            {'name': 'order', 'type': 'int', 'value': 100, 'default': 100, 'limits': (0, int(10e6)), 'tip': 'How many points on each side to use for the comparison'},
            {'name': 'mode', 'type': 'list', 'values': ['clip', 'wrap'], 'value': 'clip', 'default': 'clip', 'tip': 'How the edges of the vector are treated. ‘wrap’ (wrap around)\nor ‘clip’ (treat overflow as the same as the last (or first) element)'},
            {'name': 'removeRegions', 'type': 'bool', 'value': True, 'readonly': True, 'default': True, 'visible': False, 'tip': "remove possible multiple peaks that go one-by-one"}
        ]},
        {'title': 'Plausibility Check Params', 'name': 'Period Check Params', 'type': 'group', 'children': [
            {'name': 'T', 'type': 'str', 'value': 12.42, 'default': None, 'tip': 'Awaited period of the signal in hours. If `None`, will calculate\nthe Period `T` as the mean of difference between peaks, multiplied\nby two (i.e. T = peaks["time"].diff().mean()*2)'},
            {'name': 'hMargin', 'type': 'float', 'value': 1.5, 'default': 1.5, 'limits': (0., 100.), 'suffix': ' hours', 'tip': 'Number of hours, safety margin when comparing period length.\nSee formula below:\nT/2 - hMargin < T_i/2 < T/2 + hMargin'},
            {'name': 'Warnings', 'type': 'str', 'value': '?', 'default': '?', 'tip': 'Number of period-check warnings detected after detecting peaks.\nWarnings are raised where period condition is not met.\tHit `Plot` button to visualize errors', 'readonly': True},
        ]},
        {'name': 'Plot', 'type': 'action'}]

    def __init__(self, name, parent=None):
        super(detectPeaksTSNode, self).__init__(name, parent=parent, terminals={'In': {'io': 'in'}, 'peaks': {'io': 'out'}}, color=(250, 250, 150, 150))
        self._plotRequired = False

    def _createCtrlWidget(self, **kwargs):
        return detectPeaksTSNodeCtrlWidget(**kwargs)
        
    def process(self, In):
        df = In

        self._ctrlWidget.param('Period Check Params', 'Warnings').setValue('?')
        colname = [col for col in df.columns if isNumpyNumeric(df[col].dtype)]
        self._ctrlWidget.param('column').setLimits(colname)
        colname = [col for col in df.columns if isNumpyDatetime(df[col].dtype)]
        self._ctrlWidget.param('datetime').setLimits(colname)

        kwargs = self._ctrlWidget.prepareInputArguments()

        with BusyCursor():
            peaks = detectPeaks_ts(df, kwargs.pop('column'), plot=self._plotRequired, **kwargs)
            self._ctrlWidget.param('Period Check Params', 'Warnings').setValue(str(len(peaks[peaks['check'] == False])))
            
        return {'peaks': peaks}

    def plot(self):
        self._plotRequired = True
        self.update()
        self._plotRequired = False


class detectPeaksTSNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(detectPeaksTSNodeCtrlWidget, self).__init__(update_on_statechange=True, **kwargs)

        self.disconnect_valueChanged2upd(self.param('Period Check Params', 'Warnings'))
        self.param('Plot').sigActivated.connect(self._parent.plot)


    def prepareInputArguments(self):
        kwargs = dict()
        kwargs['column']    = self.param('column').value()
        kwargs['datetime']  = self.param('datetime').value()
        kwargs['T']         = self.paramValue('Period Check Params', 'T', datatype=(float, int, type(None)))
        kwargs['hMargin']   = self.param('Period Check Params', 'hMargin').value()
        kwargs['mode']      = self.param('Peak Detection Params', 'mode').value()
        kwargs['order']     = self.param('Peak Detection Params', 'order').value()
        kwargs['removeRegions'] = self.param('Peak Detection Params', 'removeRegions').value()
        return kwargs