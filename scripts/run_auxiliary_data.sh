#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create auxiliary data folder
mkdir $SCRIPT_DIR/auxiliary-data

# Get coverage data.

# Get code diff data.
 # BugSwarm
python3 $SCRIPT_DIR/util/approx_lines_changed.py $SCRIPT_DIR/../data/bugs/bugswarm.bugs
 # D4J
python3 $SCRIPT_DIR/util/d4j_approx_lines_changed.py $SCRIPT_DIR/../data/bugs/defects4j.bugs

# Get stack trace data.
 # BugSwarm
python3 $SCRIPT_DIR/parsers/parse_travis_log.py $SCRIPT_DIR/../data/bugs/bugswarm.bugs
 # D4J
python3 $SCRIPT_DIR/parsers/parse_d4j_log.py $SCRIPT_DIR../../data/bugs/defects4j.bugs
