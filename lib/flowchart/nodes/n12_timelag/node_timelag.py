#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph import BusyCursor

from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.TimeLag import timelag_erskine1991_method
from lib.functions.general import returnPandasDf, isNumpyDatetime


class timeLagNode(NodeWithCtrlWidget):
    """Calculate Timelag comparing given river and groundwater hydrogrpahs"""
    nodeName = "TimeLag"
    uiTemplate = [
            {'name': 'river', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Column name with RIVER hydrograph data\nin `df_w` dataframe'},
            {'name': 'river_dtime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects\nin `df_w` dataframe'},
            {'name': 'gw', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Column name with GROUNDWATER hydrograph data\nin `df_gw` dataframe'},
            {'name': 'gw_dtime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects\nin `df_gw` dataframe'},
            {'name': 'method', 'type': 'list', 'value': '1) Erskine 1991', 'default': '1) Erskine 1991', 'values': ['1) Erskine 1991'], 'tip': 'Method to calculate TimeLag. Read docs'},
            {'name': 'E', 'type': 'float', 'value': None, 'tip': 'tidal efficiency'},
            {'name': 't1', 'type': 'int', 'value': 1, 'default': 1, 'limits': (0, int(10e3)), 'tip': 'First value for timelag-iteration tuple. Read docs'},
            {'name': 't2', 'type': 'int', 'value': 60, 'default': 60, 'limits': (0, int(10e3)), 'tip': 'Last value for timelag-iteration tuple. Read docs'},
            {'name': 't_step', 'type': 'int', 'value': 1, 'default': 1, 'limits': (1, int(10e3)), 'tip': 'Step value for timelag-iteration tuple. Read docs'},
            {'name': 'tlag = ', 'type': 'str', 'readonly': True, 'value': None}
        ]

    def __init__(self, name, parent=None):
        terms = {'df_gw': {'io': 'in'},
                 'df_w': {'io': 'in'},
                 'E': {'io': 'in'},
                 'tlag': {'io': 'out'},
                 }
        super(timeLagNode, self).__init__(name, parent=parent, terminals=terms, color=(250, 250, 150, 150))

    def _createCtrlWidget(self, **kwargs):
        return timeLagNodeCtrlWidget(**kwargs)

    def process(self, df_gw, df_w, E):
        self._ctrlWidget.param('tlag = ').setValue('?')
        
        df_gw = returnPandasDf(df_gw)
        df_w = returnPandasDf(df_w)

        colname = [col for col in df_gw.columns if not isNumpyDatetime(df_gw[col].dtype)]
        self._ctrlWidget.param('gw').setLimits(colname)
        colname = [col for col in df_gw.columns if isNumpyDatetime(df_gw[col].dtype)]
        self._ctrlWidget.param('gw_dtime').setLimits(colname)
        
        colname = [col for col in df_w.columns if not isNumpyDatetime(df_w[col].dtype)]
        self._ctrlWidget.param('river').setLimits(colname)
        colname = [col for col in df_w.columns if isNumpyDatetime(df_w[col].dtype)]
        self._ctrlWidget.param('river_dtime').setLimits(colname)

        kwargs = self.ctrlWidget().prepareInputArguments()
        if E is None:
            E = kwargs['E']
        else:
            self._ctrlWidget.param('E').setValue(E)  # maybe this will provoke process onceagain.
            # and i would have to block the signals here...

        with BusyCursor():
            if kwargs['method'] == '1) Erskine 1991':
                tlag = timelag_erskine1991_method(df_gw, kwargs['gw'], kwargs['gw_dtime'],
                                    df_w, kwargs['river'], kwargs['river_dtime'],
                                    E, tlag_tuple=(kwargs['t1'], kwargs['t2'], kwargs['t_step']))
            else:
                raise Exception('Method <%s> not yet implemented' % kwargs['method'])
        
            self._ctrlWidget.param('tlag = ').setValue(str(tlag))
        return {'tlag': tlag}


class timeLagNodeCtrlWidget(NodeCtrlWidget):
    
    def __init__(self, **kwargs):
        super(timeLagNodeCtrlWidget, self).__init__(**kwargs)

    def initSignalConnections(self, update_parent=True):
        new_update_parent = {
            'action': 'disconnect',
            'parameters': self.param('tlag = ')}
        super(timeLagNodeCtrlWidget, self).initSignalConnections(new_update_parent)

    def prepareInputArguments(self):
        kwargs = dict()
        for param in self.params(ignore_groups=True):
            kwargs[param.name()] = self.p.evaluateValue(param.value())
        return kwargs
