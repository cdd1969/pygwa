from __future__ import print_function
import sys
import os


from flowchart.package import Package as Package

BASEDIR = os.path.dirname(sys.argv[0])


def projectPath(*relative_path):
    return os.path.join(BASEDIR, *relative_path)

if __name__ == '__main__':
    from PyQt5.QtCore import QT_VERSION_STR
    from PyQt5.Qt import PYQT_VERSION_STR
    from sip import SIP_VERSION_STR

    print("Qt version:", QT_VERSION_STR)
    print("SIP version:", SIP_VERSION_STR)
    print("PyQt version:", PYQT_VERSION_STR)
