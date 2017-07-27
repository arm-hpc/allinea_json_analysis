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
            sampleDict= dict() # If there is no 'activity' data just carry on
            pass
        if (not sampleDict or len(sampleDict) == 0):
            # Raise an error if the key is not found in one file
            raise KeyError("Unable to find metric " + metricName + " in JSON " +
                    "profile " + filename)

        retDict.update({numProcs : (list(sampleDict.values())[0], runtime)})

    return retDict
#### End of function read_metric_from_files

def get_min_max_y(yData):
    """
    Takes as an argument yData which is a dictionary, where the values are of
    the form (plotData, xAxisMax)

    Returns:
        The maximum of the plotData in the yData dictionary
    """
    maxY= None
    minY= None
    for key in yData:
        maybeMax= max(yData[key][0])
        maybeMin= min(yData[key][0])
        maxY = maybeMax if not maxY or maybeMax > maxY else maxY
        minY = maybeMin if not minY or maybeMin < minY else minY

    return (minY, maxY)
#### End of function get_max_y

def get_min_max_x(data, getAbsolute):
    """
    Takes as an argument data which is a dictionary, where the values are of
    the form (plotData, xAxisMax)

    Returns:
        The limits for a unified xAxis depending on the max value for the xAxes
        passed in
    """
    # It is assumed that the maximum value is positive
    maxVal= 0
    for key in data:
        maybeMax = data[key][1] if getAbsolute else len(data[key][0])
        maxVal = maybeMax if maybeMax > maxVal else maxVal
    
    # Left hand limit is always zero
    return (0, maxVal)
#### End of function get_xs

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

def plot_metric_from_files(fileList, metricName, yLabel=None,
        setXAbsolute=False, setXAxisConstant=False, setYAxisConstant=False):
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
        setXAbsolute (bool): Indicates whether the exact time should be
            obtained to plot on the x-axis
        setXAxisConstant: Indicates that the x-axes used should show the
            have the same bounds
        setYAxisConstant: Indicates the the y-axis used should be constant

    Returns:
        Nothing
    """

    yData = read_metric_from_files(fileList, metricName)
    assert (len(yData) != 0)

    # Assume that data has been read, as otherwise the above function should
    # have raised an error
    # Get the xData to plot against
    #xData = range(len(list(yData.values())[0][0]))

    yLim= get_min_max_y(yData) if setYAxisConstant else None
    xLim = get_min_max_x(yData, setXAbsolute) if setXAxisConstant else None
    
    # Now plot the data
    lineStyle = ['r-', 'g-', 'b-', 'k-', 'r--', 'g--']
    count = 0
    lineHandles = []
    numPlots= len(yData.keys())
    axStrPre = str(numPlots) + '1'
    for key in sorted(yData.keys()):
        axStr = axStrPre + str(count + 1)
        ax = plt.subplot(axStr)
        xData= get_x_data(yData[key], setXAbsolute)
        lineHandle, = ax.plot(xData, yData[key][0], lineStyle[count % len(lineStyle)], 
                label=("Procs: " + str(key)))
        lineHandles.append(lineHandle)
        if (yLim is not None):
            ax.set_ylim(bottom=yLim[0], top=yLim[1])
        if (xLim is not None):
            ax.set_xlim(left=xLim[0], right=xLim[1])
        ax.set_xlabel("Time (ms)" if setXAbsolute else "Sample number")
        count += 1
        if (not yLabel):
            ax.set_ylabel(str(metricName))
        else:
            ax.set_ylabel(yLabel)
    #plt.xlabel("Sample number")
#    if (not yLabel):
#        plt.ylabel(str(metricName))
#    else:
#        plt.ylabel(yLabel)
    #plt.legend(handles=lineHandles, loc=1, bbox_to_anchor=(1.1, 1.1))
    #plt.draw()
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
    parser.add_argument("--showTime", help="Indicates that the x-axis should" +
            " show time instead of sample number", action="store_true",
            default=False)
    parser.add_argument("--xConstant", help="Indicates that all graphs should" +
            " have the same scaling on the x-axis", action="store_true",
            default=False)
    parser.add_argument("--yConstant", help="Indicates that all graphs should" +
            " have the same scaling on the y-axis", action="store_true",
            default=False)

    # Parse the arguments
    args = parser.parse_args()

    # Get the list of files to plot from
    fileList = [line.strip() for line in args.infile.readlines()]

    # Plot the single time-dependent metric from the given file
    plot_metric_from_files(fileList, args.metricName, args.metricDescription,
            args.showTime, args.xConstant, args.yConstant)
    plt.show()
