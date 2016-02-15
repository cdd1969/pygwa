from lib.flowchart.nodes.generalNode import NodeWithCtrlWidget


class myNode(NodeWithCtrlWidget):
    '''This is test docstring'''
    nodeName = 'myTestNode'
    uiTemplate = [{'name': 'HNO3', 'type': 'list', 'value': 'Closest Time'},
                    {'name': 'C2H5OH', 'type': 'bool', 'value': 0},
                    {'name': 'H20', 'type': 'str', 'value': '?/?'}]

    def __init__(self, name, **kwargs):
        super(myNode, self).__init__(name, terminals={'In': {'io': 'in'}, 'Out': {'io': 'out'}}, **kwargs)

    def process(self, In):
        print ('processing')
