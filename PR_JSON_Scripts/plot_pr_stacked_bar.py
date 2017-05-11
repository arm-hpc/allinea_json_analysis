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
from matplotlib import rcParams
import argparse
import json
from pr_json_common import *
from json_dict_common import *

mpiSubPercentages = ["collectivePercent", "p2pPercent"]
mpiColors = ['#d0523a', '#d0382a']
mpiLabels = ["Collective MPI", "Point-to-Point MPI"]

ioSubPercentages = ["readPercent", "writePercent"]
ioColors = ['#175238', '#1f7222']
ioLabels = ["File System Read", "File System Write"]

cpuColors = ['#6c4031']
cpuLabels = ["CPU"]

allColors = cpuColors + mpiColors + ioColors
allLabels = cpuLabels + mpiLabels + ioLabels
fontSize = 16
rcParams.update({'font.size' : fontSize})

def plot_stacked_bar(barDict, ax, labels, colors):
    """
    Plots a stacked barchart with information stored in the bar dictionary
    passed in. This should be in the form 
    {
        numProcesses1 : [val1, ..., valn]
        ...
        numProcessesY : [val1, ..., valn]
    }
    """
    # For the given dictionary get a list of sorted keys
    sortedKeys = sorted(barDict.keys())
    x = range(len(sortedKeys))

    barWidth = 0.9
    barInd = 0
    # For each item in the sorted keys (i.e. for each number of processors)
    for key in sortedKeys:
        bottom = 0.
        valInd = 0
        # For each of the sub-percentages, plot this
        for val in barDict[key]:
            if (barInd == 0):
                ax.bar(barInd, val, bottom=bottom, width=barWidth,
                        align="center", color=colors[valInd],
                        label=labels[valInd])
            else:
                ax.bar(barInd, val, bottom=bottom, width=barWidth,
                        align="center", color=colors[valInd])
            # Update the bottom of the bar
            bottom += val
            valInd += 1
        # Update the index at which we are plotting
        barInd += 1

    ax.set_xticks(x)
    ax.set_xticklabels(sortedKeys)
    ax.legend(loc=1, bbox_to_anchor=(1.1, 1.1))
    return ax
### End of function plot_stacked_bar

def plot_percent_time_bars(percentDict, timeDict, labels, colors):
    """
    Plots a stacked bar chart in terms of percent and time using the data
    passed in in the dictionaries. The data passed in should be of the form
    {
        numProcesses1 : [val1, ..., valn]
        ...
        numProcessesY : [val1, ..., valn]
    }
    """
    percentAxes = plt.subplot(211)
    #percentAxes = plt.gca()
    plot_stacked_bar(percentDict, percentAxes, labels, colors)
    percentAxes.set_ylabel("Proportion of time (%)")
    percentAxes.set_xlabel("Number of processes")
    #plt.show()

    timeAxes = plt.subplot(212)
    #timeAxes = plt.gca()
    plot_stacked_bar(timeDict, timeAxes, labels, colors)
    timeAxes.set_ylabel("Wall clock time (s)")
    timeAxes.set_xlabel("Number of processes")

    plt.show()
### End of function plot_percent_time_bars

def get_mpi_components_from_files(fileList, threads=False):
    """
    Given a list of files to read input data from, gets a percentage of time
    spent in MPI, and a breakdown of that time in MPI
    """
    
    percentDict = dict()
    timeDict = dict()
    for filename in fileList:
        filename = filename.strip()
        try:
            # Open the file for reading
            with open(filename, "r") as infile:
                # Read the json
                jsonDict = json.load(infile)
                runtime = get_runtime(jsonDict)
                numprocs = get_num_threads(jsonDict) if threads else get_num_processes(jsonDict)
                # Read the overview data and get the percentage of overall time spent in mpi
                subDict = get_overview_data(jsonDict)
                mpiPercent = get_dict_field_val(subDict, ["mpi", "percent"]) #mpiTime = (percent / 100.) * runtime 
                # Now get the sub-percentage of the mpi time
                mpiEntry = get_dict_field_val(jsonDict, ["data", "mpi"])
                # Get all of the percentages (as a percentage of total time)
                mpiSubPercent = [float(get_dict_field_val(mpiEntry, [field])) * mpiPercent / 100. for field in mpiSubPercentages]
                mpiSubTime = [runtime * subpercent / 100. for subpercent in mpiSubPercent]

                percentDict[numprocs] = mpiSubPercent
                timeDict[numprocs] = mpiSubTime
        except IOError:
            print("File " + filename + " does not exist. Skipping.")
            pass
    return percentDict, timeDict
