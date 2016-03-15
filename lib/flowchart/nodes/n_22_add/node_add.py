#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import division
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from lib.functions.general import isNumpyNumeric
SPACE = ' '


class addNode(NodeWithCtrlWidget):
    """Add a constant `c` to all values in A-column `a`. Add itemwise values from a B-column `b` to an A-column `a`"""
    nodeName = "Add"
    uiTemplate = [
            {'title': 'Equation', 'name': 'eq', 'type': 'str', 'value': 'a = a + b + c', 'readonly': True},
            {'title': 'a', 'name': 'a', 'type': 'list', 'value': None, 'values': [], 'tip': 'Name of the column in A-terminal to which data will be added'},
            {'title': 'b', 'name': 'b', 'type': 'list', 'value': None, 'values': [], 'tip': 'Name of the column in B-terminal'},
            {'title': 'c', 'name': 'c', 'type': 'float', 'value': 0., 'default': 0., 'tip': 'Constant to add to all rows in A'},
        ]

    def __init__(self, name, parent=None):
        terms = {'A': {'io': 'in'}, 'B': {'io': 'in'}, 'C': {'io': 'out'}}
        super(addNode, self).__init__(name, parent=parent, terminals=terms, color=(255, 170, 255, 150))
        self.df = None

    
    def _createCtrlWidget(self, **kwargs):
        return addNodeCtrlWidget(**kwargs)


    def process(self, A, B):
        if A is None:
            self.CW().param('a').setLimits([])
            del self.df
            self.df = None
            return {'C': self.df}
        else:
            #self.CW().disconnect_valueChanged2upd(self.CW().param('a'))
            cols_A = [col for col in A.columns if isNumpyNumeric(A[col].dtype)]
            if self.CW().param('a').opts['limits'] != cols_A:
                self.CW().param('a').setLimits(cols_A)
            #self.CW().connect_valueChanged2upd(self.CW().param('a'))

        if B is not None:
            if len(A) != len(B):
                raise ValueError('Number of rows in both DataFrames must be equal. A has {0} rows, B has {1} rows'.format(len(A), len(B)))

            #self.CW().disconnect_valueChanged2upd(self.CW().param('b'))
            cols_B = [SPACE]+[col for col in B.columns if isNumpyNumeric(B[col].dtype)]
            if self.CW().param('b').opts['limits'] != cols_B:
                #print self.CW().param('b'), '>>>', self.CW().param('b').value()
                #print self.CW().param('b'), '>>>', self.CW().param('b').opts['limits']
                cached = self.CW().param('b').value()
                self.CW().param('b').setLimits(cols_B)
                #print self.CW().param('b'), '>>>', self.CW().param('b').value()
                #print self.CW().param('b'), '>>>', self.CW().param('b').opts['limits']
                self.CW().param('b').setValue(cached)
                #print self.CW().param('b'), '>>>', self.CW().param('b').value()
                #print self.CW().param('b'), '>>>', self.CW().param('b').opts['limits']
            
            #self.CW().connect_valueChanged2upd(self.CW().param('b'))
        else:
            self.CW().param('b').setLimits([])




        kwargs = self.CW().prepareInputArguments()
        # ------------------------------------------------------
        del self.df
        self.df = A.copy()  #maybe need to use deepcopy
        
        # actually do add operation
        if kwargs['b'] in [SPACE, None, '']:
            self.df[kwargs['a']] += kwargs['c']
        else:
            self.df[kwargs['a']] = self.df[kwargs['a']] + B[kwargs['b']] + kwargs['c']

        return {'C': self.df}


class addNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(addNodeCtrlWidget, self).__init__(**kwargs)
    
    def prepareInputArguments(self):
        kwargs = dict()
        kwargs['a']  = self.p['a']
        kwargs['b']  = self.p['b']
        kwargs['c']  = self.p['c']
        
        return kwargs
