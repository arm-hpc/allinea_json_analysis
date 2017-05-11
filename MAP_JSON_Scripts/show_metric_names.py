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
import argparse # For command line argument parsing
import os.path # For checking for file existence
import json # For JSON parsing

def print_indented(indentLevel, outStr):
    """
    Prints the given string at a given indentation level

    Args:
        indentLevel (int): Integer greater than zero for the indentation level
        outStr (str): The string to print

    Returns: Nothing.
    """
    assert(isinstance(indentLevel, int) and indentLevel >= 0)

    print(indentLevel * '\t' + outStr)
#### End of function print_indented

def print_dict_keys(inDict, titleStr, recurseLevel=0, indentLevel=1):
    """
    Prints the keys of the dictionary object passed in with a title string

    Args:
        inDict (dict): The dictionary for which to print the keys
        titleStr (str): Heading describing the data that is printed
        recurseLevel (int): The level of recursion to go into. A value of zero
            indicates that no recursion is to take place
        indentLevel (int): The level of indentation to use

    Returns:
        Nothing.
    """
    assert isinstance(inDict, dict)
    assert isinstance(titleStr, str) or titleStr == None

    if (titleStr):
        print(titleStr)
    for key in inDict:
        print_indented(indentLevel, key)
        if (recurseLevel > 0):
            print_dict_keys(inDict[key], None, recurseLevel-1, indentLevel+1)
    print("")
#### End of function print_dict_keys

def print_metric_names(sampleDict):
    """
    Prints the names of the metrics that are sampled over time

    Args:
        sampleDict (dict): The dictionary of samples containing several metrics

    Returns:
        Nothing
    """
    assert isinstance(sampleDict, dict)

    # Print the activity timeline names
    print_dict_keys(sampleDict["activity"], "Activity timelines available:",
            recurseLevel=1)

    # Print the metric names
    print_dict_keys(sampleDict["metrics"], "Sampled (i.e. time-series) metric names:")

#### End of function print_metric_names
        
if(__name__ == "__main__"):
    # Main program
    # Set up the correct program arguments
    # Create a parser for the option passed in
    parser = argparse.ArgumentParser(description="Print the names of available metrics in a" +
            " JSON file containing Allinea MAP profile data. For detail regarding" +
            " what the metrics mean see the Allinea Forge userguide.")
    parser.add_argument("filename", help="Name of a JSON file with Allinea MAP profile data")
    # Parse the arguments
    args = parser.parse_args()
    
    # Check that the file exists
    if(not os.path.isfile(args.filename)):
        raise IOError("File " + args.filename + " does not exist")
    
    # Read data from the filename passed in, assuming that it is in JSON format.
    # Let the json.load function perform error checking
    with open(args.filename, 'r') as jsonFile:
        profileDict = json.load(jsonFile)
    assert isinstance(profileDict, dict)

    # Show the global metrics
    print_dict_keys(profileDict["info"], "Global metrics (one per file):")

    # Show the names of the sample metrics
    print_metric_names(profileDict["samples"])
