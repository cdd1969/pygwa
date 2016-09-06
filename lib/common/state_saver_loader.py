import pyqtgraph
import decimal
from PyQt5 import uic, QtCore, QtWidgets
'''
These functions are used to Save/Load parameters of the NodeCtrlWidgets that
were created with Qt Designer. Pyqtgraph has its own Save/Load algorithm, but
in future it is planned to get rid of the "simple" pyqtgraph-parameters and
transfer all Nodes into Qt Designer forms (*.ui files)
'''

def SaveWidgetState(widget):
    '''
        Saves the `state` of the input widget depending on its type.
        We are interested to destinguish these types of widgets:

            1) spinbox
                - value
                - min
                - max
            2) datetime
                - value
                - min
                - max
            3) combobox
                - items
                - current item
            4) lineedit
                - value
            5) checkbox

        Return a dictionary with parameter and its value. The sate of the
        widget can be restored then with the neigbour-function `RestoreWidgetState()`
    '''
    if isinstance(widget, QtWidgets.QDateTimeEdit):
        # QDateTimeEdit
        state = {
            'value': widget.dateTime().toString(),
            'min':   widget.minimumDateTime().toString(),
            'max':   widget.maximumDateTime().toString(),
        }
    
    elif isinstance(widget, (pyqtgraph.widgets.SpinBox.SpinBox, QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)):
        # QSpinBox
        if isinstance(widget, pyqtgraph.widgets.SpinBox.SpinBox):  # special class introduced in PyQtGraph
            state = {
                        'value': widget.value(),
                        'min': float(widget.opts['bounds'][0]) if isinstance(widget.opts['bounds'][0], decimal.Decimal) else widget.opts['bounds'][0],
                        'max': float(widget.opts['bounds'][1]) if isinstance(widget.opts['bounds'][1], decimal.Decimal) else widget.opts['bounds'][1],
                    }
        else:
            state = {
                        'value': widget.value(),
                        'min':   widget.minimum(),
                        'max':   widget.maximum(),
                    }

    elif isinstance(widget, QtWidgets.QCheckBox):
        # QCheckBox
        state = { 'value': widget.isChecked()}
    
    elif isinstance(widget, QtWidgets.QLineEdit):
        # QLineEdit
        state = { 'value': widget.text()}
    
    elif isinstance(widget, QtWidgets.QComboBox):
        # QComboBox
        state = {
                    'index': widget.currentIndex(),
                    'count': widget.count(),
                    'items': [widget.itemText(index) for index in xrange(widget.count())]
                }
    return state









def RestoreWidgetState(widget, state):
    '''
        Restore the state of the given `widget`
        See doc to function `SaveWidgetState()`
    '''
    if isinstance(widget, QtWidgets.QDateTimeEdit):
        # QDateTimeEdit
        widget.setMinimumDateTime(QtCore.QDateTime.fromString(state['min']))
        widget.setMaximumDateTime(QtCore.QDateTime.fromString(state['max']))
        widget.setDateTime(QtCore.QDateTime.fromString(state['value']))
    
    elif isinstance(widget, (pyqtgraph.widgets.SpinBox.SpinBox, QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)):
        # QSpinBox
        widget.setMinimum(state['min'])
        widget.setMaximum(state['max'])
        widget.setValue(state['value'])

    elif isinstance(widget, QtWidgets.QCheckBox):
        # QCheckBox
        widget.setChecked(state['value'])

    elif isinstance(widget, QtWidgets.QLineEdit):
        # QLineEdit
        widget.setText(state['value'])

    elif isinstance(widget, QtWidgets.QComboBox):
        # QComboBox
        if not [widget.itemText(index) for index in xrange(widget.count())] == state['items']:
            # Clear the QComboBox, restore old items
            widget.clear()
            widget.addItems(state['items'])
        # finally set the current index
        widget.setCurrentIndex(state['index'])