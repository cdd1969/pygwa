#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import division
import pyqtgraph.parametertree.parameterTypes as pTypes
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget


## this group includes a menu allowing the user to add new parameters into its child list
class ScalableGroup(pTypes.GroupParameter):
    def __init__(self, **opts):
        opts['type'] = 'group'
        opts['addText'] = "Add"
        opts['addList'] = []
        super(ScalableGroup, self).__init__(**opts)
    
    def addNew(self, colName):
        self.addChild(dict(title='Join column:', name="%d" % (len(self.childs)+1), type='str', value=colName, removable=True, readonly=True))


class joinColNode(NodeWithCtrlWidget):
    """Join columns from table B to table A. Returns new table C"""
    nodeName = "Join Columns"
    uiTemplate = [
            ScalableGroup(title='Columns to join from B', name='grp', children=[
                #{'title': 'Add column:', 'name': '0', 'type': 'str', 'value': None, 'removable': True}
                ])
        ]

    def __init__(self, name, parent=None):
        terms = {'A': {'io': 'in'}, 'B': {'io': 'in'}, 'C': {'io': 'out'}}
        super(joinColNode, self).__init__(name, parent=parent, terminals=terms, color=(255, 170, 255, 150))
        self.id_A = None
        self.id_B = None
        self.df = None

    
    def _createCtrlWidget(self, **kwargs):
        return joinColNodeCtrlWidget(**kwargs)


    def process(self, A, B):
        del self.df
        self.df = None
        
        if B is None:
            self.CW().param('grp').setAddList([])
            self.CW().param('grp').clearChildren()
            self.id_B = None
        if A is None:
            self.id_A = None
        
        if A is None or B is None:
            return {'C': self.df}
        
        if len(A) != len(B):
            raise ValueError('Number of rows in both DataFrames must be equal. A has {0} rows, B has {1} rows'.format(len(A), len(B)))

        if self.id_B != id(B):
            self.id_B = id(B)
            self.CW().param('grp').setAddList([col_n for col_n in B.columns])

        kwargs = self.CW().prepareInputArguments()
        # ------------------------------------------------------
        self.df = A.copy()  #maybe need to use deepcopy
        
        for col_name in kwargs['cols']:
            if col_name in self.df.columns:
                continue
            self.df[col_name] = B[col_name]

        return {'C': self.df}


class joinColNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(joinColNodeCtrlWidget, self).__init__(**kwargs)
        self.disconnect_valueChanged2upd(self.param('grp'))
        self.param('grp').sigChildAdded.connect(self._parent.update)
        self.param('grp').sigChildRemoved.connect(self._parent.update)
    
    def prepareInputArguments(self):
        kwargs = dict()
        p = self.param('grp')
        col_list = [child.value() for child in p.children()]
        kwargs['cols']  = col_list
        
        return kwargs

    #def restoreState(self, state, **kwargs):
    #    # for some reason normal state restore eats children > simply add param once again
    #    self.p.clearChildren()
    #    self.p.addChild(ScalableGroup(title='Columns to add from B', name='grp'))
    #    self.disconnect_valueChanged2upd(self.param('grp'))
    #    self.param('grp').sigChildAdded.connect(self._parent.update)
    #    self.param('grp').sigChildRemoved.connect(self._parent.update)
