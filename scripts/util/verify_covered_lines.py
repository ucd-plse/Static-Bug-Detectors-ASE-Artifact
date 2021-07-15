"""
"""
import sys


class CloverCoveredLine:
    def __init__(self, image_tag, filename, line_number):
        self.image_tag = image_tag
        self.filename = filename
        self.line_number = line_number

    def __members(self):
        return (self.image_tag, self.filename, self.line_number)

    def __hash__(self):
        return hash(self.__members())

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__members() == other.__members()
        else:
            return False


def main(argv=None):
    argv = argv or sys.argv

    covered_lines_csv, faulty_lines_csv = _validate_input(argv)
    covered_lines_dict = {}
    not_covered = []
    with open(covered_lines_csv) as file:
        for csv_line in file:
            csv_line = csv_line.strip()
            # if len(csv_line.split()) != 4:
            #     print(csv_line.split())
            image_tag, _, filename, line_number = csv_line.split(',')
            covered_lines_dict[CloverCoveredLine(image_tag, filename, line_number)] = 1

    with open(faulty_lines_csv) as file:
        for csv_line in file:
            csv_line = csv_line.strip()
            image_tag, filename, line_number = csv_line.split(',')
            if CloverCoveredLine(image_tag, filename, line_number) not in covered_lines_dict:
                not_covered.append(image_tag)

    for image_tag in not_covered:
        print('{}'.format(image_tag))


def _print_usage():
    print('Usage: python3 verify_covered_lines.py <covered_lines_csv> <faulty_lines_csv>')
    print('covered_lines_csv: The filepath to the comma separated file')
    print('faulty_lines_csv: The filepath to the comma separated file')


def _validate_input(argv):
    if len(argv) != 3:
        _print_usage()
        sys.exit(1)
    covered_lines_csv = argv[1]
    faulty_lines_csv = argv[2]

    return covered_lines_csv, faulty_lines_csv


if __name__ == '__main__':
    sys.exit(main())
