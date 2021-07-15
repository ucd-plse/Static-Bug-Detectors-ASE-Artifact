#!/bin/bash
# Usage: bash infer_setup.sh analyzers/d4j.input
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

source $SCRIPT_DIR/../../config.sh

# Create sandbox
mkdir $NA_PROJ_FILES
mkdir $NA_PROJ_REPORTS

# Create directory for needed jars
mkdir ./nullaway_jars

download_nullaway_jars $SCRIPT_DIR/nullaway_jars/

# Checkout d4j files
export PATH=$PATH:$D4J_DIR/framework/bin
download_d4j_repos $NA_PROJ_FILES $CONFIG_SCRIPT_DIR/d4j.input

