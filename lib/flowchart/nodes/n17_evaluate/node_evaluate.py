#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph.flowchart.library.Data import EvalNode
from lib.common import syntaxPython
from pyqtgraph.Qt import QtCore, QtGui


class pumpedEvalNode(EvalNode):
    sigUIStateChanged = QtCore.Signal(object)

    def __init__(self, name):
        super(pumpedEvalNode, self).__init__(name)
        highlight = syntaxPython.PythonHighlighter(self.text)

        preload_libs = '#from lib.flowchart.package import Package as P; import pandas as pd'

        self.text.setPlainText("# Access inputs as args['input']\n"+preload_libs+"\nreturn {'output': None} ## one key per output terminal")

    def focusOutEvent(self, ev):
        ''' i reimplement this event to include emitting the `sigUIStateChanged` signal'''
        text = str(self.text.toPlainText())
        if text != self.lastText:
            self.lastText = text
            self.update()
            self.sigUIStateChanged.emit(self)
        return QtGui.QTextEdit.focusOutEvent(self.text, ev)
