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


class InferBug:
    def __init__(self, image_tag, version, filename, bug_type, patch_lower, patch_upper, severity):
        self.image_tag = image_tag
        self.filename = filename
        self.patch_lower = patch_lower
        self.patch_upper = patch_upper
        self.bug_type = bug_type
        self.version = version
        self.severity = severity

    def __eq__(self, other):
        if not isinstance(other, InferBug):
            return NotImplemented
        return self.image_tag == other.image_tag and self.filename == other.filename and self.patch_lower == other.patch_lower and self.patch_upper == other.patch_upper and self.bug_type == other.bug_type and self.severity == other.severity


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
    log.info('Usage: python3 infer_parser.py <report_filepath>')
    log.info('report_filepath: Path to a file the reports from infer to process.')


def _validate_input(argv):
    sandbox_dir = argv[1]
    if not os.path.isdir(sandbox_dir):
        log.error('The sandbox_dir argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    return sandbox_dir


def get_image_tag_list(directory):
    cmd = 'ls {}'.format(directory)
    _, stdout, stderr, ok = _run_command(cmd)
    if not ok:
        _print_error('Error getting list of image_tags', stdout ,stderr)

    image_tags = [x.strip() for x in stdout.split('\n')]
    if 'tmp' in image_tags:
        image_tags.remove('tmp')
    return image_tags


def main(argv=None):
    argv = argv or sys.argv

    sandbox_dir = _validate_input(argv)
    REPORT_PATH = 'infer-out/report.json'

    image_tags = get_image_tag_list(sandbox_dir)
    bugs_list = []
    for image_tag in image_tags:
        for f_or_p in ['failed', 'passed']:
            try:
                with open(os.path.join(sandbox_dir, image_tag, f_or_p, REPORT_PATH)) as file:
                    report_json = json.loads(file.read())
                    for bug in report_json:
                        if f_or_p == 'failed':
                            bugs_list.append('{},{},{},{},{},{},{}'.format(image_tag.strip(), f_or_p.strip(), bug['file'].strip(), bug['bug_type'].strip(), bug['line'], bug['line'], bug['severity']))
                        else:
                            bugs_list.append('{},{},{},{},{},{},{}'.format(image_tag.strip(), f_or_p.strip(), bug['file'].strip(), bug['bug_type'].strip(), bug['line'], bug['line'], bug['severity']))
            except:
                print('error')
                continue
    with open('infer_output.csv', 'w') as output_file:
        for bug in bugs_list:
            output_file.write('{}\n'.format(bug))



if __name__ == '__main__':
    sys.exit(main())