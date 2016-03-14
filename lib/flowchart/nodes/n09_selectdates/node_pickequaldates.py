#!/usr/bin python
# -*- coding: utf-8 -*-
import gc
from pyqtgraph import BusyCursor

from lib.functions.general import isNumpyDatetime
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget


class pickEqualDatesNode(NodeWithCtrlWidget):
    """Select values in dataframe based on passed dates from another dataframe"""
    nodeName = "Select Date-Rows"
    uiTemplate = [
            {'name': 'datetime <pattern>', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects.\nBy default is `None`, meaning that datetime objects are\nlocated within `pd.DataFrame.index`. If not `None` - pass the\ncolumn-name of dataframe where datetime objects are located.'},
            {'name': 'datetime <pickFrom>', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects.\nBy default is `None`, meaning that datetime objects are\nlocated within `pd.DataFrame.index`. If not `None` - pass the\ncolumn-name of dataframe where datetime objects are located.'},
        ]

    def __init__(self, name, parent=None):
        super(pickEqualDatesNode, self).__init__(name, parent=parent, terminals={'pattern': {'io': 'in'}, 'pickFrom': {'io': 'in'}, 'Out': {'io': 'out'}}, color=(250, 250, 150, 150))

    def _createCtrlWidget(self, **kwargs):
        return pickEqualDatesNodeCtrlWidget(**kwargs)

    def process(self, pattern, pickFrom):
        gc.collect()
        with BusyCursor():
            df1 = pickFrom
            df2 = pattern

            colname = [col for col in df1.columns if isNumpyDatetime(df1[col].dtype)]
            self._ctrlWidget.param('datetime <pickFrom>').setLimits(colname)
            colname = [col for col in df2.columns if isNumpyDatetime(df2[col].dtype)]
            self._ctrlWidget.param('datetime <pattern>').setLimits(colname)
            
            kwargs = self.ctrlWidget().prepareInputArguments()
            
            if kwargs['datetime <pattern>'] is None and kwargs['datetime <pickFrom>'] is None:
                selector = df1.index.isin(df2.index)
            elif kwargs['datetime <pattern>'] is not None and kwargs['datetime <pickFrom>'] is None:
                selector = df1[kwargs['datetime <pickFrom>']].isin(df2.index)
            elif kwargs['datetime <pickFrom>'] is None and kwargs['datetime <pickFrom>'] is not None:
                selector = df1.index.isin(df2[kwargs['datetime <pattern>']])
            elif kwargs['datetime <pattern>'] is not None and kwargs['datetime <pickFrom>'] is not None:
                selector = df1[kwargs['datetime <pickFrom>']].isin(df2[kwargs['datetime <pattern>']])
            selectedDf = df1[selector]
        return {'Out': selectedDf}


class pickEqualDatesNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(pickEqualDatesNodeCtrlWidget, self).__init__(update_on_statechange=False, **kwargs)

    def prepareInputArguments(self):
        kwargs = dict()
        kwargs['datetime <pickFrom>'] = self.param('datetime <pickFrom>').value()
        kwargs['datetime <pattern>']  = self.param('datetime <pattern>').value()
        return kwargs
