#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph import BusyCursor
from pyqtgraph.Qt import QtGui
import numpy as np

from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.general import isNumpyDatetime, isNumpyNumeric
from lib.functions.detectpeaks import full_peak_detection_routine, prepare_order, prepare_datetime


class detectPeaksTSNode(NodeWithCtrlWidget):
    """Detect peaks (minima/maxima) from passed TimeSeries, check period"""
    nodeName = "Detect Peaks"
    uiTemplate = [
        {'title': 'data', 'name': 'column', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Column name with hydrograph data'},
        {'name': 'datetime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects.'},
        {'name': 'Peak Detection Params', 'type': 'group', 'children': [
            {'name': 'T', 'type': 'float', 'value': 12.42, 'default': 12.42, 'suffix': ' hours', 'tip': 'Awaited period of the signal in hours.'},
            {'title': 'dt', 'name': 'hMargin', 'type': 'float', 'value': 1.5, 'default': 1.5, 'limits': (0., 100.), 'suffix': ' hours', 'tip': 'Number of hours, safety margin when comparing period length.\nSee formula below:\nT/2 - dt < T_i/2 < T/2 + dt'},
            {'name': 'order', 'type': 'str', 'value': '?', 'readonly': True, 'tip': 'How many points on each side to use for the comparison'},
            {'name': 'mode', 'type': 'list', 'values': ['clip', 'wrap'], 'value': 'clip', 'default': 'clip', 'tip': 'How the edges of the vector are treated. ‘wrap’ (wrap around)\nor ‘clip’ (treat overflow as the same as the last (or first) element)'},
            {'name': 'removeRegions', 'type': 'bool', 'value': True, 'readonly': True, 'default': True, 'visible': False, 'tip': "remove possible multiple peaks that go one-by-one"}
        ]},
        {'title': 'Ignore peaks', 'name': 'ignore', 'type': 'bool', 'value': True, 'default': True, 'tip': 'Checkbox to ignore peaks that are mentioned in parameter `Peak IDs', 'children': [
            {'title': 'Peak IDs', 'name': 'peaks2ignore', 'type': 'str', 'value': '', 'default': '', 'tip': 'IDs of the peaks that will be ignored. IDs can be found in table in terminal `raw`. \nInteger or a comma-separated integer list.\n Example:\n12\n0, 12, 1153'},
        ]},
        
        {'title': 'Plausibility Check Params', 'name': 'check_grp', 'type': 'group', 'children': [
            {'title': 'Neighbour MIN peaks', 'name': 'MIN_grp', 'type': 'group', 'children': [
                {'title': 'Valid Period\n(lower border)', 'name': 'range1', 'type': 'float', 'value': 10.0, 'default': 10., 'suffix': ' hours', 'tip': 'Lower border of the valid time-distance between two neigbour MIN peaks'},
                {'title': 'Valid Period\n(upper border)', 'name': 'range2', 'type': 'float', 'value': 15.0, 'default': 15., 'suffix': ' hours', 'tip': 'Upper border of the valid time-distance between two neigbour MIN peaks'},
                {'title': 'Warnings (MIN)', 'name': 'warn', 'type': 'str', 'value': '?', 'default': '?', 'readonly': True}
            ]},
            {'title': 'Neighbour MAX peaks', 'name': 'MAX_grp', 'type': 'group', 'children': [
                {'title': 'Valid Period\n(lower border)', 'name': 'range1', 'type': 'float', 'value': 10.0, 'default': 10., 'suffix': ' hours', 'tip': 'Lower border of the valid time-distance between two neigbour MAX peaks'},
                {'title': 'Valid Period\n(upper border)', 'name': 'range2', 'type': 'float', 'value': 15.0, 'default': 15., 'suffix': ' hours', 'tip': 'Upper border of the valid time-distance between two neigbour MAX peaks'},
                {'title': 'Warnings (MAX)', 'name': 'warn', 'type': 'str', 'value': '?', 'default': '?', 'readonly': True}
            ]},
            {'title': 'Neighbour ALL peaks', 'name': 'ALL_grp', 'type': 'group', 'children': [
                {'title': 'Valid Period\n(lower border)', 'name': 'range1', 'type': 'float', 'value': 4.0, 'default': 4., 'suffix': ' hours', 'tip': 'Lower border of the valid time-distance between two neigbour peaks (MIN or MAX)'},
                {'title': 'Valid Period\n(upper border)', 'name': 'range2', 'type': 'float', 'value': 9.0, 'default': 9., 'suffix': ' hours', 'tip': 'Upper border of the valid time-distance between two neigbour peaks (MIN or MAX)'},
                {'title': 'Warnings (ALL)', 'name': 'warn', 'type': 'str', 'value': '?', 'default': '?', 'readonly': True}
            ]},
            { 'title': 'Warnings (Total)', 'name': 'warn_sum', 'type': 'str', 'value': '?', 'default': '?', 'readonly': True}
        ]},
        {'name': 'Plot', 'type': 'action'}]

    def __init__(self, name, parent=None):
        super(detectPeaksTSNode, self).__init__(name, parent=parent, terminals={'In': {'io': 'in'}, 'raw': {'io': 'out'}, 'peaks': {'io': 'out'}}, color=(250, 250, 150, 150))
        self._plotRequired = False

    def _createCtrlWidget(self, **kwargs):
        return detectPeaksTSNodeCtrlWidget(**kwargs)
        
    def process(self, In):
        df = In

        self.CW().param('check_grp', 'MIN_grp', 'warn').setValue('?')
        self.CW().param('check_grp', 'MAX_grp', 'warn').setValue('?')
        self.CW().param('check_grp', 'ALL_grp', 'warn').setValue('?')
        self.CW().param('check_grp', 'warn_sum').setValue('?')
        self.CW().param('Peak Detection Params', 'order').setValue('?')
        if df is None:
            return {'raw': None, 'peaks': None}
        colname = [col for col in df.columns if isNumpyNumeric(df[col].dtype)]
        self.CW().param('column').setLimits(colname)
        colname = [col for col in df.columns if isNumpyDatetime(df[col].dtype)]
        self.CW().param('datetime').setLimits(colname)

        kwargs = self.CW().prepareInputArguments()
        kwargs['split'] = True

        with BusyCursor():
            kwargs['order'] = prepare_order(kwargs['T'], kwargs['hMargin'], prepare_datetime(df, datetime=kwargs['datetime']))
            self.CW().param('Peak Detection Params', 'order').setValue(str(kwargs['order']))


            #peaks = detectPeaks_ts(df, kwargs.pop('column'), plot=self._plotRequired, **kwargs)
            extra, raw, peaks = full_peak_detection_routine(df, col=kwargs.pop('column'), date_col=kwargs.pop('datetime'),
                    IDs2mask=kwargs.pop('IDs2mask'), valid_range=kwargs.pop('valid_range'),
                    plot=self._plotRequired,
                    **kwargs)

            n_warn_min = len(extra['warnings']['MIN'])
            n_warn_max = len(extra['warnings']['MAX'])
            n_warn_all = len(extra['warnings']['ALL'])
            self.CW().param('check_grp', 'MIN_grp', 'warn').setValue(n_warn_min)
            self.CW().param('check_grp', 'MAX_grp', 'warn').setValue(n_warn_max)
            self.CW().param('check_grp', 'ALL_grp', 'warn').setValue(n_warn_all)
            self.CW().param('check_grp', 'warn_sum').setValue(n_warn_min + n_warn_max + n_warn_all)

            
        return {'raw': raw, 'peaks': peaks}

    def plot(self):
        self._plotRequired = True
        self._plotRequired = self.check_n_warnings()
        self.update()
        self._plotRequired = False

    def check_n_warnings(self):
        n = self.CW().param('check_grp', 'warn_sum').value()
        if n == '?':
            return True
        if int(n) > 100:
            reply = QtGui.QMessageBox.question(None, 'Too many Warnings!',
                "You are going to plot {0} peak-warnings!\nThis will be slow and not informative!\n\nDo you really want to create the plot?".format(n),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

            if reply == QtGui.QMessageBox.No:
                return False
            elif reply == QtGui.QMessageBox.Yes:
                return True
        else:
            return True


class detectPeaksTSNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(detectPeaksTSNodeCtrlWidget, self).__init__(update_on_statechange=True, **kwargs)


        self.disconnect_valueChanged2upd(self.param('Peak Detection Params', 'order'))
        self.disconnect_valueChanged2upd(self.param('check_grp', 'MIN_grp', 'warn'))
        self.disconnect_valueChanged2upd(self.param('check_grp', 'MAX_grp', 'warn'))
        self.disconnect_valueChanged2upd(self.param('check_grp', 'ALL_grp', 'warn'))
        self.disconnect_valueChanged2upd(self.param('check_grp', 'warn_sum'))
        
        self.param('Plot').sigActivated.connect(self._parent.plot)


    def prepareInputArguments(self):
        kwargs = dict()
        kwargs['column']    = self.param('column').value()
        kwargs['datetime']  = self.param('datetime').value()
        kwargs['T']         = self.param('Peak Detection Params', 'T').value()
        kwargs['hMargin']   = self.param('Peak Detection Params', 'hMargin').value()
        kwargs['mode']      = self.param('Peak Detection Params', 'mode').value()
        kwargs['IDs2mask']  = [int(val) for val in self.param('ignore', 'peaks2ignore').value().split(',')] if (self.param('ignore').value() is True and self.param('ignore', 'peaks2ignore').value() != '') else []
        kwargs['removeRegions'] = self.param('Peak Detection Params', 'removeRegions').value()
        kwargs['valid_range']   = {
                                'MIN': [np.timedelta64(int(self.param('check_grp', 'MIN_grp', 'range1').value()*3600), 's'),
                                        np.timedelta64(int(self.param('check_grp', 'MIN_grp', 'range2').value()*3600), 's')],
                                'MAX': [np.timedelta64(int(self.param('check_grp', 'MAX_grp', 'range1').value()*3600), 's'),
                                        np.timedelta64(int(self.param('check_grp', 'MAX_grp', 'range2').value()*3600), 's')],
                                'ALL': [np.timedelta64(int(self.param('check_grp', 'ALL_grp', 'range1').value()*3600), 's'),
                                        np.timedelta64(int(self.param('check_grp', 'ALL_grp', 'range2').value()*3600), 's')]
        }

        
        return kwargs
