# On the Real-World Effectiveness of Static Bug Detectors at Finding Null Pointer Exceptions
![Workflow](https://github.com/ucd-plse/Static-Bug-Detectors-ASE-Artifact/blob/main/workflow-not-transparent.png)
## Data
All tool reports are located in https://drive.google.com/drive/folders/1CGStm2KTJdoidIsASVy9ZfoBoQZofxIA?usp=sharing

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
### 2. Running tools (8 hours to 1+ days)
Either run a specific tool tool (e.g. spotbugs) or all the tools. We recommend running a specific tool due to time constraints.
#### Running a specific tool (Recommended)
```
$ bash analyzers/run_tools.sh -t spotbugs
```
Note: Inputs supported are: checker-framework, eradicate, infer, nullaway, spotbugs.
#### Running all tools
```
$ bash analyzers/run_tools.sh
```

### 3. Parsing tool reports (~5 minute)
#### A. Parse tool reports
```
$ bash scripts/parsers/run_parsers.sh
```
#### B. Verify tool warnings
If ran only a specific tool then only that tool should match. All other tools will have 0 warnings. If bugs under study have become unreproducible then this may cause a mismatch in number of warnings.
```
$ bash verify-scripts/run_verify_tool_warnings.sh
```
![tableiii](https://github.com/ucd-plse/Static-Bug-Detectors-ASE-Artifact/blob/main/tableiii.PNG)
### 4. Setting up DB (~10 minutes)
#### Creating and populating database tables
We offer two options for getting results for Table IV. The first is to use the reproduced warnings that were generated when you ran Step 2. This option may not have the same results as the study due to a bug under study becoming unreproducible. To avoid this issue, you may use the tool warnings we observed in the study. This will produce the exact results reported in Table IV.

Note: Make sure that your machine has MySQL installed. Once MySQL is installed, also ensure that the `mysql_native_password` is the plugin selected for authorization on `root` using:
```
mysql> SELECT plugin from mysql.user where User='root';
``` 
If any plugin besides `mysql_native_password` is listed, you should run the following commands to ensure that the right authentication plugin is selected, otherwise the following scripts will not work:
```
mysql> UPDATE mysql.user SET plugin = 'mysql_native_password' WHERE User = 'root';
mysql> FLUSH PRIVILEGES;
```
##### Use reproduced warnings
```
$ bash scripts/database/db_wrapper.sh -r -d study_db
```
##### Use study warnings
```
$ bash scripts/database/db_wrapper.sh -d study_db
```
### 5. Bug Candidates (2 - 5 hours)
![tableiv](https://github.com/ucd-plse/Static-Bug-Detectors-ASE-Artifact/blob/main/tableiv.PNG)
#### A. Generating bug candidates via mapping methods (2 - 5 hours)
```
$ python3 scripts/database/run_mapping_methods.py study_db
```
#### B. Verifying bug candidates (~1 minute)
These results are the numerator in Table IV. If using reproduced warnings and single tool, you will only see results for the specific tool that was ran. Note that if using reproduced warnings the results may not match due to a bug under study becoming unreproducible.
```
$ python3 verify-scripts/verify_bug_candidates.py bug_candidates.json
```
#### C. Verifying true bugs (~1 minute)
These results are the denominator in Table IV. If using reproduced warnings and single tool, you will only see results for the specific tool that was ran. Note that if using reproduced warnings the results may not match due to a bug under study becoming unreproducible.
```
$ python3 verify-scripts/verify_true_bugs.py bug_candidates.json
```
