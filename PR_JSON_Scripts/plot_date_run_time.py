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
import pr_json_common as pjc
from datetime import datetime

def read_time_date_data_single_file(fname):
    with open(fname, "r") as f:
        jsonDict= json.load(f)

    # Get the runtime from the JSON dictionary
    runtime= pjc.get_runtime(jsonDict)
    startDateStr= pjc.get_start_date(jsonDict)
    startDateStr= startDateStr[:startDateStr.rfind('(')-1]
    startDate= datetime.strptime(startDateStr, "%a %b %d %Y %H:%M:%S")
    return (startDate, runtime)
#### End of  function read_time_date_data_single_file

def read_time_date_data(fname):
    timeDict= dict()
    with open(fname, "r") as f:
        # Read the file line by line
        for line in f.readlines():
            startDate, runtime= read_time_date_data_single_file(line.strip())
            timeDict[startDate] = runtime

    sortedDates= sorted(timeDict)
    sortedTimes= [timeDict[key] for key in sortedDates]

    return sortedDates, sortedTimes
#### End of funciont read_time_date_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility to plot the running" +
            " time of a series of applications stored as JSON format" +
            " Performance Report profiles. It is assumed that the series " +
            "is of the same application, showing strong scaling")

    # Add a file containing a list of files to read data from
    parser.add_argument("infile", help="File to read a list of input files from")

    parser.add_argument("--title", help="Title to set for the figure",
            default=None)

    args = parser.parse_args()

    # Read the date and time from the infiles
    sortedDates, sortedTimes= read_time_date_data(args.infile)

    sortedDates= [x.strftime("%b %d") for x in sortedDates]
    
    # Now plot the times evenly spaced
    plt.plot(range(len(sortedTimes)), sortedTimes, 'rx')
    plt.xticks(range(len(sortedTimes)), sortedDates, rotation=90)
    plt.xlabel("Date")
    plt.ylabel("Run time (s)")
    if args.title:
        plt.title(args.title)
    plt.show()
#### End of main function
