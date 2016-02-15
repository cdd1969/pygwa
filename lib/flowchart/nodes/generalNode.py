#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph.flowchart.Node import Node
from pyqtgraph import functions as fn
from pyqtgraph.Qt import QtCore

from pyqtgraph.parametertree import ParameterTree
from lib.common.Parameter import customParameter


class NodeWithCtrlWidget(Node):
    """ This is an abstract class to build other nodes.
    """

    sigUIStateChanged = QtCore.Signal(object)


    def __init__(self, name, color=(200, 200, 200, 150), ui=None, **kwargs):
        self._parent = kwargs.get('parent', None)
        kwargs['terminals'] = kwargs.get('terminals', {'In': {'io': 'in'}, 'Out': {'io': 'out'}})
        if 'parent' in kwargs.keys():
            kwargs.pop('parent')
        super(NodeWithCtrlWidget, self).__init__(name, **kwargs)
        self._init_at_first()
        self.graphicsItem().setBrush(fn.mkBrush(color))

        if ui is None:
            ui = getattr(self, 'uiTemplate', [])
        self._ctrlWidget = self._createCtrlWidget(parent=self, ui=ui)

    def _init_at_first(self):
        ''' Reimplemented this method to init something at very beginning'''
        pass
        
    def _createCtrlWidget(self, **kwargs):
        ''' Reimplemented this method to connect custom control widgets.
        For default NodeCtrlWidget **kwargs must contain...
            1) kwargs['parent']
            2) kwargs['ui']
            '''
        return NodeCtrlWidget(**kwargs)

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
    
    @QtCore.pyqtSlot()
    def changed(self, update=False):
        print 'changed... update=', update
        if update:
            self.update()
        self.sigUIStateChanged.emit(self)


class NodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None, ui=[], update_on_statechange=True):
        super(NodeCtrlWidget, self).__init__()
        self._parent = parent
        self._ui = ui

        ## Create tree of Parameter objects (self.p - MainParameter)
        self.p = customParameter(name='params', type='group', children=self._ui)
        ## set parameter tree to <self> (parameterTreeWidget)
        self.setParameters(self.p, showTop=False)
        # connect parameter signals
        self.initSignalConnections(update_parent=update_on_statechange)
        self.initUserSignalConnections()
        # save default state
        self._savedState = self.saveState()

    def initSignalConnections(self, update_parent=True):
        ''' Function searches for all parameters (nested params are included)
        within `self.p` recursively. Group parameters are omitted. Then all pa-
        rameters that are found, are connected with `self._parent.changed()`
        method with their `sigValueChanged` signal.

        That method (`self._parent.changed()`) has an optional keyword `update`
        which is responsible for trigerring `Node.update()` method. In other
        words we may control if the changes in parameter `self.p` values will
        trigger the `.update()` method of the parent Node.

        Args:
        -----
            update_parent (True, False, dict):
                This parameter allows control on which parameters
                will be (not) connected to the `self._parent.changed` slot,
                with flag to trigger `self._parent.update()` method

                True  - all params will trigger update()
                False - all params wont trigger update()
                dict  - dictionary with two keys ('connect', 'disconnect')
                    to control parameters individually. Two possibilities are given:
                    1) Dont connect any of params except param1 and param2:
                        {'action': 'connect',
                         'parameters': (param1, param2)}
                    2) Connect all params escept param1 and param2
                        {'action': 'disconnect',
                         'parameters': (param1, param2)}
                
                NOTE:
                If you want to use `dict` type, then you need to pass there
                the instances of the parameters. To do that REIMPLEMENT this
                method in your custom node e.g.:

                def initSignalConnections(self, update_parent=True):
                    new_update_parent = {
                        'action': 'connect',
                        'parameters': (self.param('foo'), self.param('bar'))
                    }
                    super(thisNodeClass, self).initSignalConnections(new_update_parent)

        '''

        if isinstance(update_parent, dict):
            # we have dictionary, treat params separately
            if update_parent['action'] in ['connect', u'connect', True]:
                default_action = False
            elif update_parent['action'] in ['disconnect', u'disconnect', False]:
                default_action = True
            else:
                raise KeyError('Invalid value {0} for key `action`'.format(update_parent['action']))
            
            if not isinstance(update_parent['parameters'], (tuple, list)):
                # if one param passed without brackets:
                #   {'parameters': self.param('foo')}
                # explicitly convert it to length=1 list to use `in` statement further
                update_parent['parameters'] = [update_parent['parameters']]

            for child in self.p.children(recursive=True, ignore_groups=True):
                if child in update_parent['parameters']:
                    child.sigStateChanged.connect(lambda: self._parent.changed(not(default_action)))
                else:
                    child.sigStateChanged.connect(lambda: self._parent.changed(default_action))

        elif isinstance(update_parent, bool):
            # we have bool, treat params all together
            default_action = update_parent
            for child in self.p.children(recursive=True, ignore_groups=True):
                child.sigStateChanged.connect(lambda: self._parent.changed(default_action))
        else:
            raise TypeError('Invalid type {0} of parameter `update_parent`. Must be `bool` or `dict`'.format(type(update_parent)))

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

    def prepareInputArguments(self, ignore_groups=False):
        kwargs = dict()
        for p in self.params(ignore_groups=ignore_groups):
            kwargs[p.name()] = p.value()
        return kwargs
