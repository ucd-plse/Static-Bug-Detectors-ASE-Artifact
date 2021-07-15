#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

tools=( "sblt" "sbht" "infer" "eradicate" "nullaway" "cfnullness" )
auxs=( "covered_lines" "diff" "trace" )
populate_script="populate_db.py"
warnings_dir="../../data/tool-warnings/"
auxs_dir="../../data/auxiliary-data/"

for tool in "${tools[@]}"
do
    python3 $SCRIPT_DIR/$populate_script $SCRIPT_DIR/$warnings_dir$tool.warnings $tool
done

for aux in "${auxs[@]}"
do
    python3 $SCRIPT_DIR/$populate_script $SCRIPT_DIR/$auxs_dir$aux.csv $aux
done
