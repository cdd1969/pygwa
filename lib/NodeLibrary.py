# these imports are for creating custom Node-Library
import pyqtgraph.flowchart.library as fclib
from flowchart.customnode_readcsv import readCSVNode
from flowchart.customnode_viewpandasdf import viewPandasDfNode
from flowchart.customnode_selectdfcolumn import selectDfColumnNode
from flowchart.customnode_plottimeseries import plotTimeseriesNode
from flowchart.customnode_df2recarray import df2recArrayNode
from flowchart.customnode_detectpeaks import detectPeaksNode
from flowchart.customnode_interpolateDf import interpolateDfNode
from flowchart.customnode_readxls import readXLSNode
from flowchart.customnode_toxls import toXLSNode
from flowchart.customnode_plot_overheadvsriverwl import plotGWLvsWLNode
from flowchart.customnode_serfes1991 import serfes1991Node
from flowchart.customnode_pickequaldates import pickEqualDatesNode
from flowchart.customnode_datetime2sec import datetime2secondsNode
from flowchart.customnode_scatterplotwidget import scatterPlotWidgetNode


def nodelib():
    del fclib.NODE_TREE['Filters']  # remove Filters from the list of available nodes
    del fclib.NODE_TREE['Operators']  # remove Operators from the list of available nodes
    #del fclib.NODE_TREE['Filter']['PythonEval']  # remove PythonEval from the list of available nodes

    
    flowchartLib = fclib.LIBRARY.copy()  # start with the default node set
    flowchartLib.addNodeType(readCSVNode, [('Input/Output',)])
    flowchartLib.addNodeType(readXLSNode, [('Input/Output',)])
    flowchartLib.addNodeType(toXLSNode, [('Input/Output',)])
    flowchartLib.addNodeType(viewPandasDfNode, [('Display',)])
    flowchartLib.addNodeType(scatterPlotWidgetNode, [('Display',)])
    flowchartLib.addNodeType(selectDfColumnNode, [('Data',)])
    flowchartLib.addNodeType(plotTimeseriesNode, [('Display',)])
    flowchartLib.addNodeType(plotGWLvsWLNode, [('Display',)])
    flowchartLib.addNodeType(detectPeaksNode, [('Processing',)])
    flowchartLib.addNodeType(interpolateDfNode, [('Processing',)])
    flowchartLib.addNodeType(serfes1991Node, [('Processing',)])
    flowchartLib.addNodeType(pickEqualDatesNode, [('Processing',)])
    flowchartLib.addNodeType(df2recArrayNode, [('Data conversion',)])
    flowchartLib.addNodeType(datetime2secondsNode, [('Data conversion',)])


    return flowchartLib