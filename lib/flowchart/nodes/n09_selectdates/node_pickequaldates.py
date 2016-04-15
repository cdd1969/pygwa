#!/usr/bin python
# -*- coding: utf-8 -*-
import gc
from lib.functions.general import isNumpyDatetime
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
import numpy as np
import pandas as pd


class pickEqualDatesNode(NodeWithCtrlWidget):
    """Select values in dataframe based on passed dates from another dataframe"""
    nodeName = "Select Date-Rows"
    uiTemplate = [
            {'name': 'datetime <pattern>', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects.\nBy default is `None`, meaning that datetime objects are\nlocated within `pd.DataFrame.index`. If not `None` - pass the\ncolumn-name of dataframe where datetime objects are located.'},
            {'name': 'datetime <pickFrom>', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects.\nBy default is `None`, meaning that datetime objects are\nlocated within `pd.DataFrame.index`. If not `None` - pass the\ncolumn-name of dataframe where datetime objects are located.'},
            {'title': 'Slice Datetime', 'name': 'slice', 'type': 'bool', 'value': False, 'expanded': True, 'tip': 'Slice table between Start and End datetimes', 'children': [
                {'name': 'Start', 'type': 'str', 'value': 'YYY-MM-DD HH:MM:SS', 'default': 'YYY-MM-DD HH:MM:SS', 'tip': 'Start value of datetime slice. Select entries that are >= `Start`'},
                {'name': 'End',   'type': 'str', 'value': 'YYY-MM-DD HH:MM:SS', 'default': 'YYY-MM-DD HH:MM:SS', 'tip': 'End value of datetime slice. Select entries that are <= `End`'}
                ]}
        ]

    def __init__(self, name, parent=None):
        super(pickEqualDatesNode, self).__init__(name, parent=parent, terminals={'pattern': {'io': 'in'}, 'pickFrom': {'io': 'in'}, 'Out': {'io': 'out'}}, color=(255, 170, 255, 150))
        self._df1_id = None

    def _createCtrlWidget(self, **kwargs):
        return pickEqualDatesNodeCtrlWidget(**kwargs)

    def process(self, pattern, pickFrom):
        df1 = pickFrom
        df2 = pattern

        if df1 is None:
            self.CW().disconnect_valueChanged2upd(self.CW().param('datetime <pickFrom>'))
            self.CW().param('datetime <pickFrom>').setLimits([None])
            self.CW().connect_valueChanged2upd(self.CW().param('datetime <pickFrom>'))
            return
        else:
            self.CW().disconnect_valueChanged2upd(self.CW().param('datetime <pickFrom>'))
            colname = [col for col in df1.columns if isNumpyDatetime(df1[col].dtype)]
            self.CW().param('datetime <pickFrom>').setLimits(colname)
            self.CW().connect_valueChanged2upd(self.CW().param('datetime <pickFrom>'))

        if df2 is None:
            self.CW().disconnect_valueChanged2upd(self.CW().param('datetime <pattern>'))
            self.CW().param('datetime <pattern>').setLimits([None])
            self.CW().connect_valueChanged2upd(self.CW().param('datetime <pattern>'))
        else:
            self.CW().disconnect_valueChanged2upd(self.CW().param('datetime <pattern>'))
            colname = [col for col in df2.columns if isNumpyDatetime(df2[col].dtype)]
            self.CW().param('datetime <pattern>').setLimits(colname)
            self.CW().connect_valueChanged2upd(self.CW().param('datetime <pattern>'))

        
       
        if self._df1_id != id(df1):
            self._df1_id = id(df1)
            
            t_vals = df1[self.CW().p['datetime <pickFrom>']].values
            t_min, t_max = pd.to_datetime(str(min(t_vals))), pd.to_datetime(str(max(t_vals)))

            self.CW().disconnect_valueChanged2upd(self.CW().param('slice', 'Start'))
            self.CW().disconnect_valueChanged2upd(self.CW().param('slice', 'End'))
            self.CW().param('slice', 'Start').setValue(t_min.strftime('%Y-%m-%d %H:%M:%S'))
            self.CW().param('slice', 'Start').setDefault(t_min.strftime('%Y-%m-%d %H:%M:%S'))
            self.CW().param('slice', 'End').setValue(t_max.strftime('%Y-%m-%d %H:%M:%S'))
            self.CW().param('slice', 'End').setDefault(t_max.strftime('%Y-%m-%d %H:%M:%S'))
            if self.CW().p['slice'] is True:
                self.CW().connect_valueChanged2upd(self.CW().param('slice', 'Start'))
                self.CW().connect_valueChanged2upd(self.CW().param('slice', 'End'))
        
        kwargs = self.ctrlWidget().prepareInputArguments()

        # now actually slice
        if kwargs['slice']:
            df = df1.set_index(kwargs['datetime <pickFrom>'])
            start = df.index.searchsorted(kwargs['slice_start'], side='left')
            end   = df.index.searchsorted(kwargs['slice_end'], side='right')
            del df
            df1 = df1[start:end].copy(deep=True)  # warning pointer to new DF!
        

        # now pick dates as in another df
        if kwargs['datetime <pattern>'] is not None and kwargs['datetime <pickFrom>'] is not None:
            selector = df1[kwargs['datetime <pickFrom>']].isin(df2[kwargs['datetime <pattern>']])
            df1 = df1[selector]

        gc.collect()
        return {'Out': df1}


class pickEqualDatesNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(pickEqualDatesNodeCtrlWidget, self).__init__(update_on_statechange=True, **kwargs)

    def prepareInputArguments(self):
        kwargs = dict()
        kwargs['datetime <pickFrom>'] = self.p['datetime <pickFrom>']
        kwargs['datetime <pattern>']  = self.p['datetime <pattern>']
        kwargs['slice']  = self.p['slice']
        if kwargs['slice'] is True:
            kwargs['slice_start'] = np.datetime64(self.p['slice', 'Start'] + 'Z')
            kwargs['slice_end']   = np.datetime64(self.p['slice', 'End'] + 'Z')

        return kwargs
