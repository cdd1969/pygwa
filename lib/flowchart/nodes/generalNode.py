#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph.flowchart.Node import Node
from pyqtgraph import functions as fn
from pyqtgraph.Qt import QtCore

from pyqtgraph.parametertree import ParameterTree, Parameter
from lib.common.Parameter import customParameter
import logging
logger = logging.getLogger(__name__)


class NodeWithCtrlWidget(Node):
    """ This is an abstract class to build other nodes.
    """

    sigUIStateChanged = QtCore.Signal(object)


    def __init__(self, name, color=(200, 200, 200, 150), ui=None, parent=None, **kwargs):
        self._parent = parent
        kwargs['terminals'] = kwargs.get('terminals', {'In': {'io': 'in'}, 'Out': {'io': 'out'}})
        super(NodeWithCtrlWidget, self).__init__(name, **kwargs)
        logger.debug("creating node [{0}] of type [{1}]".format(self.name(), self.nodeName))
        self._init_at_first()
        self.graphicsItem().setBrush(fn.mkBrush(color))

        if ui is None:
            ui = getattr(self, 'uiTemplate', [])
        self._ctrlWidget = self._createCtrlWidget(parent=self, ui=ui)
        logger.info("node [{0}] of type [{1}] created".format(self.name(), self.nodeName))

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

    def CW(self):
        return self._ctrlWidget

    def p(self):
        return self.CW().p
        
    def saveState(self):
        """overwriting standard Node method to extend it with saving ctrlWidget state"""
        state = Node.saveState(self)
        # saving additionally state of the control widget
        state['crtlWidget'] = self._ctrlWidget.saveState()
        return state
        
    def restoreState(self, state, update=False):
        """overwriting standard Node method to extend it with restoring ctrlWidget state"""
        logger.debug("restoring [{0}] Node's state".format(self.name()))
        Node.restoreState(self, state)
        logger.debug("restored state of [{0}] Node".format(self.name()))
        # additionally restore state of the control widget
        self._ctrlWidget.restoreState(state['crtlWidget'])
        if update:
            self.update()
    


class NodeCtrlWidget(ParameterTree):
    ''' This is an abstract class to accompany Nodeclass `NodeWithCtrlWidget`'''
     
    def __init__(self, parent=None, ui=[], update_on_statechange=True, **kwargs):
        super(NodeCtrlWidget, self).__init__()
        logger.debug("creacting CtrlWidget of node [{0}]".format(parent.name()))
        #print ('INTING NODE_CTRL_WDG {0} with parent {1}'.format(self, parent))

        self._parent = parent
        self._ui = ui

        ## Create tree of Parameter objects (self.p - MainParameter)
        self.p = customParameter(name='params', type='group', children=self._ui)
        ## set parameter tree to <self> (parameterTreeWidget)
        self.setParameters(self.p, showTop=False)
        # connect parameter signals
        if update_on_statechange:
            self.connect_all_valueChanged2upd(**kwargs)
        else:
            #actually connect but without UPD flag
            self.disconnect_all_valueChanged2upd(**kwargs)

        self.initUserSignalConnections()
        logger.debug("CtrlWidget of node [{0}] created".format(parent.name()))

    def parent(self):
        return self._parent

    def connect_all_valueChanged2upd(self, ignore_groups=True, ignore_actions=False):
        '''helper function to connect all params in a tree with `.update()` method of parent node'''
        for child in self.p.children(recursive=True, ignore_groups=ignore_groups, ignore_actions=ignore_actions):
            self.connect_valueChanged2upd(child)
    
    def disconnect_all_valueChanged2upd(self, ignore_groups=True, ignore_actions=False):
        '''helper function to disconnect all params in a tree from `.update()` method of parent node'''
        for child in self.p.children(recursive=True, ignore_groups=ignore_groups, ignore_actions=ignore_actions):
            self.disconnect_valueChanged2upd(child)
        
    def connect_valueChanged2upd(self, param):
        '''helper function to connect param in a tree with `.update()` method of parent node'''
        self._disconnect_param_from_valuechanged(param)
        #print ('Connecting param : {0}, {1} with UPD'.format(param, param.name()))
        param.sigValueChanged.connect(self.detectChanges_with_UPD)
    
    def disconnect_valueChanged2upd(self, param):
        '''helper function to disconnect param in a tree from `.update()` method of parent node'''
        self._disconnect_param_from_valuechanged(param)
        #print ('Connecting param : {0}, {1} without UPD'.format(param, param.name()))
        param.sigValueChanged.connect(self.detectChanges_without_UPD)

    def _disconnect_param_from_valuechanged(self, param):
        try:
            param.sigValueChanged.disconnect(self.detectChanges_with_UPD)
        except TypeError:
            #print ('Cannot disconnect param : {0}, {1} from method `detectChanges_with_UPD`'.format(param, param.name()))
            pass
        try:
            param.sigValueChanged.disconnect(self.detectChanges_without_UPD)
        except TypeError:
            #print ('Cannot disconnect param : {0}, {1} from method `detectChanges_without_UPD`'.format(param, param.name()))
            pass

    def detectChanges_with_UPD(self, param, value):
        #print ('UPD parent. Sender : {0}, {1}'.format(param, param.name()))
        self._parent.update()
        # emit signal that UI in the Node has changed => therefore unsaved-changes status will be detected
        self._parent.sigUIStateChanged.emit(self)

    def detectChanges_without_UPD(self, param, value):
        self._parent.sigUIStateChanged.emit(self)

    def initUserSignalConnections(self):
        """ This method should be reimplemented by user when creating custom node,
        if you want to connect some specific params with some specific actions.

        For example:
            self.param('Open').sigActivated.connect(self.on_loadfile_clicked)
            self.param(('Graphics', 'color')).sigValueChanged.connect(self.on_colorChanged)

        Note:
            This method is executed during initialization.
        """
        pass


    def ui(self):
        return self._ui

    def saveState(self):
        return self.p.saveState()
    
    def restoreState(self, state):
        logger.debug("restoring [{0}]-CtrlWidget's state".format(self._parent.name()))
        self.p.restoreState(state)
        logger.debug("[{0}]-CtrlWidget's state restored".format(self._parent.name()))

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
