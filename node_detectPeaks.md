# Node \<detectPeaks\>
Node is able to find local peaks (minima/maxima) of a signal (1D-array).

---
### Background
For processing data, this Node uses the function *lib/functions/detectpeaks.detectPeaks*, that is based on [scipy.signal.argrelextrema()][url:argrelextrema]. Minima and maxima peak indices are estimated separately as follows (with predefined comparators):
- maxima peak indices: `argrelextrema(signal, np.greater_equal, **kwargs)`
- minima peak indices: `argrelextrema(signal, np.less_equal, **kwargs)`

Afterwards, data corresponding to these indices is taken from input signal-array. The usage of `np.greater_equal` and `np.less_equal` comparator functions implies, that a peak-interval can appear in the output (see examples). The Node's backend-function can take care of these "peak-intervals" or "peak-regions" as well.


### Node Input
- Terminal ***In***: *\<numpy.ndarray\>*  - input signal (1-Dimensional)

### Node Output
###### Split=False: minima and maxima joined
- Terminal ***val***: *\<numpy.ndarray\>* - values of all peaks
- Terminal ***ind***: *\<numpy.ndarray\>* - indices of all peaks

###### Split=True: minima and maxima separately
- Terminal ***val:min***: *\<numpy.ndarray\>* - values of minima peaks
- Terminal ***ind:min***: *\<numpy.ndarray\>* - indices of minima peaks
- Terminal ***val:max***: *\<numpy.ndarray\>* - values of maxima peaks
- Terminal ***ind:max***: *\<numpy.ndarray\>* - indices of maxima peaks

### UI description


| **UI Name**             | **UI Type**         | **Description**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|-------------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|
| *order*             | SpinBox          |   How many points on each side to use for the comparison to consider `comparator(n, n+x)` to be `True`. This parameter will be passed to [scipy.signal.argrelextrema()][url:argrelextrema] as optional argument *order*.                                                                                                                                                                                                                                                                                                                  |
| *mode*             | ComboBox          |   How the edges of the vector are treated. 'wrap' (wrap around) or 'clip' (treat overflow as the same as the last (or first) element). This parameter will be passed to [scipy.signal.argrelextrema()][url:argrelextrema] as optional argument *mode*.                                                                                                                                                                                                                                                                                                                  |
| *split*             | CheckBox          |  This parameters defines the output terminals. If *split* is checked -- the minima and maxima peaks will be treated separately, and the Node has 4 output terminals. If *split* is unchecked (default) -- the minima and maxima peaks are joined into single array, and the Node has 2 output terminals. This may be usefull when you need to further process maxima and minima with different methods.                                                                                                                                                                                                                                                                                                                  |
| *removeRegions*             | CheckBox          |  If *removeRegions* is checked (default) -- the Node will apply function *removeRegions()* (from module *lib/functions/detectpeaks.py*) to the output arrays before they are returned. If *removeRegions* is unchecked -- will return arrays directly. The phenomena of these "peak-regions" is shown in examples below.                                                                                                                                                                                                                                                                                                                  
### Example

For working example , see tutorial Flowchart: *examples/detectpeaks.fc*. You can also execute the stand-alone module *lib/functions/detectpeaks.py*, which contains an example of how to use the `detectPeaks()` function, and shows the example of "peak-regions" phenomena.

[url:argrelextrema]: <http://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.argrelextrema.html#scipy.signal.argrelextrema>
