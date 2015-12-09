from PyQt5.QtWidgets import QTreeWidgetItem
from pyqtgraph import OrderedDict
from pyqtgraph.flowchart.NodeLibrary import isNodeClass


def fill_item(item, value):
    item.setExpanded(True)
    if isinstance(value, (OrderedDict, dict)):
        for key, val in sorted(value.iteritems()):
            child = QTreeWidgetItem()
            child.setText(0, unicode(key))
            if isNodeClass(val) and hasattr(val, '__doc__'):  # this means that value is Node
                child.setToolTip(0, unicode(val.__doc__))
            item.addChild(child)
            fill_item(child, val)


def fill_widget(widget, value):
    widget.clear()
    fill_item(widget.invisibleRootItem(), value)
