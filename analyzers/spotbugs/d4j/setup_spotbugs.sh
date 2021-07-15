#!/bin/bash
# Usage: bash spotbugs_setup.sh .
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

source $SCRIPT_DIR/../../config.sh

# Create directories.
mkdir $SBLT_PROJ_FILES
mkdir $SBLT_PROJ_REPORTS

mkdir $SBHT_PROJ_FILES
mkdir $SBHT_PROJ_REPORTS


# Checkout d4j files.
export PATH=$PATH:$D4J_DIR/framework/bin
download_d4j_repos $SBLT_PROJ_FILES $CONFIG_SCRIPT_DIR/d4j.input
download_d4j_repos $SBHT_PROJ_FILES $CONFIG_SCRIPT_DIR/d4j.input

# Download SB source and jar.
download_spotbugs_source $1
download_spotbugs_jar $1
