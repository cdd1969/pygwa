#!/usr/bin python
# -*- coding: utf-8 -*-
from lib.functions.plot_pandas import plot_direction_rose
from lib.functions.general import isNumpyNumeric
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget
from pyqtgraph.Qt import QtGui


class plotCircularHistNode(NodeWithCtrlWidget):
    """Plot Circular (Direction) Histogram (directions in degrees). Be aware of the data's polar coordinate system (theta0 and positive direction)"""
    nodeName = "Plot Circular Histogram"
    uiTemplate = [
            {'name': 'Bearing', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Name of the column with an array of bearing values. North - 0 degrees, East - 90 degrees.\nValues must be in range 0 to 360'},
            
            {'name': 'Bins', 'type': 'int', 'value': 24, 'default': 24, 'step': 1, 'limits': (1, 360), 'tip': 'Number of bins for building the histogram'},
            {'name': 'Bin Width', 'type': 'str', 'value': '', 'suffix': 'degrees', 'tip': 'Bin width', 'readonly': True},
            {'name': 'Max', 'type': 'str', 'value': '', 'tip': 'Maximum value of passed `Bearing`', 'readonly': True},
            {'name': 'Min', 'type': 'str', 'value': '', 'tip': 'Minimum value of passed `Bearing`', 'readonly': True},
            {'name': 'Mean', 'type': 'str', 'value': '', 'tip': 'Mean value of passed `Bearing`', 'readonly': True},
            {'name': 'Median', 'type': 'str', 'value': '', 'tip': 'Median value of passed `Bearing`', 'readonly': True},
            {'name': 'STD', 'type': 'str', 'value': '', 'tip': 'Standard deviation of passed `Bearing`', 'readonly': True},
            {'title': 'Theta zero', 'name': 'theta_0', 'type': 'str', 'value': u'N', 'tip': "Sets the location of theta's zero. May be one of 'N', 'NW', 'W', 'SW', 'S', 'SE', 'E', or 'NE'."},
            {'title': 'Theta direction', 'name': 'theta_dir', 'type': 'int', 'value': -1, 'tip': "Direction of the positive theta. If `1` -- counterclockwise. If `-1` -- clockwise"},
            {'title': 'Theta grid values', 'name': 'theta_grid_values', 'type': 'str', 'value': u'0, 45, 90, 135, 180, 225, 270, 315', 'tip': "Grid-values to draw on the angular grid (comma-separated integers).\nExample:\n0, 45, 90, 135, 180, 225, 270, 315"},
            {'title': 'Theta grid labels', 'name': 'theta_grid_labels', 'type': 'str', 'value': u'N, NE, E, SE, S, SW, W, NW', 'tip': "Grid-labels to draw on the corresponding grid values (comma-separated strings).\nExample:\nN, NE, E, SE, S, SW, W, NW"},
            {'title': 'Add line subplot', 'name': 'add_l_plt', 'type': 'bool', 'value': True, 'tip': 'Plot additionally the original bearing signal as a line graph.'},
            {'title': 'Radial Label Position', 'name': 'r_label_pos', 'type': 'int', 'value': 90, 'tip': "Rotation angle of the radial axis values, with respect to the theta_zero"},
            {'title': 'Relative histogram', 'name': 'relative_hist', 'type': 'bool', 'value': True, 'tip': 'flag to print relative histogram values. If `False` will plot real number of occurences in histogram-bins'},
            {'title': 'Bottom Percentage', 'name': 'bottom', 'type': 'int', 'value': 0, 'tip': "Works only if RELATIVE_HISTOGRAM is True !\nNumber of units (current units of circular histogram), to skip, before drawing the histogram, \ne.g. if BOTTOM=0 -- draw from the circle center; \nif BOTTOM=5 -- skip 5 units and begin drawing from there."},
            {'name': 'Plot', 'type': 'action'},
        ]

    def __init__(self, name, parent=None):
        super(plotCircularHistNode, self).__init__(name, parent=parent, terminals={'In': {'io': 'in'}}, color=(150, 150, 250, 150))

    def _createCtrlWidget(self, **kwargs):
        return plotCircularHistNodeCtrlWidget(**kwargs)
        
    def process(self, In):
        df = In
        if df is not None:
            # when we recieve a new dataframe into terminal - update possible selection list
            if not self._ctrlWidget.plotAllowed():
                colname = [col for col in df.columns if isNumpyNumeric(df[col].dtype)]
                self._ctrlWidget.param('Bearing').setLimits(colname)
                
                column = self._ctrlWidget.param('Bearing').value()
                Max = df[column].max()
                Min = df[column].min()
                MU  = df[column].mean()
                ME  = df[column].median()
                STD = df[column].std()
                NBins = self._ctrlWidget.param('Bins').value()
                self._ctrlWidget.param('Max').setValue('{0:.3f}'.format(Max))
                self._ctrlWidget.param('Min').setValue('{0:.3f}'.format(Min))
                self._ctrlWidget.param('Mean').setValue('{0:.3f}'.format(MU))
                self._ctrlWidget.param('Median').setValue('{0:.3f}'.format(ME))
                self._ctrlWidget.param('STD').setValue('{0:.3f}'.format(STD))
                self._ctrlWidget.param('Bin Width').setValue('{0:.3f}'.format(360./float(NBins)))
            
            if self._ctrlWidget.plotAllowed():
                kwargs = self.ctrlWidget().prepareInputArguments()

                # check that data is in range [0 to 360]
                MIN = df[kwargs['Bearing']].min()
                MAX = df[kwargs['Bearing']].max()
                
                if MAX > 360. or MAX < 0. or MIN < 0. or MIN > 360.:
                    msg = 'Note that the data you are going to plot is most likely not the directions, since the MIN={0} and MAX={1}. It is expected that the data-values fall in range [0:360].\nThe figure will be plotted anyway. Continuing...'.format(MIN, MAX)
                    QtGui.QMessageBox.warning(None, "Node: {0}".format(self.nodeName), msg)
                
                plot_direction_rose(df, COLNAME=kwargs['Bearing'],
                    N=kwargs['Bins'], RELATIVE_HIST=kwargs['relative_hist'],
                    PLOT_LINE_SUBPLOT=kwargs['add_l_plt'],
                    R_FONTSIZE='x-small',
                    THETA_DIRECTION=kwargs['theta_dir'], THETA_ZERO_LOCATION=kwargs['theta_0'],
                    THETA_GRIDS_VALUES=kwargs['theta_grid_values'],
                    THETA_GRIDS_LABELS=kwargs['theta_grid_labels'],
                    R_LABEL_POS=kwargs['r_label_pos'], BOTTOM=kwargs['bottom'])
        else:
            self._ctrlWidget.param('Bearing').setLimits([''])
            self._ctrlWidget.param('Max').setValue('')
            self._ctrlWidget.param('Min').setValue('')
            self._ctrlWidget.param('Mean').setValue('')
            self._ctrlWidget.param('Median').setValue('')
            self._ctrlWidget.param('STD').setValue('')
            self._ctrlWidget.param('Bin Width').setValue('')


class plotCircularHistNodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(plotCircularHistNodeCtrlWidget, self).__init__(update_on_statechange=False, **kwargs)
        self._plotAllowed = False

    def initUserSignalConnections(self):
        self.param('Plot').sigActivated.connect(self.on_plot_clicked)
        self.param('Bearing').sigValueChanged.connect(self._parent.update)
        self.param('Bins').sigValueChanged.connect(self._parent.update)
        
        #self.disconnect_valueChanged2upd(self.param('Bins'))

    def on_plot_clicked(self):
        self._plotAllowed = True
        self._parent.update()
        self._plotAllowed = False

    def plotAllowed(self):
        return self._plotAllowed

    def prepareInputArguments(self):
        validArgs = ['Bearing', 'Bins', 'add_l_plt', 'relative_hist', 'theta_dir', 'theta_0',
                    'theta_grid_values', 'theta_grid_labels', 'r_label_pos', 'bottom']
        kwargs = dict()
        for param in self.params(ignore_groups=True):
            if param.name() in validArgs:
                #kwargs[param.name()] = self.p.evaluateValue(param.value())
                kwargs[param.name()] = param.value()

        try:
            kwargs['theta_grid_values'] = [int(x.strip()) for x in kwargs['theta_grid_values'].split(',')]
        except:
            lst = '0, 45, 90, 135, 180, 225, 270, 315'
            msg = 'Cannot convert `theta_grid_values` {0} of type {2} to a list of integers. Will use the default list:\n{1}'.format(kwargs['theta_grid_values'], lst, type(kwargs['theta_grid_values']))
            QtGui.QMessageBox.warning(None, "Node: {0}".format(self.parent().nodeName), msg)
            kwargs['theta_grid_values'] = [int(x.strip()) for x in lst.split(',')]
        try:
            kwargs['theta_grid_labels'] = [str(x.strip()) for x in kwargs['theta_grid_labels'].split(',')]
        except:
            lst = 'N, NE, E, SE, S, SW, W, NW'
            msg = 'Cannot convert `theta_grid_labels` {0} of type {2} to a list of strings. Will use the default list:\n{1}'.format(kwargs['theta_grid_labels'], lst, type(kwargs['theta_grid_labels']))
            QtGui.QMessageBox.warning(None, "Node: {0}".format(self.parent().nodeName), msg)
            kwargs['theta_grid_labels'] = [str(x.strip()) for x in lst.split(',')]

        if len(kwargs['theta_grid_values']) != len(kwargs['theta_grid_labels']):
            msg = 'Number of values `theta_grid_values` {0} does not correspond to the number of labels `theta_grid_labels` {1}'.format(kwargs['theta_grid_values'], kwargs['theta_grid_labels'])
            QtGui.QMessageBox.warning(None, "Node: {0}".format(self.parent().nodeName), msg)
        return kwargs
