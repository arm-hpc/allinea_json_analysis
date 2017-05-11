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
def get_dict_field_val(inDict, fields):
    """
    Gets the value of the field given by the ordered list of field keys passed
    in

    Args:
        inDict (dict): Dictionary of JSON values to look into
        fields (list): Ordered list of key names in the JSON dictionary to
            look into

    Returns:
        Value at the specified key, or raises a key error
    """
    assert isinstance(inDict, dict)
    assert isinstance(fields, list)

    if len(fields) == 0:
        return None

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

def get_dict_field_vals(inDict, fields):
    """
    Gets the value of the fields passed in by the list of list of field keys
    passed in

    Args:
        inDict (dict): Dictionary of JSON values to look into
        fields (list): List of ordered lists of key names in the JSON
            dictionary to look-up

    Returns:
        List of values at the specified keys passed in
    """
    return [get_dict_field_val(inDict, field) for field in fields]
#### End of function get_dict_field_vals

