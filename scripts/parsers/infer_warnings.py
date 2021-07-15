import operator
import os
import sys


def main(argv=None):
    if argv is None:
        argv = sys.argv

    warnings_file = _validate_input(argv)
    with open(warnings_file) as f:
        lines = [line.strip().split(',')[3] for line in f.readlines()]
    warning_dict = {}
    for line in lines:
        if line in warning_dict:
            warning_dict[line] += 1
        else:
            warning_dict[line] = 1
    sorted_x = sorted(warning_dict.items(),
key=operator.itemgetter(1))

    with open('warnings.txt', 'w+') as f:
        for x in sorted_x:
            f.write('{}\n'.format(x))


def _validate_input(argv):
    warnings_file = argv[1]

    if not os.path.isfile(warnings_file):
        _print_usage()
        sys.exit(1)

    return warnings_file

if __name__ == "__main__":
    sys.exit(main())
