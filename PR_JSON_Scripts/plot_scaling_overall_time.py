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

scalings = { 'constant' : (lambda x, y : 1.),
            'lineard' : (lambda x, y : float(x) / y),
            'lineari' : (lambda x, y : float(y) / x),
            'quadraticd' : (lambda x, y : float(x**2) / y**2),
            'quadratici' : (lambda x, y : float(y**2) / x**2)
            }

def isDecreasing(name):
    assert isinstance(name, str)
    return name[-1] == 'd'
#### End of function isDecreasing

def get_label_name(name):
    return name[:-1] if (name[-1] == 'i' or name[-1] == 'd') else name
#### End of function get_label_name

def read_time_data_from_files(fileList, threads=False):
    """
    Reads the running time and process counts from the list of files passed in
    and returns these as a dictionary of (processes : time)

    Args:
        fileList (list): List of filenames to read data from
        threads (bool): Indicates whether threads, instead of processes,
            should be read from the summary files

    Returns:
        A dictionary containing the processor count with the run time
    """
    assert isinstance(fileList, list)

    timeDict = {}
    # Loop over the filenames
    for filename in fileList:
        filename = filename.strip()
        try:
            # Open the file for reading
            with open(filename, "r") as infile:
                # Read the json
                jsonDict = json.load(infile)
                runtime = get_runtime(jsonDict)
                numprocs = get_num_threads(jsonDict) if threads else get_num_processes(jsonDict)
                timeDict[numprocs] = runtime
        except IOError:
            print("File " + filename + " does not exist. Skipping.")
            pass

    return timeDict
#### End of function read_summary_data_from_files

def get_ideal_func(expected):
    return scalings[expected]
#### End of function get_ideal_func

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

def plot_time_data(timeData, number, handles=[], threads=False, labels=None,
        expectedScaling=['lineard'], logy=True):
    """
    Plots the data given in the dictionary of time data. The keys in here are
    the number of processes that are used, and the values are the wallclock
    time for the run

    Args:
        timeData (dict): A dictionary assumed to have a very specific format
        number (int): Counter indicating which set of data to plot. This has an
            effect on the style as well as the labelling of data

    Returns:
        Nothing
    """
    assert isinstance(timeData, dict)

    # Get the list of keys and sort them
    sortedKeys = sorted(timeData.keys())
    x = range(len(sortedKeys))

    # Get the data to plot
    yData = [timeData[key] for key in sortedKeys]
    pltFunc = plt.semilogy if logy else plt.plot

    #plt.autoscale(enable=True, axis='y', tight=True)

    # Plot a set of expected lines
    if number == 0:
        lineStyles = ['k-', 'k--', 'k-.']
        for cnt, expected in enumerate(expectedScaling):
            label = get_label_name(expected)
            idealFunc = max if isDecreasing(expected) else min
            idealInit = idealFunc(yData)
            idealHandle, = pltFunc(x, get_ideal_line(idealInit, sortedKeys, expected), lineStyles[cnt], label=label)
            #idealHandle, = pltFunc(x, get_ideal_line(idealInit, sortedKeys, expectedScaling), 'k-', label="expected")
            handles.append(idealHandle)

    # We want a log plot of the results
    linestyle = ['r-', 'b-', 'g-', 'c-', 'k-']
    if labels:
        label = labels[number]
    else:
        label = "actual"
    lineHandle, = pltFunc(x, yData, linestyle[number], label=label, linewidth=2)
    handles.append(lineHandle)

    # Set the legend, axes label and ticks
    plt.xticks(x, sortedKeys)
    if number == 0:
        if (threads):
            plt.xlabel("Number of Threads")
        else:
            plt.xlabel("Number of Processes")
        plt.ylabel("Run time (s)")

    # The next line sets the limits on the y-axis manually, if required, for a 
    # certain plot
    #plt.gca().set_ylim(bottom=1e3, top=4e4)
#### End of function plot_time_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility to plot the running" +
            " time of a series of applications stored as JSON format" +
            " Performance Report profiles. It is assumed that the series " +
            "is of the same application, showing strong scaling")

    # Add a file containing a list of files to read data from
    parser.add_argument("infiles", help="JSON file to read a list of input files from",
        type=argparse.FileType('r'), nargs="+")
    # Add an argument to show if the strong scaling is for threads or processes
    parser.add_argument("--threads", help="Indicates whether threads or processes" +
            " should used in the scaling analysis", action="store_true",
            default=False)
    parser.add_argument("--labels", help="Gives the labels for the different" +
            " datasets passed in. The number of labels given should be the same" +
            " as the number of input files given", nargs="+", default=None)
    parser.add_argument("--expected", help="Indicates which scaling is expected" +
            " for the model. This should be one of ['constant', 'linear[i/d]'," +
            " 'quadratic[i/d]']. The i or d suffix indicates increasing or " +
            "decreasing scale", choices=sorted(scalings.keys()), default=["lineard"], nargs="+")
    parser.add_argument("--nolog", help="Indicates that a log scale should not be used",
            action="store_true", default=False)

    args = parser.parse_args()

    # Read the list of files
    handles = []
    for cnt, infile in enumerate(args.infiles):
        fileList = infile.readlines()
        # Get the summary data from the files
        timeData = read_time_data_from_files(fileList, args.threads)
        # Plot the summary data in a bar chart
        plot_time_data(timeData, cnt, handles, args.threads, args.labels, args.expected,
                not args.nolog)

    plt.legend(handles=handles, loc=1, bbox_to_anchor=(1.1, 1.1))
    plt.show()
