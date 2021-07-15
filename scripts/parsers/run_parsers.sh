#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

mkdir -p $SCRIPT_DIR/results

# Parse Checker Framework
echo "### Running Checker Framework Parser ###"
python3 $SCRIPT_DIR/checkerframework_parser.py $SCRIPT_DIR/../../analyzers/results/checkerframework-proj-reports/

# Parse Eradicate
echo "### Running Eradicate Parser ###"
python3 $SCRIPT_DIR/infer_parser.py $SCRIPT_DIR/../../analyzers/results/eradicate-proj-reports/ eradicate

# Parse Infer
echo "### Running Infer Parser ###"
python3 $SCRIPT_DIR/infer_parser.py $SCRIPT_DIR/../../analyzers/results/infer-proj-reports/ infer

# Parse NullAway
echo "### Running NullAway Parser ###"
python3 $SCRIPT_DIR/nullaway_parser.py $SCRIPT_DIR/../../analyzers/results/nullaway-proj-reports/

# Parse SpotBugs Low
echo "### Running SpotBugs Low Threshold Parser ###"
python3 $SCRIPT_DIR/spotbugs_parser.py $SCRIPT_DIR/../../analyzers/results/sblt-proj-reports low

# Parse SpotBugs High
echo "### Running SpotBugs High Threshold Parser ###"
python3 $SCRIPT_DIR/spotbugs_parser.py $SCRIPT_DIR/../../analyzers/results/sbht-proj-reports high
