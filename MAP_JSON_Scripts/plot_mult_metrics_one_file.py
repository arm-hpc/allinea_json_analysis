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

def plot_sample_metric_fields(xData, yDataDict, fields=["means"]):
    """
    Plots sampled metrics. The xData is typically time, yData is a dictionary
    of different samples, and fields is one or more of {"mins", "maxs", "means",
    "vars"}

    Args:
        xData (list): List of values to plot on the x-axis
        yDataDict (dict): Dictionary of sampled metrics to be plotted
        fields (list): A list of fields to be plotted. This is one or more of
            {"mins", "maxs", "means", "vars"}

    Returns:
        Handles to the lines plotted. This can be used to add a legend to a
        graph
    """
    assert isinstance(xData, list)
    assert isinstance(yDataDict, dict)
    legend_handles = []

    # For each metric
    for metricName in yDataDict:
        # For each field
        for field in fields:
            # Use an existing plot
            line_handle, = plt.plot(xData, yDataDict[metricName][field], '-',
                    label=metricName)
            legend_handles.append(line_handle)
    return legend_handles
#### End of function plot_sample_metric_fields

def plot_activity_metric(xData, yDataDict):
    """
    Plots the values in the dictionary passed in against the x-axis data

    Args:
        xData (list): List of x-values. Typically this would be time
        yDataDict (dict): Dictionary containing lists of data to plot

    Returns:
        List of handles to the lines plotted. This can be used in creating
        a legend for the plot
    """
    assert isinstance(xData, list)
    assert isinstance(yDataDict, dict)
    legend_handles = []

    # For each metric
    for metricName in yDataDict:
        # Use an existing plot
        line_handle, = plt.plot(xData, yDataDict[metricName], '-',
                label=metricName)
        legend_handles.append(line_handle)

    return legend_handles
#### End of function plot_activity_metric

def plot_metrics_single(profileDict, metricFile, plotTitle=None):
    """
    Plots the metrics given in the metricFile

    Args:
        profileDict (dict): Dictionary containing profile data from an Allinea
            MAP profile
        metricFile (file): File containing a list of metrics to plot
        plotTitle (str): Title to plot

    Returns:
        Nothing
    """
    assert isinstance(profileDict, dict)

    # Read the names of the metrics
    metricNames = metricFile.readlines()

    # Get the times to plot on an x-axis
    times = get_window_start_times(profileDict)

    # Get the values to plot on a y-axis
    subDict = get_metric_samples(profileDict["samples"]["metrics"],
            metricNames)
    try:
        activitySamples= profileDict["samples"]["activity"]
    except KeyError:
        activityDict= dict()
        pass

    activityDict = get_activity_samples(activityDict,
            metricNames)

    # Plot the sampled metrics passed in
    # Create a new figure
    plt.figure()
    plt.xlabel("Time (ms)")
    legend_handles = []
    if (len(subDict) > 0):
        legend_handles.extend(plot_sample_metric_fields(times, subDict))
    if (len(activityDict) > 0):
        legend_handles.extend(plot_activity_metric(times, activityDict))
    if (len(legend_handles) > 0):
        plt.legend(handles=legend_handles, loc=1, bbox_to_anchor=(1.1, 1.1))
    if (plotTitle):
        plt.title(plotTitle)
    plt.draw()
#### End of function plot_metrics_single


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility to plot multiple time dependent metrics" +
        " contained in the JSON export of an Allinea MAP file")

    # Add a file to read input from
    parser.add_argument("infile", help="JSON file to read MAP profile information from",
        type=argparse.FileType('r'))
    # Add a file to read metrics from
    parser.add_argument("metricFile", help="Name of a file containing metrics to be plotted",
        type=argparse.FileType('r'))

    # Parse the arguments
    args = parser.parse_args()

    # Read in the JSON as a dictionary
    profileDict = json.load(args.infile)

    # Read in a single JSON file and plot the metrics
    fileName = args.infile.name.split('/')[-1]
    plot_metrics_single(profileDict, args.metricFile, fileName)
    plt.show()
