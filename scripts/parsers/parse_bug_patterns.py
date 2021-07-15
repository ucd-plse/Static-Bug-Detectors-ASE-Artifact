"""
Given text file of the bug patterns from spotbugs. This script will parse and count the number of prefixes.
"""

import datetime
import docker
import os
import json
import subprocess
import sys
import time
import re


def _run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    stdout = stdout.decode('utf-8').strip()
    stderr = stderr.decode('utf-8').strip()
    ok = process.returncode == 0
    return process, stdout, stderr, ok


def _print_usage():
    log.info('Usage: python3 parse_bug_patterns.py ')
    log.info('image_tags_file: Path to a file containing a newline-separated list of image tags to process.')


def _validate_input(argv):
    if len(argv) != 2:
        _print_usage()
        sys.exit(1)
    input_file = argv[1]
    if not os.path.isfile(input_file):
        log.error('The input_file argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    return input_file


def main(argv=None):
    argv = argv or sys.argv

    input_file = _validate_input(argv)
    bug_patterns = {}

    with open(input_file) as file:
        for line in file:
            line = line.strip()
            m = re.search(r'^([a-zA-Z][a-zA-Z]):', line)
            if m:
                bug_pattern = m.group(1)
                if bug_pattern in bug_patterns:
                    bug_patterns[bug_pattern] = bug_patterns[bug_pattern] + 1
                else:
                    bug_patterns[bug_pattern] = 1

    for bp in bug_patterns:
        print('{}:{}'.format(bp, bug_patterns[bp]))


if __name__ == '__main__':
    sys.exit(main())
