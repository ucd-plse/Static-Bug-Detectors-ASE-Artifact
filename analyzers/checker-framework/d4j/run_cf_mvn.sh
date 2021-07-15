#!/bin/bash
source ../../config.sh
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
MODIFY_SCRIPT=${SCRIPT_DIR}/modify_pom.py

proj_id=$1$2
echo $proj_id
cd ${CF_PROJ_FILES}/$proj_id
python3 ${MODIFY_SCRIPT} pom.xml
mvn clean install -U -fn -DskipTests -Dcheckstyle.skip -Denforcer.skip=true -Danimal.sniffer.skip=true &> nullness.txt
