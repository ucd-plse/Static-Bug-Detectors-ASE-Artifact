#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "### Preparing Database ###"

# Extract command line arguments.
OPTS=$(getopt -o d:r --name "$0" -- "$@")
while true; do
    case "$1" in
      -r            ) repro_flag="$1"; shift        ;;
	  -d            ) db_name="$2"; shift; shift    ;;
      *             ) break                         ;;
    esac
done

echo "### Creating Database and Tables ###"
python3 $SCRIPT_DIR/create_tables.py $db_name

if [ -z ${repro_flag} ]; then
	echo "### Populating Tables ###"
	bash $SCRIPT_DIR/populate_tables.sh -d $db_name
else
	echo "### Populating Tables ###"
	bash $SCRIPT_DIR/populate_tables.sh -r -d $db_name
fi


