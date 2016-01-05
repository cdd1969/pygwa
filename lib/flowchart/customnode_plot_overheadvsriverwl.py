#!/usr/bin python
# -*- coding: utf-8 -*-

import os, sys
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.flowchart.Node import Node
from pyqtgraph.parametertree import Parameter, ParameterTree
from ..functions.evaluatedictionary import evaluateDict, evaluationFunction
from ..functions import plot_pandas
import webbrowser
from pyqtgraph import BusyCursor
from ..functions.general import returnPandasDf
from ..common.NodeWithCtrlWidget import NodeWithCtrlWidget


class plotGWLvsWLNode(NodeWithCtrlWidget):
    """Plot Growundwater-level VS River water-level (matplotlib)"""
    nodeName = "plotGWLvsWL"


    def __init__(self, name, parent=None):
        super(plotGWLvsWLNode, self).__init__(name, parent=parent, terminals={'In': {'io': 'in'}}, color=(150, 150, 250, 150))
        self._ctrlWidget = plotGWLvsWLNodeCtrlWidget(self)

        
    def process(self, In):
        df = returnPandasDf(In)
        if df is not None:
            # when we recieve a new dataframe into terminal - update possible selection list
            if not self._ctrlWidget.plotAllowed():
                colname = [col for col in df.columns]
                self._ctrlWidget.p.param('Y: Well GWL').setLimits(colname)
                self._ctrlWidget.p.param('X: River WL').setLimits(colname)
            if self._ctrlWidget.plotAllowed():
                kwargs = self.ctrlWidget().evaluateState()
                with BusyCursor():

                    if self._ctrlWidget.p['plot overheads'] is True:
                        y_name = kwargs['y'][0]
                        x_name = kwargs['x'][0]
                        overhead_name = y_name+' - '+x_name
                        df[overhead_name] = df[y_name]-df[x_name]
                        kwargs['y'] = [overhead_name]
                    
                    plot_pandas.plot_pandas_scatter_special1(df, **kwargs)
                    
                    if self._ctrlWidget.p['plot overheads'] is True:
                        del df[overhead_name]
        return






