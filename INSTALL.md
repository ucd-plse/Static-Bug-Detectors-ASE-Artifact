# On the Real-World Effectiveness of Static Bug Detectors at Finding Null Pointer Exceptions
![Workflow](https://github.com/ucd-plse/Static-Bug-Detectors-ASE-Artifact/blob/main/workflow-not-transparent.png)
## Data
All data used in the results are located under `data/`
#### Bug IDs (in `data/bugs/`)
* `bugswarm.bugs` contains the list of bugs from the BugSwarm included the study.
* `defects4j.bugs` contains the list of bugs from the Defects4J included the study.
* `bugswarm-subset.bugs` contains the subset of the list of bugs from the BugSwarm included the study.
* `defects4j-subset.bugs` contains a subset of the list of bugs from the Defects4J included the study.
#### Tool warnings (in `data/tool-warnings/`)
* `sblt.warnings` contains all parsed warnings from SpotBugsLT.
* `sbht.warnings` contains all parsed warnings from SpotBugsHT.
* `infer.warnings` contains all parsed warnings from Infer.
* `nullaway.warnings` contains all parsed warnings from NullAway.
* `eradicate.warnings` contains all parsed warnings from Eradicate.
* `cfnullness.warnings` contains all parsed warnings from Checker Framework's Nullness Checker.
#### Auxiliary data (in `data/auxiliary-data/`)
* `covered_lines.csv` contains all code coverage information for each bug.
* `diff.csv` contains all code diff information for each bug.
* `tace.csv` contains all stack trace information for each bug.
#### Found bugs (in `data/found-bugs/`)
* `sblt.found` contains all found bugs by SpotBugsLT.
* `sbht.found` contains all found bugs by SpotBugsHT.
* `infer.found` contains all found bugs by Infer.
* `nullaway.found` contains all found bugs by NullAway.
* `eradicate.found` contains all found bugs by Eradicate.
* `cfnullness.found` contains all found bugs by Checker Framework's Nullness Checker.
## Prerequisites
1. Have BugSwarm configured (https://github.com/BugSwarm/bugswarm#setting-up-bugswarm).
2. Have Defects4J requirements installed (https://github.com/rjust/defects4j#requirements).
3. Have Docker installed (https://docs.docker.com/get-docker/).
## Steps to replicate study
Note: Original study was ran on Ubuntu 16.04
### 1. Prepare environment for study (~1 hour)
#### A. Initialize environment
```
$ bash analyzers/init_env.sh
```
#### B. Export Defects4J
```
$ export PATH=$PATH:$PWD/analyzers/defects4j/framework/bin
```
### 2. Running tools (1 hour to 1+ days)
#### Running all tools
```
$ bash analyzers/run_tools.sh
```
Note: Inputs supported are: checker-framework, eradicate, infer, nullaway, spotbugs.
#### Optional: Running the study on a sample of bugs
```
$ bash analyzers/run_tools.sh -b data/bugs/bugswarm-subset.bugs -d analyzers/d4j_with_info-sample.input -n analyzers/nullaway/d4j/nullaway-sample.input
```
#### Optional: Running a specific tool
```
$ bash analyzers/run_tools.sh -t <tool-name>
```
### 3. Parsing tool reports (~5 minute)
![tableiii](https://github.com/ucd-plse/Static-Bug-Detectors-ASE-Artifact/blob/main/tableiii.png)
#### A. Parse tool reports
```
$ bash scripts/parsers/run_parsers.sh
```
#### B. Verify tool warnings
```
$ bash verify-scripts/run_verify_tool_warnings.sh
```
### 4. Setting up DB (~10 minutes)
#### Creating and populating database tables
```
$ bash scripts/database/db_wrapper.sh
```
### 5. Bug Candidates (~5 hours)
![tableiv](https://github.com/ucd-plse/Static-Bug-Detectors-ASE-Artifact/blob/main/tableiv.png)
#### A. Generating bug candidates via mapping methods (~5 hours)
Note: All bug candidates needs to be manually inspected to determine if they are true bugs.
```
$ python3 scripts/database/run_mapping_methods.py
```
#### B. Verifying bug candidates (~1 minute)
```
$ python3 verify-scripts/verify_bug_candidates.py bug_candidates.json
```
#### C. Verifying true bugs (~1 minute)
```
$ python3 verify-scripts/verify_true_bugs.py bug_candidates.json
```
