import re
import sys

import pymysql.cursors

from bugswarm.common import github_wrapper

from db_utils import DatabaseConnection


def main(argv=None):
    argv = argv or sys.argv

    image_tag_file, table_name = _validate_input(argv)

    db = DatabaseConnection('root', 'password')
    db.select_database('analyzer_study')
    value_tuples = []
    with open(image_tag_file) as file:
        value_tuples = [line.strip().split(',') for line in file.readlines()]

    if table_name == 'diff':
        db.insert_github_table(table_name,value_tuples)
    elif table_name == 'trace':
        db.insert_travis_table(table_name, value_tuples)
    elif 'covered_lines' in table_name:
        db.insert_covered_lines_table(table_name, value_tuples)
    elif 'severity' in table_name:
        db.insert_tool_severity_table(table_name, value_tuples)
    else:
        db.insert_tool_table(table_name, value_tuples)


def _print_usage():
    print('Usage: python approx_lines_changed.py <image_tag_filepath> <table_name>')
    print('image_tag_filepath:' \
          'The filepath to the new-line separated file containing image-tags')
    print('table_name: Either github, spotbugs, errorprone, infer, etc')


def _validate_input(argv):
    if len(argv) != 3:
        _print_usage()
        sys.exit(1)
    image_tag_file = argv[1]
    table_name = argv[2]
    print(image_tag_file)
    print(table_name)
    return image_tag_file, table_name


if __name__ == '__main__':
    sys.exit(main())
