#!/usr/bin python
# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtCore
from pyqtgraph import BusyCursor

from lib.functions import plot_pandas
from lib.functions.general import returnPandasDf, getCallableArgumentList, isNumpyNumeric
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget


class plotGWLvsWLNode(NodeWithCtrlWidget):
    """Plot Growundwater-level VS River water-level (matplotlib) or so-called overhead"""
    nodeName = "Plot Overhead"
    uiTemplate = [
            {'title': 'X: River WL', 'name': 'x', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Name of the column with river waterlevel data.\nWill be plotted on X-axis'},
            {'title': 'Y: Well GWL', 'name': 'y', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Name of the column with well groundwater-level\ndata. It will be plotted on Y-axis'},
            {'name': 'plot overheads', 'type': 'bool', 'value': False, 'default': False, 'tip': 'If checked, will substract X-values from Y-values element-wise (Yvalues-Xvalues) before\nplotting. This means that so called "overheads" will be plotted on Y-axis and not the\nactual groundwater-levels.\nIf not checked - plots real values of Y-column'},
            {'title': 'trendline', 'name': 'trendlinemode', 'type': 'list', 'value': 'None', 'default': 'None', 'values': ['Normal', 'Shifted', 'None'], 'tip': 'Normal - draw trendlines using all data points\nShifted - draw trendlines using all data points, and shift them to the most-far-lying point\nNone - do not draw trendline'},

            {'name': 'Hydrological Values', 'type': 'bool', 'expanded': False, 'children': [
                {'name': 'MHW', 'type': 'float', 'limits': (-25., 25.), 'step': 0.1, 'tip': 'Mean High Water (ger. MThw)'},
                {'name': 'MLW', 'type': 'float', 'limits': (-25., 25.), 'step': 0.1, 'tip': 'Mean Low Water (ger. MTnw)'},
                {'name': 'MLWS', 'type': 'float', 'limits': (-25., 25.), 'step': 0.1, 'tip': 'Mean Low Water Springs (ger. MSpTnw)'},
                {'name': 'LLW', 'type': 'float', 'limits': (-25., 25.), 'step': 0.1, 'tip': 'Lowest Low Water (ger. NNTnw)'},
            ]},
            {'name': 'Plot Parameters', 'type': 'group', 'expanded': False, 'children': [
                {'name': 'title', 'type': 'str', 'value': None, 'default': None, 'tip': 'Figure title (default None)'},
                {'name': 'title_fontsize', 'type': 'float', 'value': 20., 'default': 20., 'tip': ''},
                {'name': 'xlabel', 'type': 'str', 'value': None, 'default': None, 'tip': 'None, or string for labeling x-axes'},
                {'name': 'ylabel', 'type': 'str', 'value': None, 'default': None, 'tip': 'None, or string for labeling y-axes'},
                {'name': 'axeslabel_fontsize', 'type': 'float', 'value': 10., 'default': 10., 'tip': ''},
                {'name': 'legendlabels', 'type': 'str', 'value': [None], 'default': [None], 'tip': 'List of legendnames or [None]. If default ([None]) - standart names are used'},
                {'name': 'legend_fontsize', 'type': 'float', 'value': 8., 'default': 8., 'tip': ''},
                {'name': 'axesvalues_fontsize', 'type': 'float', 'value': 10., 'default': 10., 'tip': ''},
                {'name': 'annotation_fontsize', 'type': 'float', 'value': 10., 'default': 10., 'tip': 'Fontsize of `Hydrological Values`'},
                {'name': 'marker', 'type': 'list', 'value': 'o', 'default': 'o', 'values': ['o', '.', 'x', '+', 'h'], 'tip': 'marker style for points'},
                {'title': 'marker size', 'name': 's', 'type': 'int', 'value': 10, 'default': 10, 'tip': 'marker point size'},
                {'name': 'xlim', 'type': 'str', 'value': None, 'default': None, 'tip': 'None, or list for x-limits [xmin, xmax] of the plot. (i.e. [0., 1.])'},
                {'name': 'ylim', 'type': 'str', 'value': None, 'default': None, 'tip': 'None, or list for y-limits [ymin, ymax] of the plot. (i.e. [-0.5, 0.5])'},
            ]},
            {'name': 'Plot', 'type': 'action'},
        ]

    def __init__(self, name, parent=None):
        super(plotGWLvsWLNode, self).__init__(name, parent=parent, terminals={'In': {'io': 'in'}}, color=(150, 150, 250, 150))

    def _createCtrlWidget(self, **kwargs):
        return plotGWLvsWLNodeCtrlWidget(**kwargs)
        
    def process(self, In):
        df = returnPandasDf(In)
        if df is not None:
            # when we recieve a new dataframe into terminal - update possible selection list
            if not self._ctrlWidget.plotAllowed():
                colname = [col for col in df.columns if isNumpyNumeric(df[col].dtype)]
                self._ctrlWidget.param('y').setLimits(colname)
                self._ctrlWidget.param('x').setLimits(colname)
            
            if self._ctrlWidget.plotAllowed():
                kwargs = self.ctrlWidget().prepareInputArguments()
                print kwargs, '\n'
                with BusyCursor():
                    if self._ctrlWidget.param('plot overheads').value() is True:
                        y_name = kwargs['y'][0]
                        x_name = kwargs['x'][0]
                        overhead_name = y_name+' - '+x_name
                        df[overhead_name] = df[y_name]-df[x_name]
                        kwargs['y'] = [overhead_name]
                    
                    plot_pandas.plot_pandas_scatter_special1(df, **kwargs)
                    
                    if self._ctrlWidget.param('plot overheads').value() is True:
                        del df[overhead_name]



class plotGWLvsWLNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(plotGWLvsWLNodeCtrlWidget, self).__init__(update_on_statechange=False, **kwargs)
        self._plotAllowed = False

    def initUserSignalConnections(self):
        self.param('Plot').sigActivated.connect(self.on_plot_clicked)

    @QtCore.pyqtSlot()
    def on_plot_clicked(self):
        self._plotAllowed = True
        self._parent.update()
        self._plotAllowed = False

    def plotAllowed(self):
        return self._plotAllowed

    def prepareInputArguments(self):
        validArgs = getCallableArgumentList(plot_pandas.plot_pandas_scatter_special1, get='args')
        validArgs += ['MHW', 'MLW', 'MLWS', 'LLW']
        kwargs = dict()
        for param in self.params(ignore_groups=True):
            if param.name() in validArgs:
                kwargs[param.name()] = self.p.evaluateValue(param.value())

        if kwargs['xlabel'] in [None, 'None', '']: kwargs['xlabel'] = kwargs['x']
        if kwargs['ylabel'] in [None, 'None', '']: kwargs['ylabel'] = kwargs['y']
        kwargs['x'] = [kwargs.pop('x')]
        kwargs['y'] = [kwargs.pop('y')]

        if self.paramValue('Hydrological Values'):
            kwargs['HYDR_VALS'] = dict()
        for name in ['MHW', 'MLW', 'MLWS', 'LLW']:
            if self.paramValue('Hydrological Values'):
                kwargs['HYDR_VALS'][name] = kwargs.pop(name)
            else:
                kwargs.pop(name)

        return kwargs
