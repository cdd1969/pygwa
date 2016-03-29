#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtGui
from pyqtgraph import BusyCursor
import numpy as np

from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.TidalEfficiency import tidalEfficiency_method1, tidalEfficiency_method2, tidalEfficiency_method3
from lib.functions.general import isNumpyDatetime, isNumpyNumeric


class tidalEfficiencyNode(NodeWithCtrlWidget):
    """Calculate Tidal Efficiency comparing given river and groundwater hydrogrpahs"""
    nodeName = "Tidal Efficiency"
    uiTemplate = [
            {'name': 'river', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Column name with RIVER hydrograph data'},
            {'name': 'gw', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Column name with GROUNDWATER hydrograph data'},
            {'name': 'datetime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects.'},
            {'name': 'method', 'type': 'list', 'value': '1) STD', 'default': '1) STD', 'values': ['1) STD', '2) Cyclic amplitude', '3) Cyclic STD'], 'tip': 'Method to calculate Tidal Efficiency. Read docs'},
            {'name': 'E = ', 'type': 'str', 'readonly': True, 'value': None}
        ]

    def __init__(self, name, parent=None):
        terms = {'df': {'io': 'in'},
                 'matched_peaks': {'io': 'in'},
                 'E': {'io': 'out'}}
        super(tidalEfficiencyNode, self).__init__(name, parent=parent, terminals=terms, color=(250, 250, 150, 150))
    
    def _createCtrlWidget(self, **kwargs):
        return tidalEfficiencyNodeCtrlWidget(**kwargs)

    def p(self):
        return self.CW().p

    def process(self, df, matched_peaks):
        E = None
        self.CW().param('E = ').setValue(str(E))
        self.CW().param('gw').setWritable(True)
        
        if df is not None:
            for name in ['river', 'gw', 'datetime']:
                self.CW().disconnect_valueChanged2upd(self.CW().param(name))
            colname = [col for col in df.columns if isNumpyNumeric(df[col].dtype)]
            self.CW().param('river').setLimits(colname)
            self.CW().param('gw').setLimits(colname)
            colname = [col for col in df.columns if isNumpyDatetime(df[col].dtype)]
            self.CW().param('datetime').setLimits(colname)
            
            for name in ['river', 'gw', 'datetime']:
                self.CW().connect_valueChanged2upd(self.CW().param(name))

            kwargs = self.ctrlWidget().prepareInputArguments()
            
            if kwargs['method'] == '1) STD':
                E = tidalEfficiency_method1(df, kwargs['river'], kwargs['gw'])

            elif kwargs['method'] == '2) Cyclic amplitude':
                if matched_peaks is None:
                    QtGui.QMessageBox.warning(None, "Node: {0}".format(self.nodeName), 'To use method `Cyclic amplitude` please provide data in terminal `matched_peaks` (a valid data-set can be created with node `Match Peaks`)')
                    raise ValueError('To use method `Cyclic amplitude` please provide data in terminal `matched_peaks` (a valid data-set can be created with node `Match Peaks`)')
                self.CW().disconnect_valueChanged2upd(self.CW().param('gw'))
                self.CW().param('gw').setWritable(False)
                self.CW().param('gw').setLimits(['see matched peaks'])
                self.CW().connect_valueChanged2upd(self.CW().param('gw'))
                # select only valid cycles
                df_slice = matched_peaks.loc[~matched_peaks['md_N'].isin([np.nan, None])]
                E, N = tidalEfficiency_method2(df_slice['tidal_range'], df_slice['md_tidal_range'])
                #print( 'Method2: Calculated E with {0} tidal-cycles'.format(N))

            elif kwargs['method'] == '3) Cyclic STD':
                if matched_peaks is None:
                    QtGui.QMessageBox.warning(None, "Node: {0}".format(self.nodeName), 'To use method `Cyclic STD` please provide data in terminal `matched_peaks` (a valid data-set can be created with node `Match Peaks`)')
                    raise ValueError('To use method `Cyclic STD` please provide data in terminal `matched_peaks` (a valid data-set can be created with node `Match Peaks`)')
                self.CW().disconnect_valueChanged2upd(self.CW().param('gw'))
                self.CW().param('gw').setWritable(False)
                self.CW().param('gw').setLimits(['see matched peaks'])
                self.CW().connect_valueChanged2upd(self.CW().param('gw'))
                with BusyCursor():
                    mPeaks_slice = matched_peaks.loc[~matched_peaks['md_N'].isin([np.nan, None])]

                    E, N = tidalEfficiency_method3(df,  kwargs['river'], kwargs['gw'], kwargs['datetime'],
                        mPeaks_slice['time_min'], mPeaks_slice['time_max'],
                        mPeaks_slice['md_time_min'], mPeaks_slice['md_time_max'])
                #print( 'Method3: Calculated E with {0} tidal-cycles'.format(N))
            else:
                raise Exception('Method <%s> not yet implemented' % kwargs['method'])
        
            self.CW().param('E = ').setValue('{0:.4f}'.format(E))
        return {'E': E}





class tidalEfficiencyNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(tidalEfficiencyNodeCtrlWidget, self).__init__(update_on_statechange=True, **kwargs)
        self.disconnect_valueChanged2upd(self.param('E = '))

    def prepareInputArguments(self):
        kwargs = dict()
        for param in self.params(ignore_groups=True):
            kwargs[param.name()] = self.p.evaluateValue(param.value())
        del kwargs['E = ']
        return kwargs
