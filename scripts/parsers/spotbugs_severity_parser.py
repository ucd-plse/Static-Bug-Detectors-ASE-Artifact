import os
import subprocess
import sys

from bs4 import BeautifulSoup


class SpotBugsBug:
    def __init__(self, image_tag, version, filename, bug_type,patch_lower,
                 patch_upper, severity):
        self.image_tag = image_tag
        self.filename = filename
        self.patch_lower = patch_lower
        self.patch_upper = patch_upper
        self.bug_type = bug_type
        self.version = version
        self.severity = severity

    def to_CSV(self):
        return '{},{},{},{},{},{},{}'.format(self.image_tag, self.version, self.filename, self.bug_type,
                                          self.patch_lower, self.patch_upper, self.severity)


def main(argv=None):
    argv = argv or sys.argv
    reports_dir = _validate_input(argv)
    image_tags = get_image_tag_list(reports_dir)
    bug_list = []

    for image_tag in image_tags:
        for f_or_p in ['failed', 'passed']:
            spotbug_reports_list = get_spotbugs_reports(reports_dir, image_tag, f_or_p)
            if spotbug_reports_list is None:
                continue
            for report in spotbug_reports_list:
                soup = BeautifulSoup(open(report), 'lxml-xml')
                bug_instance_list = soup.BugCollection.find_all("BugInstance")
                for bug_instance in bug_instance_list:
                    for bug_class in bug_instance.find_all('Class'):
                        if bug_class.SourceLine.get('start') is not None and 'NP_' in bug_instance.get('type'):
                            bug_list.append(
                                    SpotBugsBug(image_tag, f_or_p,
                                    bug_class.SourceLine.get('sourcepath'),
                                    bug_instance.get('type'),
                                    bug_class.SourceLine.get('start'),
                                    bug_class.SourceLine.get('end'),
                                    _get_severity(int(bug_instance.get('rank')))))

    with open('spotbugs-severity-lt-output.csv', 'w') as file:
        for bug in bug_list:
            file.write('{}\n'.format(bug.to_CSV()))


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


def get_image_tag_list(directory):
    cmd = 'ls {}'.format(directory)
    _, stdout, stderr, ok = _run_command(cmd)
    if not ok:
        _print_error('Error getting list of image_tags', stdout ,stderr)

    image_tags = [x.strip() for x in stdout.split('\n')]
    return image_tags


def _get_severity(rank):
    if rank <= 4 and rank > 0:
        return 'scariest'
    elif rank <= 9 and rank > 4:
        return 'scary'
    elif rank <= 14 and rank > 9:
        return 'troubling'
    elif rank <= 20 and rank > 14:
        return 'concerning'
    else:
        return 'out-of-bounds'


def get_spotbugs_reports(reports_dir, image_tag, f_or_p):
    cmd = 'find {}/{}/{} -name "spotbugsXml.xml"'.format(reports_dir, image_tag, f_or_p)
    _, stdout, stderr, ok = _run_command(cmd)
    if not ok:
        _print_error('Error getting spotbug-reports', stdout, stderr)
        return None
    return stdout.split('\n')

def _print_usage():
    print('Usage: python3 spotbugs_severity_parser.py <reports_dir>')
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