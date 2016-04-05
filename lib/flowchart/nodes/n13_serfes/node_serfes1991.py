#!/usr/bin python
# -*- coding: utf-8 -*-
import gc
import copy
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import BusyCursor

from lib.functions import filterSerfes1991 as serfes
from lib.functions.general import isNumpyDatetime, isNumpyNumeric
from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget, NodeCtrlWidget


class serfes1991Node(NodeWithCtrlWidget):
    """Apply Serfes Filter to hydrograph (see Sefes 1991)"""
    nodeName = "Serfes Filter"
    uiTemplate = [
        {'name': 'datetime', 'type': 'list', 'value': None, 'default': None, 'values': [None], 'tip': 'Location of the datetime objects.\nBy default is `None`, meaning that datetime objects are\nlocated within `pd.DataFrame.index`. If not `None` - pass the\ncolumn-name of dataframe where datetime objects are located.\nThis is needed to determine number of measurements per day.\nNote: this argument is ignored if `N` is not `None` !!!'},
        {'name': 'N', 'type': 'str', 'value': None, 'default': None, 'tip': '<int or None>\nExplicit number of measurements in 24 hours. By\ndefault `N=None`, meaning that script will try to determine\nnumber of measurements per 24 hours based on real datetime\ninformation provided with `datetime` argument'},
        {'name': 'Calculate N', 'type': 'action'},
        {'name': 'verbose', 'type': 'bool', 'value': False, 'default': False, 'tip': 'If `True` - will keep all three iterations\nin the output. If `False` - will save only final (3rd) iteration.\nThis may useful for debugging, or checking this filter.'},
        {'title': 'Keep Original Data', 'name': 'keep_origin', 'type': 'bool', 'value': True, 'default': True, 'tip': 'If `True` - will keep original data and append new columns with results.\nIf `False` - will create new table only with results.'},
        {'name': 'log', 'type': 'bool', 'value': False, 'default': False, 'visible': False, 'tip': 'flag to show some prints in console'},
        {'name': 'Apply to columns', 'type': 'group', 'children': []},
        {'name': 'Apply Filter', 'type': 'action'},
        ]

    def __init__(self, name, parent=None):
        super(serfes1991Node, self).__init__(name, parent=parent, color=(250, 250, 150, 150))

    def _createCtrlWidget(self, **kwargs):
        return serfes1991NodeCtrlWidget(**kwargs)
        
    def process(self, In):
        gc.collect()
        # populate USE COLUMNS param, but only on item received, not when we click button
        if not self._ctrlWidget.calculateNAllowed() and not self._ctrlWidget.applyAllowed():
            self._ctrlWidget.param('Apply to columns').clearChildren()
        
        with BusyCursor():
            df = copy.deepcopy(In)
            # check out http://docs.scipy.org/doc/numpy-dev/neps/datetime-proposal.html

            colnames = [col for col in df.columns if isNumpyDatetime(df[col].dtype)]+[None]
            self._ctrlWidget.param('datetime').setLimits(colnames)
            self._ctrlWidget.param('datetime').setValue(colnames[0])

            # populate (Apply to columns) param, but only on item received, not when we click button
            if not self._ctrlWidget.calculateNAllowed() and not self._ctrlWidget.applyAllowed():
                colnames = [col for col in df.columns if isNumpyNumeric(df[col].dtype)]
                for col_name in colnames:  # cycle through each column...
                    self._ctrlWidget.param('Apply to columns').addChild({'name': col_name, 'type': 'bool', 'value': True})

            kwargs = self.ctrlWidget().prepareInputArguments()

            if self._ctrlWidget.calculateNAllowed():
                N = serfes.get_number_of_measurements_per_day(df, datetime=kwargs['datetime'], log=kwargs['log'])
                self._ctrlWidget.param('N').setValue(N)

            if self._ctrlWidget.applyAllowed():
                if kwargs['N'] in [None, '']:
                    QtGui.QMessageBox.warning(None, "Node: {0}".format(self.nodeName), 'First set number of measurements per day in parameter `N`')
                    raise ValueError('First set number of measurements per day in parameter `N`')
                result = serfes.filter_wl_71h_serfes1991(df, **kwargs)
                return {'Out': result}



class serfes1991NodeCtrlWidget(NodeCtrlWidget):
    def __init__(self, **kwargs):
        super(serfes1991NodeCtrlWidget, self).__init__(update_on_statechange=False , **kwargs)
        self._applyAllowed = False
        self._calculateNAllowed = False

    def initUserSignalConnections(self):
        self.param('Apply Filter').sigActivated.connect(self.on_apply_clicked)
        self.param('Calculate N').sigActivated.connect(self.on_calculateN_clicked)
    
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

    def prepareInputArguments(self):
        validArgs = ['datetime', 'N', 'verbose', 'log', 'keep_origin']
        kwargs = dict()
        for param in self.params(ignore_groups=True):
            if param.name() in validArgs:
                kwargs[param.name()] = self.p.evaluateValue(param.value())
        
        # now get usecols
        usecols = list()
        for child in self.param('Apply to columns').children():
            if child.value() is True:
                usecols.append(child.name())
        kwargs['usecols'] = usecols
        return kwargs
