import os, sys
import traceback
from pyqtgraph.Qt import QtGui


class ErrorPopupMessagBox(object):
    '''
    This is a class to pop up QMessageBox.critical().
    Optionally display nicely the traceback of the last error.
    '''
    def __init__(self, parent=None, title='', text='Error!', include_traceback=True):
        if include_traceback:
            tb_msg = '<br><br><hr>{0}<br><br><font color="red"><i>{1}</i></font>'.format(
                    '<br>'.join(traceback.format_tb(sys.exc_info()[2])),
                    '<br>'.join(traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], None)))
            text = text+tb_msg

        QtGui.QMessageBox.critical(parent, 'Critical Error: '+title, text)
        return None
