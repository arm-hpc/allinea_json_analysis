#!/bin/bash
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

# Check that the map and performance reports commands are found
MAP_CMD=map
PR_CMD=perf-report

EXPORT_MAP=true
EXPORT_PR=true

MAP_FILE_DIR=""

if [ $# != 0 ]
then
    MAP_FILE_DIR="$1/"
fi

echo "${MAP_FILE_DIR}*.map"

which ${MAP_CMD} &> /dev/null
if [ $? -ne 0 ]
then
    echo "Unable to find Allinea MAP with command: ${MAP_CMD}"
    echo "Not exporting MAP files to JSON"
    EXPORT_MAP=false
fi

which ${PR_CMD} &> /dev/null
if [ $? -ne 0 ]
then
    echo "Unable to find Allinea Performance Reports with command: ${PR_CMD}"
    echo "Not exporting MAP files to Performance Reports"
    EXPORT_PR=false
fi

if [ "$EXPORT_MAP" = false ] && [ "$EXPORT_PR" = false ]
then
    echo "Unable to find MAP or Performance Reports commands. Nothing to do!"
    exit 1
fi

for mapfile in ${MAP_FILE_DIR}*.map ;
do
    MAP_BASENAME=$(echo ${mapfile} | awk -F'/' '{print $NF}')
    MAP_JSON_FNAME=${MAP_BASENAME/.map/.json}
    PR_JSON_FNAME=pr_${MAP_JSON_FNAME}

    if [ "$EXPORT_MAP" = true ] && ! [ -e ${MAP_JSON_FNAME} ]
    then
        ${MAP_CMD} --export=${MAP_JSON_FNAME} ${mapfile}
    fi

    if [ "$EXPORT_PR" = true ] && ! [ -e ${PR_JSON_FNAME} ]
    then
        ${PR_CMD} -o ${PR_JSON_FNAME} ${mapfile}
    fi
done
