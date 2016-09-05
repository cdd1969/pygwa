#!/usr/bin python
# -*- coding: utf-8 -*-
from __future__ import division
import os, sys
from PyQt5 import uic, QtCore, QtWidgets
import numpy as np
from pyqtgraph import BusyCursor
from lib.functions.tide import generate_tide
from lib.functions.general import isNumpyNumeric
from pyqtgraph.flowchart.Node import Node
from pyqtgraph import functions as fn
from lib.common.state_saver_loader import SaveWidgetState, RestoreWidgetState
import logging
logger = logging.getLogger(__name__)


beta = 4.8e-10
rho = 1000.
g = 9.81


class genCurveNode_v2(Node):
    """Generate Signal based on different governing equations"""
    nodeName = "Generate Signal (v2)"

    def __init__(self, name, parent=None):
        terms = {'tides': {'io': 'in'}, 'sig': {'io': 'out'}}
        super(genCurveNode_v2, self).__init__(name, terminals=terms)
        self.graphicsItem().setBrush(fn.mkBrush(250, 250, 150, 150))
        self._ctrlWidget = genCurveNodeCtrlWidget(self)

        self._tides_id = None

    def process(self, tides):
        df = None

        if id(tides) != self._tides_id:
            logger.debug('clearing genCurveNodeCtrlWidget_v2 (Tide Components Section) on_process()')
            #print 'setting tides components'
            self._tides_id = id(tides)
            self.ctrlWidget().clearTideComponents()
            self.ctrlWidget().on_tides_received(tides)


        kwargs = self.ctrlWidget().prepareInputArguments()
        with BusyCursor():
            if kwargs['eq'] == 'tide':
                df = generate_tide(kwargs['t0'], kwargs['dt'], kwargs['tend'], components=kwargs['tides'], W=kwargs['W'], F=kwargs['F'], label=kwargs['label'], equation=kwargs['eq'])
            elif kwargs['eq'] == 'ferris':
                df = generate_tide(kwargs['t0'], kwargs['dt'], kwargs['tend'], components=kwargs['tides'], W=kwargs['W'], F=kwargs['F'], label=kwargs['label'], equation=kwargs['eq'],
                    D=kwargs['ferris']['D'], x=kwargs['x'])
            elif kwargs['eq'] == 'xia':
                df = generate_tide(kwargs['t0'], kwargs['dt'], kwargs['tend'], components=kwargs['tides'], W=kwargs['W'], F=kwargs['F'], label=kwargs['label'], equation=kwargs['eq'],
                    x=kwargs['x'],
                    alpha=kwargs['xia']['alpha'], beta=kwargs['xia']['beta'], theta=kwargs['xia']['theta'],
                    L=kwargs['xia']['L'], K1=kwargs['xia']['K1'], b1=kwargs['xia']['b1'],
                    K=kwargs['xia']['K'], b=kwargs['xia']['b'],
                    K_cap=kwargs['xia']['K_cap'], b_cap=kwargs['xia']['b_cap'])
            elif kwargs['eq'] == 'song':
                #df = generate_tide()
                pass
            else:
                df = None

        return {'sig': df}


    def ctrlWidget(self):
        return self._ctrlWidget

    def saveState(self):
        """overwriting stadart Node method to extend it with saving ctrlWidget state"""
        state = Node.saveState(self)
        # sacing additionaly state of the control widget
        state['crtlWidget'] = self.ctrlWidget().saveState()
        return state
        
    def restoreState(self, state):
        """overwriting stadart Node method to extend it with restoring ctrlWidget state"""
        Node.restoreState(self, state)
        # additionally restore state of the control widget
        self.ctrlWidget().restoreState(state['crtlWidget'])





class genCurveNodeCtrlWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(genCurveNodeCtrlWidget, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'generate_signal.ui'), self)
        self._parent = parent

        self.init_connections()
        self.init_widget_params()

        self.cb_eq.setCurrentIndex(0)  # to propagate changes

        # here I define the list of widgets, which state will be saved when the method `saveState()` is called
        self._widgets2save = [
            self.sb_main_factor,
            self.sb_main_const,
            self.cb_eq,
            self.sb_x,
            self.le_label,
            self.dt_start,
            self.dt_end,
            self.sb_timestep,

            self.sb_ferris_d,

            self.sb_xia_L_roof,
            self.cb_xia_inf_L,
            self.sb_xia_kf_roof,
            self.sb_xia_b_roof,
            self.sb_xia_kf_cap,
            self.sb_xia_b_cap,
            self.sb_xia_kf_aq,
            self.sb_xia_b_aq,
            self.sb_xia_a_aq,
            self.sb_xia_ne_aq,
        ]



    def init_widget_params(self):
        # init metric widget params
        #self.sb_x.setOpts(dec=True, minStep=0.1)
        #self.sb_xia_L_roof.setOpts(dec=True, minStep=0.1)
        #self.sb_xia_b_roof.setOpts(dec=True, minStep=0.1)
        
        # init diffusivity widget parameters
        opts = {
            'dec': True,
            'minStep': 1.e-10,
        }
        self.sb_ferris_d.setOpts(**opts)
        self.sb_xia_kf_roof.setOpts(value=1.e-7, **opts)
        self.sb_xia_kf_cap.setOpts(value=1.e-9, **opts)
        self.sb_xia_kf_aq.setOpts(value=5.e-4, **opts)
        self.sb_xia_a_aq.setOpts(value=1.e-8, **opts)
        
        self.sb_xia_Ss.setOpts(**opts)
        self.sb_xia_Ss.setReadOnly(True)
        self.sb_xia_D.setOpts(**opts)
        self.sb_xia_D.setReadOnly(True)

    def init_connections(self):
        self.sb_xia_Ss.valueChanged.connect(self.update_xia_D)
        self.sb_xia_kf_aq.valueChanged.connect(self.update_xia_D)
        self.sb_xia_a_aq.valueChanged.connect(self.update_xia_Ss)
        self.sb_xia_ne_aq.valueChanged.connect(self.update_xia_Ss)

        # --------------------------------------------------------------------
        # here I define the list of widgets, which's change of value will cause calculation of the signal
        self.sb_main_factor.valueChanged.connect(self.nodeUpdateRequred)
        self.sb_main_const.valueChanged.connect(self.nodeUpdateRequred)
        self.cb_eq.currentIndexChanged.connect(self.nodeUpdateRequred)
        self.sb_x.valueChanged.connect(self.nodeUpdateRequred)
        self.le_label.textChanged.connect(self.nodeUpdateRequred)
        self.dt_start.dateTimeChanged.connect(self.nodeUpdateRequred)
        self.dt_end.dateTimeChanged.connect(self.nodeUpdateRequred)
        self.sb_timestep.valueChanged.connect(self.nodeUpdateRequred)

        self.cb_tides_A.currentIndexChanged.connect(self.nodeUpdateRequred)
        self.cb_tides_omega.currentIndexChanged.connect(self.nodeUpdateRequred)
        self.cb_tides_phi.currentIndexChanged.connect(self.nodeUpdateRequred)

        self.sb_ferris_d.valueChanged.connect(self.nodeUpdateRequred)

        self.sb_xia_L_roof.valueChanged.connect(self.nodeUpdateRequred)
        self.cb_xia_inf_L.stateChanged.connect(self.nodeUpdateRequred)
        self.sb_xia_kf_roof.valueChanged.connect(self.nodeUpdateRequred)
        self.sb_xia_b_roof.valueChanged.connect(self.nodeUpdateRequred)
        self.sb_xia_kf_cap.valueChanged.connect(self.nodeUpdateRequred)
        self.sb_xia_b_cap.valueChanged.connect(self.nodeUpdateRequred)
        self.sb_xia_kf_aq.valueChanged.connect(self.nodeUpdateRequred)
        self.sb_xia_b_aq.valueChanged.connect(self.nodeUpdateRequred)
        self.sb_xia_a_aq.valueChanged.connect(self.nodeUpdateRequred)
        self.sb_xia_ne_aq.valueChanged.connect(self.nodeUpdateRequred)
        # --------------------------------------------------------------------

    def saveState(self):
        STATE = {}

        for widget in self._widgets2save:
            STATE[widget.objectName()] = SaveWidgetState(widget)
        return STATE
    
    def restoreState(self, state):
        for widget_name, widget_state in state.iteritems():
            child = self.findChild(QtWidgets.QWidget, name=widget_name)
            if child:
                #print 'restoring state of widget [{0}]'.format(widget_name)
                RestoreWidgetState(child, widget_state)

    def clearTideComponents(self):
        '''
            Call this method, when you want to clear the ComboBoxes
            in the `Tide Components` GroupBox. This is usefull, when
            a new data set is received by the parent Node.

            After this, you would probably want to populate the ComboBoxes
            with new data

            See method `on_tides_received()`
        '''
        self.cb_tides_A.clear()
        self.cb_tides_omega.clear()
        self.cb_tides_phi.clear()
        self.le_n_tides.setText('')
        self.sb_main_const.setValue(0.0)

    def on_tides_received(self, tides):
        '''
            Populate nessesary widgets whith the information
            from the DataFrame

            Args:
                tides (pd.DataFrame):
                    Specially designed dataframe. See docs
        '''
        self.le_n_tides.setText(str(len(tides)-1))
        
        colnames = [col for col in tides.columns if isNumpyNumeric(tides[col].dtype)]
        self.cb_tides_A.addItems(colnames)
        self.cb_tides_omega.addItems(colnames)
        self.cb_tides_phi.addItems(colnames)

        self.cb_tides_A.setCurrentIndex(0)
        self.cb_tides_omega.setCurrentIndex(1)
        self.cb_tides_phi.setCurrentIndex(2)

        W = tides[self.cb_tides_A.currentText()][0]  # 1st value from column `A`
        self.sb_main_const.setValue(W)

    @QtCore.pyqtSlot(int)
    def on_cb_eq_currentIndexChanged(self, index):
        '''
            Update the allowed X ranges
        '''
        self.sb_x.setEnabled(True)
        
        if index == 0:
            # simple tide
            self.sb_x.setEnabled(False)
        elif index in [1, 3]:
            # ferris, song
            self.sb_x.setMinimum(0.0)
        elif index in [2,]:
            # xia
            self.sb_x.setMinimum(max( (-10000.0, -self.sb_xia_L_roof.value()) ))

    @QtCore.pyqtSlot(float)
    def on_sb_xia_L_roof_valueChanged(self, value):
        '''
            Update the allowed X ranges
        '''
        if self.cb_eq.currentIndex() == 2:  # Xia
            self.sb_x.setMinimum(-value)

    @QtCore.pyqtSlot(QtCore.QDateTime)
    def on_dt_start_dateTimeChanged(self, datetime):
        '''
            Update the minimum date of the stop-QDateTimeEdit
        '''
        self.dt_end.setMinimumDateTime(datetime)

    @QtCore.pyqtSlot(float)
    def update_xia_Ss(self, value):
        alpha = self.sb_xia_a_aq.value()
        theta = self.sb_xia_ne_aq.value()
        Ss = rho*g*(alpha + beta*theta)
        self.sb_xia_Ss.setValue(Ss)

    @QtCore.pyqtSlot(float)
    def update_xia_D(self, value):
        Kf = self.sb_xia_kf_aq.value()
        Ss = self.sb_xia_Ss.value()
        if Ss != 0.:
            D = Kf / Ss
        else:
            D = 0.
        self.sb_xia_D.setValue(D)

    def nodeUpdateRequred(self, value=None):
        '''
            A helper method, that is used to connect `valueChanged` signal of a widget
            with the `update()` method of the Node. We cannot do it directly since the
            signal `valueChanged` is overloaded
        '''
        self._parent.update()

    def prepareInputArguments(self):
        kwargs = dict()

        if self.cb_eq.currentIndex() == 0:
            kwargs['eq']    = 'tide'
        elif self.cb_eq.currentIndex() == 1:
            kwargs['eq']    = 'ferris'
        elif self.cb_eq.currentIndex() == 2:
            kwargs['eq']    = 'xia'
        elif self.cb_eq.currentIndex() == 3:
            kwargs['eq']    = 'song'

        kwargs['W']     = self.sb_main_const.value()
        kwargs['F']     = self.sb_main_factor.value()

        kwargs['t0']    = np.datetime64(self.dt_start.dateTime().toString() + 'Z')  # zulu time
        kwargs['dt']    = np.timedelta64(self.sb_timestep.value(), 's')
        kwargs['tend']  = np.datetime64(self.dt_end.dateTime().toString + 'Z')  # zulu time
        kwargs['label'] = self.le_label.text()
        
        kwargs['df_A']     = self.cb_tides_A.currentText()
        kwargs['df_omega'] = self.cb_tides_omega.currentText()
        kwargs['df_phi']   = self.cb_tides_phi.currentText()
        
        kwargs['x']   = self.sb_x.value()

        # --------  Ferris ------
        kwargs['ferris'] = {}
        kwargs['ferris']['D'] = self.sb_ferris_d.value()

        # --------  XIA ------
        kwargs['xia'] = {}
        kwargs['xia']['alpha']  = self.sb_xia_a_aq.value()
        kwargs['xia']['beta']   = beta
        kwargs['xia']['theta']  = self.sb_xia_ne_aq.value()
        kwargs['xia']['K']      = self.sb_xia_kf_aq.value()
        kwargs['xia']['b']      = self.sb_xia_b_aq.value()
        kwargs['xia']['K1']     = self.sb_xia_kf_roof.value()
        kwargs['xia']['b1']     = self.sb_xia_b_roof.value()
        kwargs['xia']['K_cap']  = self.sb_xia_kf_cap.value()
        kwargs['xia']['b_cap']  = self.sb_xia_b_cap.value()
        kwargs['xia']['L']      = self.sb_xia_L_roof.value() if not self.cb_xia_inf_L.isChecked() else float('inf')
        return kwargs