class plotGWLvsWLNodeCtrlWidget(ParameterTree):
    
    def __init__(self, parent=None):
        super(plotGWLvsWLNodeCtrlWidget, self).__init__()
        self._parent = parent

        params = self.params()
        ## Create tree of Parameter objects
        self.p = Parameter.create(name='params', type='group', children=params)

        ## set parameter tree to <self> (parameterTreeWidget)
        self.setParameters(self.p, showTop=False)
        self.initConnections()
        # save default state
        self._savedState = self.saveState()
        self._plotAllowed = False

    def initConnections(self):
        self.p.child('Help').sigActivated.connect(self.on_help_clicked)
        self.p.child('Plot').sigActivated.connect(self.on_plot_clicked)

    @QtCore.pyqtSlot()  #default signal
    def on_plot_clicked(self):
        self._plotAllowed = True
        self._parent.update()
        self._plotAllowed = False

    def plotAllowed(self):
        return self._plotAllowed

    @QtCore.pyqtSlot()  #default signal
    def on_help_clicked(self):
        webbrowser.open('https://github.com/cdd1969/pygwa/blob/gh-pages/node_plotGWLvsWL.md')

    def params(self):
        params = [
            {'name': 'Help', 'type': 'action'},
            {'name': 'X: River WL', 'type': 'list', 'value': 'None', 'default': None, 'values': [None], 'tip': 'Name of the column with river waterlevel data.\nWill be plotted on X-axis'},
            {'name': 'Y: Well GWL', 'type': 'list', 'value': 'None', 'default': None, 'values': [None], 'tip': 'Name of the column with well groundwater-level\ndata. It will be plotted on Y-axis'},
            {'name': 'plot overheads', 'type': 'bool', 'value': False, 'default': False, 'tip': 'If checked, will substract X-values from Y-values element-wise (Yvalues-Xvalues) before\nplotting. This means that so called "overheads" will be plotted on Y-axis and not the\nactual groundwater-levels.\nIf not checked - plots real values of Y-column'},
            
            {'name': 'Plot parameters', 'type': 'group', 'expanded': False, 'children': [
                {'name': 'trendlinemode', 'type': 'list', 'value': 'None', 'default': 'None', 'values': [1, 3, "None"], 'tip': '1    - draw trendlines using all data points\n3    - draw trendlines using all data points, and shift them to the most-far-lying point\nNone - do not draw trendline'},
                {'name': 'marker', 'type': 'list', 'value': 'o', 'default': 'o', 'values': ['o', '.', 'x', '+', 'h'], 'tip': 'marker style for points'},
                {'name': 's', 'type': 'int', 'value': 10, 'default': 10, 'tip': 'point size'},
                {'name': 'title', 'type': 'str', 'value': None, 'default': None, 'tip': 'Figure title (default None)'},
                {'name': 'xlabel', 'type': 'str', 'value': None, 'default': None, 'tip': 'None, or string for labeling x-axes'},
                {'name': 'ylabel', 'type': 'str', 'value': None, 'default': None, 'tip': 'None, or string for labeling y-axes'},
                {'name': 'legendlabels', 'type': 'str', 'value': [None], 'default': [None], 'tip': 'List of legendnames or [None]. If default ([None]) - standart names are used'},
                {'name': 'xlim', 'type': 'str', 'value': None, 'default': None, 'tip': 'None, or list for y-limits [ymin, ymax] of the plot. (i.e. ylim=[0., 1.])'},
                {'name': 'ylim', 'type': 'str', 'value': None, 'default': None, 'tip': 'None, or list for x-limits [xmin, xmax] of the plot. (i.e. xlim=[-0.5, 0.5])'},
                {'name': 'axeslabel_fontsize', 'type': 'float', 'value': 10., 'default': 10., 'tip': ''},
                {'name': 'axesvalues_fontsize', 'type': 'float', 'value': 10., 'default': 10., 'tip': ''},
                {'name': 'title_fontsize', 'type': 'float', 'value': 20., 'default': 20., 'tip': ''},
                {'name': 'annotation_fontsize', 'type': 'float', 'value': 10., 'default': 10., 'tip': ''},
                {'name': 'legend_fontsize', 'type': 'float', 'value': 8., 'default': 8., 'tip': ''},
                {'name': 'HYDR_VALS', 'type': 'text', 'value': "#{'MThw':  2.28,\n# 'MTnw': -1.57,\n# 'NNTnw': -3.42,\n# 'HThw':  4.99,\n# 'MspTnw': -1.87}\nNone", 'default': "#{'MThw':  2.28,\n# 'MTnw': -1.57,\n# 'NNTnw': -3.42,\n# 'HThw':  4.99,\n# 'MspTnw': -1.87}\nNone", 'tip': 'WORKS ONLY IF `trendlinemode` is not None !!!\nDictionary with special hydrological values', 'expanded': False},
            ]},
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


        listWithDicts = evaluateDict(state['children'], functionToDicts=evaluationFunction, log=False,
            function4arguments=plot_pandas.plot_pandas_scatter_special1)
        kwargs = dict()
        for d in listWithDicts:
            # {'a': None}.items() => [('a', None)] => two times indexing
            kwargs[d.items()[0][0]] = d.items()[0][1]

        kwargs['x'] = [state['children']['X: River WL']['value']]
        kwargs['y'] = [state['children']['Y: Well GWL']['value']]
        if kwargs['trendlinemode'] == 'None': kwargs['trendlinemode'] = None
        if kwargs['title'] == 'None': kwargs['title'] = None
        if kwargs['xlabel'] == 'None': kwargs['xlabel'] = None
        if kwargs['ylabel'] == 'None': kwargs['ylabel'] = None

        return kwargs
