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

def get_min_max(fileList, metric, threads, indFrom, indTo):
    # Initialise the y-date to an empty list
    ys = dict()
    xs = []

    # For each file
    for filename in fileList:
        # Read the JSON dictionary
        with open(filename, 'r') as f:
            profileDict = json.load(f)


        # Get the number of threads / processes used
        numProcs = get_num_threads(profileDict) if threads else get_num_processes(profileDict)
        xs.append(numProcs)

        # Get the min and the max of the metric
        profileDict = profileDict["samples"]["metrics"]
        data = [get_dict_field_val(profileDict, [metric, field]) for field in
                ["mins", "means", "maxs"]]
        if not indTo:
            indTo == len(data[0])

        for i, _ in enumerate(data):
            data[i] = data[i][indFrom:indTo]

        ys[numProcs] = [get_avg_over_samples(dataItem) for dataItem in data]

    return xs, ys
#### End of function get_min_max

def get_min_max_total(fileList, metric, threads, indFrom, indTo):
    ys = dict()
    xs = []
    # For each file
    for filename in fileList:
        # Read the JSON dictionary
        with open(filename, 'r') as f:
            profileDict = json.load(f)

        #Get the number of processes / threads used
        numProcs = get_num_threads(profileDict) if threads else get_num_processes(profileDict)
        xs.append(numProcs)

        # Get the 'total' of the metric. It is assumed that the metric
        # requested stores a running total
        profileDict = profileDict["samples"]["metrics"]
        data = [get_dict_field_val(profileDict, [metric, field]) for field in ["mins", "means", "maxs"]]
        maxs = [data[i][indTo] for i in range(0,len(data))]
        mins = [data[i][indFrom] for i in range(0,len(data))]
        ys[numProcs] = [maxs[i] - mins[i] for i in range(0,len(data))]

    return xs, ys
#### End of function get_min_max_total

def plot_min_max_bar(fileList, metric, threads, logy, ylabel, getTotal, indFrom,
        indTo):
    if (getTotal):
        [xs, ys] = get_min_max_total(fileList, metric, threads, indFrom, indTo)
    else:
        [xs, ys] = get_min_max(fileList, metric, threads, indFrom, indTo)
    # The data to plot on the x-axis should be evenly spaced
    xData = range(len(xs))
    # Turn the number of processes into string labels
    xs = [str(x) for x in xs]
    # Get the width of an individual bar
    barWidth = 0.95

    # Sort the keys by the number of processes
    sortedKeys = sorted(ys.keys())
    xInd= 0
    barHandles= []
    colors = ['r', 'g', 'b']
    labels = ['min', 'mean', 'max']
    for key in sortedKeys:
        barData= ys[key]
        bottom = 0.
        # We assume that the max is greater than the min, and so we can 
        if logy:
            barData = [log(x,10) if x > 0 else x for x in barData]
        for i in range(len(barData)-1, 0, -1):
            barData[i] -= barData[i-1]
        for cnt, barDatum in enumerate(barData):
            if xInd == 0:
                barHandles.append(plt.bar(xData[xInd], barDatum, bottom=bottom, width=barWidth,
                    color=colors[cnt], align='center', label=labels[cnt]))
            else:
                plt.bar(xData[xInd], barDatum, bottom=bottom, width=barWidth,
                        color=colors[cnt], align='center')
            bottom += barDatum
        xInd += 1

    # Set the x-tick labels
    plt.xticks(xData, sortedKeys)
    xlabel = "Number of threads" if threads else "Number of processes"
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(loc=1, bbox_to_anchor=(1.1, 1.1))
#### End of function plot_bar

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(description="Utility to plot a stacked bar " +
            "chart of the minimum, maximum and mean of a metric given a set of " +
            "files that are assumed to be the JSON export of a MAP profile. The " +
            "files are assumed to be generated from a set of strong or weak " +
            "scaling experiments.")

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
    plot_min_max_bar(fileList, args.metric, args.threads, args.logY, args.ylabel, args.isTotal,
            args.indFrom, args.indTo)

    plt.show()
#### End of main function


