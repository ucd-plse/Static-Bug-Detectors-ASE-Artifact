import csv
import lxml
import os
import re
import subprocess
import sys

from bs4 import BeautifulSoup

from bugswarm.common import github_wrapper
from bugswarm.common import log
from bugswarm.common.rest_api.database_api import DatabaseAPI
from bugswarm.private.credentials import DATABASE_PIPELINE_TOKEN
from bugswarm.private.credentials import GITHUB_TOKENS


REGEX_LIST = [
    'object returned by .* could be null and is dereferenced at line .*',
    'object returned by .* could be null and is dereferenced by call to .* at line .*',
    'object .* could be null and is dereferenced by call to .* at line .*',
    'object .* could be null and is dereferenced at line .*',
    'object .* last assigned on line .* could be null and is dereferenced .*',
]


def main(argv=None):
    if argv is None:
        argv = sys.argv

    msgs_filepath = _validate_input(argv)
    msg_dict = {}

    with open(msgs_filepath) as file:
        for line in file:
            line = line.strip()
            msg_dict = _get_message_type(line, msg_dict)

    sum = 0
    for key in msg_dict:
        sum += msg_dict[key]
        print('{}: {}'.format(key, msg_dict[key]))

    print('Sum: {}'.format(sum))


def _get_message_type(line, message_dict):
    found = False
    for regex in REGEX_LIST:
        m = re.search(r'{}'.format(regex), line)
        if m:
            if regex in message_dict:
                message_dict[regex] += 1
            else:
                message_dict[regex] = 1
            found = True
            break
    return message_dict


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
    print('Usage: python3 infer_message_parser.py <messages_filepath>')


def _validate_input(argv):
    msgs_filepath = argv[1]

    if not os.path.isfile(msgs_filepath):
        log.error('The msgs_filepath argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    return msgs_filepath


if __name__ == '__main__':
    sys.exit(main())
