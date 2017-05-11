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
from json_dict_common import *

def plot_metrics_as_bar(dataDict, labels, yLabel, threads=False):
    """
    Plot metrics on a bar char from the list of metrics supplied, where the
    metric values are read from the dictionary supplied

    Args:
        dataDict (dict): Dictionary of the form {numProcs: [list, of, metrics]}
            with data to plot
        labels (list): Labels for legends of the data
        yLabel (str): Label for the y-axis of the graph
        threads (bool): Indicator whether to label the x-axis as scaling of threads or processes

    Returns:
        Nothing
    """
    # Get the xData
    xData = range(len(dataDict))

    # Get the width of an individual bar
    totalBarsWidth = 0.95
    barsPerProc = len(list(dataDict.values())[0])
    barWidth = float(totalBarsWidth) / barsPerProc
    barsPerProc -= 1

    # For each of the processes plot a bar
    colors = ['r', 'b', 'g', 'k']
    sortedKeys = sorted(dataDict.keys())
    xInd = 0
    for key in sortedKeys:
        # For each of the metrics plot a bar
        barData = dataDict[key]
        ind = 0
        barLoc = xData[xInd] - float(barsPerProc) * barWidth / 2
        barHandles = []
        for barItem in barData:
            barHandles.append(plt.bar(barLoc, barItem, width=barWidth, color=colors[ind % len(colors)],
                    align='center', label=labels[ind]))
            barLoc += barWidth
            ind += 1
        xInd += 1
    plt.xticks(xData, sortedKeys)
    if (threads):
        plt.xlabel("Number of Threads")
    else:
        plt.xlabel("Number of Processes")
    plt.ylabel(yLabel)

    plt.legend(handles=barHandles, loc=1, bbox_to_anchor=(1.1, 1.1))
#### End of function plot_metrics_as_bar

def get_mem_use_mpi_percent(fileList, threads=False):
    """
    Gets the percentage memory usage per core and the MPI usage reported in the
    files that are passed in. It is assumed that the files are JSON representations
    of Performance report profiles, and that they are in a series showing
    strong scaling from a program

    Args:
        fileList (list): List of files from which to read JSON Performance Reports data
        threads (bool): Indicates whether the number of processes or number of threads should be read

    Returns:
        Dictionary of the format {numProcs : [memUsage, MPIUsage]}
    """
    # Read in the list of files
    dataDict = {}
    for filename in fileList:
        profileDict = {}
        # Read the json in from file
        with open(filename, 'r') as f:
            profileDict = json.load(f)
        # Get the total memory per-node
        memPerNode = get_mem_per_node(profileDict)
        # Get the number of nodes
        numNodes = get_num_nodes(profileDict)

        # Get the memory used in the application per-process
        meanMem = get_dict_field_val(profileDict, ["data", "memory", "mean"])
        # Get the number of processes
        numProcs = get_num_processes(profileDict)
        memPercent = (meanMem * numProcs * 100) / (memPerNode * numNodes)

        # Get the percentage time spent in MPI
        mpiPercent = get_dict_field_val(profileDict, ["data", "overview", 
            "mpi", "percent"])
        #mpiPercent = float(mpiPercent) * get_runtime(profileDict)

        # Get the number of processes or threads used
        numProcs = get_num_threads(profileDict) if threads else numProcs
        # Update the dictionary of data to plot
        dataDict.update({numProcs : [memPercent, mpiPercent]})
    return dataDict
#### End of function get_mem_use_mpi_percent

def plot_mem_use_mpi_percent_as_bar(fileList, threads=False):
    """
    Plots the percentage memory usage per core next to the MPI usage reported
    in the files that are passed in. It is assumed that the files are JSON
    representations of Performance Report profiles, and that they are in a series
    showing strong scaling for a program

    Args:
        fileList (list): List of files from which to read JSON Performance Reports data
        threads (bool): Indicates whether the number of processes or number of threads should be read

    Returns:
        Nothing
    """
    dataDict = get_mem_use_mpi_percent(fileList, threads)

    # Plot the metrics
    plot_metrics_as_bar(dataDict, ["Memory Use", "MPI Time"], "Proportion (%)", threads)
#### End of function plot_mem_use_mpi_percent_as_bar

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(description="Utility to plot a bar chart" +
            " of the percentage memory usage vs the percentage of time spent " +
            "in MPI calls in a program run.")
            
    # Add a file containing a list of files to read data from
    parser.add_argument("infile", help="JSON file to read a list of input files from." +
            " It is assumed that the input files are part of a series of runs that " +
            "show weak scaling of a program", type=argparse.FileType('r'))
    # Add an argument to show if the strong scaling is for threads or processes
    parser.add_argument("--threads", help="Indicates whether threads or processes" +
            " should used in the scaling analysis", action="store_true",
            default=False)

    args = parser.parse_args()

    # Plot the memory usage and MPI percentage run time from the file passed in
    fileList = [line.strip() for line in args.infile.readlines()]
    plot_mem_use_mpi_percent_as_bar(fileList, args.threads)
    plt.show()

