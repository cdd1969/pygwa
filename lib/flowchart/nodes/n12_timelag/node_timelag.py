#!/usr/bin python
# -*- coding: utf-8 -*-

from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph import BusyCursor

from ....functions.evaluatedictionary import evaluateDict, evaluationFunction
from ....common.NodeWithCtrlWidget import NodeWithCtrlWidget
from ....functions.TimeLag import timelag_erskine1991_method
from ....functions.general import returnPandasDf, isNumpyDatetime



class timeLagNode(NodeWithCtrlWidget):
    """Calculate Timelag comparing given river and groundwater hydrogrpahs"""
    nodeName = "TimeLag"


    def __init__(self, name, parent=None):
        terms = {'df_gw': {'io': 'in'},
                 'df_w': {'io': 'in'},
                 'E': {'io': 'in'},
                 'tlag': {'io': 'out'},
                 }
        super(timeLagNode, self).__init__(name, parent=parent, terminals=terms, color=(250, 250, 150, 150))
        self._ctrlWidget = timeLagNodeCtrlWidget(parent=self)
        
    def process(self, df_gw, df_w, E):
        self._ctrlWidget.p.param('tlag = ').setValue('?')
        
        df_gw = returnPandasDf(df_gw)
        df_w = returnPandasDf(df_w)

        colname = [col for col in df_gw.columns if not isNumpyDatetime(df_gw[col].dtype)]
        self._ctrlWidget.p.param('gw').setLimits(colname)
        colname = [None]+[col for col in df_gw.columns if isNumpyDatetime(df_gw[col].dtype)]
        self._ctrlWidget.p.param('gw_dtime').setLimits(colname)
        
        colname = [col for col in df_w.columns if not isNumpyDatetime(df_w[col].dtype)]
        self._ctrlWidget.p.param('river').setLimits(colname)
        colname = [None]+[col for col in df_w.columns if isNumpyDatetime(df_w[col].dtype)]
        self._ctrlWidget.p.param('river_dtime').setLimits(colname)

        kwargs = self.ctrlWidget().evaluateState()
        if E is None:
            E = kwargs['E']
        else:
            self._ctrlWidget.p.param('E').setValue(E)  # maybe this will provoke process onceagain.
            # and i would have to block the signals here...

        with BusyCursor():
            if kwargs['method'] == '1) Erskine 1991':
                tlag = timelag_erskine1991_method(df_gw, kwargs['gw'], kwargs['gw_dtime'],
                                    df_w, kwargs['river'], kwargs['river_dtime'],
                                    E, tlag_tuple=(kwargs['t1'], kwargs['t2'], kwargs['t_step'])
                                    )
            else:
                raise Exception('Method <%s> not yet implemented' % kwargs['method'])
        
            self._ctrlWidget.p.param('tlag = ').setValue(str(tlag))
            return {'tlag': tlag}




class timeLagNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(timeLagNodeCtrlWidget, self).__init__()
        self._parent = parent

        params = self.params()
        ## Create tree of Parameter objects
        self.p = Parameter.create(name='params', type='group', children=params)

        ## set parameter tree to <self> (parameterTreeWidget)
        self.setParameters(self.p, showTop=False)
        self.initConnections()
        # save default state
        self._savedState = self.saveState()

    def initConnections(self):
        for d in self.params():
            if d['type'] not in ['group', 'action']:
                if 'readonly' in d and d['readonly'] is True:
                    continue
                self.p.child(d['name']).sigValueChanged.connect(self._parent.update)
                
        #self.p.child('river').sigValueChanged.connect(self._parent.update)
        #self.p.child('river_dtime').sigValueChanged.connect(self._parent.update)
        #self.p.child('gw').sigValueChanged.connect(self._parent.update)
        #self.p.child('gw_dtime').sigValueChanged.connect(self._parent.update)
        #self.p.child('E').sigValueChanged.connect(self._parent.update)
        #self.p.child('t1').sigValueChanged.connect(self._parent.update)
        #self.p.child('t2').sigValueChanged.connect(self._parent.update)
        #self.p.child('t_step').sigValueChanged.connect(self._parent.update)
        #self.p.child('method').sigValueChanged.connect(self._parent.update)
        #self.p.child('make_copies').sigValueChanged.connect(self._parent.update)

    
    def params(self):
        params = [
            {'name': 'river', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Column name with RIVER hydrograph data\nin `df_w` dataframe'},
            {'name': 'river_dtime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects\nin `df_w` dataframe'},
            {'name': 'gw', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Column name with GROUNDWATER hydrograph data\nin `df_gw` dataframe'},
            {'name': 'gw_dtime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects\nin `df_gw` dataframe'},
            {'name': 'method', 'type': 'list', 'value': '1) Erskine 1991', 'default': '1) Erskine 1991', 'values': ['1) Erskine 1991'], 'tip': 'Method to calculate TimeLag. Read docs'},
            {'name': 'E', 'type': 'float', 'value': None, 'tip': 'tidal efficiency'},
            {'name': 't1', 'type': 'int', 'value': 1, 'default': 1, 'limits': (0, int(10e3)), 'tip': 'First value for timelag-iteration tuple. Read docs'},
            {'name': 't2', 'type': 'int', 'value': 60, 'default': 60, 'limits': (0, int(10e3)), 'tip': 'Last value for timelag-iteration tuple. Read docs'},
            {'name': 't_step', 'type': 'int', 'value': 1, 'default': 1, 'limits': (1, int(10e3)), 'tip': 'Step value for timelag-iteration tuple. Read docs'},
            {'name': 'tlag = ', 'type': 'str', 'readonly': True, 'value': None}

        ]
        return params


    def saveState(self):
        return self.p.saveState()
    
    def restoreState(self, state):
        self.p.restoreState(state)

    def evaluateState(self, state=None):
        """ function evaluates passed state , reading only necessary parameters,
            those that can be passed to pandas.read_csv() as **kwargs
            user should reimplement this function for each Node"""

        if state is None:
            state = self.saveState()
        validArgs = [d['name'] for d in self.params()]
        listWithDicts = evaluateDict(state['children'], functionToDicts=evaluationFunction, log=False, validArgumnets=validArgs)
        kwargs = dict()
        for d in listWithDicts:
            # {'a': None}.items() >>> [('a', None)] => two times indexing
            kwargs[d.items()[0][0]] = d.items()[0][1]
        return kwargs
