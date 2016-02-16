# Node \<interpolateDF\>
Node can interpolate missing data in *pandas.DataFrame* column-wise.

---
### Background
Node loads *pd.DataFrame* into the memory, for each column of the *DataFrame* it creates an expandable sub-menu with parameters. Then the Node searches for ```np.nan```(NaN) values. If *NaNs* are found, the so-called "missing-value-regions" (multiple NaN values and offset data values (refered further as "interpolationMargin") grouped together) are created to speed-up processing, by applying the interpolation-function only to these "regions" and not to the whole data-set. Finally the interpolation function is applied to the DataFrame column-wise with parameters specified in the GUI.

The processing is based on `createInterpolationRanges()` and `applyInterpolationBasedOnRanges()` functions from module ***/lib/functions/interpolate.py***. The actuall data interpolation is performed with help of native [pandas.DataFrame.interpolate()][url:interpolate] method, with arguments gathered from GUI.

Wheneever a parameter in the GUI is changed, the interpolation routine is executed.

### Node Input
- Terminal ***In***: *\<pandas.DataFrame\>*  - data to be interpolated

### Node Output
- Terminal ***Out***: *\<pandas.DataFrame\>* - data with interpolated values


### UI description


| **UI Name**             | **UI Type**         | **Description**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|-------------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|
| *Entries*             | ReadOnly          |   Number of entries in current column (or length of the 1D array).                                                                                                                                                                                                                                                                                                                  |
| *NaNs before*             | ReadOnly          |   Number of NaN values found in the input dataframe (before interpolation).                                                                                                                                                                                                                                                                                                                  |
| *NaNs after*             | ReadOnly          |  Number of NaN values in the output dataframe (after interpolation). Sometimes a wrong method, or an attemt to extrapolate missing values results in non-zero number of NaNs. This field is very useful to check results (see also *Plot* button).                                                                                                                                                                                                                                                                                                               |
| *interpolateMargin*             | SpinBox          |  Numer of non-NaN values to consider left and right from a NaN value. In other words, this parameter defines a region of data around missing value *X*, that will be used for the interpolation of *X*. For details see doc-string of the function *createInterpolationRanges()* in module ***/lib/functions/interpolate.py***                                                                                                                                                                                                                                                                                                                 |
| *method*             | ComboBox          |  Method of the interpolation. For sinusoidal signals it is suggested to use *polinomial*. This argument is passed to [pandas.DataFrame.interpolate()][url:interpolate]                                                                                                                                                        |       
| *order*             | SpinBox          |  Order of the Polynom or Spline for interpolation. Used only if *method* is set to *polynomial* or *spline*. This argument is passed to [pandas.DataFrame.interpolate()][url:interpolate] |         
| *\*\*kwargs*             | TextBox          |  All other arguments (except *method* and *order*) that will be passed to [pandas.DataFrame.interpolate()][url:interpolate]. They may include for example *axis*, *limit*, *inplace*, *limit_direction*, *downcast* and others. You should write them in form of python-dictionary (i.e. `{'axis': 1, 'limit_direction': 'both'}`). If *method* or *order* are passed here -- they are ignored, and taken from fields above.|         
| *Plot*             | Button          |  Show the results of the interpolation in a graphical form. Opens a new window with two subplots: the upper one shows original data in blue and interpolated values in red; the bottom subplot shows the output data after interpolation. This button very usefull for finding correct parameters used for interpolation. Note, that this button is shown only for those columns, where NaNs values were detected (*NaNs before* > 0).|             


### Example

For working example , see tutorial Flowchart: *examples/interpolation.fc*. You can also execute the stand-alone module *lib/functions/interpolate.py*, which contains an example of how to use `createInterpolationRanges()` and `applyInterpolationBasedOnRanges()` functions.

[url:interpolate]: <http://pandas.pydata.org/pandas-docs/version/0.17.1/generated/pandas.DataFrame.interpolate.html>
