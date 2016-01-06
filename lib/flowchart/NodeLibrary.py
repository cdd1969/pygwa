# these imports are for creating custom Node-Library
import pyqtgraph.flowchart.library as fclib
from customnode_readcsv import readCSVNode
from customnode_viewpandasdf import viewPandasDfNode
from customnode_selectdfcolumn import selectDfColumnNode
from customnode_plottimeseries import plotTimeseriesNode
from customnode_df2recarray import df2recArrayNode
from customnode_detectpeaks import detectPeaksNode
from customnode_detectpeaks_ts import detectPeaksTSNode
from customnode_interpolateDf import interpolateDfNode
from customnode_readxls import readXLSNode
from customnode_toxls import toXLSNode
from customnode_plot_overheadvsriverwl import plotGWLvsWLNode
from customnode_serfes1991 import serfes1991Node
from customnode_pickequaldates import pickEqualDatesNode
from customnode_datetime2sec import datetime2secondsNode
from customnode_scatterplotwidget import scatterPlotWidgetNode
from customnode_tidalefficiency import tidalEfficiencyNode
from customnode_matchpeaks import matchPeaksNode
from customnode_pipe import pipeNode
from customnode_makeTimeseriesCurve import makeTimeseriesCurveNode


def nodelib():
    del fclib.NODE_TREE['Filters']  # remove Filters from the list of available nodes
    del fclib.NODE_TREE['Operators']  # remove Operators from the list of available nodes
    del fclib.NODE_TREE['Display']['CanvasWidget']  # remove Operators from the list of available nodes
    del fclib.NODE_TREE['Display']['PlotWidget']  # remove Operators from the list of available nodes
    del fclib.NODE_TREE['Display']['ScatterPlot']  # remove Operators from the list of available nodes
    #del fclib.NODE_TREE['Filter']['PythonEval']  # remove PythonEval from the list of available nodes

    
    flowchartLib = fclib.LIBRARY.copy()  # start with the default node set
    flowchartLib.addNodeType(readCSVNode, [('Input/Output',)])
    flowchartLib.addNodeType(readXLSNode, [('Input/Output',)])
    flowchartLib.addNodeType(toXLSNode, [('Input/Output',)])
    
    flowchartLib.addNodeType(viewPandasDfNode, [('Display', 'Widgets')])
    flowchartLib.addNodeType(scatterPlotWidgetNode, [('Display', 'Widgets')], override=True)
    flowchartLib.addNodeType(plotTimeseriesNode, [('Display', 'Widgets')])
    flowchartLib.addNodeType(plotGWLvsWLNode, [('Display',)])
    flowchartLib.addNodeType(makeTimeseriesCurveNode, [('Display',)])

    flowchartLib.addNodeType(detectPeaksNode, [('Processing',)])
    flowchartLib.addNodeType(detectPeaksTSNode, [('Processing',)])
    flowchartLib.addNodeType(interpolateDfNode, [('Processing',)])
    flowchartLib.addNodeType(serfes1991Node, [('Processing',)])
    flowchartLib.addNodeType(matchPeaksNode, [('Processing',)])
    flowchartLib.addNodeType(pickEqualDatesNode, [('Processing',)])
    flowchartLib.addNodeType(tidalEfficiencyNode, [('Processing',)])

    flowchartLib.addNodeType(df2recArrayNode, [('Data conversion',)])
    flowchartLib.addNodeType(datetime2secondsNode, [('Data conversion',)])
    flowchartLib.addNodeType(selectDfColumnNode, [('Data',)])
    flowchartLib.addNodeType(pipeNode, [('Appearance',)])


    return flowchartLib