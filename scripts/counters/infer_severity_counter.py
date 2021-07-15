import os
import subprocess
import sys

from bs4 import BeautifulSoup


def main(argv=None):
    argv = argv or sys.argv
    reports_dir = _validate_input(argv)

    severities = {}
    with open(reports_dir) as file:
        lines = [(y.split(',')[3], y.split(',')[6]) for y in [x.strip() for x in file.readlines()]]
        for line in lines:
            if 'NULL_DEREFERENCE' not in line[0]:
                continue
            severity = line[1]
            if severity in severities:
                severities[severity] += 1
            else:
                severities[severity] = 1

    for severity in severities:
        print('{}: {}'.format(severity, severities[severity]))


def _run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    stdout = stdout.decode('utf-8').strip()
    stderr = stderr.decode('utf-8').strip()
    ok = process.returncode == 0
    return process, stdout, stderr, ok


def _print_error(msg, stdout=None, stderr=None):
    print('Error: ' + msg)
    if stdout is not None:
        print('stdout:\n{}'.format(stdout))
    if stderr is not None:
        print('stderr:\n{}'.format(stderr))


def _print_usage():
    print('Usage: python3 infer_severity_counter.py <reports_dir>')
    print('reports_dir: Path to the directory of reports')


def _validate_input(argv):
    if len(argv) != 2:
        _print_usage()
        sys.exit(1)
    reports_dir = argv[1]
    if not os.path.exists(reports_dir):
        print('The reports_dir argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    return reports_dir


if __name__ == '__main__':
    sys.exit(main())