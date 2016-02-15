#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph import BusyCursor
import numpy as np

from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.TidalEfficiency import tidalEfficiency_method1, tidalEfficiency_method2, tidalEfficiency_method3
from lib.functions.general import returnPandasDf, isNumpyDatetime, isNumpyNumeric


class tidalEfficiencyNode(NodeWithCtrlWidget):
    """Calculate Tidal Efficiency comparing given river and groundwater hydrogrpahs"""
    nodeName = "tidalEfficiency"
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

    def process(self, df, matched_peaks):
        E = None
        df = returnPandasDf(df)
        matched_peaks = returnPandasDf(matched_peaks)
        self._ctrlWidget.param('E = ').setValue(str(E))
        
        with BusyCursor():
            colname = [col for col in df.columns if isNumpyNumeric(df[col].dtype)]
            self._ctrlWidget.param('river').setLimits(colname)
            self._ctrlWidget.param('gw').setLimits(colname)
            colname = [col for col in df.columns if isNumpyDatetime(df[col].dtype)]
            self._ctrlWidget.param('datetime').setLimits(colname)
            
            kwargs = self.ctrlWidget().prepareInputArguments()
            
            if kwargs['method'] == '1) STD':
                E = tidalEfficiency_method1(df, kwargs['river'], kwargs['gw'])

            elif kwargs['method'] == '2) Cyclic amplitude':
                # select only valid cycles
                df_slice = matched_peaks.loc[~matched_peaks['md_N'].isin([np.nan, None])]
                E, N = tidalEfficiency_method2(df_slice['tidehub'], df_slice['md_tidehub'])
                print( 'Method2: Calculated E with {0} tidal-cycles'.format(N))

            elif kwargs['method'] == '3) Cyclic STD':
                mPeaks_slice = matched_peaks.loc[~matched_peaks['md_N'].isin([np.nan, None])]

                E, N = tidalEfficiency_method3(df,  kwargs['river'], kwargs['gw'], kwargs['datetime'],
                    mPeaks_slice['time_min'], mPeaks_slice['time_max'],
                    mPeaks_slice['md_time_min'], mPeaks_slice['md_time_max'])
                print( 'Method3: Calculated E with {0} tidal-cycles'.format(N))
            else:
                raise Exception('Method <%s> not yet implemented' % kwargs['method'])
        
        self._ctrlWidget.param('E = ').setValue(str(E))
        return {'E': E}



class tidalEfficiencyNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(tidalEfficiencyNodeCtrlWidget, self).__init__(**kwargs)

    def initSignalConnections(self, update_parent=True):
        new_update_parent = {
            'action': 'disconnect',
            'parameters': self.param('E = ')}
        super(tidalEfficiencyNodeCtrlWidget, self).initSignalConnections(new_update_parent)

    def prepareInputArguments(self):
        kwargs = dict()
        for param in self.params(ignore_groups=True):
            kwargs[param.name()] = self.p.evaluateValue(param.value())
        del kwargs['E = ']
        return kwargs
