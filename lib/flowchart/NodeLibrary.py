# these imports are for creating custom Node-Library
import pyqtgraph.flowchart.library as fclib
import os
import json
from lib.functions.importFromURI import importFromURI
from lib import projectPath


def readNodeFile(fname):
    """ Function reads JSON node register file (*.node) and
    return the data stored in it as a dictionary. Additionally
    converts the relative name in `filename` to absolute.

    Args:
    -----
        fname (str):
            path to the *.node file (file must has JSON syntax)

    Return:
    -------
        data (dict[str, list[str]]):
            {'filename': '...',
             'classname': '...',
             'libpath': ['...', '...']}
    """
    # >>> Read *.node File
    fname = os.path.abspath(fname)
    if not os.path.exists(fname):
        raise EOFError('File doesnt exist {1}'.format(fname))
    if os.path.splitext(fname)[1] != '.node':
        raise EOFError('Invalid extension. Must be `.node`. Received {1}'.format(fname))
    
    with open(fname) as node_file:
        data = json.load(node_file)

    for attr in [u'filename', u'classname', u'libpath']:
        if attr not in data.keys():
            raise EOFError('Parameter `{0}` not found in file {1}'.format(attr, fname))

    data['filename'] = os.path.join(os.path.dirname(fname), data['filename'])
    return data


def importNodeClass(data, absl=False):
    """ Functions imports given class data['calssname']
    from a given module data['filename'] dynamically.

    Args:
    -----
        data (dict):
            {'filename': 'my_module.py',
             'classname': 'myClass'}
        absl (bool):
            flag to treat data['filename']
            as absolute path

    Return:
    -------
        nodeClass (class):
            alias to the imported class
    """
    # >>> load python module
    module = importFromURI(data['filename'], absl=absl)
    if not hasattr(module, data['classname']):
        print ('Warning! module {0} doesnot have attribute {1}'.format(module, data['classname']))
    nodeClass = getattr(module, data['classname'])
    return nodeClass


def registerNode(library, fname):
    """ Procedure registers node in a given `library`. The
    node is described in file `fname`.

    Args:
    -----
        library (pyqtgraph.NodeLibrary):
            library to which the node will be registered

        fname (str):
            path to the *.node file (file must has JSON syntax)
    """
    data = readNodeFile(fname)
    nodeClass = importNodeClass(data, absl=True)
    library.addNodeType(nodeClass, [tuple(data['libpath'])], override=data.get('override', True))


def nodelib():
    del fclib.NODE_TREE['Filters']  # remove Filters from the list of available nodes
    del fclib.NODE_TREE['Operators']  # remove Operators from the list of available nodes
    del fclib.NODE_TREE['Display']['CanvasWidget']  # remove Operators from the list of available nodes
    del fclib.NODE_TREE['Display']['PlotWidget']  # remove Operators from the list of available nodes
    del fclib.NODE_TREE['Display']['ScatterPlot']  # remove Operators from the list of available nodes
    #del fclib.NODE_TREE['Filter']['PythonEval']  # remove PythonEval from the list of available nodes

    
    flowchartLib = fclib.LIBRARY.copy()  # start with the default node set

    with open(projectPath('resources/defaultLibrary.json')) as lib_file:
        data = json.load(lib_file)
    
    for k, nodeRegFile in data.iteritems():
        if not k.startswith('_'):
            registerNode(flowchartLib, nodeRegFile)

    return flowchartLib
