#!/usr/bin python
# -*- coding: utf-8 -*-

import os, sys
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.flowchart.Node import Node


class df2recArrayNode(Node):
    """Convert pandas.DataFrame to record array"""
    nodeName = "df2recArray"


    def __init__(self, name, parent=None):
        super(df2recArrayNode, self).__init__(name, terminals={'In': {'io': 'in'}, 'Out': {'io': 'out'}})
        self._ctrlWidget = QtGui.QWidget()

        
    def process(self, In):
        """ In - should be a pandas dataframe"""
        return{'Out': In.unpack().to_records()}

    def ctrlWidget(self):
        return self._ctrlWidget
