# PyGWA
---
<img src="https://cloud.githubusercontent.com/assets/14345411/12567590/3eb00da2-c3c0-11e5-8c1b-25a1393ca5bc.png" width="30%"></img> <img src="https://cloud.githubusercontent.com/assets/14345411/12567591/3ecd124e-c3c0-11e5-9a2e-13f1707bc8f9.png" width="30%"></img> <img src="https://cloud.githubusercontent.com/assets/14345411/12567593/3ed3fabe-c3c0-11e5-9fbb-3b8985f4eae0.png" width="30%"></img>

---

PyQtGraph-based GUI-tool for analysis of the groundwater hydrograph data.

The workflow concept is the "flowchart", meaning that the typical usage will include splitting the whole job into small parts and solving them step-by-step using small subprograms -- so-called "Nodes" (gui-wrapped processing scripts). For example the task "determine the mean hydraulic gradient in tidal-influenced aquifer" may have following solution algorithm: *Read well data > Interpolate missing data > Check data plausability > Filter out tidal influence > Calculate mean hydraulic gradient > Visualize result > Export result*. The idea behind PyGWA is to provide the library of scripts for solving this kind of small tasks as well as to give user the possibility to extend the library by adding his own "Nodes".

# Installation
No specific installation is needed. Make sure you have installed all the required dependencies, then download the [source-code][pygwa_source] from GitHub repo and place it anywhere on your machine. Now you may launch the tool by executing *pygwa.py* file
```sh
$ git clone https://github.com/cdd1969/pygwa.git pygwa
$ cd pygwa
$ python pygwa.py
```
# Dependencies
- Program is known to run on Linux
- [Python 2.7][python2]
- [QT 5][qt5] (5.4.1)
- py: [PyQt 5][pyqt5] (5.5)
- py: [pyqtgraph][pyqtgraph]
    - version: branch *devel*, commit *fd7644345883d1a5d484c3fe4abcbf06f5c3c3b0*
- py: [pandas][pandas] (>= 0.17.0)
- py: [matplotlib][mpl] (>= 1.5.0)
- py: [openpyxl][openpyxl] (1.8.6, not older!)
- py: [xlwt][xlwt]

# Documentation
There are many example-flowcharts available in */examples* folder. You may find them useful to get the feeling of how things roll. To acess them launch PyGWA, click Menu-> Open Flowchart -> select the desired example.

Some "Nodes" do have "Help" button in their UI. 

The documentation itself does not exist yet.

# Author
Copyright 2016, Nikolai Chernikov ([nikolai.chernikov.ru@gmail.com][my_mail]), Hamburg University of Technology

# Licence
MIT



[my_mail]: <mailto:nikolai.chernikov.ru@gmail.com>
[pygwa_source]: <https://github.com/cdd1969/pygwa/tree/master>
[python2]: <https://www.python.org/downloads/>
[qt5]: <http://www.qt.io/download/>
[pyqt5]: <https://riverbankcomputing.com/software/pyqt/download5>
[pandas]: <http://pandas.pydata.org/>
[mpl]: <http://matplotlib.org/>
[openpyxl]: <https://openpyxl.readthedocs.org/en/default/changes.html#id181>
[xlwt]: <https://pypi.python.org/pypi/xlwt>
[pyqtgraph]: <http://www.pyqtgraph.org/>