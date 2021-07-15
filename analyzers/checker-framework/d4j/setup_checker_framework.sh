#!/bin/bash
source ../../config.sh
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create sandbox
mkdir $CF_PROJ_FILES
mkdir $CF_PROJ_REPORTS

# Download Checker Framework and build
download_checker_framework $SCRIPT_DIR/checker-framework
export CHECKERFRAMEWORK=$SCRIPT_DIR/checker-framework
cd $CHECKERFRAMEWORK
./gradlew assemble

# Checkout d4j files
export PATH=$PATH:$D4J_DIR/framework/bin
download_d4j_repos $CF_PROJ_FILES $CONFIG_SCRIPT_DIR/d4j.input
