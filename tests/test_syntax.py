from PyQt5 import QtWidgets
import lib.common.syntaxPython as syntaxPython
from lib import projectPath


app = QtWidgets.QApplication([])
editor = QtWidgets.QPlainTextEdit()
highlight = syntaxPython.PythonHighlighter(editor.document())
editor.show()

# Load syntax.py into the editor for demo purposes
infile = open(projectPath('../lib/common/syntaxPython.py'), 'r')
editor.setPlainText(infile.read())

app.exec_()