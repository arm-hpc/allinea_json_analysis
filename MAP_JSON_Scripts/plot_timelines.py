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
from operator import add

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility to plot information" +
        " contained in the JSON export of an Allinea MAP file")

    # Add a file to read input from
    parser.add_argument("infile", help="JSON file to read MAP profile information from",
        type=argparse.FileType('r'))

    # Parse the arguments
    args = parser.parse_args()

    # Read in the JSON as a dictionary
    profileDict = json.load(args.infile)

    # Get the CPU activity data
    cpuData = get_cpu_activity(profileDict)

    # Get the I/O activity data
    ioData = get_io_activity(profileDict)

    # Get the MPI activity data
    mpiData = get_mpi_activity(profileDict)

    # Get the openMP activity data
    openmpData = get_omp_active_activity(profileDict)

    # Get the x-axis to plot against
    xData = range(len(mpiData))

    cpuHandle = plt.bar(xData, cpuData, color='g', label="cpu", width=1.0)
    bottom = cpuData
    ioHandle = plt.bar(xData, ioData, color='r', label="io", bottom=bottom, width=1.0)
    bottom = list(map(add, bottom, ioData))
    openMPHandle = plt.bar(xData, openmpData, color='y', label="openmp", bottom=bottom, width=1.0)
    bottom = list(map(add, bottom, openmpData))
    mpiHandle = plt.bar(xData, mpiData, color='b', label="mpi", bottom=bottom, width=1.0)

    legend_handles = [cpuHandle, ioHandle, mpiHandle, openMPHandle]
    plt.xticks([], [])
    plt.ylabel("% time")
    plt.legend(handles=legend_handles, loc=1, bbox_to_anchor=(1.1, 1.1))
    plotTitle = args.infile.name.split('/')[-1]
    print(plotTitle)
    plt.title(plotTitle)

    plt.show()
