#!/bin/bash
# Usage: bash infer_setup.sh analyzers/d4j.input
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

source $SCRIPT_DIR/../../config.sh

# Create sandbox
mkdir $INFER_PROJ_FILES
mkdir $INFER_PROJ_REPORTS


# Checkout d4j files
export PATH=$PATH:$D4J_DIR/framework/bin
download_d4j_repos $INFER_PROJ_FILES $CONFIG_SCRIPT_DIR/d4j.input

