# Node \<readCSV\>
Node is able to read CSV datasets into the memory. The input ASCII file must contain column-based data separated wtih some specific symbol (usually with ';' or ','). This file also usually contains a header row, describing column names.

---
### Background
Internally the [pandas][url:pandas] module is used for processing, namely it's function [read_csv()][url:read_csv]. Basically, this node is the gui to the mentioned function. Most of the optional arguments of the *read_csv()* function are available with similar names within the node's ui. You may also pass non-described parameters via text-box *Manual parameters*.


### Node Input
*\<emty\>  (no input)*

### Node Output
*\<pandas.DataFrame\> object*

### UI description
Since this node is a graphical interface to the available function, the description of the majority of ui-parameters can be omitted and referred to original function's documentation. Here we will describe parameters, which needs comment (*date_parser*), which have been altered (*header*) and newly introduced (all others). Table below summarizes the ui-elements of the node.

**NOTE:** all string based parameters will be first evaluated by python with `eval()` function before being passed to *read_csv()*

| **UI Name**             | **UI Type**         | **Description**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|-------------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *Select File*             | PushButton          |  Toggle FileDialog to choose ASCII data-file. Whenever the file is successfully chosen, the button will become flat, and it's tooltip will reflect the filename. This filename will be passed as the first argument to *read_csv()*                                                                                                                                                                                                                                                                                                                   |
| *header*                  | LineEdit            |  Same as in *read_csv()*. But the default value is set to `0` not taking into account possible definition of the `names` argument. Originally it *"defaults to `0` if no `names` passed, otherwise `None`"*                                                                                                                                                                                                                                                                                                                                           |
| *date_parser*             | LineEdit            |  This parameter has not been changed. But a couple of comments could be helpful. As stated by *pandas.read_csv* documentation, a function must be passed here. Usually we are converting a formatted string into datetime object. Thus our function could look like `lambda x: datetime.datetime.strptime(x, '%d.%m.%Y %H:%M')` (this is a default function). In this example we are able to understand datetime strings of following format *06.08.1991 12:30*. For more information about datetime formats visit [python documentation][url:strptime]. But what if we our date- and time- strings are located in different columns? Let's assume that column-1 contains date in  `'%d.%m.%Y'` format, where column-2 -- time in `%H:%M:%S'`. In this case we need to pass lambda function with two arguments as follows `lambda x1, x2: datetime.datetime.strptime(x1+' '+x2, '%d.%m.%Y %H:%M:%S')`. Check out the tutorials for more examples.                                                                                                            |
| *Manually set parameters* | CheckBox            |  Toggle manual parameter input. Since not all arguments to *read_csv()* have an ui control in this node, the user might want to pass them. In that case, this CheckBox has to be switched-on and **ALL** optional arguments should be written in the form of python dictionary within the underlying TextBox *Manual parameter*. Basically, switching this option results in ignoring all the previous settings (except *Select File*) and running `read_csv(filename, **kwargs)`, where `**kwargs` are taken from the TextBox *Manual parameter*     |
| *Manual parameter*        | TextBox             |  String that will be evaluated into python dictionary with optional arguments, which will be passed as `**kwargs`.                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| *Load File*               | PushButton          |  Load file into memory by executing the *read_csv()* function. If the file has been loaded successfully, the output will be placed into the output terminal of the node                                                                                                                                                                                                                                                                                                                                                                               |

### Example

For example usage, see tutorial Flowcharts

[url:pandas]: <http://pandas.pydata.org/>
[url:read_csv]: <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html#pandas-read-csv>
[url:strptime]: <https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior>
