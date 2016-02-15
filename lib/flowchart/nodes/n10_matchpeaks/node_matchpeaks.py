#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph import BusyCursor

from lib.flowchart.package import Package
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.detectpeaks import match_peaks
from lib.functions.general import returnPandasDf, isNumpyDatetime


class matchPeaksNode(NodeWithCtrlWidget):
    """Match peaks from two DataFrames. Peaks should be detected before"""
    nodeName = "matchpeaks"
    uiTemplate = [
            {'name': 'Match Option', 'type': 'list', 'value': 'Closest Time', 'default': 'Closest Time', 'values': ['Closest Time'], 'tip': 'Match option:\n"Closest Time" - match gw_peaks which have closest datetime to w_peaks'},
            {'name': 'Closest Time', 'type': 'group', 'children': [
                {'name': 'Match Column', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Data will be matched based on this column'},
                {'name': 'side', 'type': 'list', 'values': ['right (>=t)', 'right (>t)', 'left (<=t)', 'left (<t)', 'both'], 'value': 'right (>=t)', 'default': 'right (>=t)', 'tip': 'search direction with respect to `t`.\n"right (>=t)"  - search after or at `t`\n"right (>t)" - search after `t`\n"left (<=t)" - search before or at `t`\n"left (<t)" - search before `t`\n"both"  - search before and after `t` or at `t`'},
                {'name': 'use_window', 'type': 'bool', 'value': False, 'default': False, 'tip': 'Search matching peaks within time-window\n[t-window : t+window]\nEnables `window` float spinbox'},
                {'name': 'window', 'type': 'float', 'value': 0, 'default': 0, 'limits': (0, int(10e6)), 'tip': 'Is read only if `use_window` is checked!\nNumber of hours to determine time-window'},
            ]},
            {'name': 'MATCHED/PEAKS', 'type': 'str', 'value': '?/?', 'readonly': True},
            ]

    def __init__(self, name, parent=None):
        super(matchPeaksNode, self).__init__(name, parent=parent, terminals={'W_peaks': {'io': 'in'}, 'GW_peaks': {'io': 'in'}, 'matched': {'io': 'out'}}, color=(250, 250, 150, 150))
    
    def _createCtrlWidget(self, **kwargs):
        return matchPeaksNodeCtrlWidget(**kwargs)
        
    def process(self, W_peaks, GW_peaks):
        N_md = '?'
        df_w  = returnPandasDf(W_peaks)
        df_gw = returnPandasDf(GW_peaks)

        colname = [col for col in df_w.columns if isNumpyDatetime(df_w[col].dtype)]
        self._ctrlWidget.param('Closest Time', 'Match Column').setLimits(colname)

        kwargs = self._ctrlWidget.prepareInputArguments()
        with BusyCursor():
            mode = kwargs.pop('Match Option')
            if mode == 'Closest Time':
                print kwargs
                matched_peaks = match_peaks(df_w, df_gw, kwargs.pop('Match Column'), **kwargs)
                
            N_md = matched_peaks['md_N'].count()
            
        self._ctrlWidget.param('MATCHED/PEAKS').setValue('{0}/{1}'.format(N_md, len(df_w)))
        return {'matched': Package(matched_peaks)}


class matchPeaksNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(matchPeaksNodeCtrlWidget, self).__init__(**kwargs)

    def initSignalConnections(self, update_parent=True):
        new_update_parent = {
            'action': 'disconnect',
            'parameters': self.param('MATCHED/PEAKS')}
        super(matchPeaksNodeCtrlWidget, self).initSignalConnections(new_update_parent)

    def prepareInputArguments(self):
        kwargs = dict()
        for param in self.params(ignore_groups=True):
            if param.name() != 'MATCHED/PEAKS' :
                kwargs[param.name()] = self.p.evaluateValue(param.value())
        if kwargs['use_window'] is False:
            del kwargs['window']
            del kwargs['use_window']
        return kwargs
