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
import numbers

def get_sample_count(profileDict):
    """
    Gets the number of samples taken from a dictionary representing data from an
    Allinea MAP file

    Args:
        profileDict (dict): Dictionary from which to obtain the count of samples

    Returns:
        The number of samples taken (non-negative integer)
    """
    assert isinstance(profileDict, dict)

    return profileDict["samples"]["count"]
#### End of function get_sample_count

def get_samples(profileDict):
    """
    Returns the samples only for the metrics (i.e. does not return any
    information from the activity timeline)
    """
    return profileDict["samples"]["metrics"]
#### End of function get_samples

def get_runtime(profileDict):
    """
    Gets the runtime (in milliseconds) of an application run

    Args:
        profileDict (dict): Dictionary which is assumed to be taken from the
            JSON representation of a MAP profile

    Returns:
        The runtime of the application
    """
    assert isinstance(profileDict, dict)

    return int(profileDict["info"]["runtime"])
#### End of function get_runtime

def get_sample_interval(profileDict):
    """
    Gets an approximation to the size of the interval of a sample during the
    run
    """
    assert isinstance(profileDict, dict)

    return float(get_runtime(profileDict)) / get_sample_count(profileDict)
#### End of function get_sample_interval

def get_window_start_times(profileDict):
    """
    Gets the times of the start of the sampling windows used in the profiled
    run

    Args:
        profileDict (dict): Dictionary of values representing an Allinea MAP
            profiled run

    Returns:
        List of start times of sampling window
    """
    assert isinstance(profileDict, dict) and "samples" in profileDict

    return profileDict["samples"]["window_start_offsets"]
#### End of function get_window_start_times

def get_metric_samples(metricDict, metricNames):
    """
    Returns a dictionary of samples for the given metric name

    Args:
        metricDict (dict): Dictionary of sampled metrics
        metricNames (list): Names of the keys of the metric to return

    Returns:
        Dictionary of samples of the min, max, mean and variance
    """
    assert isinstance(metricDict, dict)
    assert isinstance(metricNames, str) or isinstance(metricNames, list)

    retDict = {}
    if isinstance(metricNames, str):
        retDict[metricNames] = metricDict[metricNames]
        return retDict

    # metricNames must be a list
    for metricName in metricNames:
        metricName = metricName.strip()
        try:
            retDict[metricName] = metricDict[metricName]
        except KeyError:
            print("Metric " + metricName + " does not exist - skipping")
            pass

    return retDict
#### End of function get_metric_samples

def get_metric_samples_for_keys(metricDict, metricNames, keyVals=["means"]):
    """
    Returns a dictionary of samples for the given metric names, and extracts
    the samples for the given list of keys. The keys should be a list of the
    following "means", "mins", "maxs", "sums", "vars"

    Args:
        metricDict (dict): Dictionary of sampled metrics
        metricNames (list): Names of the metrics for which to return the samples
        keyVals (list): Names of the fields in the metric to return the samples
            for

    Returns:
        Dictionary of samples for the keys that are given
    """

    # Get all of the samples
    retDict = get_metric_samples(metricDict, metricNames)
    for key in retDict:
        retDict[key] = [retDict[key][keyVal] for keyVal in keyVals]

    return retDict
#### End of function get_metric_samples_for_keys

def get_metric_key_samples(metricDict, metricNames, keyVal="means"):
    """
    Returns a dictionary of samples for the given metric name, but only extracts
    the samples for the given key

    Args:
        metricDict (dict): Dictionary of sampled metrics
        metricNames (list): Names of the keys of the metric to return
        keyVal (str): The value of the key for which data is to be extracted.
            Must be one of {"mins", "maxs", "means", "vars"}

    Returns:
        Dictionary of samples of the given {"mins", "maxs", "means", "vars", "sums"}
    """
    assert keyVal in ["mins", "maxs", "means", "vars", "sums"]

    retDict = get_metric_samples(metricDict, metricNames)
    for key in retDict:
        retDict[key] = retDict[key][keyVal]

    return retDict
#### End of function get_metric_key_samples

