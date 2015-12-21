#!/usr/bin python
# -*- coding: utf-8 -*-
from lib.functions import filterSerfes1991 as serfes
from pyqtgraph import BusyCursor
from lib.flowchart.package import Package
import copy
import os, sys
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.flowchart.Node import Node
from pyqtgraph.parametertree import Parameter, ParameterTree
from ..functions.evaluatedictionary import evaluateDict, evaluationFunction
from ..functions.general import isNumpyDatetime
import webbrowser
from ..functions.general import returnPandasDf
import numpy as np
import gc


class serfes1991Node(Node):
    """Apply Serfes Filter to hydrograph (see Sefes 1991)"""
    nodeName = "Serfes Filter"


    def __init__(self, name, parent=None):
        super(serfes1991Node, self).__init__(name, terminals={'In': {'io': 'in'}, 'Out': {'io': 'out'}})
        self._ctrlWidget = serfes1991NodeCtrlWidget(self)

        
    def process(self, In):
        gc.collect()
        with BusyCursor():
            df = copy.deepcopy(returnPandasDf(In))
            # check out http://docs.scipy.org/doc/numpy-dev/neps/datetime-proposal.html
            

            colname = [None]+[col for col in df.columns if isNumpyDatetime(df[col].dtype)]
            self._ctrlWidget.p.param('datetime').setLimits(colname)
            kwargs = self.ctrlWidget().evaluateState()

            if self._ctrlWidget.calculateNAllowed():
                N = serfes.get_number_of_measurements_per_day(df, datetime=kwargs['datetime'], log=kwargs['log'])
                self._ctrlWidget.p.param('N').setValue(N)


            if self._ctrlWidget.applyAllowed():
                result = serfes.filter_wl_71h_serfes1991(df, **kwargs)
                return {'Out': Package(result)}
            #else:
            #    pass
                #return {'Out': None}

    def ctrlWidget(self):
        return self._ctrlWidget

    def saveState(self):
        """overriding stadart Node method to extend it with saving ctrlWidget state"""
        state = Node.saveState(self)
        # sacing additionaly state of the control widget
        state['crtlWidget'] = self.ctrlWidget().saveState()
        return state
        
    def restoreState(self, state):
        """overriding stadart Node method to extend it with restoring ctrlWidget state"""
        Node.restoreState(self, state)
        # additionally restore state of the control widget
        self.ctrlWidget().restoreState(state['crtlWidget'])
        #self.update()  # we do not call update() since we want to process only on LoadButton clicked
















class serfes1991NodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(serfes1991NodeCtrlWidget, self).__init__()
        self._parent = parent

        params = self.params()
        ## Create tree of Parameter objects
        self.p = Parameter.create(name='params', type='group', children=params)

        ## set parameter tree to <self> (parameterTreeWidget)
        self.setParameters(self.p, showTop=False)
        self.initConnections()
        # save default state
        self._savedState = self.saveState()
        self._applyAllowed = False
        self._calculateNAllowed = False

    def initConnections(self):
        self.p.child('Help').sigActivated.connect(self.on_help_clicked)
        self.p.child('Apply Filter').sigActivated.connect(self.on_apply_clicked)
        self.p.child('Calculate N').sigActivated.connect(self.on_calculateN_clicked)
    
    def applyAllowed(self):
        return self._applyAllowed

    def calculateNAllowed(self):
        return self._calculateNAllowed

    @QtCore.pyqtSlot()  #default signal
    def on_apply_clicked(self):
        self._applyAllowed = True
        self._parent.update()
        self._applyAllowed = False

    @QtCore.pyqtSlot()  #default signal
    def on_calculateN_clicked(self):
        self._calculateNAllowed = True
        self._parent.update()
        self._calculateNAllowed = False

    @QtCore.pyqtSlot()  #default signal
    def on_help_clicked(self):
        webbrowser.open('https://github.com/cdd1969/pygwa/blob/gh-pages/node_serfes91filter.md')

    def params(self):
        params = [
            {'name': 'Help', 'type': 'action'},
            {'name': 'datetime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects.\nBy default is `None`, meaning that datetime objects are\nlocated within `pd.DataFrame.index`. If not `None` - pass the\ncolumn-name of dataframe where datetime objects are located.\nThis is needed to determine number of measurements per day.\nNote: this argument is ignored if `N` is not `None` !!!'},
            {'name': 'N', 'type': 'str', 'value': None, 'default': None, 'tip': '<int or None>\nExplicit number of measurements in 24 hours. By\ndefault `N=None`, meaning that script will try to determine\nnumber of measurements per 24 hours based on real datetime\ninformation provided with `datetime` argument'},
            {'name': 'usecols', 'type': 'str', 'value': None, 'default': None, 'tip': '<List[str] or None>\nExplicitly pass the name of the columns\nthat will be evaluated. These columns must have numerical dtype\n(i.e. int32, int64, float32, float64). Default value is `None`\nmeaning that all numerical columns will be processed'},
            {'name': 'verbose', 'type': 'bool', 'value': False, 'default': False, 'tip': 'If `True` - will keep all three iterations\nin the output. If `False` - will save only final (3rd) iteration.\nThis may useful for debugging, or checking this filter.'},
            {'name': 'log', 'type': 'bool', 'value': False, 'default': False, 'tip': 'flag to show some prints in console'},
            {'name': 'Calculate N', 'type': 'action'},
            {'name': 'Apply Filter', 'type': 'action'},

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


        listWithDicts = evaluateDict(state['children'], functionToDicts=evaluationFunction, log=False,
            function4arguments=serfes.filter_wl_71h_serfes1991)
        kwargs = dict()
        for d in listWithDicts:
            # {'a': None}.items() => [('a', None)] => two times indexing
            kwargs[d.items()[0][0]] = d.items()[0][1]

        for k, v in kwargs.iteritems():
            if k == 'datetime':
                kwargs[k] = str(v)  # ve careful with lists. If we have an imported datetime module, and 'datetime' list-entry , it will be evaluated as dtype object! therefore we explicitly convert it to strings
            if v == 'None':
                kwargs[k] = None


        return kwargs
