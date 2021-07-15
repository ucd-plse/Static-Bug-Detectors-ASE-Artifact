import sys
import pymysql.cursors

from mapping_methods import generate_code_diff_query
from mapping_methods import generate_report_diff_query
from mapping_methods import generate_stack_trace_query
from mapping_methods import generate_covered_lines_query

class DatabaseConnection:
    def __init__(self, user, password, db=None, host='localhost', port=3306):
        print('Going to connect to database {} in server {}, for user {}'.format(db, host, user))
        try:
            self.connection = pymysql.connect(host,
                                             user=user,
                                             password=password,
                                             db=db,
                                             charset='utf8mb4',
                                             cursorclass=pymysql.cursors.DictCursor)
        except BaseException as e:
            print('Error: {}'.format(e))

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

    def insert(self, sql_command):
        cur = self.connection.cursor()
        try:
            cur.execute(sql_command)
        except BaseException:
            print("Copy already exists.")
            print(sql_command)
            self.connection.rollback()
            return
    
    def code_diff(self, diff_table, tool_table):
        cur = self.connection.cursor()
        try:
            sql_command = generate_code_diff_query(diff_table, tool_table)
            cur.execute(sql_command)
            return cur.fetchall()
        except BaseException:
            self.connection.rollback()
            return

    def report_diff(self, tool_table):
        cur = self.connection.cursor()
        try:
            sql_command = generate_report_diff_query(tool_table)
            cur.execute(sql_command)
            return cur.fetchall()
        except BaseException:
            self.connection.rollback()
            return

    def stack_trace(self, diff_table, tool_table):
        cur = self.connection.cursor()
        try:
            sql_command = generate_stack_trace_query(diff_table, tool_table)
            cur.execute(sql_command)
            return cur.fetchall()
        except BaseException:
            self.connection.rollback()
            return

    def covered_lines(self, diff_table, tool_table):
        cur = self.connection.cursor()
        try:
            sql_command = generate_covered_lines_query(diff_table, tool_table)
            cur.execute(sql_command)
            return cur.fetchall()
        except BaseException:
            self.connection.rollback()
            return

    def create(self, sql_command):
        '''
        Create an new SQL table if it does not already exist.
        '''
        cur = self.connection.cursor()
        try:
            cur.execute(sql_command)
        except:
            print("Table Creation Error")
            print(sql_command)
            raise

    def execute(self, sql_command):
        cur = self.connection.cursor()
        try:
            cur.execute(sql_command)
            rows = cur.fetchall()
            return rows
        except:
            print(sql_command)
            raise

    def create_db(self, db_name):
        '''
        Create an new SQL table if it does not already exist.
        '''
        cur = self.connection.cursor()
        try:
            mysql = "create database {}".format(db_name)
            cur.execute(mysql)
        except BaseException as e:
            print("Could not create db {}".format(db_name))
            print(e)
            raise

    def select_database(self, db_name):
        if self._database_exists(db_name) is False:
            print("Database {} does not exist".format(db_name))
            return None
        try:
            self.connection.select_db(db_name)
        except BaseException as e:
            print("Could not select db {}".format(db_name))
            print(e)
            raise

    def create_travis_table(self, table_name):
        cur = self.connection.cursor()

        sql_command = "CREATE TABLE `{}` (" \
                      "`trace_id` INT NOT NULL AUTO_INCREMENT," \
                      "`image_tag` VARCHAR(200) NOT NULL," \
                      "`file` VARCHAR(200) NOT NULL," \
                      "`line` VARCHAR(200) NOT NULL," \
                      "PRIMARY KEY (`trace_id`));".format(table_name)
        try:
            cur.execute(sql_command)
            print('Created {} table successfully.'.format(table_name))
        except:
            print("Table Creation Error")
            print(sql_command)
            raise

    def create_clover_table(self, db_name):
        cur = self.connection.cursor()

        sql_command = "CREATE TABLE `{}` (" \
                      "`id` INT NOT NULL AUTO_INCREMENT," \
                      "`image_tag` VARCHAR(200) NOT NULL," \
                      "`filepath` VARCHAR(400) NOT NULL," \
                      "`file` VARCHAR(200) NOT NULL," \
                      "`line` VARCHAR(200) NOT NULL," \
                      "PRIMARY KEY (`id`));".format(db_name)
        try:
            cur.execute(sql_command)
            print('Created {} table successfully.'.format(db_name))
        except:
            print("Table Creation Error")
            print(sql_command)
            raise

    def create_tool_message_table(self, tool_name):
        cur = self.connection.cursor()

        sql_command = "CREATE TABLE `{}` (" \
                      "`bug_id` INT NOT NULL AUTO_INCREMENT," \
                      "`image_tag` VARCHAR(200) NOT NULL," \
                      "`version` VARCHAR(45) NOT NULL," \
                      "`file` VARCHAR(200) NOT NULL," \
                      "`bug_type` VARCHAR(200) NOT NULL," \
                      "`bug_lower` INT NOT NULL," \
                      "`bug_upper` INT NOT NULL," \
                      "`message` VARCHAR(1000) NOT NULL," \
                      "PRIMARY KEY (`bug_id`));".format(tool_name)
        try:
            cur.execute(sql_command)
            print('Created {} table successfully.'.format(tool_name))
        except:
            print("Table Creation Error")
            print(sql_command)
            raise

    def create_tool_severity_table(self, tool_name):
        cur = self.connection.cursor()

        sql_command = "CREATE TABLE `{}` (" \
                      "`bug_id` INT NOT NULL AUTO_INCREMENT," \
                      "`image_tag` VARCHAR(200) NOT NULL," \
                      "`version` VARCHAR(45) NOT NULL," \
                      "`file` VARCHAR(200) NOT NULL," \
                      "`bug_type` VARCHAR(200) NOT NULL," \
                      "`bug_lower` INT NOT NULL," \
                      "`bug_upper` INT NOT NULL," \
                      "`severity` VARCHAR(100) NOT NULL," \
                      "PRIMARY KEY (`bug_id`));".format(tool_name)
        try:
            cur.execute(sql_command)
            print('Created {} table successfully.'.format(tool_name))
        except:
            print("Table Creation Error")
            print(sql_command)
            raise

    def create_tool_table(self, tool_name):
        cur = self.connection.cursor()

        sql_command = "CREATE TABLE `{}` (" \
                      "`bug_id` INT NOT NULL AUTO_INCREMENT," \
                      "`image_tag` VARCHAR(200) NOT NULL," \
                      "`version` VARCHAR(45) NOT NULL," \
                      "`file` VARCHAR(500) NOT NULL," \
                      "`bug_type` VARCHAR(10000) NOT NULL," \
                      "`bug_lower` INT NOT NULL," \
                      "`bug_upper` INT NOT NULL," \
                      "PRIMARY KEY (`bug_id`));".format(tool_name)
        try:
            cur.execute(sql_command)
            print('Created {} table successfully.'.format(tool_name))
        except:
            print("Table Creation Error")
            print(sql_command)
            raise

    def create_github_table(self, db_name):
        cur = self.connection.cursor()
        sql_command = "CREATE TABLE `{}` (" \
                      "`id` int(11) NOT NULL AUTO_INCREMENT," \
                      "`image_tag` varchar(200) NOT NULL," \
                      "`file` varchar(200) NOT NULL," \
                      "`patch_lower` int(11) NOT NULL," \
                      "`patch_upper` int(11) NOT NULL," \
                      "PRIMARY KEY (`id`)" \
                      ")".format(db_name)
        try:
            cur.execute(sql_command)
            print('Created {} table successfully.'.format('diff'))
        except:
            print("Table Creation Error")
            print(sql_command)
            raise

    def _table_exists(self, tablename):
        cur = self.connection.cursor()

        sql_command = "SELECT * FROM `INFORMATION_SCHEMA`.`TABLES` WHERE `TABLE_NAME` LIKE %s"
        cur.execute(sql_command, (tablename))
        if cur.fetchone() is not None:
            return True
        print('{} does not exist'.format(tablename))
        return False

    def _database_exists(self, databasename):
        cur = self.connection.cursor()
        sql_command = "SHOW DATABASES LIKE %s"
        try:
            cur.execute(sql_command, (databasename))
        except:
            raise

        if cur.fetchone() is not None:
            return True
        return False

    def init_database(self, list_of_tools):
        if not isinstance(list_of_tools, (list)):
            return None
        if self._database_exists('github'):
            return None
        try:
            self.create_db('github')
            self.select_database('github')
            self.create_github_table()
            for tool in list_of_tools:
                self.create_tool_table(tool)
        except BaseException as e:
            raise

    def insert_tool_messages_table(self, tool_name, values_tuples):
        if not self._table_exists(tool_name):
            print('{} table doesnt exist'.format(tool_name))
            return None
        for values_tuple in values_tuples:
          if len(values_tuple) != 6:
              print('{} table requires {} values but was given {}'
                    .format(tool_name, 6, len(values_tuple)))
              return None
          sql_command = "INSERT INTO `{}_messages`" \
                "(`image_tag`, `version`, `file`, `bug_type`, `bug_lower`, `bug_upper`, message) VALUES" \
                "('{}', '{}', '{}', '{}', {}, {}, {})".format(tool_name, values_tuple[0],
                                               values_tuple[1], values_tuple[2],
                                               values_tuple[3], values_tuple[4],
                                               values_tuple[5], values_tuple[6])
          cur = self.connection.cursor()
          cur.execute(sql_command)
        try:
            cur.connection.commit()
            print('insert Successfully')
        except BaseException as e:
            print('error inserting')
            print(e)
            raise

    def insert_tool_severity_table(self, tool_name, values_tuples):
        if not self._table_exists(tool_name):
            print('{} table doesnt exist'.format(tool_name))
            return None
        for values_tuple in values_tuples:
          if len(values_tuple) != 7:
              print('{} table requires {} values but was given {}'
                    .format(tool_name, 7, len(values_tuple)))
              return None
          sql_command = "INSERT INTO `{}`" \
                "(`image_tag`, `version`, `file`, `bug_type`, `bug_lower`, `bug_upper`, `severity`) VALUES" \
                "('{}', '{}', '{}', '{}', {}, {}, '{}')".format(tool_name, values_tuple[0],
                                               values_tuple[1], values_tuple[2],
                                               values_tuple[3], values_tuple[4],
                                               values_tuple[5], values_tuple[6])
          cur = self.connection.cursor()
          cur.execute(sql_command)
        try:
            cur.connection.commit()
            print('insert Successfully')
        except BaseException as e:
            print('error inserting')
            print(e)
            raise

    def insert_travis_table(self, table_name, values_tuples):
        if not self._table_exists('github'):
            print('travis table doesnt exist')
            return None
        for values_tuple in values_tuples:
          if len(values_tuple) != 3:
              print('travis table requires {} values but was given {}'
                    .format(3, len(values_tuple)))
              return None
          sql_command = "INSERT INTO `{}`" \
                "(`image_tag`, `file`, `line`) VALUES" \
                "('{}', '{}', {} )".format(table_name, values_tuple[0], values_tuple[1],
                                              values_tuple[2])
          cur = self.connection.cursor()
          cur.execute(sql_command)
        try:
            cur.connection.commit()
            print('insert Successfully')
        except BaseException as e:
            print('error inserting')
            print(e)
            raise

    def insert_covered_lines_table(self, db_name,values_tuples):
        if not self._table_exists(db_name):
            print('clover table doesnt exist')
            return None
        for values_tuple in values_tuples:
          # print(values_tuple)
          if len(values_tuple) != 4:
              print('clover table requires {} values but was given {}'
                    .format(4, len(values_tuple)))
              return None
          sql_command = "INSERT INTO `{}`" \
                "(`image_tag`, `filepath`, `file`, `line`) VALUES" \
                "('{}', '{}', '{}', {} )".format(db_name, values_tuple[0], values_tuple[1],
                                           values_tuple[2], values_tuple[3])
          cur = self.connection.cursor()
          cur.execute(sql_command)
        try:
            cur.connection.commit()
            print('insert Successfully')
        except BaseException as e:
            print('error inserting')
            print(e)
            raise

    def insert_results_table(self, values_tuples):
        if not self._table_exists('results'):
            print('results table doesnt exist')
            return None
        for values_tuple in values_tuples:
          if len(values_tuple) != 4:
              print('results table requires {} values but was given {}'
                    .format(4, len(values_tuple)))
              return None
          sql_command = "INSERT INTO `results`" \
                "(`image_tag`, `found`, `bug_id`, `tool`) VALUES" \
                "('{}', {}, {}, '{}')".format(values_tuple[0], values_tuple[1],
                                              values_tuple[2], values_tuple[3])
          cur = self.connection.cursor()
          cur.execute(sql_command)
        try:
            cur.connection.commit()
            print('insert Successfully')
        except BaseException as e:
            print('error inserting')
            print(e)
            raise

    def insert_github_table(self, table_name, values_tuples):
        if not self._table_exists(table_name):
            print('github table doesnt exist')
            return None
        for values_tuple in values_tuples:
          if len(values_tuple) != 4:
              print('github table requires {} values but was given {}'
                    .format(4, len(values_tuple)))
              return None
          sql_command = "INSERT INTO `{}`" \
                "(`image_tag`, `file`, `patch_lower`, `patch_upper`) VALUES" \
                "('{}', '{}', {}, {})".format(table_name,values_tuple[0], values_tuple[1],
                                              values_tuple[2], values_tuple[3])
          cur = self.connection.cursor()
          cur.execute(sql_command)
        try:
            cur.connection.commit()
            print('insert Successfully')
        except BaseException as e:
            print('error inserting')
            print(e)
            raise

    def insert_tool_table(self, tool_name, values_tuples):
        if not self._table_exists(tool_name):
            print('{} table doesnt exist'.format(tool_name))
            return None
        for values_tuple in values_tuples:
          if len(values_tuple) != 6:
              print('{} table requires {} values but was given {}'
                    .format(tool_name, 6, len(values_tuple)))
              return None
          sql_command = "INSERT INTO `{}`" \
                "(`image_tag`, `version`, `file`, `bug_type`, `bug_lower`, `bug_upper`) VALUES" \
                "('{}', '{}', '{}', '{}', {}, {})".format(tool_name, values_tuple[0],
                                               values_tuple[1], values_tuple[2],
                                               values_tuple[3], values_tuple[4],
                                               values_tuple[5])
          cur = self.connection.cursor()
          cur.execute(sql_command)
        try:
            cur.connection.commit()
            print('insert Successfully')
        except BaseException as e:
            print('error inserting')
            print(e)
            raise

    def test(self):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM github"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)


def main():
    db = DatabaseConnection('root', 'password')
    # db.init_database(['spotbugs'])
    db.select_database('github')
    db.create_github_table()
    # db.create_tool_table('nullaway_new_bs')
    # db.execute('DROP TABLE spotbugslt_severity')
    # db.create_clover_table('clover_fse')
    # db.create_clover_table()
    # db.create_clover_table('clover_checkfornull')
    # db.create_tool_table('sb_ht_112')
    #db.create_tool_severity_table('sblt_old_bs_nullable')
    #db.create_travis_table()
    # db.create_results_table()
    # db.insert_tool_table('spotbugs',('yamcs-yamcs-186324159','failed','org/yamcs/simulation/SimulationPpProvider.java','DM_DEFAULT_ENCODING',37,412))
    # db.insert_github_table(('yamcs-yamcs-186324159','yamcs-core/src/main/java/org/yamcs/xtce/SpreadsheetLoader.java',1214,1221))
    # db.insert_results_table(('yamcs-yamcs-186324159', 0, 3, 'spotbugs'))

if __name__ == '__main__':
    sys.exit(main())
