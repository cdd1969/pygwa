#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtGui
from pyqtgraph import BusyCursor
import numpy as np
import pandas as pd

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
                 'md_peaks': {'io': 'in'},
                 'E_cyclic': {'io': 'out'},
                 'E': {'io': 'out'}}
        super(tidalEfficiencyNode, self).__init__(name, parent=parent, terminals=terms, color=(250, 250, 150, 150))
    
    def _createCtrlWidget(self, **kwargs):
        return tidalEfficiencyNodeCtrlWidget(**kwargs)

    def p(self):
        return self.CW().p

    def process(self, df, md_peaks):
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
                E_c = None

            elif kwargs['method'] == '2) Cyclic amplitude' or kwargs['method'] == '3) Cyclic STD':
                if md_peaks is None:
                    msg = 'To use method `{0}` please provide "matched-peaks" data in terminal `md_peaks` (a valid data-set can be created with node `Match Peaks`)'.format(kwargs['method'])
                    QtGui.QMessageBox.warning(None, "Node: {0}".format(self.nodeName), msg)
                    raise ValueError(msg)
                self.CW().disconnect_valueChanged2upd(self.CW().param('gw'))
                self.CW().param('gw').setWritable(False)
                self.CW().param('gw').setLimits(['see matched peaks'])
                self.CW().connect_valueChanged2upd(self.CW().param('gw'))
                
                mPeaks_slice = md_peaks.loc[~md_peaks['md_N'].isin([np.nan, None])]  # select only valid cycles

                if kwargs['method'] == '2) Cyclic amplitude':
                    E, E_cyclic = tidalEfficiency_method2(mPeaks_slice['tidal_range'], mPeaks_slice['md_tidal_range'])

                elif kwargs['method'] == '3) Cyclic STD':
                    with BusyCursor():
                        river_name  = mPeaks_slice['name'][0]
                        well_name   = mPeaks_slice['md_name'][0]
                        E, E_cyclic = tidalEfficiency_method3(df, river_name, well_name, kwargs['datetime'],
                            mPeaks_slice['time_min'], mPeaks_slice['time_max'],
                            mPeaks_slice['md_time_min'], mPeaks_slice['md_time_max'])

                # now do nice output table
                E_c = pd.DataFrame({'N': mPeaks_slice['N'],
                                    'md_N': mPeaks_slice['md_N'],
                                    'E_cyclic': E_cyclic,
                                    })
            else:
                raise Exception('Method <%s> is not yet implemented' % kwargs['method'])
        
            self.CW().param('E = ').setValue('{0:.4f}'.format(E))
        return {'E': E, 'E_cyclic': E_c}





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
