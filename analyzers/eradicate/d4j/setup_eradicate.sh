#!/bin/bash
# Usage: bash eradicate_setup.sh
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

source $SCRIPT_DIR/../../config.sh

download_infer $SCRIPT_DIR

# Create sandbox
mkdir $ERAD_PROJ_FILES
mkdir $ERAD_PROJ_REPORTS

# Checkout d4j files
export PATH=$PATH:$D4J_DIR/framework/bin
download_d4j_repos $ERAD_PROJ_FILES $CONFIG_SCRIPT_DIR/d4j.input

