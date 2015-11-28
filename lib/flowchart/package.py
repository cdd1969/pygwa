class Package(object):
    """ this is a class to standardise all possible data transfer,
        not taking into account data properties
    """

    def __init__(self, data):
        self._data = data

    def unpack(self):
        return self._data 