import csv
import lxml
import os
import subprocess
import sys

from bs4 import BeautifulSoup

from bugswarm.common import github_wrapper
from bugswarm.common import log
from bugswarm.common.rest_api.database_api import DatabaseAPI
from bugswarm.private.credentials import DATABASE_PIPELINE_TOKEN
from bugswarm.private.credentials import GITHUB_TOKENS


def main(argv=None):
    if argv is None:
        argv = sys.argv

    CSV_filepath, keyword = _validate_input(argv)
    bugs = []
    with open(CSV_filepath) as file:
        reader = csv
        content = file.readlines()
        for l in content:
            bugs.append(l.strip().split(','))

    filter_bugs = []
    for i in range(0,len(bugs)-2):
        lines_same = _compare_lines(bugs[i], bugs[i+1])
        if not lines_same:
            filter_bugs.append(bugs[i])

    keyword_filter_bugs = []
    for bug in filter_bugs:
        # print(bug[3])
        if keyword in bug[3]:
            keyword_filter_bugs.append(bug)

    with open('filtered_output-sb-ts.csv','w') as file:
        for bug in keyword_filter_bugs:
            file.write('{}\n'.format(','.join(bug)))

    print('Done processing all image-tags')


def _compare_lines(line1, line2):
    for i in range(0,len(line1)-1):
        if line1[i] != line2[i]:
            return False
    return True


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
    print('Usage: python3 filer_csv.py <CSV_filepath> <keyword>')



def _validate_input(argv):
    CSV_filepath = argv[1]

    if not os.path.isfile(CSV_filepath):
        log.error('The CSV_filepath argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    keyword = argv[2]
    return CSV_filepath, keyword


if __name__ == '__main__':
    sys.exit(main())
