#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph.flowchart.Node import Node
from pyqtgraph import functions as fn


class NodeWithCtrlWidget(Node):
    """ This class simply reduces 3 methods from my custom Nodes
        and saves around 30 lines :)
    """
    def __init__(self, name, color=(200, 200, 200, 150), **kwargs):
        self._parent = kwargs.get('parent', None)
        if 'parent' in kwargs.keys():
            kwargs.pop('parent')
        super(NodeWithCtrlWidget, self).__init__(name, **kwargs)
        self._ctrlWidget = None
        self.graphicsItem().setBrush(fn.mkBrush(color))

    def ctrlWidget(self):
        return self._ctrlWidget

    def saveState(self):
        """overwriting standard Node method to extend it with saving ctrlWidget state"""
        state = Node.saveState(self)
        # saving additionally state of the control widget
        state['crtlWidget'] = self._ctrlWidget.saveState()
        return state
        
    def restoreState(self, state, update=False):
        """overwriting standard Node method to extend it with restoring ctrlWidget state"""
        Node.restoreState(self, state)
        # additionally restore state of the control widget
        self._ctrlWidget.restoreState(state['crtlWidget'])
        if update:
            self.update()
