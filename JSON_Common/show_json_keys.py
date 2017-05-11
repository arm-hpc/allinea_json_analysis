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
import argparse
import json

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

def print_dict_keys(inDict, recurseLevel=0, indentLevel=1, showAll=False):
    """
    Prints the keys of the dictionary object passed in with a title string

    Args:
        inDict (dict): The dictionary for which to print the keys
        recurseLevel (int): The level of recursion to go into. A value of zero
            indicates that no recursion is to take place
        indentLevel (int): The level of indentation to use

    Returns:
        Nothing.
    """
    assert isinstance(inDict, dict)

    for key in inDict:
        print_indented(indentLevel, key)
        if (recurseLevel > 0 or showAll):
            if isinstance(inDict[key], dict):
                print_dict_keys(inDict[key], recurseLevel-1, indentLevel+1,
                        showAll)
    print("")
#### End of function print_dict_keys


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility to show the keys in" +
            " a JSON file up to a given depth")
    # Add a file to read input from
    parser.add_argument("infile", help="JSON file to read information from",
        type=argparse.FileType('r'))

    parser.add_argument("--level", help="Maximum level to iterate to",
            nargs="?", type=int, default=1)
    parser.add_argument("--all", help="Flags whether to show all keys in the JSON file",
            action='store_true', default=False)

    # Parse the arguments
    args = parser.parse_args()

    # Read in the JSON as a dictionary
    jsonDict = json.load(args.infile)

    if (not isinstance(jsonDict, dict)):
        print("JSON read a single value: " + str(jsonDict))
    else:
        print_dict_keys(jsonDict, recurseLevel=args.level, indentLevel=0,
                showAll=args.all)
