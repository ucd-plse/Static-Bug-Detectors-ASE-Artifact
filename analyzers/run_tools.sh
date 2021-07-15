#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

USAGE='Usage: bash run_tools.sh [-t <tool-name>] [-b <bugswarm-ids>] [-d defects4j-ids] [-n d4j-na-ids] [-h]'

# Extract command line arguments.
OPTS=$(getopt -o t:b:d:n:h -n 'run-tools' -- "$@")
while true; do
    case "$1" in
      # Shift twice for options that take an argument.
      -t            ) tool_name="$2";             shift; shift ;;
      -b            ) bugswarm_file="$2";         shift; shift ;;
      -d            ) d4j_file="$2";              shift; shift ;;
      -n            ) d4j_na_file="$2";           shift; shift ;;
      -h            ) echo $USAGE; exit 0;                     ;;
      *             ) break                                    ;;
    esac
done

BUGSWARM_FILE=$SCRIPT_DIR/../data/bugs/bugswarm.bugs
D4J_FILE=$SCRIPT_DIR/d4j_with_info.input
D4J_NA_FILE=nullaway.input

if [ -n "${bugswarm_file}" ]; then
    BUGSWARM_FILE=$SCRIPT_DIR/../$bugswarm_file
fi

if [ -n "${d4j_file}" ]; then
    D4J_FILE=$SCRIPT_DIR/../$d4j_file
fi

if [ -n "${d4j_na_file}" ]; then
    D4J_NA_FILE=$d4j_na_file
fi


run_checker_framework () {
    # Run Checker Framework
    echo "Running Checker Framework"
     # Run BugSwarm
    cd $SCRIPT_DIR/checker-framework/bugswarm/
    python3 main.py $BUGSWARM_FILE bugswarm/images 2
     # Run D4J
    cd $SCRIPT_DIR/checker-framework/d4j/
    python3 run_checker_framework.py $D4J_FILE
}

run_eradicate () {
    # Run Eradicate
    echo "Running Eradicate"
     # Run BugSwarm
    cd $SCRIPT_DIR/eradicate/bugswarm/
    python3 main.py $BUGSWARM_FILE failed bugswarm/images
    python3 main.py $BUGSWARM_FILE passed bugswarm/images
     # Run D4J
    cd $SCRIPT_DIR/eradicate/d4j/
    python3 run_eradicate.py $D4J_FILE
}

run_infer () {
    # Run Infer
    echo "Running Infer"
     # Run BugSwarm
    cd $SCRIPT_DIR/infer/bugswarm/
    python3 main.py $BUGSWARM_FILE failed bugswarm/images 2
    python3 main.py $BUGSWARM_FILE passed bugswarm/images 2
     # Run D4J
    cd $SCRIPT_DIR/infer/bugswarm/
    python3 run_infer.py $D4J_FILE
}

run_nullaway () {
    # Run Nullaway
    echo "Running NullAway"
     # Run BugSwarm
    cd $SCRIPT_DIR/nullaway/bugswarm/
    python3 main.py $BUGSWARM_FILE bugswarm/images 2
     # Run D4J
    cd $SCRIPT_DIR/nullaway/d4j/
    python3 run_nullaway.py $D4J_NA_FILE
}

run_spotbugs () {
    # Run SpotBugs Low Threshold
    echo "Running SpotBugs Low Threshold"
     # Run BugSwarm
    cd $SCRIPT_DIR/spotbugs/bugswarm/
    python3 main.py $BUGSWARM_FILE bugswarm/images low 1
     # Run D4J
    cd $SCRIPT_DIR/spotbugs/d4j/
    python3 run_spotbugs.py $D4J_FILE low
    # Run SpotBugs High Threshold
    echo "Running SpotBugs High Threshold"
     # Run BugSwarm
    cd $SCRIPT_DIR/spotbugs/bugswarm/
    python3 main.py $BUGSWARM_FILE bugswarm/images high 2
     # Run D4J
    cd $SCRIPT_DIR/spotbugs/d4j/
    python3 run_spotbugs.py $D4J_FILE high
}

if [ -n "${tool_name}" ]; then
    case $tool_name in
        checker-framework)
            run_checker_framework
            ;;
        eradicate)
            run_eradicate
            ;;
        infer)
            run_infer
            ;;
        nullaway)
            run_nullaway
            ;;
        spotbugs)
            run_spotbugs
            ;;
        *)
            echo "Not supported tool."
            ;;
    esac
else # Run all tools
    # Run Checker Framework
    run_checker_framework
    # Run Eradicate
    run_eradicate
    # Run Infer
    run_infer
    # Run Nullaway
    run_nullaway
    # Run SpotBugs
    run_spotbugs
fi


