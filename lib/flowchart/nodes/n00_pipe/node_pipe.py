#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph import functions as fn
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget


class pipeNode(NodeWithCtrlWidget):
    """Transmits the data further without processing"""
    nodeName = "Pipe"
    uiTemplate = [
            {'title': 'Close Pipe', 'name': 'closed', 'type': 'bool', 'value': False, 'tip': 'If Checked -- close pipe, and do not transmit data further'}]
    
    def __init__(self, name, parent=None):

        terms = {'In': {'io': 'in'}, 'Out': {'io': 'out'}}
        super(pipeNode, self).__init__(name, parent=parent, terminals=terms, color=(95, 66, 94, 100))
        self.opened_color = (95, 66, 94, 100)
        self.closed_color = (255, 0, 0, 100)

    def _createCtrlWidget(self, **kwargs):
        return pipeNodeCtrlWidget(**kwargs)
    

    def process(self, In):
        kwargs = self.CW().prepareInputArguments()
        if kwargs['closed']:
            self.graphicsItem().setBrush(fn.mkBrush(self.closed_color))
            return {'Out': None}
        else:
            self.graphicsItem().setBrush(fn.mkBrush(self.opened_color))
            return {'Out': In}


class pipeNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(pipeNodeCtrlWidget, self).__init__(update_on_statechange=True, **kwargs)
    
    def prepareInputArguments(self):
        kwargs = dict()
        kwargs['closed'] = self.p['closed']
        return kwargs
