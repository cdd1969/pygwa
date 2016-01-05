import scipy.signal as sg
import numpy as np


a = [1.87, 1.97, 2.07, 2.17, 2.25, 2.35, 2.42, 2.47, 2.51, 2.53, 2.52, 2.53, 2.48]
a = np.array(a)
print sg.argrelextrema(a, np.greater_equal, order=10)
#>>> (array([ 9, 11]),)


"""
So that is our problem! We want only one peak!
"""