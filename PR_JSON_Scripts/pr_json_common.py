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
import sys
sys.path.append('../JSON_Common')
import json_dict_common as jdc

def get_overview_data(jsonDict):
    """
    Gets the overview element from the given dictionary of items

    Args:
        jsonDict (dict): A dictionary which we assume to be of a JSON format

    Returns:
        Value of the overview element of the given dictionary
    """
    return jdc.get_dict_field_val(jsonDict, ["data", "overview"])
#### End of function get_overview_data

def get_num_processes(jsonDict):
    """
    Gets the number of processes used in a program run stored in the
    dictionary, which is assumed to be a JSON representation of a Performance
    Report

    Args:
        jsonDict (dict): Dictionary of JSON values representing a Performance
            Report

    Returns:
        The number of processes used in the program run represented by the
        JSON dictionary passed in
    """
    assert isinstance(jsonDict, dict)

    return int(jdc.get_dict_field_val(jsonDict, ["data", "applicationDetails",
        "processes", "plain"]))
#### End of function get_num_processes

def get_num_threads(jsonDict):
    """
    Gets the number of threads used in a program run. Run data is stored in the
    dictionary passed in, which is assumed to be a JSON representation of a
    Performance Report

    Args:
        jsonDict (dict): Dictionary of JSON values representing a Performance
            Report

    Returns:
        The number of threads used in the program run represented by the
        JSON dictionary passed in
    """
    assert isinstance(jsonDict, dict)

    return int(jdc.get_dict_field_val(jsonDict, ["data", "applicationDetails",
        "ompNumThreads"]))
#### End of function get_num_threads

def get_mem_per_node(jsonDict):
    """
    Gets the memory available per node from the JSON dictionary passed in

    Args: 
        jsonDict (dict): Dictionary of JSON values representing a Performance
            Report

    Returns:
        Memory per node reported in the JSON dictionary passed in
    """
    assert isinstance(jsonDict, dict)

    return float(jdc.get_dict_field_val(jsonDict, ["data", "applicationDetails",
        "hostMemory", "plain", "value"]))
#### End of fucntion get_mem_per_node

def get_num_nodes(jsonDict):
    """
    Gets the number of nodes used from the JSON dictionary passed in

    Args:
        jsonDict (dict): Dictionary of JSON values representing a Performance
            Report

    Returns:
        Number of nodes reported in the JSON dictionary passed in
    """
    assert isinstance(jsonDict, dict)

    return jdc.get_dict_field_val(jsonDict, ["data", "applicationDetails",
        "nodes", "plain"])
### End of function get_num_nodes

def get_start_date(jsonDict):
    """
    Gets the start date timestamp in the jsonDict passed through

    Args:
        jsonDict (dict): Dictionary of JSON values representing a Performance
            Report

    Returns:
        The timestamp of the start of the profile
    """
    assert isinstance(jsonDict, dict)

    return jdc.get_dict_field_val(jsonDict, ["data", "applicationDetails",
        "startDate"])
#### End of function get_start_date

def get_runtime(jsonDict):
    """
    Gets the run time in the jsonDict passed through

    Args:
        jsonDict (dict): Dictionary of JSON values representing a Performance
            Report

    Returns:
        The run time of the profiled run represented by the JSON dictionary
        passed in
    """
    assert isinstance(jsonDict, dict)

    return jdc.get_dict_field_val(jsonDict, ["data", "applicationDetails",
        "time", "plain"])
#### End of function get_runtime
