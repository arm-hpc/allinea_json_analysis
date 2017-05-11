#!/usr/bin/env python
#    Copyright 2015-2017 ARM Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import matplotlib.pyplot as plt
import argparse
import json
from math import log
from map_json_common import *
import sys
sys.path.append('../JSON_Common')
from json_dict_common import *

scalingDefs = { 'constant' : (lambda x, y : 1.),
            'lineard' : (lambda x, y : float(x) / y),
            'lineari' : (lambda x, y : float(y) / x),
            'quadraticd' : (lambda x, y : float(x**2) / y**2),
            'quadratici' : (lambda x, y : float(y**2) / x**2)
            }

def get_ideal_func(expected):
    return scalingDefs[expected]
#### End of function get_ideal_func

def get_scaling_label(expected):
    assert isinstance(expected, str)
    return expected[0:-1] if expected[-1] == "i" or expected[-1] == "d" else expected
#### End of function get_scaling_label

def is_decreasing(scaling):
    assert isinstance(scaling, str)
    return scaling[-1] == "d"
#### End of function is_decreasing

def get_ideal_line(initTime, coreCounts, expected):
    """
    Gets data for an ideal scaling line in either the weak or strong case.

    Args:
        initTime (float): The initial time from which to draw an ideal scaling
        coreCounts (list): List of counts of cores from which the ideal line
            can be calculated
        expected (str): Indicates what sort of scaling is expected for the
            ideal line
    """

    idealData = [0. for _ in coreCounts]
    idealData[0] = initTime

    scalingFunc = get_ideal_func(expected)
    for i in range(1,len(coreCounts)):
        idealData[i] = idealData[i-1] * scalingFunc(coreCounts[i-1], coreCounts[i])

    return idealData
#### End of function get_ideal_line

def get_avgs(fileList, metric, threads, indFrom, indTo):
    # Initialise the y-data to an empty list
    ys = dict()
    xs = []
    # For each file
    for filename in fileList:
        # Read the JSON dictionary in
        with open(filename, 'r') as f:
            profileDict = json.load(f)

        # Get the number of threads / processes used
        numProcs = get_num_threads(profileDict) if threads else get_num_processes(profileDict)
        xs.append(numProcs)

        # Get the mean of the metric
        #profileDict= profileDict["samples"]["metrics"]
        means = get_dict_field_val(profileDict["samples"]["metrics"], [metric, "means"])
        if indTo == -1:
            indTo = len(means)

        means = means[indFrom:indTo]

        # Take the average of the mean
        ys[numProcs] = get_avg_over_samples(means)

    return xs, ys
#### End of function get_avgs

def get_total(fileList, metric, threads, indFrom, indTo):
    ys = dict()
    xs = []
    # For each file
    for filename in fileList:
        # Read the JSON dictionary in
        with open(filename, 'r') as f:
            profileDict = json.load(f)

        # Get the number of processes / threads used
        numProcs = get_num_threads(profileDict) if threads else get_num_processes(profileDict)
        xs.append(numProcs)

        # Get the 'total' of the metric. It is assumed that the metric
        # requested stores a running total 
        profileDict= profileDict["samples"]["metrics"]
        totals= get_dict_field_val(profileDict, [metric, "sums"])

        # Get the last value in the metric
        ys[numProcs] = totals[indTo] - totals[indFrom]

    return xs, ys
#### End of function get_total

def plot_bar(fileList, metric, threads, logy, ylabel, getTotal, indFrom, indTo):
    if (getTotal):
        [xs, ys] = get_total(fileList, metric, threads, indFrom, indTo)
    else:
        [xs, ys] = get_avgs(fileList, metric, threads, indFrom, indTo)
    # The data to plot on the x-axis should be evenly spaced
    xData = range(len(xs))
    # Get the width of an individual bar
    barWidth = 0.95

    # Sort the keys by the number of processes
    sortedKeys = sorted(ys.keys())
    xInd= 0
    barHandles= []
    if logy:
        for key in sortedKeys:
            ys[key] = log(ys[key], 10)
    for key in sortedKeys:
        barData= ys[key]
        barHandles.append(plt.bar(xData[xInd], barData, width=barWidth, color='r',
            align='center', label=metric))
        xInd += 1

    # Set the x-tick labels
    plt.xticks(xData, sortedKeys)
    xlabel = "Number of threads" if threads else "Number of processes"
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
#### End of function plot_bar

