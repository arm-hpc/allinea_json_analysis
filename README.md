# Allinea MAP / Performance Reports JSON export analysis scripts

## Introduction

Allinea MAP is capable of exporting performance data from the .map files into the open JSON format.
This data can then be post-processed and for analysis and visualisation.

This data can also be generated from Performance Reports at runtime.

This collection of python scripts provide a starting point for those looking to interpret this data.
They demonstrate taking this data and plotting it using pyplot.
As such these scripts are intended to be modified and adapted to the specific requirements of users.

## JSON Export

The export capabilities of the Allinea tools are documented in the corresponding user guides:

* [MAP User Guide](https://www.allinea.com/user-guide/forge/ExportingprofilerdatainJSONformat.html#x36-31600031)
* [Performance Reports User Guide](https://www.allinea.com/user-guide/reports/userguide.html)

### MAP

MAP can export the performance data from a .map as follows:

        $ map --export=profile.json profile.map

### Performance Reports

Performance Reports can export the data as follows:

        $ perf-report --output=report.json mpirun ...

Alternatively, Performance Reports can generate a report based on a .map file, again to JSON.

        $ perf-report --output=report.json profile.map

## Script Usage

Each python script provides a help text:

        $ python plot_map_bar.py –help

And can be used as follows:

        $ python ./MAP_JSON_Scripts/show_metric_names.py ./profile.json


These scripts have been tested with Python 2.7 and 3.5, but should still be considered experimental.


## Script Description

### Scripts for MAP Profiles

Located in the `MAP_JSON_Scripts/` folder.

#### generate\_sample\_csv.py

Generates a CSV file of the metric values in a MAP profile. The rows represent metrics and the columns a sample.

#### map\_json\_common.py

Common functions to extract information from the JSON export of a map file.

#### plot\_map\_bar.py

Plots a graph given a list of JSON exported MAP profiles.
For example, given a set of strong scaling experiments and the name of a metric (for example the number of POSIX bytes written) will plot a bar chart for each of the process counts.
It is also possible to plot a line graph with expected scaling, and log axes.

#### plot\_map\_min\_max\_bar.py

Plots a stacked bar chart of the minimum, mean and maximum of a given metric over a specified range of sample values.
This takes in a list of MAP files which are assumed to show strong / weak scaling.


#### plot\_mult\_metrics\_one\_file.py

Given the JSON export of a MAP file and a list of metrics, will plot the values of the metrics on the same axes.
This makes sense for comparison of metrics such as bytes read / written.

#### plot\_one\_metric\_mult\_files\_axes.py

Given the name of a metric and a list of MAP files, plots the same metric on different axes.
The x-axes are labelled with absolute time from zero to the maximum recorded time.

#### plot\_one\_metric\_mult\_files.py

Given the name of a metric and a list of MAP files, plots the same metric on the same axes.

#### plot\_single\_metric.py

Plots a single metric from a single MAP profile as a line graph.

#### show\_metric\_names.py

Shows the names of the metrics available in a MAP profile.

----

### Scripts for Performance Reports Profiles

Located in the `PR_JSON_Scripts/` folder.

#### plot\_pr\_bar.py

Plots a bar chart of different metrics from the JSON export of a Performance Report profile from a series of profiles.
It is assumed that the series of profiles show the strong / weak scaling of an application.

#### plot\_pr\_stacked\_bar.py

Plots a stacked bar chart of MPI, I/O and CPU activity over a set of Performance Report profiles.
It is assumed that the set of profiles are generated from strong / weak scaling experiments.

#### plot\_scaling\_components.py

Plots line charts for the MPI, I/O and CPU activity recorded over a set of strong / weak scaling experiments.

#### plot\_scaling\_overall\_time.py

Plots a line chart to show the scaling of the overall run time of a set of strong / weak scaling experiments.

#### pr\_json\_common.py

Useful functions for handling JSON exports of Performance Reports.

#### pr\_plot\_mem\_use\_mpi\_bar.py

Example of how to target some more specific information contained in a Performance Report.
This plots the % memory usage vs MPI time measured in a performance report profile.

----

### Common JSON Scripts

Located in the `JSON_Common/` folder.

#### json\_dict\_common.py

Functions useful for accessing data in a JSON dictionary.

#### show\_json\_keys.py

Lists the keys (hierarchically) in a JSON file. Useful for figuring out which field values to access.

#### show\_json\_value.py

Given a list of field identifiers, shows the value contained in a given field in a JSON file.
