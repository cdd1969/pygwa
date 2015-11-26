from Node import Node
a = Node('node A', allowAddInput=False, allowAddOutput=False, allowRemove=True)

print a

b = Node('node B', terminals={
    'dataIn': {'io': 'in'},
    'dataOut': {'io': 'out'}
}, allowAddInput=False, allowAddOutput=False, allowRemove=True)

print b
