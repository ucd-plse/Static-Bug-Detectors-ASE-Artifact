#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source $SCRIPT_DIR/config.sh

cd $CONFIG_SCRIPT_DIR
git clone -q https://github.com/rjust/defects4j.git
cd defects4j
./init.sh
