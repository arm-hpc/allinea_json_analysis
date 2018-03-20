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
import map_json_common as mjc

def get_total_runtime(jsonDict):
    """
    Gets the total run time of the profile in seconds (in MAP file this is
    stored in milliseconds)

    Args:
        jsonDict (dict): Dictionary representing the JSON exported data of a
            MAP profile

    Returns:
        Floating point number, which is the runtime of the profile in seconds
    """
    seconds_per_ms= 0.001
    return mjc.get_runtime(jsonDict) * seconds_per_ms
#### End of function get_total_runtime

def get_io_time(jsonDict):
    """
    Gets the approximate amount of time spent in I/O in the application

    Args:
        jsonDict (dict): Dictionary representing the JSON exported data of a
            MAP profile

    Returns:
        The floating point value of the approximate time in seconds spent in
        I/O routines in the application
    """
    total_time= get_total_runtime(jsonDict)
    io_percent_timeline= mjc.get_io_activity(jsonDict)
    io_time= sum(io_percent_timeline) / len(io_percent_timeline) * total_time
    return io_time
#### End of function get_io_time


def get_cpu_time(jsonDict):
    """
    Gets the approximate amount of time spent in CPU activity in the
    application

    Args:
        jsonDict (dict): Dictionary representing the JSON exported data of a
            MAP profile

    Returns:
        The floating point value of the approximate time in seconds spent in
        CPU routines in the application
    """

    total_time= get_total_runtime(jsonDict)
    cpu_percent_timeline= mjc.get_cpu_activity(jsonDict)
    cpu_time= sum(cpu_percent_timeline) / len(cpu_percent_timeline) * total_time
    return cpu_time
#### End of function get_cpu_time

def get_mpi_time(jsonDict):
    """
    Gets the approximate amount of time spent in MPI activity in the
    application

    Args:
        jsonDict (dict): Dictionary representing the JSON exported data of a
            MAP profile

    Returns:
        The floating point value of the approximate time in seconds spent in
        MPI routines in the application
    """
    total_time= get_total_runtime(jsonDict)
    mpi_percent_timeline= mjc.get_mpi_activity(jsonDict)
    mpi_time= sum(mpi_percent_timeline) / len(mpi_percent_timeline) * total_time
    return mpi_time
#### End of function get_mpi_time

def get_non_sleeping_time(jsonDict):
    """
    Gets the approximate amount of time spent not sleeping during program
    execution. This is approximated as the sum of the CPU, I/O and MPI time

    Args:
        jsonDict (dict): Dictionary representing the JSON exported data of a
            MAP profile

    Returns:
        The floating point value of the approximate time in seconds spent not
        sleeping by the application
    """
    mpi_time= get_mpi_time(jsonDict)
    cpu_time= get_cpu_time(jsonDict)
    io_time= get_io_time(jsonDict)
    return mpi_time + cpu_time + io_time
#### End of function get_non_sleeping_time

def read_time_data_from_file(fname, category):
    # Open the file for reading
    with open(fname, "r") as f:
        # Parse the data as a JSON dictionary
        jsonDict= json.load(f)

    categoryDict= {
            'total': get_total_runtime,
            'io': get_io_time,
            'mpi': get_mpi_time,
            'cpu': get_cpu_time,
            'non-sleeping': get_non_sleeping_time
        }
    # Switch on the category
    timeData= categoryDict.get(category)(jsonDict)
    return (mjc.get_num_processes(jsonDict), timeData)
#### End of function read_time_data_from_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Given a set of MAP " +
            "JSON files, will plot a box plot for each of the core " +
            "counts of the run time. The run time plotted can be overall time, " +
            "I/O time, MPI time, CPU time, or the sum of I/O, MPI and CPU time " +
            "(this is the time outside of sleeping and thread synchronisation " +
            "functions). Currently this script only gives accurate information " +
            "for single-threaded applications")

    # Provide a text file with a list of files to read from
    parser.add_argument("infile", help="JSON file to read a list of input files from",
        type=argparse.FileType('r'))
    parser.add_argument("--category", help='The category of time data to ' +
            'display. This is one of {"total", "io", "cpu", "mpi", "non-sleeping"}',
            choices=["total", "io", "cpu", "mpi", "non-sleeping"], default="total")
    parser.add_argument("--title", help='Title string to show for the plot',
            default=None)

    args = parser.parse_args()

    # Read the list of JSON files to use
    fileList= args.infile.readlines()
    # Populate the data to plot
    plotDict= dict()
    for fname in fileList:
        numProcs, runtime= read_time_data_from_file(fname.strip(), args.category)
        if numProcs in plotDict:
            plotDict[numProcs].append(runtime)
        else:
            plotDict[numProcs] = [runtime]

    yLabels= sorted(plotDict)
    data = []
    # For each key in the dictionary
    for label in yLabels:
        data.append(plotDict[label])

    plt.boxplot(data)
    locs, _ = plt.xticks()
    assert len(locs) == len(yLabels), print(str(yLabels) + "\n" + str(locs))

    title_str = {
            'total': "Runtime",
            'io': "I/O Time",
            'cpu': "CPU Time",
            'mpi': "MPI Time",
            'non-sleeping': "Active Time"
        }

    plt.xticks(locs, yLabels)
    plt.xlabel("Processes")
    plt.ylabel("Time (s)")
    plt.title(args.title if args.title else title_str[args.category])
    plt.show()
#### End of main program
