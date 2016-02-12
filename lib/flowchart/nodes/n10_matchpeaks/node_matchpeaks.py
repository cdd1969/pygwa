#!/usr/bin python
# -*- coding: utf-8 -*-

from pyqtgraph import BusyCursor
from pyqtgraph.parametertree import Parameter, ParameterTree

from ...package import Package
from ....functions.detectpeaks import match_peaks
from ....functions.evaluatedictionary import evaluateDict, evaluationFunction
from ....common.NodeWithCtrlWidget import NodeWithCtrlWidget
from ....functions.general import returnPandasDf, isNumpyDatetime


class matchPeaksNode(NodeWithCtrlWidget):
    """Match peaks from two DataFrames. Peaks should be detected before"""
    nodeName = "matchpeaks"


    def __init__(self, name, parent=None):
        super(matchPeaksNode, self).__init__(name, parent=parent, terminals={'W_peaks': {'io': 'in'}, 'GW_peaks': {'io': 'in'}, 'matched': {'io': 'out'}}, color=(250, 250, 150, 150))
        self._ctrlWidget = matchPeaksNodeCtrlWidget(parent=self)
        self._plotRequired = False

        
    def process(self, W_peaks, GW_peaks):
        N_md = '?'
        df_w  = returnPandasDf(W_peaks)
        df_gw = returnPandasDf(GW_peaks)

        colname = [None]+[col for col in df_w.columns if isNumpyDatetime(df_w[col].dtype)]
        self._ctrlWidget.p.child('Closest Time').child('Match Column').setLimits(colname)


        kwargs = self._ctrlWidget.evaluateState()
        with BusyCursor():
            mode = kwargs.pop('Match Option')
            if mode == 'Closest Time':
                matched_peaks = match_peaks(df_w, df_gw, kwargs.pop('Match Column'), **kwargs)
                
            N_md = matched_peaks['md_N'].count()
            
        self._ctrlWidget.p.child('MATCHED/PEAKS').setValue('{0}/{1}'.format(N_md, len(df_w)))
        return {'matched': Package(matched_peaks)}





class matchPeaksNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(matchPeaksNodeCtrlWidget, self).__init__()
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

        self.p.sigValueChanged.connect(self._parent.update)

        self.p.child('Match Option').sigValueChanged.connect(self._parent.update)

        self.p.child('Closest Time').child('Match Column').sigValueChanged.connect(self._parent.update)
        self.p.child('Closest Time').child('side').sigValueChanged.connect(self._parent.update)
        self.p.child('Closest Time').child('use_window').sigValueChanged.connect(self._parent.update)
        self.p.child('Closest Time').child('window').sigValueChanged.connect(self._parent.update)


    
    def params(self):
        params = [
            {'name': 'Match Option', 'type': 'list', 'value': 'Closest Time', 'default': 'Closest Time', 'values': ['Closest Time'], 'tip': 'Match option:\n"Closest Time" - match gw_peaks which have closest datetime to w_peaks'},
            
            {'name': 'Closest Time', 'type': 'group', 'children': [
                {'name': 'Match Column', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Data will be matched based on this column'},

                {'name': 'side', 'type': 'list', 'values': ['right (>=t)', 'right (>t)', 'left (<=t)', 'left (<t)', 'both'], 'value': 'right (>=t)', 'default': 'right (>=t)', 'tip': 'search direction with respect to `t`.\n"right (>=t)"  - search after or at `t`\n"right (>t)" - search after `t`\n"left (<=t)" - search before or at `t`\n"left (<t)" - search before `t`\n"both"  - search before and after `t` or at `t`'},

                {'name': 'use_window', 'type': 'bool', 'value': False, 'default': False, 'tip': 'Search matching peaks within time-window\n[t-window : t+window]\nEnables `window` float spinbox'},
                {'name': 'window', 'type': 'float', 'value': 0, 'default': 0, 'limits': (0, int(10e6)), 'tip': 'Is read only if `use_window` is checked!\nNumber of hours to determine time-window'},
            ]},
            {'name': 'MATCHED/PEAKS', 'type': 'str', 'value': '?/?', 'readonly': True},
        
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
        listWithDicts = evaluateDict(state['children'], functionToDicts=evaluationFunction, log=False, validArgumnets=['Match Option', 'Match Column', 'side', 'use_window', 'window'])
        kwargs = dict()
        for d in listWithDicts:
            # {'a': None}.items() >>> [('a', None)] => two times indexing
            kwargs[d.items()[0][0]] = d.items()[0][1]

        if kwargs['use_window'] is False:
            kwargs['window'] = None
        del kwargs['use_window']

        return kwargs
