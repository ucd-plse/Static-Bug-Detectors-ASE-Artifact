import os
import shutil
import subprocess
import sys

from pathlib import Path

MODIFY_BUILD_XML_SCRIPT='modify_build_xml.py'
MODIFY_POM_XML_SCRIPT='modify_pom.py'
BUG_DIR='../../results/checkerframework-proj-files'
REPORTS_DIR='../../results/checkerframework-proj-reports'


def _run_command(command:str):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    stdout = stdout.decode('utf-8').strip()
    stderr = stderr.decode('utf-8').strip()
    ok = process.returncode == 0
    return process, stdout, stderr, ok

def run_checker_framework(bug_id: str, build_script: str):
    for b_or_f in ['b', 'f']:
        bug_id_dir = os.path.join(BUG_DIR, bug_id + b_or_f)
        bug_id_dir_path = Path(bug_id_dir).absolute()
        report_dir = os.path.join(REPORTS_DIR, bug_id, b_or_f)
        report_dir_path = Path(report_dir).absolute()
        mkdir_cmd = 'mkdir -p {}'.format(report_dir_path)
        _, stdout, stderr, ok = _run_command(mkdir_cmd)
        if 'build.xml' in build_script:
            # Call run_cf_ant.sh
            _, stdout, stderr, ok = _run_command('bash run_cf_ant.sh {} {}'.format(bug_id, b_or_f))
        else: # build_script == 'pom.xml'
            if 'JacksonDatabind' in bug_id:
                # Call run_cf_mvn_JD.sh
                _, stdout, stderr, ok = _run_command('bash run_cf_mvn_JD.sh {} {}'.format(bug_id, b_or_f))
            else:
                # Call run_cf_mvn.sh
                _, stdout, stderr, ok = _run_command('bash run_cf_mvn.sh {} {}'.format(bug_id, b_or_f))
        cp_cmd = 'cp {}/nullness.txt {}'.format(bug_id_dir, report_dir_path)
        _, stdout, stderr, _ = _run_command(cp_cmd)
        print('Copied nullness.txt to {}'.format(report_dir))

def _validate_input(argv):
    if len(argv) != 2:
        _print_usage()
        sys.exit(1)
    fp = argv[1]
    return fp

def main(argv=None):
    argv = argv or sys.argv

    bugs_fp = _validate_input(argv)
    bug_tuples = []
    with open(bugs_fp) as f:
        bug_tuples = [bug.strip().split(',') for bug in f.readlines()]
    
    for bug in bug_tuples:
        print(bug[0], bug[1])
        run_checker_framework(bug[0], bug[1])

if __name__ == '__main__':
    sys.exit(main())

