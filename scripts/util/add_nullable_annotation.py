"""
DEPRECATED
"""
import csv
import os
import re
import subprocess
import sys

def main(argv=None):
    if argv is None:
        argv = sys.argv

    java_files = _validate_input(argv)
    with open(java_files) as f:
        for l in f:
            lines = []
            java_file = l.strip()
            added_nullable = False
            has_package = False
            with open(java_file) as file:
                for line in file:
                    if 'package ' in line:
                        has_package = True
                    if 'import ' in line and not added_nullable:
                        lines.append(line)
                        lines.append('import javax.annotation.Nullable;\n')
                        added_nullable = True
                    match_obj = re.search(r'([a-zA-Z<>]+ )+[a-zA-Z]+\(([a-zA-Z ,\n]+)\)[a-zA-Z ]*( {|{)', line)
                    if match_obj:
                        parameters = match_obj.group(2).split(',')
                        parameters_strip = []
                        parameters_nullable = []
                        for p in parameters:
                            parameters_strip.append(p.strip())
                        for p in parameters_strip:
                            if p[0].isupper():
                                parameters_nullable.append('@Nullable ' + p)
                            else:
                                parameters_nullable.append(p)
                        lines.append(line.replace(match_obj.group(2), ','.join(parameters_nullable)))
                    if not match_obj:
                        lines.append(line)

            if not added_nullable:
                if has_package:
                    prev_line_package = False
                    prev_line = None
                    for line in lines:
                        if 'package ' in line:
                            prev_line = line
                            prev_line_package = True
                        elif prev_line_package:
                            index = lines.index(prev_line)
                            lines.insert(index+1, 'import javax.annotation.Nullable;\n')
                            break

            with open(java_file, 'w') as file:
                for line in lines:
                    file.write('{}'.format(line))


def _validate_input(argv):
    java_files = argv[1]
    if not os.path.isfile(java_files):
        sys.exit(1)
    return java_files


if __name__ == '__main__':
    sys.exit(main())
