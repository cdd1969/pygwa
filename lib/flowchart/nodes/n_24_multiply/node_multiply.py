#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import division
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.general import isNumpyNumeric


class multiplyNode(NodeWithCtrlWidget):
    """Multiply all values in A-column `a` with a constant `c`. Multiply itemwise A-column `a` with B-column `b`"""
    nodeName = "Multiply"
    uiTemplate = [
            {'title': 'Equation', 'name': 'eq', 'type': 'str', 'value': 'a = a * b * c', 'readonly': True},
            {'title': 'a', 'name': 'a', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Name of the column in A-terminal that will be mutiplied'},
            {'title': 'b', 'name': 'b', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Name of the column in B-terminal'},
            {'title': 'c', 'name': 'c', 'type': 'float', 'value': 1., 'default': 1.},
        ]

    def __init__(self, name, parent=None):
        terms = {'A': {'io': 'in'}, 'B': {'io': 'in'}, 'Out': {'io': 'out'}}
        super(multiplyNode, self).__init__(name, parent=parent, terminals=terms, color=(255, 170, 255, 150))
        self.df = None

    
    def _createCtrlWidget(self, **kwargs):
        return multiplyNodeCtrlWidget(**kwargs)


    def process(self, A, B):
        if A is None:
            del self.df
            self.df = None
            return {'Out': self.df}
        else:
            self.CW().disconnect_valueChanged2upd(self.CW().param('a'))
            cols_A = [col for col in A.columns if isNumpyNumeric(A[col].dtype)]
            self.CW().param('a').setLimits(cols_A)
            self.CW().connect_valueChanged2upd(self.CW().param('a'))

        if B is not None:
            if len(A) != len(B):
                raise ValueError('Number of rows in both DataFrames must be equal. A has {0} rows, B has {1} rows'.format(len(A), len(B)))

            self.CW().disconnect_valueChanged2upd(self.CW().param('b'))
            cols_B = [None]+[col for col in B.columns if isNumpyNumeric(B[col].dtype)]
            self.CW().param('b').setLimits(cols_B)
            self.CW().connect_valueChanged2upd(self.CW().param('b'))

            


        kwargs = self.CW().prepareInputArguments()
        # ------------------------------------------------------
        del self.df
        self.df = A.copy()  #maybe need to use deepcopy
        
        # actually do add operation
        if kwargs['b'] is None:
            self.df[kwargs['a']] *= kwargs['c']
        else:
            self.df[kwargs['a']] = self.df[kwargs['a']] * B[kwargs['b']] * kwargs['c']

        return {'Out': self.df}


class multiplyNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(multiplyNodeCtrlWidget, self).__init__(**kwargs)
    
    def prepareInputArguments(self):
        kwargs = dict()
        kwargs['a']  = self.p['a']
        kwargs['b']  = self.p['b']
        kwargs['c']  = self.p['c']
        
        return kwargs
