import os
import shutil
import subprocess
import sys

from pathlib import Path

MODIFY_BUILD_XML_SCRIPT='modify_build_xml.py'
MODIFY_POM_XML_SCRIPT='modify_pom.py'
BUGS_DIR='../../results/sb-proj-files'
REPORTS_DIR='../../results/sb-proj-reports'


def _run_command(command:str):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    stdout = stdout.decode('utf-8').strip()
    stderr = stderr.decode('utf-8').strip()
    ok = process.returncode == 0
    return process, stdout, stderr, ok

def run_spotbugs(bug_id: str, build_script: str, low_or_high: str):
    for b_or_f in ['b', 'f']:
        bug_id_dir = os.path.join(BUGS_DIR, bug_id + b_or_f)
        report_dir = os.path.join(REPORTS_DIR, bug_id, b_or_f)
        report_dir_path = Path(report_dir).absolute()
        mkdir_cmd = 'mkdir -p {}'.format(report_dir)
        _, _, _, ok = _run_command(mkdir_cmd)
        if build_script == 'build.xml':
            cmd = 'python3 {} {} {}'.format(MODIFY_BUILD_XML_SCRIPT, os.path.join(bug_id_dir, build_script), low_or_high)
            _, stdout, stderr, ok = _run_command(cmd)
            compile_cmd = 'cd {} && ant compile && ant spotbugs'.format(bug_id_dir)
            _, sb_output, stderr, ok = _run_command(compile_cmd)
            cp_cmd = 'cp {}/spotbugsXml.xml {}'.format(bug_id_dir, report_dir_path)
            _, _, _, _ = _run_command(cp_cmd)
        else:
            cmd = 'python3 {} {} {}'.format(MODIFY_POM_XML_SCRIPT, os.path.join(bug_id_dir, build_script), low_or_high)
            _, stdout, stderr, ok = _run_command(cmd)
            compile_cmd = 'cd {} && mvn test-compile compile'.format(bug_id_dir)
            _, sb_output, stderr, ok = _run_command(compile_cmd)
            sb_cmd = 'cd {} && mvn com.github.spotbugs:spotbugs-maven-plugin:3.1.6:spotbugs'.format(bug_id_dir)
            _, sb_output, stderr, ok = _run_command(sb_cmd)
            cp_cmd = 'pwd && cd {} && pwd && cp target/spotbugsXml.xml {}'.format(bug_id_dir, report_dir_path)
            _, stdout, stderr, _ = _run_command(cp_cmd)
        print('Copied spotbugsXml.xml to {}'.format(report_dir_path))

def _validate_input(argv):
    if len(argv) != 3:
        _print_usage()
        sys.exit(1)
    fp = argv[1]
    low_or_high = argv[2]
    return fp, low_or_high

def main(argv=None):
    argv = argv or sys.argv

    bugs_fp, low_or_high = _validate_input(argv)
    global BUGS_DIR
    global REPORTS_DIR
    effort = 'lt' if low_or_high == 'low' else 'ht'
    BUGS_DIR='../../results/sb{}-proj-files'.format(effort)
    REPORTS_DIR='../../results/sb{}-proj-reports'.format(effort)

    bug_tuples = []
    with open(bugs_fp) as f:
        bug_tuples = [bug.strip().split(',') for bug in f.readlines()]
    
    for bug in bug_tuples:
        print(bug[0], bug[1])
        run_spotbugs(bug[0], bug[1], low_or_high)

if __name__ == '__main__':
    sys.exit(main())

