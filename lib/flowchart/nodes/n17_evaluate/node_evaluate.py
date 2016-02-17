#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph.flowchart.library.Data import EvalNode
from lib.common import syntaxPython

class pumpedEvalNode(EvalNode):
    def __init__(self, name):
        super(pumpedEvalNode, self).__init__(name)
        highlight = syntaxPython.PythonHighlighter(self.text)