def get_activity_samples(activityDict, metricNames, activityName="main_thread"):
    """
    Returns a list of samples of thread activity for the given activity
    (default is return data for the main_thread)

    Args:
        activityDict (dict): Dictionary of activity timeline data
        metricNames (list): List of strings of keys of activity data to return
        activityName (str): The name of an activity timeline to access. By
            default this is the main_thread activity

    Returns:
        Dictionary of samples of thread activity for the given activity
    """
    assert isinstance(activityDict, dict)
    assert isinstance(metricNames, list) or isinstance(metricNames, str)
    
    retDict = {}
    subDict = {}
    try:
       subDict = activityDict[activityName]
    except KeyError:
        print("Activity " + activityName + " not found")
        return retDict

    if(isinstance(metricNames, str)):
        retDict[metricNames] = subDict[metricNames]
        return retDict
    
    # For each metric
    for metricName in metricNames:
        metricName = metricName.strip()
        try:
            retDict[metricName] = subDict[metricName]
        except KeyError:
            #print("Metric " + metricName + " does not exist - skipping")
            pass

    return retDict
### End of function get_activity_samples

def sum_activity_metrics(activityDict, metricNames, activityName="main_thread"):
    """
    Sums the values in the list of samples for the metrics that are passed in

    Args:
        activityDict (dict): Dictionary of activity samples from which to read
        metricNames (list): List of metric names to read samples for
        activityName (str): Name of the activity from which samples are to be
            read

    Returns:
        List of summed values
    """
    assert isinstance(activityDict, dict)
    
    return [sum(x) for x in zip(
        *(get_activity_samples(activityDict, metricNames, activityName).values()))]
#### End of function sum_activity_metrics

def get_cpu_activity(profileDict, activityName="main_thread"):
    """
    Returns a list of sample values for the percentage of CPU activity (as a
    sum of the different CPU activities)

    Args:
        profileDict (dict): Dictionary of the JSON format of a MAP profile
        activityName (str): Name of the activity timeline from which to read
            data

    Returns:
        List of values of accumulated CPU activity percentage
    """
    assert isinstance(profileDict, dict)

    metricNames = ["normal_compute"]

    computeSamples = sum_activity_metrics(profileDict["samples"]["activity"],
            metricNames, activityName)

    return computeSamples
#### End of function get_cpu_activity

def get_total_cpu_activity(profileDict, activityName="main_thread"):
    """
    Returns a list of all cpu related activity (in openmp and single threaded
    regions)

    Args:
        profileDict (dict): Dictionary of the JSON format of a MAP profile
        activityName (str): Name of the activity timeline from which to read
            data

    Returns:
        List of values of accumulated CPU activity percentage
    """
    metricNames = ["normal_compute", "openmp"]
    computeSamples = sum_activity_metrics(profileDict["samples"]["activity"],
            metricNames, activityName)
    return computeSamples
#### End of function get_total_cpu_activity

def get_mpi_activity(profileDict, activityName="main_thread"):
    """
    Returns a list of sample values for the percentage of MPI activity (as a
    sum of the different MPI activities)

    Args:
        profileDict (dict): Dictionary of the JSON format of a MAP profile
        activityName (str): Name of the activity timeline from which to read
            data

    Returns:
        List of values of accumulated MPI activity percentage
    """
    assert isinstance(profileDict, dict)
    metricNames = ["collective_mpi", "collective_mpi_openmp",
            "point_to_point_mpi", "point_to_point_mpi_openmp"]

    return sum_activity_metrics(profileDict["samples"]["activity"],
            metricNames, activityName)
#### End of function get_mpi_activity

def get_io_activity(profileDict, activityName="main_thread"):
    """
    Returns a list of sample values for the percentage of IO activity (as a sum
    of the different IO activities)

    Args:
        profileDict (dict): Dictionary of the JSON format of a MAP profile
        activityName (str): Name of the activity timeline from which to read
            data

    Returns:
        List of values of accumulated IO activity percentage
    """
    assert isinstance(profileDict, dict)
    metricNames = ["io_reads", "io_reads_openmp", "io_writes",
            "io_writes_openmp"] 

    return sum_activity_metrics(profileDict["samples"]["activity"],
            metricNames, activityName)
#### End of function get_io_activity

def get_accelerator_activity(profileDict, activityName="main_thread"):
    """
    Returns a list of sample values for the percentage time spent on an
    accelerator

    Args:
        profileDict (dict): Dictionry of the JSON format of a MAP profile
        activityName (str): Name of the activity timeline from which to read
            data

    Returns:
        List of values of accumulated percentage time spent on an accelerator
    """
    assert isinstance(profileDict, dict)

    metricNames = ["accelerator"]

    return sum_activity_metrics(profileDict["samples"]["activity"],
            metricNames, activityName)
