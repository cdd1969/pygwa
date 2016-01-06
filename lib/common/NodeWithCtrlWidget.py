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
        """overriding stadart Node method to extend it with saving ctrlWidget state"""
        state = Node.saveState(self)
        # sacing additionaly state of the control widget
        state['crtlWidget'] = self.ctrlWidget().saveState()
        return state
        
    def restoreState(self, state, update=False):
        """overriding stadart Node method to extend it with restoring ctrlWidget state"""
        Node.restoreState(self, state)
        # additionally restore state of the control widget
        self.ctrlWidget().restoreState(state['crtlWidget'])
        if update:
            self.update()  # we do not call update() since we want to process only on LoadButton clicked or on_other_action