### End of function get_mpi_component_from_files

def get_io_components_from_files(fileList, threads=False):
    """
    Given a list of input files to read input data from, gets a percentage of
    time spent in IO and a breakdown of that time in I/O
    """

    percentDict = dict()
    timeDict = dict()
    for filename in fileList:
        filename = filename.strip()
        try:
            with open(filename, "r") as infile:
                # Read the json
                jsonDict = json.load(infile)
                runtime = get_runtime(jsonDict)
                numprocs = get_num_threads(jsonDict) if threads else get_num_processes(jsonDict)
                # Read the overview and get the percentage of overall time spent in io
                subDict = get_overview_data(jsonDict)
                ioPercent = get_dict_field_val(subDict, ["io", "percent"])
                ioJson = get_dict_field_val(jsonDict, ["data", "io"])

                ioSubPercent = [float(get_dict_field_val(ioJson, [field])) * ioPercent / 100. for field in ioSubPercentages]
                ioSubTime = [runtime * subpercent / 100. for subpercent in ioSubPercent]

                percentDict[numprocs] = ioSubPercent
                timeDict[numprocs] = ioSubTime
        except IOError:
            print("File " + filename + " does not exist. Skipping.")
            pass
    return percentDict, timeDict
### End of function get_io_components_from_files

def get_cpu_components_from_files(fileList, threads=False):
    """
    Given a list of input files to read input data from, shows the percentage
    of time spent in CPU
    """

    percentDict = dict()
    timeDict = dict()
    for filename in fileList:
        filename = filename.strip()
        try:
            with open(filename, "r") as infile:
                # Read the JSON
                jsonDict = json.load(infile)
                runtime = get_runtime(jsonDict)
                numprocs = get_num_threads(jsonDict) if threads else get_num_processes(jsonDict)
                # Read the overview and get the percentage of overall time spent in cpu
                cpuPercent = get_dict_field_val(jsonDict, ["data", "overview", "cpu", "percent"])
                
                percentDict[numprocs] = [cpuPercent]
                timeDict[numprocs] = [runtime * cpuPercent / 100.]
        except IOError:
            print("File " + filename + " does not exist. Skipping.")
            pass
    return percentDict, timeDict
### End of function get_cpu_components_from_files

def get_all_components_from_files(fileList, threads=False):
    """
    Given a list of input files to read input data from, shows the percentage
    of time spent in CPU, IO and MPI, as well as breaking this down somewhat
    """
    cpuPercent, cpuTime = get_cpu_components_from_files(fileList)
    ioPercent, ioTime = get_io_components_from_files(fileList)
    mpiPercent, mpiTime = get_mpi_components_from_files(fileList)

    allPercent = cpuPercent
    for key in allPercent.keys():
        allPercent[key] += mpiPercent[key] + ioPercent[key]

    allTime = cpuTime
    for key in allTime.keys():
        allTime[key] += mpiTime[key] + ioTime[key]

    return allPercent, allTime
### End of function get_all_components_from_files

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(description="Utility to plot a stacked bar" +
            " chart of the sub-types of CPU, MPI and I/O recorded in a " +
            "performance report")
    # Add a file containing a list of files to read data from
    parser.add_argument("infile", help="JSON file to read a list of input files from." +
            " The files are assumed to be JSON format Performance Reports",
            type=argparse.FileType('r'))

    args = parser.parse_args()

    # Read in the list of files from which to read Performance Report data
    fileList = [line.strip() for line in args.infile.readlines()]

    # Get the component of the MPI time and plot them in a bar chart
#    percentDict, timeDict = get_mpi_components_from_files(fileList)
#    plot_percent_time_bars(percentDict, timeDict, mpiLabels, mpiColors)

    # Get the components of the IO time and plot them in a bar chart
#    percentDict, timeDict = get_io_components_from_files(fileList)
#    plot_percent_time_bars(percentDict, timeDict, ioLabels, ioColors)

    percentDict, timeDict = get_all_components_from_files(fileList)
    plot_percent_time_bars(percentDict, timeDict, allLabels, allColors)

