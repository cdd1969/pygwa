#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph.flowchart.Node import Node
from pyqtgraph import functions as fn
from pyqtgraph.Qt import QtCore

from pyqtgraph.parametertree import ParameterTree
from lib.common.Parameter import customParameter


class newNodeWithCtrlWidget(Node):
    """ This is an abstract class to build other nodes.
    """

    sigUIStateChanged = QtCore.Signal(object)


    def __init__(self, name, color=(200, 200, 200, 150), ui=None, **kwargs):
        self._parent = kwargs.get('parent', None)
        kwargs['terminals'] = kwargs.get('terminals', {'In': {'io': 'in'}, 'Out': {'io': 'out'}})
        if 'parent' in kwargs.keys():
            kwargs.pop('parent')
        super(newNodeWithCtrlWidget, self).__init__(name, **kwargs)
        self.graphicsItem().setBrush(fn.mkBrush(color))

        if ui is None:
            ui = getattr(self, 'uiTemplate', [])
        self._ctrlWidget = newNodeCtrlWidget(parent=self, ui=ui)

    def ctrlWidget(self):
        return self._ctrlWidget

    def saveState(self):
        """overwriting standard Node method to extend it with saving ctrlWidget state"""
        state = Node.saveState(self)
        # saving additionally state of the control widget
        state['crtlWidget'] = self._ctrlWidget.saveState()
        return state
        
    def restoreState(self, state, update=False):
        """overwriting standard Node method to extend it with restoring ctrlWidget state"""
        Node.restoreState(self, state)
        # additionally restore state of the control widget
        self._ctrlWidget.restoreState(state['crtlWidget'])
        if update:
            self.update()

    def changed(self, update=False):
        if update:
            self.update()
        self.sigUIStateChanged.emit(self)


class newNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None, ui=None):
        super(newNodeCtrlWidget, self).__init__()
        self._parent = parent
        self._ui = ui

        ## Create tree of Parameter objects (self.p - MainParameter)
        self.p = customParameter(name='params', type='group', children=self._ui)
        ## set parameter tree to <self> (parameterTreeWidget)
        self.setParameters(self.p, showTop=False)
        # connect parameter signals
        self.initSignalConnections()
        self.initUserSignalConnections()
        # save default state
        self._savedState = self.saveState()

    def initSignalConnections(self):
        update_parent = True
        for child in self.p.children(recursive=True, ignore_groups=True):
            child.sigStateChanged.connect(lambda: self._parent.changed(update_parent))

    def initUserSignalConnections(self):
        """ This method should be reimplemented by user when creating custom node,
        if you want to connect some specific params with some specific actions.

        For example:
            self.param('Open').sigActivated.connect(self.on_loadfile_clicked)
            self.param(('Graphics', 'color')).sigValueChanged.connect(self.on_colorChanged)

        Note:
            This method is executed in during initialization.
        """
        pass


    def ui(self):
        return self._ui

    def saveState(self):
        return self.p.saveState()
    
    def restoreState(self, state):
        self.p.restoreState(state)

    def param(self, *names):
        ''' alias to p.child'''
        return self.p.child(*names)
    
    def params(self, recursive=True, ignore_groups=False):
        ''' alias to p.children()'''
        return self.p.children(recursive=recursive, ignore_groups=ignore_groups)

    def paramValue(self, *names, **opts):
        ''' alias to p.childValue()'''
        return self.p.childValue(*names, **opts)
