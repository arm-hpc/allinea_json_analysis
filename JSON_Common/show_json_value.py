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

def get_dict_field_val(inDict, fields):
    """
    Shows the value of the field given by the ordered list of field keys passed
    in

    Args:
        inDict (dict): Dictionary of JSON values to look into
        fields (list): Ordered list of key names in the JSON dictionary to
            look into

    Returns:
        Nothing
    """
    assert isinstance(inDict, dict)
    assert isinstance(fields, list)

    outVal = inDict
    tried = ""
    for field in fields:
        try:
            tried += str(field) + ", "
            outVal = outVal[field]
        except KeyError:
            print("Field '" + tried + "' not found")
            return None
    return outVal
#### End of function get_dict_field_val

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility to show the value " +
            "stored at a given field in a JSON file")
    # Add a file to read input from
    parser.add_argument("infile", help="JSON file to read information from",
        type=argparse.FileType('r'))

    # Add a list of (ordered) field names
    parser.add_argument("fields", help="List of fields to recurse into." +
            " This is ordered, and each entry goes down a level in the " +
            "JSON object", nargs='+') 

    args = parser.parse_args()

    # Read in the JSON as a dictionary
    jsonDict = json.load(args.infile)

    val = get_dict_field_val(jsonDict, args.fields)
    print(str(val))
    # Print out the value requested
    with open("kbrab.json", "w") as outFile:
        json.dump(val, outFile)
