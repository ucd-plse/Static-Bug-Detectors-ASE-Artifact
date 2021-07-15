import os
import subprocess
import sys

from bs4 import BeautifulSoup


class CloverCoveredLine:
    def __init__(self, image_tag, filepath, filename, line_number):
        self.image_tag = image_tag
        self.filepath = filepath
        self.filename = filename
        self.line_number = line_number

    def __members(self):
        return (self.image_tag, self.filepath, self.filename, self.line_number)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__members() == other.__members()
        else:
            return False

    def to_CSV(self):
        return '{},{},{},{}'.format(self.image_tag, self.filepath, self.filename, self.line_number)


def main(argv=None):
    argv = argv or sys.argv
    reports_dir, is_bugswarm, image_tag = _validate_input(argv)

    image_tags = get_image_tag_list(reports_dir) if image_tag is None else [image_tag]
    covered_lines = []

    for image_tag in image_tags:
        img_tag_covered_lines = {}
        # Parse the POM.
        clover_reports = get_clover_reports(reports_dir, image_tag, is_bugswarm)
        if clover_reports is None:
            continue

        for report in clover_reports:
            if report == '' or report is None:
                continue
            soup = BeautifulSoup(open(report), 'lxml-xml')
            # Get all packages for the source and test code
            project_packages = soup.project.find_all('package')
            testproject_packages = soup.testproject.find_all('package')

            # Iterate throguh all project packages collecting lines with greater than 0 counts
            for package in project_packages:
                for file in package.find_all('file'):
                    for line in file.find_all('line'):
                        line_count = line.get('count')
                        line_count = int(line.get('count')) if line_count is not None else 0
                        # if line_count is None:
                        #     continue
                        # else:
                        #     line_count = int(line_count)
                        if line_count > 0:
                            clover_line = CloverCoveredLine(image_tag, file.get('path'), file.get('name'), line.get('num'))
                            # if clover_line.to_CSV() not in img_tag_covered_lines:
                            img_tag_covered_lines[clover_line.to_CSV()] = 1

            for test_package in testproject_packages:
                for file in test_package.find_all('file'):
                    for line in file.find_all('line'):
                        line_count = line.get('count')
                        if line_count is None:
                            continue
                        else:
                            line_count = int(line_count)
                        if line_count > 0:
                            clover_line = CloverCoveredLine(image_tag, file.get('path'), file.get('name'), line.get('num'))
                            # if clover_line.to_CSV() not in img_tag_covered_lines:
                            img_tag_covered_lines[clover_line.to_CSV()] = 1

        covered_lines.extend(list(img_tag_covered_lines.keys()))

    with open('clover-covered-lines.csv', 'w+') as file:
        for covered_line in covered_lines:
            file.write('{}\n'.format(covered_line))


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


def get_clover_reports(reports_dir, image_tag, is_bugswarm):
    bs_cmd = 'find {}/{}/failed/targetsite -name "clover.xml"'.format(reports_dir, image_tag)
    d4j_cmd = 'find {}/{}/b -name "coverage.xml"'.format(reports_dir, image_tag)
    cmd = bs_cmd if is_bugswarm else d4j_cmd
    print(cmd)
    _, stdout, stderr, ok = _run_command(cmd)
    if not ok:
        _print_error('Error getting clover-reports', stdout, stderr)
        return None
    return stdout.split('\n')


def get_image_tag_list(directory):
    cmd = 'ls {}'.format(directory)
    _, stdout, stderr, ok = _run_command(cmd)
    if not ok:
        _print_error('Error getting list of image_tags', stdout ,stderr)

    image_tags = [x.strip() for x in stdout.split('\n')]
    if 'from_host' in image_tags:
        image_tags.remove('from_host')
    return image_tags


def _print_usage():
    print('Usage: python3 clover_parser.py <reports_dir> [image_tag]')
    print('reports_dir: Path to the directory of reports')


def _validate_input(argv):
    if len(argv) != 3 and len(argv) != 4:
        _print_usage()
        sys.exit(1)
    reports_dir = argv[1]
    is_bugswarm = True if arg[2] == 'true' else False
    image_tag = argv[3] if len(argv) == 4 else None

    if not os.path.isdir(reports_dir) and os.path.exists(reports_dir):
        print('The reports_dir argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)

    return reports_dir, is_bugswarm, image_tag


if __name__ == '__main__':
    sys.exit(main())
