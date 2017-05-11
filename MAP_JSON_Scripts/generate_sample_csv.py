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
import csv
import argparse
import json
import os
import map_json_common as mjc

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(description="Gets the sample values from a" +
            " JSON format MAP file and outputs them in CSV format. Each row" +
            " represents a metric, and each column a sample")

    parser.add_argument("infile", help="JSON file which is the export of a MAP" +
            " file")

    parser.add_argument("-o", "--outfile", help="Name of file to write output" +
            " to", default=None)
    parser.add_argument("--field", help="Name of the field to obtain at each" +
            " sample. Must be one of [mins, maxs, means]", 
            choices=["mins", "maxs", "means"], default="means")

    args = parser.parse_args()

    # Read in the JSON export of a MAP file
    if(not os.path.isfile(args.infile)):
        raise IOError("File " + args.infile + " does not exist")

    with open(args.infile, 'r') as jsonFile:
        profileDict = json.load(jsonFile)

    if not args.outfile:
        dotInd = args.infile.rfind(".")
        if dotInd < 0:
            outFName = args.infile + "_allsamples.txt"
            fieldFName = outfile[:-4] + "_fieldnames.txt"
        else:
            outFName = args.infile[:dotInd] + "_allsamples.txt"
            fieldFName = args.infile[:dotInd] + "_fieldnames.txt"
    else:
        outFName = args.outfile
        dotInd = outFName.rfind(".")
        if dotInd < 0:
            fieldFName = outFName + "_fieldnames.txt"
        else:
            fieldFName = outFName[:dotInd] + "_fieldnames.txt"

    # Get the sample values from the JSON dictionary (i.e. disregard the
    # activity timeline values)
    metrics = mjc.get_samples(profileDict)

    # Write to CSV
    with open(outFName, "w") as outfile, open(fieldFName, "w") as fieldfile:
        writer = csv.writer(outfile)
        for metric in metrics:
            fieldfile.write(metric + "\n")
            writer.writerow(metrics[metric][args.field])

    print("Written samples to " + outFName)
    print("Written field names to " + fieldFName)
#### End of main program

