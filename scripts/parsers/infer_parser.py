import json
import os
import shutil
import subprocess
import sys
import time

from os.path import abspath

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

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
    print('Usage: python3 infer_parser.py <report_filepath> <is_bugswarm>')
    print('report_filepath: Path to a file the reports from infer to process.')
    print('is_bugswarm: true or false.')


def _validate_input(argv):
    if len(argv) != 3:
        print('Provide the correct amount of arguments.')
        _print_usage()
        sys.exit()
    sandbox_dir = argv[1]
    if not os.path.isdir(sandbox_dir):
        print('The sandbox_dir argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    infer_or_erad = argv[2]
    return sandbox_dir, infer_or_erad


def get_image_tag_list(directory):
    cmd = 'ls {}'.format(directory)
    _, stdout, stderr, ok = _run_command(cmd)
    if not ok:
        _print_error('Error getting list of image_tags', stdout ,stderr)
    image_tags = [x.strip() for x in stdout.split('\n')]
    return image_tags


def get_f_or_p(reports_dir, image_tag):
    cmd = 'ls {}'.format(os.path.join(reports_dir, image_tag))
    _, stdout, stderr, ok = _run_command(cmd)
    return stdout.split('\n')


def main(argv=None):
    argv = argv or sys.argv
    sandbox_dir, infer_or_erad = _validate_input(argv)
    REPORT_PATH = 'report.json'

    image_tags = get_image_tag_list(sandbox_dir)
    bugs_list = []
    for image_tag in image_tags:
        for f_or_p in get_f_or_p(sandbox_dir, image_tag):
            try:
                with open(os.path.join(sandbox_dir, image_tag, f_or_p, REPORT_PATH)) as file:
                    report_json = json.loads(file.read())
                    for bug in report_json:
                        f_or_p = 'failed' if f_or_p == 'b' else 'passed'
                        bugs_list.append('{},{},{},{},{},{}\n'.format(image_tag.strip(), f_or_p.strip(), bug['file'].strip(), bug['bug_type'].strip(), bug['line'], bug['line']))
            except BaseException as e:
                continue
    with open(abspath('{}/results/{}.warnings'.format(SCRIPT_DIR, infer_or_erad)), 'w+') as output_file:
        for bug in bugs_list:
            output_file.write(bug)


if __name__ == '__main__':
    sys.exit(main())
