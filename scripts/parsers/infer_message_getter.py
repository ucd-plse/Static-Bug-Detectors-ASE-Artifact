import json
import os
import shutil
import subprocess
import sys
import time

from bugswarm.common import log
from bugswarm.common.shell_wrapper import ShellWrapper
from bugswarm.common.artifact_processing import utils as procutils
from bugswarm.common.artifact_processing.runners import CopyAndExecuteArtifactRunner
from bugswarm.common.artifact_processing.runners import ParallelArtifactRunner

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
    log.info('Usage: python3 infer_message_getter.py <report_filepath> <infer_report_path> <is_bugswarm>')
    log.info('report_filepath: Path to a file the reports from infer to process.')
    log.info('infer_report_filepath: Path to a file the reports from infer to process. e.g. infer-out/report.json.')
    log.info('is_bugswarm: true or false.')


def _validate_input(argv):
    sandbox_dir = argv[1]
    if not os.path.isdir(sandbox_dir):
        log.error('The sandbox_dir argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    report_path = argv[2]
    is_bugswarm = True if argv[3] == 'true' else False
    return sandbox_dir, report_path, is_bugswarm


def get_image_tag_list(directory):
    cmd = 'ls {}'.format(directory)
    _, stdout, stderr, ok = _run_command(cmd)
    if not ok:
        _print_error('Error getting list of image_tags', stdout ,stderr)

    image_tags = [x.strip() for x in stdout.split('\n')]
    if 'tmp' in  image_tags:
        image_tags.remove('tmp')
    return image_tags

def main(argv=None):
    argv = argv or sys.argv

    sandbox_dir, report_path, is_bugswarm = _validate_input(argv)
    REPORT_PATH = report_path

    image_tags = get_image_tag_list(sandbox_dir)
    bugs_list = []
    count = 0
    for image_tag in image_tags:
        ver_dirs = ['failed', 'passed'] if is_bugswarm else ['b', 'f']
        for f_or_p in ver_dirs:
            try:
                with open('{}/{}/{}/{}'.format(sandbox_dir, image_tag, f_or_p, REPORT_PATH)) as file:
                    report_json = json.loads(file.read())
                    for bug in report_json:
                        if bug['bug_type'] == 'NULL_DEREFERENCE' or 'ERAD' in bug['bug_type']:
                            count += 1
                            bugs_list.append(bug['qualifier'])
            except:
                print('No file for : {}/{}'.format(image_tag, f_or_p))
    with open('infer_output.csv', 'w') as output_file:
        for bug in bugs_list:
            output_file.write('{}\n'.format(bug))

    print(count)

if __name__ == '__main__':
    sys.exit(main())
