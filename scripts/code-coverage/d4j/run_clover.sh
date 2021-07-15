#!/bin/bash

# bash run_infer_non_chart.sh /tmp/chart_4b chart-4 b
# COMP_DIR=/home/dtomassi/fse2020/StaticBugCheckers/infer
DEFECTS4J_SANDBOX=/home/dtomassi/bugswarm-sandbox-d4j-clover
MODIFY_SCRIPT=/home/dtomassi/archive/fse2020/StaticBugCheckers/clover/modify_build_xml.py
#export PATH=$PATH:/home/dtomassi/fse2020/StaticBugCheckers/defects4j/framework/bin
export PATH=$PATH:/home/dtomassi/github/defects4j/framework/bin
# echo ${value}
cd $1
python3 ${MODIFY_SCRIPT} $6
#python3 ${MODIFY_SCRIPT} maven-build.xml
defects4j compile
ant clean compile -keep-going with.clover test clover.xml -Dtestclass=$2 -Dtestmethod=$3

mkdir -p ${DEFECTS4J_SANDBOX}/$4/$5
cp $1/coverage.xml ${DEFECTS4J_SANDBOX}/$4/$5
