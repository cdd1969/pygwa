# Node \<df2recArray\>
Node will convert passed *pandas.DataFrame* object to *record array*. This can be useful for engaging nodes that require record-array as their input.

---
### Background
Node receives a *pandas.DataFrame* object and converts it to *record array* applying built-in method [to_records()][url:to_records].


### Node Input
*\<pandas.DataFrame\> object*

### Node Output
*\<numpy.recarray\> object*

### UI description


### Example

For example usage, see tutorial Flowcharts

[url:pandas]: <http://pandas.pydata.org/>
[url:to_records]: <http://pandas.pydata.org/pandas-docs/version/0.17.0/generated/pandas.DataFrame.to_records.html>