def plot_line(fileList, metric, threads, logy, ylabel, getTotal, expectedScaling,
        indFrom, indTo):
    if (getTotal):
        [xs, ys] = get_total(fileList, metric, threads, indFrom, indTo)
    else:
        [xs, ys] = get_avgs(fileList, metric, threads, indFrom, indTo)

    xData = range(len(xs))

    sortedKeys = sorted(ys.keys())
    yData = []
    for key in sortedKeys:
        yData.append(ys[key])

    handles=[]
    handle, = plt.semilogy(xData, yData, 'r-', label='actual') if logy else plt.plot(xData, yData, label='actual')
    #if logy:
    #    handle, = plt.semilogy(xData, yData, 'r-')
    #else:
    #    handle, = plt.plot(xData, yData)

    handles.append(handle)

    if expectedScaling:
        pltFunc = plt.semilogy if logy else plt.plot
        idealInit = max(yData) if is_decreasing(expectedScaling) else min(yData)
        #handle, = pltFunc(xData, get_ideal_line(idealInit, sortedKeys, expectedScaling), 'k-', label="expected")
        handle, = pltFunc(xData, get_ideal_line(idealInit, sortedKeys, expectedScaling), 
                'k-', label=get_scaling_label(expectedScaling))
        handles.append(handle)
        plt.legend(handles=handles, loc=1, bbox_to_anchor=(1.1, 1.1))
        #plt.legend(handles=handles, loc=1, bbox_to_anchor=(0.25, 1.1))


    plt.xticks(xData, sortedKeys)
    xlabel = "Number of threads" if threads else "Number of processes"
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
### End of function plot_line

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(description="Utility to plot a bar chart" +
            " of the averages of different metrics stored in a series of JSON files, assumed to" +
            " be the export of a MAP profile. It is also assumed " +
            "that the files are generated from a series of runs that show " +
            "strong / weak scaling of an application")

    # Add a file containing a list of files to read data from
    parser.add_argument("infile", help="Text file to read a list of input files from",
        type=argparse.FileType('r'))
    parser.add_argument("metric", help="Name of a metric to plot. This is the " +
            "name of the metric under the 'samples -> metrics' level of the JSON " +
            "export of a MAP file")
    # Add an argument to show if the strong scaling is for threads or processes
    parser.add_argument("--threads", help="Indicates whether threads or processes" +
            " should used in the scaling analysis", action="store_true",
            default=False)
    parser.add_argument("--isTotal", help="Indicates that the metric to show " +
            "is a total, and we want to plot the total", action="store_true",
            default=False)
    parser.add_argument("--logY", help="Indicates that the y-axis should have a log scale",
            action="store_true", default=False)
    parser.add_argument("--line", help="Indicates whether a line should be drawn instead of a bar graph",
            action="store_true", default=False)
    parser.add_argument("--expected", help="Indicates which scaling is expected" +
            " for the model. This should be one of ['constant', 'linear[i/d]'," +
            " 'quadratic[i/d]']. The i or d suffix indicates increasing or " +
            "decreasing scale", choices=sorted(scalingDefs.keys()), default=None)
    defaultYLabel = "Proportion of Time (%)"
    parser.add_argument("--ylabel", help="Label for the y-axis. Default is " +
        defaultYLabel.replace('%','%%'), default=defaultYLabel)
    parser.add_argument("--indFrom", help="Zero based index from which to start" +
            " taking values", type=int, default=0)
    parser.add_argument("--indTo", help="Zero based index up to which to take values",
            type=int, default=-1)

    args = parser.parse_args()

    # Read in the list of files
    fileList = [line.strip() for line in args.infile.readlines()]
    fileList.sort()

    # Plot the summary of the metric in a bar chart
    if not args.line:
        plot_bar(fileList, args.metric, args.threads, args.logY, args.ylabel,
                args.isTotal, args.indFrom, args.indTo)
    else:
        plot_line(fileList, args.metric, args.threads, args.logY, args.ylabel, 
                args.isTotal, args.expected, args.indFrom, args.indTo)

    plt.show()

