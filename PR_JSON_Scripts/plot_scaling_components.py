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
from math import nan

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

def read_summary_data_from_files(fileList, threads=False):
    """
    Reads the MPI, IO and CPU percentage fields from the list of files passed
    in. It is assumed that the files all relate to the same application, but
    that the number of processes differs

    Args:
        fileList (list): List of filenames to read data from
        threads (bool): Indicates whether threads, instead of processes,
            should be read from the summary files

    Returns:
        A dictionary containing the processor count with the tuple of I/O, MPI
        and CPU data (in that order)
    """
    assert isinstance(fileList, list)

    barDict = {}
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
                # Read the overview data
                subDict = get_overview_data(jsonDict)
                vals = [get_dict_field_val(subDict, [key, "percent"]) for key in ["io", "mpi", "cpu"]]
                timevals = [(x / 100.) * runtime for x in vals]
                barDict[numprocs] = vals
                timeDict[numprocs] = timevals
        except IOError:
            print("File " + filename + " does not exist. Skipping.")
            pass

    return barDict, timeDict
#### End of function read_summary_data_from_files

def get_ideal_func(expected):
    return scalings[expected]

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

def plot_bar_data(barData, threads=False):
    """
    Plots the data contained in the dictionary passed in. This should be of the
    form
    { numprocs : [io, mpi, cpu] }
    where all the variables listed are numeric

    Args:
        barData (dict): A dictionary assumed to have a very specific format

    Returns:
        Nothing
    """
    assert isinstance(barData, dict)

    # Get the list of keys and sort them
    sortedKeys = sorted(barData.keys())
    x = range(len(sortedKeys))

    # Get the appropriate data
    ioData = [barData[key][0] for key in sortedKeys]
    mpiData = [barData[key][1] for key in sortedKeys]
    cpuData = [barData[key][2] for key in sortedKeys]

    # Set the width of the bar
    barWidth=0.3

    # Plot the appropriate data. Use the current figure
    #ax = plt.gca()
    ax = plt.subplot(211)
    ax.bar([item - barWidth for item in x], ioData, width=barWidth, color='r', align='center', label="io")
    ax.bar(x, mpiData, width=barWidth, color='b', align='center', label="mpi")
    ax.bar([item + barWidth for item in x], cpuData, width=barWidth, color='g', align='center', label="cpu")
    ax.set_xticks(x)
    ax.set_xticklabels(sortedKeys)
    if (threads):
        ax.set_xlabel("Number of Threads")
    else:
        ax.set_xlabel("Number of Processes")
    ax.set_ylabel("Proportion of Time (%)")

    ax.legend(loc=1, bbox_to_anchor=(1.1, 1.1))
#### End of function plot_bar_data

def noneIfZero(myList, func):
    return None if all(item == 0 for item in myList) else func(myList)
#### End of function noneIfZero

def plot_time_data(timeData, threads=False, expected=None):
    """
    Plots the data given in the dictionary of time data. The keys in here are
    the number of processes that are used, and the values are the wallclock
    time for the I/O, MPI and CPU portions of a run. It is assumed that the
    runs represent the strong scaling of a program to more processes.

    Specifically, the data is of the form
    { numprocs : [io, mpi, cpu] }
    where all the variables listed are numeric

    Args:
        timeData (dict): A dictionary assumed to have a very specific format

    Returns:
        Nothing
    """
    assert isinstance(timeData, dict)

    # Get the list of keys and sort them
    sortedKeys = sorted(timeData.keys())
    x = range(len(sortedKeys))

    # Get the appropriate data
    ioData = [timeData[key][0] for key in sortedKeys]
    mpiData = [timeData[key][1] for key in sortedKeys]
    cpuData = [timeData[key][2] for key in sortedKeys]

    #ax = plt.gca()
    ax = plt.subplot(212)
    handles = []
    if expected:
        #idealInit = (sum(ioData) + sum(mpiData) + sum(cpuData)) / \
        #    (len(ioData) + len(mpiData) + len(cpuData))
        expectedStyles = ['k-', 'k--']
        for cnt, scaling in enumerate(expected):
            label = scaling[0:-1] if scaling[-1] == 'i' or scaling == 'd' else scaling
            # Plot an ideal line
            idealFunc = max if isDecreasing(scaling) else min
            #idealInit = idealFunc([idealFunc(data) for data in [ioData, mpiData, cpuData]]) 
            idealInit = idealFunc([data for data in [noneIfZero(ioData, idealFunc),
            noneIfZero(mpiData, idealFunc), noneIfZero(cpuData, idealFunc)] if data]) * 2
            idealHandle, = ax.semilogy(x, get_ideal_line(idealInit, sortedKeys, scaling),
                    expectedStyles[cnt], label=label)
            handles.append(idealHandle)

    # We want a log plot of the results
    if (any(ioData)):
        ioHandle, = ax.semilogy(x, ioData, 'r-', label="io", linewidth=2)
        handles.append(ioHandle)
    if (any(mpiData)):
        mpiHandle, = ax.semilogy(x, mpiData, 'b-', label="mpi", linewidth=2)
        handles.append(mpiHandle)
    if (any(cpuData)):
        cpuHandle, = ax.semilogy(x, cpuData, 'g-', label="cpu", linewidth=2)
        handles.append(cpuHandle)

    # Set the legend, axes label and ticks
    #ax.legend(handles=handles, loc=1, bbox_to_anchor=(1.1, 1.1))
    ax.legend(handles=handles, loc=1, bbox_to_anchor=(0.25, 1.1))
    ax.set_xticks(x)
    ax.set_xticklabels(sortedKeys)
    if (threads):
        ax.set_xlabel("Number of Threads")
    else:
        ax.set_xlabel("Number of Processes")
    ax.set_ylabel("Wallclock time (s)")
#### End of function plot_time_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility to plot a set of line " +
            "charts for the MPI, I/O and CPU activity recorded in a set of " +
            "Performance Report profiles. It is assumed that the set of profiles " +
            "passed in is generated for strong / weak scaling runs for a " +
            "particular program")

    # Add a file containing a list of files to read data from
    parser.add_argument("infile", help="Text file to read a list of input files from",
        type=argparse.FileType('r'))
    # Add an argument to show if the strong scaling is for threads or processes
    parser.add_argument("--threads", help="Indicates whether threads or processes" +
            " should used in the scaling analysis", action="store_true",
            default=False)
    parser.add_argument("--expected", help="Indicates which scaling is expected" +
            " for the model. This should be one of ['constant', 'linear[i/d]'," +
            " 'quadratic[i/d]']. The i or d suffix indicates increasing or " +
            "decreasing scale", choices=sorted(scalings.keys()), nargs="+",
            default=None)

    args = parser.parse_args()

    # Read the list of files
    fileList = args.infile.readlines()
    # Get the summary data from the files
    barData, timeData = read_summary_data_from_files(fileList, args.threads)
    # Plot the summary data in a bar chart
    plot_bar_data(barData, args.threads)
    #plt.show()
    plot_time_data(timeData, args.threads, args.expected)
    plt.show()
