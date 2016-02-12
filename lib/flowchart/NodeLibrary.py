# these imports are for creating custom Node-Library
import pyqtgraph.flowchart.library as fclib
from nodes.n00_pipe.node_pipe import pipeNode
from nodes.n01_quickview.node_viewpandasdf import viewPandasDfNode
from nodes.n02_readcsv.node_readcsv import readCSVNode
from nodes.n03_readxls.node_readxls import readXLSNode
from nodes.n04_writexls.node_toxls import toXLSNode
from nodes.n05_timeseriescurve.node_makeTimeseriesCurve import makeTimeseriesCurveNode
from nodes.n06_plottimeseries.node_plottimeseries import plotTimeseriesNode
from nodes.n07_interpolate.node_interpolateDf import interpolateDfNode
from nodes.n08_detectpeaks.node_detectpeaks import detectPeaksTSNode
from nodes.n09_selectdates.node_pickequaldates import pickEqualDatesNode
from nodes.n10_matchpeaks.node_matchpeaks import matchPeaksNode
from nodes.n11_tidalefficiency.node_tidalefficiency import tidalEfficiencyNode
from nodes.n12_timelag.node_timelag import timeLagNode
from nodes.n13_serfes.node_serfes1991 import serfes1991Node
from nodes.n14_overheadplot.node_plot_overheadvsriverwl import plotGWLvsWLNode
from nodes.n15_scatterplotwigdet.node_scatterplotwidget import scatterPlotWidgetNode


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

    #flowchartLib.addNodeType(detectPeaksNode, [('Processing',)])
    flowchartLib.addNodeType(detectPeaksTSNode, [('Processing',)])
    flowchartLib.addNodeType(interpolateDfNode, [('Processing',)])
    flowchartLib.addNodeType(serfes1991Node, [('Processing',)])
    flowchartLib.addNodeType(matchPeaksNode, [('Processing',)])
    flowchartLib.addNodeType(pickEqualDatesNode, [('Processing',)])
    flowchartLib.addNodeType(tidalEfficiencyNode, [('Processing',)])
    flowchartLib.addNodeType(timeLagNode, [('Processing',)])

    #flowchartLib.addNodeType(df2recArrayNode, [('Data conversion',)])
    #flowchartLib.addNodeType(datetime2secondsNode, [('Data conversion',)])
    #flowchartLib.addNodeType(selectDfColumnNode, [('Data',)])
    flowchartLib.addNodeType(pipeNode, [('Appearance',)])


    return flowchartLib
