#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph.flowchart.library.Data import EvalNode
from lib.common import syntaxPython
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.flowchart.Node import Node


class pumpedEvalNode(EvalNode):
    """Return the output of a string evaluated/executed by the python interpreter.
    The string may be either an expression or a python script, and inputs are accessed as the name of the terminal.
    For expressions, a single value may be evaluated for a single output, or a dict for multiple outputs.
    For a script, the text will be executed as the body of a function."""

    sigUIStateChanged = QtCore.Signal(object)

    def __init__(self, name):
        super(pumpedEvalNode, self).__init__(name)
        self.text.setAcceptRichText(False)
        self.text.setTabStopWidth(20)
        highlight = syntaxPython.PythonHighlighter(self.text)

        preload_libs = '#import pandas as pd'

        self.text.setPlainText("# Access inputs as args['input']\n"+preload_libs+"\nreturn {'output': None} ## one key per output terminal")

    def focusOutEvent(self, ev):
        ''' i reimplement this event to include emitting the `sigUIStateChanged` signal'''
        # see this thread about decoding
        # http://stackoverflow.com/questions/27662653/get-unicode-string-from-a-pyqt5-plaintextedit
        text = str(self.text.toPlainText().encode('utf-8'))
        print text
        if text != self.lastText:
            self.lastText = text
            self.update()
            self.sigUIStateChanged.emit(self)
        return QtGui.QTextEdit.focusOutEvent(self.text, ev)

    def process(self, display=True, **args):
        ''' I have to reimplement this method in order to insure UTF8 encoding'''
        l = locals()
        l.update(args)
        ## try eval first, then exec
        try:
            text = str(self.text.toPlainText().encode('utf-8')).replace('\n', ' ')
            output = eval(text, globals(), l)
        except SyntaxError:
            fn = "def fn(**args):\n"
            run = "\noutput=fn(**args)\n"
            text = fn + "\n".join(["    "+l for l in str(self.text.toPlainText().encode('utf-8')).split('\n')]) + run
            exec(text)
        except:
            print("Error processing node: %s" % self.name())
            raise
        return output

    def saveState(self):
        state = Node.saveState(self)
        state['text'] = str(self.text.toPlainText().encode('utf-8'))
        return state
