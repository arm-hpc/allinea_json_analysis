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

def read_metric_from_file(infile, metricName, fieldnames):
    retDict = {}
    # Read the appropriate data from the given file
    profileDict = {}
    with open(infile, "r") as f:
        profileDict = json.load(f)

    # If no data has been read move on to the next file
    if (not profileDict or len(profileDict) == 0):
        return None

    numProcs = get_num_processes(profileDict)

    # Try and read from the sample metrics
    sampleDict = get_metric_samples_for_keys(profileDict["samples"]["metrics"], 
            [metricName], fieldnames)
    if (sampleDict and len(sampleDict) != 0):
        # If we have found a metric, update the dictionary with the number
        retDict.update({numProcs : list(sampleDict.values())[0]})
        return retDict
    
    # Try and read from the activity timeline
    try:
        sampleDict = get_activity_samples(profileDict["samples"]["activity"],
                [metricName])
    except KeyError:
        sampleDict= None
        pass
    if (not sampleDict or len(sampleDict) == 0):
        # Raise an error if the key is not found in one file
        raise KeyError("Unable to find metric " + metricName + " in JSON " +
                "profile " + infile)

    retDict.update({numProcs : list(sampleDict.values())[0]})

    return retDict
#### End of function read_metric_from_files

def plot_metric_from_file(infile, metricName, fieldnames, yLabel=None,
        indFrom=0, indTo=-1):
    yData = list(read_metric_from_file(infile, metricName, fieldnames).values())[0]
    assert (len(yData) != 0)
    assert isinstance(indFrom, int)
    assert isinstance(indTo, int)
    if indTo == -1:
        indTo=len(yData[0])

    # yData should be a list of lists
    for i, _ in enumerate(yData):
        yData[i]= yData[i][indFrom:indTo]

    # Assume that data has been read, as otherwise the above function should
    # have raised an error
    # Get the xData to plot against
    xData = range(len(yData[0]))
    
    # Now plot the data
    lineStyle = ['r-', 'b-', 'g-', 'k-', 'r--', 'g--']
    lineHandles = []
    lineLabels = {"sums" : "total",
            "mins" : "min",
            "maxs" : "max",
            "means" : "mean",
            "vars" : "variance"}
    # For each of the line to plot
    for cnt, lineData in enumerate(yData):
        lineHandle, = plt.plot(xData, lineData, lineStyle[cnt % len(lineStyle)],
                label=lineLabels[fieldnames[cnt]])
        lineHandles.append(lineHandle)
    plt.xlabel("Sample number")
    if (not yLabel):
        plt.ylabel(str(metricName))
    else:
        plt.ylabel(yLabel)
    #plt.legend(handles=lineHandles, loc=1, bbox_to_anchor=(1.1, 1.1))
    plt.legend(handles=lineHandles, loc=1, bbox_to_anchor=(0.3, 0.9))
    plt.draw()
#### End of function plot_metric_from_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility to plot a single time dependent metric" +
        " contained in the JSON export of multiple Allinea MAP files")

    # Add a file to read input from
    parser.add_argument("infile", help="Export to JSON of a MAP file to plot a metric from")
    # Add a file to read metrics from
    parser.add_argument("metricName", help="Name of the metric to plot")
    parser.add_argument("fields", 
            help="Name of the fields to plot. Should be one of 'sums', 'maxs', 'mins', 'means' or 'vars'",
            nargs="+")
    # Add an optional description of the metric name
    parser.add_argument("--metricDescription", help="Description of the metric name passed in." +
            " This is used as the y-label of the output graph", default=None)
    parser.add_argument("--indFrom", help="Zero based index of the sample number" +
            " from which to start plotting the metric", type=int, default=0)
    parser.add_argument("--indTo", help="Zero based index of the sample number" +
            " at which to end plotting the metric", type=int, default=-1)

    # Parse the arguments
    args = parser.parse_args()

    # Plot the single time-dependent metric from the given file
    plot_metric_from_file(args.infile, args.metricName, args.fields, args.metricDescription,
            args.indFrom, args.indTo)
    plt.show()

