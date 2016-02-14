#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph.flowchart.Node import Node
from pyqtgraph import functions as fn


class pipeNode(Node):
    """Transmits the data further without processing !!!"""
    nodeName = "pipe"


    def __init__(self, name, parent=None):
        super(pipeNode, self).__init__(name, terminals={'In': {'io': 'in'}, 'Out': {'io': 'out'}})
        self.parent = parent
        color = (95, 66, 94, 100)
        self.graphicsItem().setBrush(fn.mkBrush(color))
       
    def process(self, In):
        return {'Out': In}
