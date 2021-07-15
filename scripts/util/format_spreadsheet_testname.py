"""
"""
import re
import sys


def main(argv=None):
    argv = argv or sys.argv

    tsv_file = _validate_input(argv)
    testname_lines = []

    with open(tsv_file) as f:
        tsv_lines = [x.strip().split('\t') for x in f.readlines()]
        for line in tsv_lines:
            testname_lines.append((line[0], line[1].split(',')[0]))

    with open('testnames.csv', 'w+') as out_f:
        for l in testname_lines:
            out_f.write('{},{}\n'.format(l[0],l[1]))


def _print_usage():
    print('Usage: python3 format_spreadsheet_faulty_line.py <tsv_file>')
    print('tsv_file: The filepath to the tsv separated file containing stuff from the spreadsheet.')


def _validate_input(argv):
    if len(argv) != 2:
        _print_usage()
        sys.exit(1)
    tsv_file = argv[1]

    return tsv_file


if __name__ == '__main__':
    sys.exit(main())
