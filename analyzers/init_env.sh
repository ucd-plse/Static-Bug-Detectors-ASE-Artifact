#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source $SCRIPT_DIR/config.sh

echo "Starting initializing environment"

# Make results directory
mkdir $RESULTS_DIR

# Initialize D4J
echo "Initializing Defects4J"
bash $SCRIPT_DIR/init_d4j.sh

# Setup tools
echo "Setting up Checker Framework"
cd $SCRIPT_DIR/checker-framework/d4j
bash setup_checker_framework.sh

echo "Setting up Eradicate"
cd $SCRIPT_DIR/eradicate/d4j
bash setup_eradicate.sh

echo "Setting up Infer"
cd $SCRIPT_DIR/infer/d4j
bash setup_infer.sh

echo "Setting up NullAway"
cd $SCRIPT_DIR/nullaway/d4j
bash setup_nullaway.sh

echo "Setting up SpotBugs"
cd $SCRIPT_DIR/spotbugs/d4j
bash setup_spotbugs.sh

echo "Done initializing environment"
