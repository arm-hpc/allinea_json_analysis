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
from pr_json_common import *
import sys
sys.path.append('../JSON_Common')
from json_dict_common import *

def plot_metrics_as_bar(fileList, metricList, labelList, threads, ylabel):
    """
    Plot metrics on a bar char from the list of metrics supplied, where the
    metric values are read from the list of files supplied. It is assumed that
    the list of files are generated from a series of runs which show strong
    scaling of a code

    Args:
        fileList (list): List of filenames from which to read information
        metricList (list): List of metrics to read
        labelList (list): List of labels for the metrics to use in the legend
        threads (bool): Indicates whether threads or processes are used
        ylabel (str): Label for the y-axis

    Returns:
        Nothing
    """

    yData = {}
    for filename in fileList:
        profileDict = {}
        # Read the json in from file
        with open(filename, 'r') as f:
            profileDict = json.load(f)
        # Get the number of processes or threads used
        numProcs = get_num_threads(profileDict) if threads else get_num_processes(profileDict)

        # Read the given metrics and update the values to plot
        yData.update({numProcs : get_dict_field_vals(profileDict, metricList)})

    # Plot the data
    # Get the x-axis data
    xData = range(len(yData))
    
    # Get the width of an individual bar
    totalBarsWidth = 0.95
    barsPerProc = len(list(yData.values())[0])
    barWidth = float(totalBarsWidth) / barsPerProc
    barsPerProc -= 1

    # For each of the processes plot a bar
    colors = ['r', 'b', 'g', 'k']
    sortedKeys = sorted(yData.keys())
    xInd = 0
    for key in sortedKeys:
        # For each of the metrics plot a bar
        barData = yData[key]
        ind = 0
        barLoc = xData[xInd] - float(barsPerProc) * barWidth / 2
        barHandles = []
        for barItem in barData:
            barHandles.append(plt.bar(barLoc, barItem, width=barWidth, color=colors[ind % len(colors)],
                    align='center', label=labelList[ind]))
            barLoc += barWidth
            ind += 1
        xInd += 1
    plt.xticks(xData, sortedKeys)
    if (threads):
        plt.xlabel("Number of Threads")
    else:
        plt.xlabel("Number of Processes")
    plt.ylabel(ylabel)

    plt.legend(handles=barHandles, loc=1, bbox_to_anchor=(1.1, 1.1))
#### End of function plot_metrics_as_bar

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(description="Utility to plot a bar chart" +
            " of different metrics stored in a series of JSON files, assumed to" +
            " be the export of a Performance Report. It is also assumed " +
            "that the files are generated from a series of runs that show " +
            "strong / weak scaling of an application")

    # Add a file containing a list of files to read data from
    parser.add_argument("infile", help="JSON file to read a list of input files from",
        type=argparse.FileType('r'))
    # Add an argument to provide a file with a list of metrics in
    parser.add_argument("metricFile", help="File from which to read a list of " +
            "metrics to show. The contents of the file is of the following form:\n" +
            "\tlist, of, dictionary, keys [: label]\n" +
            "where the label is optional, and is used as a label in a legend", 
            type=argparse.FileType('r'))
    # Add an argument to show if the strong scaling is for threads or processes
    parser.add_argument("--threads", help="Indicates whether threads or processes" +
            " should used in the scaling analysis", action="store_true",
            default=False)
    defaultYLabel = "Proportion of Time (%)"
    parser.add_argument("--ylabel", help="Label for the y-axis. Default is " +
        defaultYLabel.replace('%','%%'), default=defaultYLabel)

    args = parser.parse_args()

    # Read in the list of files
    fileList = [line.strip() for line in args.infile.readlines()]

    # Read in the list of metrics
    metricList = []
    labelList = []
    for line in args.metricFile.readlines():
        vals = line.strip().split(':')
        if (len(vals) == 1):
            metricList.append([val.strip() for val in vals[0].split(',')])
            labelList.append(''.join(vals[0].split()[-1]))
        else:
            metricList.append([val.strip() for val in vals[0].split(',')])
            labelList.append(' '.join(vals[1:]))

    # Plot the metrics from the files
    plot_metrics_as_bar(fileList, metricList, labelList, args.threads, args.ylabel)
    plt.show()
