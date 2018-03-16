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

def read_metric_from_files(fileList, metricName, deduplicate):
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
    cnt= 0
    for filename in fileList:
        # Read the appropriate data from the given file
        profileDict = {}
        with open(filename, "r") as f:
            profileDict = json.load(f)

        numProcs = get_num_processes(profileDict) if deduplicate else filename.split("/")[-1]
        runtime = get_runtime(profileDict)

        # If no data has been read move on to the next file
        if (not profileDict or len(profileDict) == 0):
            continue
        # Try and read from the sample metrics
        sampleDict = get_metric_key_samples(profileDict["samples"]["metrics"], 
                [metricName])
        if (sampleDict and len(sampleDict) != 0):
            retDict.update({numProcs : (list(sampleDict.values())[0], runtime)})
            continue

        # Try and read from the activity timeline
        try:
            sampleDict = get_activity_samples(profileDict["samples"]["activity"],
                    [metricName])
        except KeyError:
            # If there is no 'activity' data, deal with this case in a sensible way (i.e. ignore it)
            sampleDict= dict()
            pass
        if (not sampleDict or len(sampleDict) == 0):
            # Raise an error if the key is not found in one file
            raise KeyError("Unable to find metric " + metricName + " in JSON " +
                    "profile " + filename)

        retDict.update({numProcs : (list(sampleDict.values())[0], runtime)})

    return retDict
#### End of function read_metric_from_files

def get_x_data(data, convertToTime):
    """
    Gets the x-axis data to plot from the data passed in. The data is of the
    form (yvalues, time). The convertToTime parameter indicates whether to
    return just the range of the values passed in, or whether to convert this
    to a (zero-based) time
    """
    numSamples= len(data[0])
    if (not convertToTime):
        return range(numSamples)

    spacing = float(data[1]) / numSamples
    return [i*spacing for i in range(numSamples)]
### End of function get_x_data

def plot_metric_from_files(fileList, metricName, deduplicate, showTime, yLabel=None):
    """
    Plots the metric identified by the metric name from the list of files
    passed in. The list of files are assumed to be of a series of programs
    which display strong scaling of data.

    Args:
        fileList (list): List of names of JSON files, assumed to be JSON
            representations of MAP profiles.
        metricName (str): Name of the metric to plot
        deduplicate (bool): Indicates that the same number of processes should
                            be plotted twice
        showTime (bool): Indicates that wallclock time should be shown on the
                         x-axis
        yLabel (str): String representation of the metric name to plot on the
            y-label of the graph

    Returns:
        Nothing
    """

    yData = read_metric_from_files(fileList, metricName, deduplicate)
    assert (len(yData) != 0)

    # Assume that data has been read, as otherwise the above function should
    # have raised an error
    
    # Now plot the data
    lineStyle = ['r-', 'g-', 'b-', 'k-', 'r--', 'g--', 'b--', 'k--', 'r-.', 'g-.', 'b-.']
    count = 0
    lineHandles = []
    for key in sorted(yData.keys()):
        xData= get_x_data(yData[key], showTime)
        lineHandle, = plt.plot(xData, yData[key][0], lineStyle[count % len(lineStyle)], 
                label=(str(key)))
        lineHandles.append(lineHandle)
        count += 1
    xLabel= "Sample number" if not showTime else "Time (ms)"
    plt.xlabel(xLabel)
    if (not yLabel):
        plt.ylabel(str(metricName))
    else:
        plt.ylabel(yLabel)
    plt.legend(handles=lineHandles, loc=1, bbox_to_anchor=(0.5, 1.1))
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
    parser.add_argument("--deduplicate", help="Indicates that duplicate entries for the number of processes should be ignored",
            action="store_true", default=False)
    parser.add_argument("--showTime", help="Indicates that the plots should show wallclock time on the x-axis rather than" +
            "normalised time", action="store_true", default=False)

    # Parse the arguments
    args = parser.parse_args()

    # Get the list of files to plot from
    fileList = [line.strip() for line in args.infile.readlines()]

    # Plot the single time-dependent metric from the given file
    plot_metric_from_files(fileList, args.metricName, args.deduplicate, args.showTime, args.metricDescription)
    plt.show()
