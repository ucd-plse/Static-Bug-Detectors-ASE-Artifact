#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "### Preparing Database ###"

echo "### Creating Database and Tables ###"
python3 $SCRIPT_DIR/create_tables.py

echo "### Populating Tables ###"
bash $SCRIPT_DIR/populate_tables.sh $1
