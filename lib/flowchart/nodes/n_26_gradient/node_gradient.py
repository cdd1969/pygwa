#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import division

from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
import numpy as np
import pandas as pd
from lib.functions.general import isNumpyDatetime, isNumpyNumeric
from lib.functions.devlin2003 import devlin2003pandas



class gradientNode(NodeWithCtrlWidget):
    """Estimate hydraulic gradient using head data of multiple wells (method of Devlin 2003) for a given timestep"""
    nodeName = "Gradient"
    uiTemplate = [
            {'title': 'Well X/Y coordinates', 'name': 'coords_grp', 'type': 'group', 'children': [
                {'name': 'x', 'type': 'list', 'value': None, 'values': [None], 'tip': 'Name of the column in <coord> dataframe with x-coordinates'},
                {'name': 'y', 'type': 'list', 'value': None, 'values': [None], 'tip': 'Name of the column in <coord> dataframe with y-coordinates'},

            ]},
            {'name': 'Datetime', 'type': 'list', 'value': None, 'values': [None], 'tip': 'Name of the column in <data> dataframe with datetime'},
            {'title': 'Timestep', 'name': 't', 'type': 'str', 'value': ''},
            
            {'title': 'Gradient', 'name': 'grad', 'type': 'float', 'value': None, 'readonly': True},
            {'title': 'Direction', 'name': 'angle', 'type': 'float', 'value': None, 'readonly': True, 'suffix': ' degrees N'}
            ]


    def __init__(self, name, parent=None):
        terms = {'coord': {'io': 'in'},
                 'data': {'io': 'in'},
                 'df': {'io': 'out'},
                 'gradient': {'io': 'out'},
                 'direction': {'io': 'out'}}
        super(gradientNode, self).__init__(name, parent=parent, terminals=terms, color=(250, 250, 150, 150))
        self.data = None
    
    def _createCtrlWidget(self, **kwargs):
        return gradientNodeCtrlWidget(**kwargs)


    def process(self, coord, data):
        if data is not None:
            colname = [col for col in data.columns if isNumpyDatetime(data[col].dtype)]
            self._ctrlWidget.param('Datetime').setLimits(colname)
            self.data = data
        else:
            self.data = None
            return dict(df=None, gradient=None, direction=None)
        
        if coord is not None:
            colname = [col for col in coord.columns if isNumpyNumeric(coord[col].dtype)]
            self._ctrlWidget.param('coords_grp', 'x').setLimits(colname)
            self._ctrlWidget.param('coords_grp', 'y').setLimits(colname)
            self.CW().disconnect_valueChanged2upd(self.CW().param('coords_grp', 'x'))
            self.CW().disconnect_valueChanged2upd(self.CW().param('coords_grp', 'y'))

            self.CW().param('coords_grp', 'x').setValue(colname[0])
            self.CW().param('coords_grp', 'y').setValue(colname[1])
            self.CW().connect_valueChanged2upd(self.CW().param('coords_grp', 'x'))
            self.CW().connect_valueChanged2upd(self.CW().param('coords_grp', 'y'))
        else:
            return dict(df=None, gradient=None, direction=None)


        # now make sure all well specified in `coord` dataframe are found in `data`
        well_names = coord.index.values
        for well_n in well_names:
                if well_n not in data.columns:
                    raise ValueError('Well named `{0}` not found in `data` but is declared in `coords`'.format(well_n))


        kwargs = self.ctrlWidget().prepareInputArguments()

        # select row whith user-specified datetime `timestep`
        row = data.loc[data[kwargs['datetime']] == kwargs['t']]
        if row.empty:
            raise IndexError('Selected timestep `{0}` not found in `data`s column {1}. Select correct one'.format(kwargs['t'], kwargs['datetime']))

        # now prepare dataframe for devlin calculations
        df = coord.copy()
        df['z'] = np.zeros(len(df.index))
        for well_n in well_names:
            df.loc[well_n, 'z'] = float(row[well_n])



        gradient, direction = devlin2003pandas(df, kwargs['x'], kwargs['y'], 'z')
        
        self.CW().param('grad').setValue(gradient)
        self.CW().param('angle').setValue(direction)

        return dict(df=df, gradient=gradient, direction=direction)


class gradientNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(gradientNodeCtrlWidget, self).__init__(**kwargs)
        self.UPDATE_T_DEFAULT = True

        self.disconnect_valueChanged2upd(self.param('grad'))
        self.disconnect_valueChanged2upd(self.param('angle'))
        self.param('Datetime').sigValueChanged.connect(self.update_default_t)

    def update_default_t(self, value):
        df = self.parent().data
        if df is not None:
            t_vals = df[value].values
            t_min = pd.to_datetime(str(min(t_vals)))

            self.disconnect_valueChanged2upd(self.param('t'))
            self.param('t').setValue(t_min.strftime('%Y-%m-%d %H:%M:%S'))
            self.connect_valueChanged2upd(self.param('t'))


    def prepareInputArguments(self):
        kwargs = dict()

        kwargs['datetime'] = self.p['Datetime']
        if self.p['t'] is '':
            self.update_default_t(kwargs['datetime'])
        kwargs['t'] = np.datetime64(self.p['t']+'Z')  # zulu time
        kwargs['x'] = self.p['coords_grp', 'x']
        kwargs['y'] = self.p['coords_grp', 'y']
        return kwargs