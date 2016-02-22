#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph.flowchart.library.Data import EvalNode
from lib.common import syntaxPython
from pyqtgraph.Qt import QtCore, QtGui


class pumpedEvalNode(EvalNode):
    """Return the output of a string evaluated/executed by the python interpreter.
    The string may be either an expression or a python script, and inputs are accessed as the name of the terminal.
    For expressions, a single value may be evaluated for a single output, or a dict for multiple outputs.
    For a script, the text will be executed as the body of a function."""

    sigUIStateChanged = QtCore.Signal(object)

    def __init__(self, name):
        super(pumpedEvalNode, self).__init__(name)
        highlight = syntaxPython.PythonHighlighter(self.text)

        preload_libs = '#from lib import Package as P; import pandas as pd'

        self.text.setPlainText("# Access inputs as args['input']\n"+preload_libs+"\nreturn {'output': None} ## one key per output terminal")

    def focusOutEvent(self, ev):
        ''' i reimplement this event to include emitting the `sigUIStateChanged` signal'''
        text = str(self.text.toPlainText())
        if text != self.lastText:
            self.lastText = text
            self.update()
            self.sigUIStateChanged.emit(self)
        return QtGui.QTextEdit.focusOutEvent(self.text, ev)
