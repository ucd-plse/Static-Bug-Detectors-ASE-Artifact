import os
import re
import subprocess
import sys

from bs4 import BeautifulSoup

from os.path import abspath

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class NullAwayBug:
    def __init__(self, image_tag, filename, patch_lower,
                 patch_upper, bug_type, version):
        self.image_tag = image_tag
        self.filename = filename
        self.patch_lower = patch_lower
        self.patch_upper = patch_upper
        self.bug_type = bug_type
        self.version = version

    def to_CSV(self):
        return '{},{},{},{},{},{}'.format(self.image_tag, self.version, self.filename, self.bug_type, self.patch_lower, self.patch_upper)


def main(argv=None):
    argv = argv or sys.argv
    reports_dir = _validate_input(argv)
    bug_list = []
    image_tags = get_image_tag_list(reports_dir)
    for line in image_tags:
        line = line.strip()
        # Parse the POM.
        for f_or_p in get_f_or_p(reports_dir, line):
            nullaway_reports_list = get_nullaway_reports(reports_dir, line, f_or_p)
            if nullaway_reports_list is None:
                continue
            for report in nullaway_reports_list:
                if report == '':
                    continue
                with open(report) as file_report:
                    for l in file_report:
                        l = l.strip()
                        m = re.match(r'.* (/[\w/-]+\.java):([0-9]+): \w+: \[NullAway\] (.+)', l)
                        if m:
                            filename = m.group(1)
                            patch = m.group(2)
                            bug_type = m.group(3).replace('.','').replace(',','').replace("'","")
                            version = 'failed' if f_or_p == 'b' or f_or_p == 'failed' else 'passed'
                            bug_list.append(
                                NullAwayBug(line, filename, patch, patch,
                                            bug_type, version))

    with open(abspath('{}/results/nullaway.warnings'.format(SCRIPT_DIR)), 'w+') as file:
        for bug in bug_list:
            file.write('{}\n'.format(bug.to_CSV()))


def get_f_or_p(reports_dir, image_tag):
    cmd = 'ls {}'.format(os.path.join(reports_dir, image_tag))
    _, stdout, stderr, ok = _run_command(cmd)
    return stdout.split('\n')


def get_image_tag_list(directory):
    cmd = 'ls {}'.format(directory)
    _, stdout, stderr, ok = _run_command(cmd)
    if not ok:
        _print_error('Error getting list of image_tags', stdout ,stderr)

    image_tags = [x.strip() for x in stdout.split('\n')]
    return image_tags


def _run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, shell=True)
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


def get_nullaway_reports(reports_dir, image_tag, f_or_p):
    cmd = 'find {}/{}/{} -name "*.txt"'.format(
        reports_dir, image_tag, f_or_p)
    _, stdout, stderr, ok = _run_command(cmd)
    if not ok:
        _print_error('Error getting NullAway Report', stdout, stderr)
        return None
    return stdout.split('\n')

def _print_usage():
    print('Usage: python3 nullaway_parser.py <reports_dir> <is_bugswarm>')
    print('reports_dir: Path to the directory of reports.')
    print('is_bugswarm: true or false.')


def _validate_input(argv):
    if len(argv) != 2:
        _print_usage()
        sys.exit(1)
    reports_dir = argv[1]
    if not os.path.isdir(reports_dir) and os.path.exists(reports_dir):
        print('The reports_dir argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    return reports_dir


if __name__ == '__main__':
    sys.exit(main())
