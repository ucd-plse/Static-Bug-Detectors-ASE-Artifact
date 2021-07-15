#!/bin/bash

CONFIG_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
D4J_DIR=$CONFIG_SCRIPT_DIR/defects4j
RESULTS_DIR="$CONFIG_SCRIPT_DIR/results"

# SpotBugs file paths.
SBLT_PROJ_FILES=$RESULTS_DIR/"sblt-proj-files"
SBLT_PROJ_REPORTS=$RESULTS_DIR/"sblt-proj-reports"
SBHT_PROJ_FILES=$RESULTS_DIR/"sbht-proj-files"
SBHT_PROJ_REPORTS=$RESULTS_DIR/"sbht-proj-reports"

# Infer file paths.
INFER_PROJ_FILES=$RESULTS_DIR/"infer-proj-files"
INFER_PROJ_REPORTS=$RESULTS_DIR/"infer-proj-reports"

# Eradicate file paths.
ERAD_PROJ_FILES=$RESULTS_DIR/"eradicate-proj-files"
ERAD_PROJ_REPORTS=$RESULTS_DIR/"eradicate-proj-reports"

# NullAway file paths.
NA_PROJ_FILES=$RESULTS_DIR/"nullaway-proj-files"
NA_PROJ_REPORTS=$RESULTS_DIR/"nullaway-proj-reports"

# Checkerframework NullNess Checker file paths.
CF_PROJ_FILES=$RESULTS_DIR/"checkerframework-proj-files"
CF_PROJ_REPORTS=$RESULTS_DIR/"checkerframework-proj-reports"

download_infer () {
    URL="https://github.com/facebook/infer/releases/download/v0.14.0/infer-linux64-v0.14.0.tar.xz"
    curl -sSL $URL | tar -C $1 -xJ
}

download_checker_framework () {
    URL="https://github.com/typetools/checker-framework.git"
    git clone $URL $1
}

download_spotbugs_source () {
    URL="https://repo.maven.apache.org/maven2/com/github/spotbugs/spotbugs/3.1.6/spotbugs-3.1.6.tgz"
    wget -c $URL -O - | tar -xz $1
}

download_spotbugs_jar () {
    URL="https://repo1.maven.org/maven2/com/github/spotbugs/spotbugs-ant/3.1.6/spotbugs-ant-3.1.6.jar"
    wget $URL $1
}

download_nullaway_jars () {
    dataflow_URL="https://repo1.maven.org/maven2/org/checkerframework/dataflow/2.5.7/dataflow-2.5.7.jar"
    wget $dataflow_URL -P $1

    jformat_URL="https://repo1.maven.org/maven2/com/google/code/findbugs/jFormatString/3.0.0/jFormatString-3.0.0.jar"
    wget $jformat_URL -P $1

    dataflow_shaded_URL="https://repo1.maven.org/maven2/org/checkerframework/dataflow-shaded/3.1.2/dataflow-shaded-3.1.2.jar"
    wget $dataflow_shaded_URL -P $1

    javacutil_URL="https://repo1.maven.org/maven2/org/checkerframework/javacutil/2.5.7/javacutil-2.5.7.jar"
    wget $javacutil_URL -P $1

    threeten_URL="https://repo1.maven.org/maven2/org/threeten/threeten-extra/1.5.0/threeten-extra-1.5.0.jar"
    wget $threeten_URL -P $1

    nullaway_URL="https://repo1.maven.org/maven2/com/uber/nullaway/nullaway/0.3.0/nullaway-0.3.0.jar"
    wget $nullaway_URL -P $1

    javac_URL="https://repo1.maven.org/maven2/com/google/errorprone/javac/9+181-r4173-1/javac-9+181-r4173-1.jar"
    wget $javac_URL -P $1
}

download_d4j_repos () {
    # $1 Directory to store files.
    # $2 File with projects,bugid.
    while IFS="," read -r repo id
    do
        defects4j checkout -p ${repo} -v ${id} -w $1/${repo}-${id}
    done < $2
}
