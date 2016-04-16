#!/usr/bin python
# -*- coding: utf-8 -*-
from lib.functions import plot_pandas
from lib.functions.general import isNumpyNumeric
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget


class plotHistNode(NodeWithCtrlWidget):
    """Plot Histogram and Cumulative Histogram of an Array"""
    nodeName = "Plot Histogram"
    uiTemplate = [
            {'name': 'Signal', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Name of the column with an array to be evaluated'},
            {'name': 'Signal Units', 'type': 'str', 'value': u'm AMSL', 'default': u'', 'tip': 'Units of the `Signal` to be displayed'},
            {'name': 'Histogram Type', 'type': 'list', 'value': 'Frequency', 'values': ['Frequency', 'Relative Frequency', 'Normalized'], 'tip': 'Type of the histogram.'},
            {'name': 'Bins', 'type': 'int', 'value': 10, 'default': 10, 'step': 1, 'limits': (1, 200), 'tip': 'Number of bins for building histogram'},
            {'name': 'Bin Width', 'type': 'str', 'value': '', 'tip': 'Bin width', 'readonly': True},
            {'name': 'Max', 'type': 'str', 'value': '', 'tip': 'Maximum value of passed `Signal`', 'readonly': True},
            {'name': 'Min', 'type': 'str', 'value': '', 'tip': 'Minimum value of passed `Signal`', 'readonly': True},
            {'name': 'Mean', 'type': 'str', 'value': '', 'tip': 'Mean value of passed `Signal`', 'readonly': True},
            {'name': 'Median', 'type': 'str', 'value': '', 'tip': 'Median value of passed `Signal`', 'readonly': True},
            {'name': 'STD', 'type': 'str', 'value': '', 'tip': 'Standard deviation of passed `Signal`', 'readonly': True},
            {'name': 'Plot', 'type': 'action'},
        ]

    def __init__(self, name, parent=None):
        super(plotHistNode, self).__init__(name, parent=parent, terminals={'In': {'io': 'in'}}, color=(150, 150, 250, 150))

    def _createCtrlWidget(self, **kwargs):
        return plotHistNodeCtrlWidget(**kwargs)
        
    def process(self, In):
        df = In
        if df is not None:
            # when we recieve a new dataframe into terminal - update possible selection list
            if not self._ctrlWidget.plotAllowed():
                colname = [col for col in df.columns if isNumpyNumeric(df[col].dtype)]
                self._ctrlWidget.param('Signal').setLimits(colname)
                
                column = self._ctrlWidget.param('Signal').value()
                Max = df[column].max()
                Min = df[column].min()
                MU  = df[column].mean()
                ME  = df[column].median()
                STD  = df[column].std()
                NBins = self._ctrlWidget.param('Bins').value()
                self._ctrlWidget.param('Max').setValue('{0:.3f}'.format(Max))
                self._ctrlWidget.param('Min').setValue('{0:.3f}'.format(Min))
                self._ctrlWidget.param('Mean').setValue('{0:.3f}'.format(MU))
                self._ctrlWidget.param('Median').setValue('{0:.3f}'.format(ME))
                self._ctrlWidget.param('STD').setValue('{0:.3f}'.format(STD))
                self._ctrlWidget.param('Bin Width').setValue('{0:.3f}'.format((Max-Min)/float(NBins)))
            
            if self._ctrlWidget.plotAllowed():
                kwargs = self.ctrlWidget().prepareInputArguments()
                plot_pandas.plot_statistical_analysis(df[kwargs['Signal']],
                    plot_title='Original Signal: {0}'.format(kwargs['Signal']),
                    bins=kwargs['Bins'],
                    data_units=kwargs['Signal Units'],
                    hist_type=kwargs['Histogram Type'])
        else:
            self._ctrlWidget.param('Signal').setLimits([''])
            self._ctrlWidget.param('Max').setValue('')
            self._ctrlWidget.param('Min').setValue('')
            self._ctrlWidget.param('Mean').setValue('')
            self._ctrlWidget.param('Median').setValue('')
            self._ctrlWidget.param('STD').setValue('')
            self._ctrlWidget.param('Bin Width').setValue('')


class plotHistNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(plotHistNodeCtrlWidget, self).__init__(update_on_statechange=False, **kwargs)
        self._plotAllowed = False

    def initUserSignalConnections(self):
        self.param('Plot').sigActivated.connect(self.on_plot_clicked)
        self.param('Signal').sigValueChanged.connect(self._parent.update)
        self.param('Bins').sigValueChanged.connect(self._parent.update)
        
        self.disconnect_valueChanged2upd(self.param('Bins'))

    def on_plot_clicked(self):
        self._plotAllowed = True
        self._parent.update()
        self._plotAllowed = False

    def plotAllowed(self):
        return self._plotAllowed

    def prepareInputArguments(self):
        validArgs = ['Signal', 'Signal Units', 'Histogram Type', 'Bins']
        kwargs = dict()
        for param in self.params(ignore_groups=True):
            if param.name() in validArgs:
                kwargs[param.name()] = self.p.evaluateValue(param.value())
        return kwargs
