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
import json
import argparse
from map_json_common import *

def read_metric_from_files(fileList, metricName):
    """
    Returns the values of the metric identified by the metric name from the
    list of files passed in. 

    Args:
        fileList (list): List of names of JSON files, assumed to be JSON
            representations of MAP profiles.
        metricName (str): Name of the metric to get the values for

    Returns:
        Dictionary of sampled metrics read in from the list of files passed in where
        the key is the number of processes used and the value is the list of samples
    """
    retDict = {}
    for filename in fileList:
        # Read the appropriate data from the given file
        profileDict = {}
        with open(filename, "r") as f:
            profileDict = json.load(f)

        numProcs = get_num_processes(profileDict)

        # If no data has been read move on to the next file
        if (not profileDict or len(profileDict) == 0):
            continue
        # Try and read from the sample metrics
        sampleDict = get_metric_key_samples(profileDict["samples"]["metrics"], 
                [metricName])
        if (sampleDict and len(sampleDict) != 0):
            retDict.update({numProcs : list(sampleDict.values())[0]})
            continue

        # Try and read from the activity timeline
        sampleDict = get_activity_samples(profileDict["samples"]["activity"],
                [metricName])
        if (not sampleDict or len(sampleDict) == 0):
            # Raise an error if the key is not found in one file
            raise KeyError("Unable to find metric " + metricName + " in JSON " +
                    "profile " + filename)

        retDict.update({numProcs : list(sampleDict.values())[0]})

    return retDict
#### End of function read_metric_from_files

def plot_metric_from_files(fileList, metricName, yLabel=None):
    """
    Plots the metric identified by the metric name from the list of files
    passed in. The list of files are assumed to be of a series of programs
    which display strong scaling of data.

    Args:
        fileList (list): List of names of JSON files, assumed to be JSON
            representations of MAP profiles.
        metricName (str): Name of the metric to plot
        yLabel (str): String representation of the metric name to plot on the
            y-label of the graph

    Returns:
        Nothing
    """

    yData = read_metric_from_files(fileList, metricName)
    assert (len(yData) != 0)

    # Assume that data has been read, as otherwise the above function should
    # have raised an error
    # Get the xData to plot against
    xData = range(len(list(yData.values())[0]))
    
    # Now plot the data
    lineStyle = ['r-', 'g-', 'b-', 'k-', 'r--', 'g--']
    count = 0
    lineHandles = []
    for key in sorted(yData.keys()):
        lineHandle, = plt.plot(xData, yData[key], lineStyle[count % len(lineStyle)], 
                label=("Procs: " + str(key)))
        lineHandles.append(lineHandle)
        count += 1
    plt.xlabel("Sample number")
    if (not yLabel):
        plt.ylabel(str(metricName))
    else:
        plt.ylabel(yLabel)
    plt.legend(handles=lineHandles, loc=1, bbox_to_anchor=(1.1, 1.1))
    plt.draw()
#### End of function plot_metric_from_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility to plot a single time dependent metric" +
        " contained in the JSON export of multiple Allinea MAP files")

    # Add a file to read input from
    parser.add_argument("infile", help="File containing list of JSON files" +
            " (assumed to be exports of Allinea MAP files) to read metric" +
            " information from", type=argparse.FileType('r'))
    # Add a file to read metrics from
    parser.add_argument("metricName", help="Name of the metric to plot")
    # Add an optional description of the metric name
    parser.add_argument("--metricDescription", help="Description of the metric name passed in." +
            " This is used as the y-label of the output graph", default=None)

    # Parse the arguments
    args = parser.parse_args()

    # Get the list of files to plot from
    fileList = [line.strip() for line in args.infile.readlines()]

    # Plot the single time-dependent metric from the given file
    plot_metric_from_files(fileList, args.metricName, args.metricDescription)
    plt.show()
