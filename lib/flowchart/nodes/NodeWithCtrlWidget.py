#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph.flowchart.Node import Node
from pyqtgraph import functions as fn



class NodeWithCtrlWidget(Node):
    """ This class simply reduces 3 methods from my custom Nodes
        and saves around 30 lines :)
    """
    def __init__(self, name, color=(200, 200, 200, 150), **kwargs):
        self._parent = kwargs.get('parent', None)
        if 'parent' in kwargs.keys():
            kwargs.pop('parent')
        super(NodeWithCtrlWidget, self).__init__(name, **kwargs)
        self._ctrlWidget = None
        self.graphicsItem().setBrush(fn.mkBrush(color))

    def ctrlWidget(self):
        return self._ctrlWidget

    def saveState(self):
        """overriding stadart Node method to extend it with saving ctrlWidget state"""
        state = Node.saveState(self)
        # sacing additionaly state of the control widget
        state['crtlWidget'] = self._ctrlWidget.saveState()
        return state
        
    def restoreState(self, state, update=False):
        """overriding stadart Node method to extend it with restoring ctrlWidget state"""
        Node.restoreState(self, state)
        # additionally restore state of the control widget
        self._ctrlWidget.restoreState(state['crtlWidget'])
        if update:
            self.update()  # we do not call update() since we want to process only on LoadButton clicked or on_other_action

'''
class parameterNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(parameterNodeCtrlWidget, self).__init__(parent)
        self._parent = parent

        params = self.params()
        ## Create tree of Parameter objects
        self.p = Parameter.create(name='params', type='group', children=params)

        ## set parameter tree to <self> (parameterTreeWidget)
        self.setParameters(self.p, showTop=False)
        self.initConnections()

    def initConnections(self):
        """this method has to be reimplemented
        """
        pass

    def setYAxisLabel(self):
        self._gr.setYAxisTextAndUnits(self.p.child('Y:Label').value, self.p.child('Y:Units').value)

    def params(self):
        params = [
            {'name': 'Label', 'type': 'str', 'value': 'Hydrographs', 'default': 'Hydrographs'},
            {'name': 'Y:Label', 'type': 'str', 'value': 'Waterlevel', 'default': 'Waterlevel'},
            {'name': 'Y:Units', 'type': 'str', 'value': 'm AMSL', 'default': 'm AMSL'},
            {'name': 'Legend', 'type': 'bool', 'value': False, 'default': False},
            {'name': 'Crosshair', 'type': 'bool', 'value': False, 'default': False},
            {'name': 'Data Points', 'type': 'bool', 'value': False, 'default': False},
            
            {'name': 'Plot', 'type': 'action'},
        ]
        return params

    def saveState(self):
        return self.p.saveState()
    
    def restoreState(self, state):
        self.p.restoreState(state)

    def evaluateState(self, state=None):
        """ function evaluates passed state , reading only necessary parameters,
            those that can be passed to pandas.read_csv() as **kwargs (see function4arguments)

            user should reimplement this function for each Node"""

        if state is None:
            state = self.saveState()


        if state is None:
            state = self.saveState()
        validArgs = [d['name'] for d in self.params()]
        listWithDicts = evaluateDict(state['children'], functionToDicts=evaluationFunction, log=False, validArgumnets=validArgs)
        kwargs = dict()
        for d in listWithDicts:
            # {'a': None}.items() >>> [('a', None)] => two times indexing
            kwargs[d.items()[0][0]] = d.items()[0][1]
        return kwargs
'''