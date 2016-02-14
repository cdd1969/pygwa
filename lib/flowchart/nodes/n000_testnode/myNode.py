from lib.flowchart.nodes.generalNode import newNodeWithCtrlWidget


class myNode(newNodeWithCtrlWidget):
    '''This is test docstring'''
    nodeName = 'myTestNode'
    uiTemplate = [{'name': 'HNO3', 'type': 'list', 'value': 'Closest Time'},
                    {'name': 'H2', 'type': 'str', 'value': '?/?', 'readonly': True}]

    def __init__(self, name, **kwargs):
        super(myNode, self).__init__(name, **kwargs)
