# PyGWA
---
<img src="https://cloud.githubusercontent.com/assets/14345411/12567590/3eb00da2-c3c0-11e5-8c1b-25a1393ca5bc.png" width="30%"></img> <img src="https://cloud.githubusercontent.com/assets/14345411/12567591/3ecd124e-c3c0-11e5-9a2e-13f1707bc8f9.png" width="30%"></img> <img src="https://cloud.githubusercontent.com/assets/14345411/12567593/3ed3fabe-c3c0-11e5-9fbb-3b8985f4eae0.png" width="30%"></img>

---

**PyGWA** is a GUI-tool based on [PyQtGraph][pyqtgraph] for analysis of the groundwater hydrograph data.

The work-flow concept is the "flowchart", meaning that the typical usage will include splitting the whole job into small parts and solving them step-by-step using small subprograms -- so-called "Nodes" (gui-wrapped processing scripts). For example the task "determine the mean hydraulic gradient in tidal-influenced aquifer" may have following solution algorithm: *Read well data > Interpolate missing data > Check data plausibility > Filter out tidal influence > Calculate mean hydraulic gradient > Visualize result > Export result*. The idea behind PyGWA is to provide the library of scripts for solving this kind of small tasks as well as to give user the possibility to extend the library by adding his own "Nodes".

## Installation
Find all information on [Wiki Installation][wiki_inst] page.


## Documentation
Check out the project's [wiki][wiki].

## Author
Copyright 2016, Nikolai Chernikov ([nikolai.chernikov.ru@gmail.com][my_mail]), Hamburg University of Technology

## License
[MIT](https://opensource.org/licenses/MIT)



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


[wiki]: <https://github.com/cdd1969/pygwa/wiki>
[wiki_inst]: <https://github.com/cdd1969/pygwa/wiki/Installation>