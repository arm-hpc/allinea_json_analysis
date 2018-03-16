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

def plot_lustre_read_approx_integrals(profileDict):
    assert isinstance(profileDict, dict)

    # Get the field for the lustre read rate
    samples= get_metric_key_samples(profileDict["samples"]["metrics"], ["lustre_bytes_read"], "means")
    lustReadRate= samples["lustre_bytes_read"]

    # Get the field for the total bytes read from lustre
    samples= get_metric_key_samples(profileDict["samples"]["metrics"], ["lustre_rchar_total"], "sums")
    lustReadTotal= samples["lustre_rchar_total"]

    # Calcualte the approximate integral for the lustre read rate
    sampleLen= get_sample_interval(profileDict) / 1000. # convert to seconds rather than milliseconds
    numNodes= get_num_nodes(profileDict)

    lustReadRate[0]= lustReadRate[0] * sampleLen * numNodes
    for i in range(1,len(lustReadRate)):
        lustReadRate[i] = lustReadRate[i-1] + lustReadRate[i] * sampleLen * numNodes

    # Plot the approximate integrals
    lineHandles= []
    lineHandle, = plt.plot(range(len(lustReadRate)), lustReadRate, 'k--', label="Approx bytes read")
    lineHandles.append(lineHandle)

    lineHandle, = plt.plot(range(len(lustReadTotal)), lustReadTotal, 'k-', label="Actual bytes read")
    lineHandles.append(lineHandle)
    plt.legend(handles=lineHandles, loc=1, bbox_to_anchor=(0.5, 1.1))
#### End of plot_lustre_read_approx_integrals

def plot_lustre_write_approx_integrals(profileDict):
    assert isinstance(profileDict, dict)

    # Get the samples for the Lustre write rate
    samples= get_metric_key_samples(profileDict["samples"]["metrics"], ["lustre_bytes_written"], "means")
    lustWriteRate= samples["lustre_bytes_written"]

    # Get the field for the rate of MPI collective calls
    samples= get_metric_key_samples(profileDict["samples"]["metrics"], ["lustre_wchar_total"], "sums")
    lustWriteTotal= samples["lustre_wchar_total"]

    # Calculate the approximate integral for the lustre write rate
    sampleLen= get_sample_interval(profileDict) / 1000. # convert to milliseconds
    numNodes= get_num_nodes(profileDict)

    lustWriteRate[0]= lustWriteRate[0] * sampleLen * numNodes
    for i in range(1,len(lustWriteRate)):
        lustWriteRate[i] = lustWriteRate[i-1] + lustWriteRate[i] * sampleLen * numNodes

    # Plot the approximate integral
    lineHandles= []
    lineHandle, = plt.plot(range(len(lustWriteRate)), lustWriteRate, 'k--', label="Approx bytes written")
    lineHandles.append(lineHandle)

    lineHandle, = plt.plot(range(len(lustWriteTotal)), lustWriteTotal, 'k-', label="Actual bytes written")
    lineHandles.append(lineHandle)
    plt.legend(handles=lineHandles, loc=1, bbox_to_anchor=(0.5, 1.1))
    plt.show()
#### End of function plot_lustre_write_approx_integrals

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility to plot multiple time dependent metrics" +
        " contained in the JSON export of an Allinea MAP file")

    # Add a file to read input from
    parser.add_argument("infile", help="JSON file to read MAP profile information from",
        type=argparse.FileType('r'))

    # Parse the arguments
    args = parser.parse_args()

    # Read in the JSON as a dictionary
    profileDict = json.load(args.infile)

    # Read in a single JSON file and plot the metrics
    fileName = args.infile.name.split('/')[-1]

    # Plot the write rate integrals as well as the totals
    plot_lustre_write_approx_integrals(profileDict)
    # Plot the read reate integrals as well as the totals
    plot_lustre_read_approx_integrals(profileDict)
    plt.show()
#### End of main program
