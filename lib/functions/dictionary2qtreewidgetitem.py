from PyQt5.QtWidgets import QTreeWidgetItem
from pyqtgraph import OrderedDict
from pyqtgraph.flowchart.NodeLibrary import isNodeClass
from pyqtgraph.Qt import QtGui


def fill_item(item, value):
    item.setExpanded(True)
    if isinstance(value, (OrderedDict, dict)):
        for key, val in sorted(value.iteritems()):
            child = QTreeWidgetItem()
            child.setText(0, unicode(key))
            if isNodeClass(val) and hasattr(val, '__doc__'):  # this means that `val` is Node instance
                child.setToolTip(0, unicode(val.__doc__))
            else:
                # make group keys bold, italic and with gray background
                font = QtGui.QFont("Ubuntu", 10, QtGui.QFont.Bold, True)
                child.setFont(0, font)
                child.setBackground(0, QtGui.QBrush(QtGui.QColor('#C0C0C0')))
            item.addChild(child)
            fill_item(child, val)


def fill_widget(widget, value):
    widget.clear()
    fill_item(widget.invisibleRootItem(), value)
