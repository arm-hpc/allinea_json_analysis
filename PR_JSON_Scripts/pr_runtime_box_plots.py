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
import pr_json_common as prj

def read_time_data_from_file(fname, category):
    # Open the file for reading
    with open(fname, "r") as f:
        # Parse the data as a JSON dictionary
        jsonDict= json.load(f)

    categoryDict= {
            'total': prj.get_runtime,
            'io': prj.get_io_time,
            'mpi': prj.get_mpi_time,
            'cpu': prj.get_cpu_time
        }
    # Switch on the category
    timeData= categoryDict.get(category)(jsonDict)
    return (prj.get_num_processes(jsonDict), timeData)
#### End of function read_time_data_from_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Given a set of Performance " +
            "Reports JSON files, will plot a box plot for each of the core " +
            "counts of the run time. The run time plotted can be overall time, " +
            "I/O time, MPI time, CPU time, or the sum of I/O, MPI and CPU time " +
            "(this is the time outside of sleeping and thread synchronisation " +
            "functions)")

    # Provide a text file with a list of files to read from
    parser.add_argument("infile", help="JSON file to read a list of input files from",
        type=argparse.FileType('r'))
    parser.add_argument("--category", help='The category of time data to ' +
            'display. This is one of {"total", "io", "cpu", "mpi"}',
            choices=["total", "io", "cpu", "mpi"], default="total")
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
            'mpi': "MPI Time"
        }

    plt.xticks(locs, yLabels)
    plt.xlabel("Processes")
    plt.ylabel("Time (s)")
    plt.title(args.title if args.title else title_str[args.category])
    plt.show()
#### End of main program
