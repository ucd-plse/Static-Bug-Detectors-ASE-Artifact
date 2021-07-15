import os
import subprocess
import sys

from bs4 import BeautifulSoup


class SpotBugsBug:
    def __init__(self, image_tag, filename, patch_lower,
                 patch_upper, bug_type, version):
        self.image_tag = image_tag
        self.filename = filename
        self.patch_lower = patch_lower
        self.patch_upper = patch_upper
        self.bug_type = bug_type
        self.version = version

    def to_CSV(self):
        return '{},{},{},{},{},{}'.format(self.image_tag, self.filename,
                                          self.patch_lower, self.patch_upper,
                                          self.bug_type, self.version)


def main(argv=None):
    argv = argv or sys.argv
    reports_dir = _validate_input(argv)
    bug_list = []
    image_tags = get_image_tag_list(reports_dir)
    for image_tag in image_tags:
        for f_or_p in ['failed', 'passed']:
            spotbug_reports_list = get_spotbugs_reports(reports_dir, image_tag, f_or_p)
            if spotbug_reports_list is None:
                continue
            for report in spotbug_reports_list:
                soup = BeautifulSoup(open(report), 'lxml-xml')
                bug_instance_list = soup.BugCollection.find_all("ShortMessage")
                for bug_instance in bug_instance_list:
                    # print(bug_instance.text.strip())
                    bug_list.append(bug_instance.text.strip())

    with open('output.csv', 'w') as file:
        for bug in bug_list:
            file.write('{}\n'.format(bug))


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


def get_spotbugs_reports(reports_dir, image_tag, f_or_p):
    cmd = 'find {}/{}/{} -name "spotbugsXml.xml"'.format(reports_dir, image_tag, f_or_p)
    _, stdout, stderr, ok = _run_command(cmd)
    if not ok:
        _print_error('Error getting spotbug-reports', stdout, stderr)
        return None
    return stdout.split('\n')

def get_image_tag_list(directory):
    cmd = 'ls {}'.format(directory)
    _, stdout, stderr, ok = _run_command(cmd)
    if not ok:
        _print_error('Error getting list of image_tags', stdout ,stderr)

    image_tags = [x.strip() for x in stdout.split('\n')]
    return image_tags

def _print_usage():
    print('Usage: python3 spotbugs_parser.py <reports_dir>')
    print('reports_dir: Path to the directory of reports')


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
