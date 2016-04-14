#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph import BusyCursor

from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.TimeLag import timelag_erskine1991_method
from lib.functions.general import isNumpyDatetime


class timeLagNode(NodeWithCtrlWidget):
    """Calculate Timelag comparing given river and groundwater hydrogrpahs"""
    nodeName = "Time Lag"
    uiTemplate = [
            {'name': 'river', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Column name with RIVER hydrograph data\nin `df_w` dataframe'},
            {'name': 'river_dtime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects\nin `df_w` dataframe'},
            {'name': 'gw', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Column name with GROUNDWATER hydrograph data\nin `df_gw` dataframe'},
            {'name': 'gw_dtime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects\nin `df_gw` dataframe'},
            {'name': 'method', 'type': 'list', 'value': '1) Erskine 1991', 'default': '1) Erskine 1991', 'values': ['1) Erskine 1991'], 'tip': 'Method to calculate TimeLag. Read docs'},
            
            {'title': 'Tidal Efficiency Parameters', 'name': 'E_grp', 'type': 'group', 'tip': '', 'expanded': True, 'children': [
                {'title': 'Tidal Efficiency', 'name': 'E', 'type': 'float', 'value': None, 'limits': (0, 1), 'step': 0.1, 'tip': 'Tidal Efficiency (dimensionless)'},
                {'title': 'Set `E` Manually', 'name': 'manual_E', 'type': 'bool', 'value': False, 'tip': 'Use `E` value received in terminal or set manually'}
                ]},
            {'title': 'Time Lag Parameters', 'name': 'tlag_grp', 'type': 'group', 'tip': '', 'expanded': True, 'children': [
                {'name': 't1', 'type': 'int', 'value': 0, 'default': 0, 'limits': (0, int(10e3)), 'tip': 'First value for timelag-iteration tuple. In minutes. Read docs'},
                {'name': 't2', 'type': 'int', 'value': 60, 'default': 60, 'limits': (0, int(10e3)), 'tip': 'Last value for timelag-iteration tuple. In minutes. Read docs'},
                {'name': 't_step', 'type': 'int', 'value': 1, 'default': 1, 'limits': (1, int(10e3)), 'tip': 'Step value for timelag-iteration tuple. In minutes. Read docs'},
                {'name': 'tlag = ', 'type': 'str', 'readonly': True, 'value': None}
                ]}
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
        self.CW().param('tlag_grp', 'tlag = ').setValue('?')

        colname = [col for col in df_gw.columns if not isNumpyDatetime(df_gw[col].dtype)]
        self.CW().param('gw').setLimits(colname)
        colname = [col for col in df_gw.columns if isNumpyDatetime(df_gw[col].dtype)]
        self.CW().param('gw_dtime').setLimits(colname)
        
        colname = [col for col in df_w.columns if not isNumpyDatetime(df_w[col].dtype)]
        self.CW().param('river').setLimits(colname)
        colname = [col for col in df_w.columns if isNumpyDatetime(df_w[col].dtype)]
        self.CW().param('river_dtime').setLimits(colname)

        if not self.CW().param('E_grp', 'manual_E').value():
            self.CW().disconnect_valueChanged2upd(self.CW().param('E_grp', 'E'))
            self.CW().param('E_grp', 'E').setValue(E)  # maybe this will provoke process onceagain.
            self.CW().connect_valueChanged2upd(self.CW().param('E_grp', 'E'))
        
        kwargs = self.CW().prepareInputArguments()
        E = kwargs['E']
        # and i would have to block the signals here...
        with BusyCursor():
            if kwargs['method'] == '1) Erskine 1991':
                tlag = timelag_erskine1991_method(df_gw, kwargs['gw'], kwargs['gw_dtime'],
                                    df_w, kwargs['river'], kwargs['river_dtime'],
                                    E, tlag_tuple=(kwargs['t1'], kwargs['t2'], kwargs['t_step']))
            else:
                raise Exception('Method <%s> not yet implemented' % kwargs['method'])
        
            self.CW().param('tlag_grp', 'tlag = ').setValue(str(tlag))
        return {'tlag': tlag}


class timeLagNodeCtrlWidget(NodeCtrlWidget):
    
    def __init__(self, **kwargs):
        super(timeLagNodeCtrlWidget, self).__init__(update_on_statechange=True, **kwargs)
        self.disconnect_valueChanged2upd(self.param('tlag_grp', 'tlag = '))
        #self.disconnect_valueChanged2upd(self.param('E_grp', 'manual_E'))
        #self.param('E_grp', 'manual_E').sigValueChanged.connect(self.toggle_manualE)

    def toggle_manualE(self):
        if self.param('E_grp', 'manual_E').value() is True:
            self.param('E_grp', 'E').setOpts({'enabled': False})
        else:
            self.param('E_grp', 'E').setOpts({'enabled': True})
            #self.param('E_grp', 'E').setWritable(False)


    def prepareInputArguments(self):
        kwargs = dict()
        for param in self.params(ignore_groups=True):
            kwargs[param.name()] = self.p.evaluateValue(param.value())
        return kwargs