#### End of function get_accelerator_activity

def get_omp_active_activity(profileDict, activityName="main_thread"):
    """
    Returns a list of sample values for the percentage time spent in OpenMP
    regions, actively peforming something

    Args:
        profileDict (dict): Dictionary of the JSON format of a MAP profile
        activityName (str): Name of the activity timeline from which to read
            data

    Returns:
        List of values of accumulated percentage time spent actively performing
        something in OpenMP regions
    """
    assert isinstance(profileDict, dict)

    metricNames = ["openmp"]
    return sum_activity_metrics(profileDict["samples"]["activity"],
            metricNames, activityName)
#### End of function get_omp_active_activity

def get_sleep_activity(profileDict, activityName="main_thread"):
    """
    Returns a list of sample values for the percentage time spent sleeping

    Args:
        profileDict (dict): Dictionary of the JSON format of a MAP profile
        activityName (str): Name of the activity timeline from which to read
            data

    Returns:
        List of values of accumulated percentage time spent sleeping
    """
    assert isinstance(profileDict, dict)

    metricNames = ["sleep"]
    return sum_activty_metrics(profileDict["samples"]["activity"],
            metricNames, activityName)
#### End of function_get_sleep_activity

def get_openmp_overhead_activity(profileDict, activityName="main_thread"):
    """
    Returns a list of sample values for the percentage time spent in OpenMP
    overhead regions

    Args:
        profileDict (dict): Dictionary of the JSON format of a MAP profile
        activityName (str): Name of the activity timeline from which to read
            data

    Returns:
        List of values of accumulated percentage time spent in OpenMP overhead
    """
    assert isinstance(profileDict, dict)

    metricNames = ["openmp_overhead_in_region", "open_mp_overhead_no_region"]
    return sum_activity_metrics(profileDict["samples"]["activity"],
            metricNames, activityName)
#### End of function get_openmp_overhead_activity

def get_synchronisation_activity(profileDict, activityName="main_thread"):
    """
    Returns a list of sample values for the percentage time spent in
    synchronisation overhead

    Args:
        profileDict (dict): Dictionary of the JSON format of a MAP profile
        activityName (str): Name of the activity timeline from which to read
            data
    
    Returns:
        List of values of accumulated percentage time spent in synchronisation
    """
    assert isinstance(profileDict, dict)

    metricNames = ["synchronisation"]
    return sum_activity_metrics(profileDict["samples"]["activity"],
            metricNames, activityName)
#### End of function get_synchronisation_activity

def get_num_processes(profileDict):
    """
    Returns the number of processes used in the given profile

    Args:
        profileDict (dict): Dictionary of the JSON format of a MAP profile

    Returns:
        Number of processes used in the profile passed in
    """
    assert isinstance(profileDict, dict)

    return profileDict["info"]["number_of_processes"]
#### End of function get_num_processes

def get_num_nodes(profileDict):
    """
    Returns the number of nodes used in the given profile

    Args:
        profileDict (dict): Dictionary of the JSON format of a MAP profile

    Returns:
        Number of nodes used in the profile passed in
    """
    assert isinstance(profileDict, dict)

    return profileDict["info"]["number_of_nodes"]
#### End of function get_num_nodes

def get_num_threads(profileDict):
    """
    Returns the number of threads used in the given profile

    Args:
        profileDict (dict): Dictionary of the JSON format of a MAP profile
    """
    assert isinstance(profileDict, dict)

    # Assume that the number of OpenMP threads is the same on all processes, so
    # getting the min, max or mean will give the same value
    return profileDict["info"]["metrics"]["num_omp_threads_per_process"]["max"]
#### End of function get_num_threads

def get_avg_over_samples(sampleList, first=0, last=-1):
    """
    Returns the average of the list passed in. This is used to get a summary
    over a range in a list

    Args:
        sampleList (list): List of numeric samples to sum over

    Returns:
        The average over the requested range
    """
    assert isinstance(sampleList, list)
    assert len(sampleList) > 0
    assert isinstance(sampleList[0], numbers.Number)

    if (last == -1):
        last = len(sampleList)

    return sum(sampleList[first:last]) / (last - 1 - first)
#### End of function get_avg_over_samples
