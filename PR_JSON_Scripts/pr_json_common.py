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

    return float(jdc.get_dict_field_val(jsonDict, ["data", "applicationDetails",
        "time", "plain"]))
#### End of function get_runtime

def get_io_percent(jsonDict):
    """
    Gets the percentage of time spent in I/O operations

    Args:
        jsonDict (dict): Dictionary of JSON values representing a Performance
            Report

    Returns:
        The percentage of the overall run time spent in I/O operations as a
        floating point number
    """
    assert isinstance(jsonDict, dict)

    return float(jdc.get_dict_field_val(jsonDict,
        ["data", "overview", "io", "percent"]))
#### End of function get_io_percent

def get_io_time(jsonDict):
    """
    Gets the run time in seconds spent in I/O activity

    Args:
        jsonDict (dict): Dictionary of JSON values representing a Performance
            Report

    Returns:
        The time in seconds spent in I/O operations as a floating point number
    """
    assert isinstance(jsonDict, dict)

    ioPercent= get_io_percent(jsonDict)
    totalTime= get_runtime(jsonDict)

    return totalTime * ioPercent / 100.
#### End of functoin get_io_time

def get_cpu_percent(jsonDict):
    """
    Gets the percentage of run time spent in CPU operations

    Args:
        jsonDict (dict): Dictionary of JSON values representing a Performance
            Report

    Returns:
        The percentage of total run time spent in CPU operations
    """
    assert isinstance(jsonDict, dict)

    return float(jdc.get_dict_field_val(jsonDict,
        ["data", "overview", "cpu", "percent"]))
#### End of function get_cpu_time

def get_cpu_time(jsonDict):
    """
    Gets the time in seconds spent in CPU operations

    Args:
        jsonDict (dict): Dictionary of JSON values representing a Performance
            Report

    Returns:
        The time in seconds spent in CPU operations
    """
    assert isinstance(jsonDict, dict)

    cpuPercent= get_cpu_percent(jsonDict)
    totalTime= get_runtime(jsonDict)

    return totalTime * cpuPercent / 100.
#### End of function get_cpu_time

def get_mpi_percent(jsonDict):
    """
    Gets the percentage of run time spent in (non IO) MPI operations

    Args:
        jsonDict (dict): Dictionary of JSON values representing a Performance
            Report

    Returns:
        The percentage of total run time spent in (non IO) MPI operations
    """
    assert isinstance(jsonDict, dict)

    return float(jdc.get_dict_field_val(jsonDict,
        ["data", "overview", "mpi", "percent"]))
#### End of function get_mpi_percent

def get_mpi_time(jsonDict):
    """
    Gets the time in seconds spent in (non IO) MPI operations

    Args:
        jsonDict (dict): Dictionary of JSON values representing a Performance
            Report

    Returns:
        The time in seconds spent in (non IO) MPI operations
    """
    assert isinstance(jsonDict, dict)

    mpiPercent= get_mpi_percent(jsonDict)
    totalTime= get_runtime(jsonDict)

    return totalTime * mpiPercent / 100.
#### End of function get_mpi_time
