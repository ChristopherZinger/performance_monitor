import sqlite3
from datetime import datetime


class DBManager():
    def __init__(self):
        pass

    def insert_evens_to_db(self, list_to_save):
        #create connection and cursor
        conn = sqlite3.connect('performance_monitor.db')
        c = conn.cursor()
        # create table if not exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS
            table_event(event_type TEXT, event_name TEXT, event_direction TEXT, event_x REAL, event_y REAL, event_time REAL)
        ''')
        # save and commit
        for entry in list_to_save:
            try:
                c.execute(
                    '''INSERT INTO table_event(event_type, event_name, event_direction, event_x, event_y, event_time)
                    VALUES ( ?, ?, ?, ?, ?, ?)''',
                    (entry[0], entry[1], entry[2], entry[3], entry[4], entry[5])
                )
            except Exception as e:
                print(e)
        conn.commit()
        # close connection
        c.close()
        conn.close()

    def insert_active_window_to_db(self, item, previous_item):
        print('process name: ', item[0], '  ', datetime.now() )
        #create connection and cursor
        conn = sqlite3.connect('performance_monitor.db')
        c = conn.cursor()
        # create table if not exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS
            table_window(process_name TEXT, window_title TEXT, start_time REAL, end_time REAL  )
        ''')
        conn.commit()
        # check if previous window need end_time record
        if previous_item :
            c.execute("""
                UPDATE table_window
                SET end_time=? WHERE
                start_time=?
                """,
                (previous_item[3],previous_item[2])
                )
        conn.commit()
        # self.c.close()
        # self.c = self.conn.cursor()
        # save and commit
        try:
            c.execute(
                '''INSERT INTO table_window(process_name, window_title, start_time, end_time)
                VALUES ( ?, ?, ?, ?)''',
                (item[0], item[1], item[2], item[3])
            )
        except Exception as e:
            print(e)
        # commit and close connection
        conn.commit()
        c.close()
        conn.close()



db_manager = DBManager()
