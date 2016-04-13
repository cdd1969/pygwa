from __future__ import print_function
from collections import OrderedDict
import sys
import os

import PROJECTMETA
import pyqtgraph
from scipy import __version__ as scipy_ver
from numpy import __version__ as numpy_ver
from pandas import __version__ as pandas_ver
from matplotlib import __version__ as matplotlib_ver
from seaborn import __version__ as seaborn_ver
from openpyxl import __version__ as openpyxl_ver

from sip import SIP_VERSION_STR


BASEDIR = os.path.dirname(sys.argv[0])


def projectPath(*relative_path):
    return os.path.join(BASEDIR, *relative_path)

def version_info():
    V = OrderedDict()
    V['pygwa'] = PROJECTMETA.__version__
    V['Qt'] = pyqtgraph.Qt.QtCore.QT_VERSION_STR
    V['SIP'] = SIP_VERSION_STR
    V['PyQt'] = pyqtgraph.Qt.Qt.PYQT_VERSION_STR
    V['pyqtgraph'] = pyqtgraph.__version__
    V['scipy'] = scipy_ver
    V['numpy'] = numpy_ver
    V['pandas'] = pandas_ver
    V['matplotlib'] = matplotlib_ver
    V['seaborn'] = seaborn_ver
    V['openpyxl'] = openpyxl_ver
    return V

if __name__ == '__main__':


    print("Qt version:", QT_VERSION_STR)
    print("SIP version:", SIP_VERSION_STR)
    print("PyQt version:", PYQT_VERSION_STR)
