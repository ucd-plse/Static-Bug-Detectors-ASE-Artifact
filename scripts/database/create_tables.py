import re
import sys

import pymysql.cursors

from db_utils import DatabaseConnection


def main():
    db = DatabaseConnection('root', 'password')

    # Create and select DB
    db.create_db('analyzer_study')
    db.select_database('analyzer_study')

    # Create auxillary data tables
    db.create_clover_table('covered_lines')
    db.create_github_table('diff')
    db.create_travis_table('trace')

    # Create tool tables
    db.create_tool_table('sblt')
    db.create_tool_table('sbht')
    db.create_tool_table('infer')
    db.create_tool_table('eradicate')
    db.create_tool_table('nullaway')
    db.create_tool_table('cfnullness')

if __name__ == '__main__':
    sys.exit(main())
