#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import division
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget

import numpy as np
from pandas import DataFrame, Series


class dropnaNode(NodeWithCtrlWidget):
    """Remove all rows from the table, in which at least one NaN value is found"""
    nodeName = "Drop NaNs"

    def __init__(self, name, parent=None):
        terms = {'In': {'io': 'in'}, 'Out': {'io': 'out'}}
        super(dropnaNode, self).__init__(name, parent=parent, terminals=terms, color=(255, 170, 255, 150))
        self.df = None

    def process(self, In):
        if In is None:
            return {'Out': None}
        
        elif isinstance(In, np.ndarray) :
            return {'Out': np.copy(In[np.logical_not(np.isnan(In))])}
        
        elif isinstance(In, (DataFrame, Series)) :
            return {'Out': In.dropna()}
        
        elif isinstance(In, (list, tuple)) :
            return {'Out': [value for value in In if not np.isnan(value)]}

        else:
            raise TypeError('Unsupported type received in terminal `In`: {0}'.format(type(In)))

