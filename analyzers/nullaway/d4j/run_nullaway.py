import os
import shutil
import subprocess
import sys

from os.path import abspath
from pathlib import Path

MODIFY_BUILD_XML_SCRIPT='modify_build_xml.py'
MODIFY_POM_XML_SCRIPT='modify_pom.py'
BUG_DIR = abspath('../../results/nullaway-proj-files')
REPORTS_DIR = abspath('../../results/nullaway-proj-reports')



def _run_command(command:str):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    stdout = stdout.decode('utf-8').strip()
    stderr = stderr.decode('utf-8').strip()
    ok = process.returncode == 0
    return process, stdout, stderr, ok

def run_nullaway(bug_id: str, build_script: str, group_id: str):
    for b_or_f in ['b', 'f']:
        bug_id_dir = os.path.join(BUG_DIR, bug_id + b_or_f)
        report_dir = os.path.join(REPORTS_DIR, bug_id, b_or_f)
        report_dir_path = Path(report_dir).absolute()
        mkdir_cmd = 'mkdir -p {}'.format(report_dir_path)
        _, stdout, stderr, ok = _run_command(mkdir_cmd)
        if 'build.xml' in build_script:
            cmd = 'python3 {} {} {}'.format(MODIFY_BUILD_XML_SCRIPT, os.path.join(bug_id_dir, build_script), group_id)
            _, stdout, stderr, ok = _run_command(cmd)
            compile_cmd = 'cd {} && ant compile >> nullaway.txt 2>&1'.format(bug_id_dir)
            _, na_output, stderr, ok = _run_command(compile_cmd)
        else: # build_script == 'pom.xml'
            cmd = 'python3 {} {} {}'.format(MODIFY_POM_XML_SCRIPT, os.path.join(bug_id_dir, build_script), group_id)
            _, stdout, stderr, ok = _run_command(cmd)
            compile_cmd = 'cd {} && mvn compile >> nullaway.txt 2>&1'.format(os.path.join(bug_id_dir, comp_dir), comp_dir)
            _, na_output, stderr, ok = _run_command(compile_cmd)
        report_dir = os.path.join(REPORTS_DIR, bug_id, b_or_f)
        cp_cmd = 'cp {}/nullaway.txt {}'.format(bug_id_dir, report_dir_path)
        _, stdout, stderr, _ = _run_command(cp_cmd)
        print('Copied nullaway.txt to {}'.format(report_dir))

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
        print(bug[0], bug[1], bug[2])
        run_nullaway(bug[0], bug[1], bug[2])

if __name__ == '__main__':
    sys.exit(main())

