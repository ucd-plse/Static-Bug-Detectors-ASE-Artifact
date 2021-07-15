#!/bin/bash
source ../../config.sh
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
MODIFY_SCRIPT=${SCRIPT_DIR}/modify_build_xml.py

proj_id=$1$2
cd ${CF_PROJ_FILES}/$proj_id
python3 ${MODIFY_SCRIPT} build.xml
python3 ${MODIFY_SCRIPT} maven-build.xml
ant check-nullness &> nullness.txt
