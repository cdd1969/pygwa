class Package(object):
    """ this is a class to standardise all possible data transfer,
        not taking into account data properties
        Standard Node Terminal has two downsides:
            1) cannot pass Pandas.DataFrame
            2) displays large arrays (very slow)
        To overcome these issues I will pack my data before transmitting
        into `Package` and unpack it on receive
    """

    def __init__(self, data):
        self._data = data

    def unpack(self):
        return self._data
