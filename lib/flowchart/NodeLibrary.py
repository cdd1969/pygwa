# these imports are for creating custom Node-Library
import os
import json
from pyqtgraph.flowchart.NodeLibrary import NodeLibrary
from pyqtgraph.flowchart.Node import Node

from lib.functions.importFromURI import importFromURI


def isNodeClass(cls):
    try:
        if not issubclass(cls, Node):
            return False
    except:
        return False
    return hasattr(cls, 'nodeName')
    

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
        raise EOFError('File doesnt exist {0}'.format(fname))
    if os.path.splitext(fname)[1] != '.node':
        raise EOFError('Invalid extension. Must be `.node`. Received {0}'.format(fname))
    
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


class customNodeLibrary(NodeLibrary):
    """
    This class is an extension of pyqtgraph.flowchart.NodeLibrary class:

    Additions:
        - getNodeList()
        - registerExternalNode()
        - buildDefault()
    """

    def __init__(self):
        #super(customNodeLibrary, self).__init__()
        NodeLibrary.__init__(self)  # super is not working because calss NodeLibrary is OldStyle. NewStyle would add inheritance from `object` like this NodeLibrary(object)

    def getNodeList(self):
        return self.nodeList.keys()

    def buildDefault(self, json_lib=None, include_pyqtgraph=False):
        """ Method build default library

        Args:
        -----
            json_lib (str or None):
                URI of the JSON file with links to default nodes
                The file has format:
                    { "_comment": "underscore is ignored",
                      "key1" : "path/to/noderegister/file1.node",
                      "key2" : "path/to/noderegister/file2.node",
                    }
                Keys are not important (keys starting with underscore
                will be ignored)

                If `None` - no file is read

            include_pyqtgraph (bool):
                flag to inculude default pyqtgraph node library
        """
        if include_pyqtgraph:
            # Add all nodes to the default library
            from pyqtgraph.flowchart.library import Data, Display, Filters, Operators
            for mod in [Data, Display, Filters, Operators]:
                nodes = [getattr(mod, name) for name in dir(mod) if isNodeClass(getattr(mod, name))]
                for node in nodes:
                    self.addNodeType(node, [(mod.__name__.split('.')[-1],)])
        else:
            # Add all nodes to the default library
            from pyqtgraph.flowchart.library import Data
            from pyqtgraph.flowchart.library import Display
            #for mod, node in zip((Data, Display), (Data.EvalNode, Display.PlotCurve)):
            for mod, node in zip((Display,), (Display.PlotCurve,)):
                self.addNodeType(node, [(mod.__name__.split('.')[-1],)])
        
        if json_lib:
            with open(json_lib) as lib_file:
                data = json.load(lib_file)
    
            for k, nodeRegFile in data.iteritems():
                if not k.startswith('_'):
                    self.registerExternalNode(nodeRegFile)

    def registerExternalNode(self, fname):
        """ Procedure registers node. The
        node is described in file `fname`.
        Args:
        -----
            fname (str):
                path to the *.node file (file must has JSON syntax)
        """
        data = readNodeFile(fname)
        nodeClass = importNodeClass(data, absl=True)
        self.addNodeType(nodeClass, [tuple(data['libpath'])], override=data.get('override', True))
