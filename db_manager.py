import sqlite3


class DBManager():
    def __init__(self):
        pass

    def insert_evens_to_db(self, list_to_save):
        #create connection and cursor
        self.conn = sqlite3.connect('performance_monitor.db')
        self.c = self.conn.cursor()
        # create table if not exist
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS
            table_event(event_type TEXT, event_name TEXT, event_direction TEXT, event_x REAL, event_y REAL, event_time REAL)
        ''')
        # save and commit
        for entry in list_to_save:
            try:
                self.c.execute(
                    '''INSERT INTO table_event(event_type, event_name, event_direction, event_x, event_y, event_time)
                    VALUES ( ?, ?, ?, ?, ?, ?)''',
                    (entry[0], entry[1], entry[2], entry[3], entry[4], entry[5])
                )
            except Exception as e:
                print(e)
        self.conn.commit()
        # close connection
        self.c.close()
        self.conn.close()

    def insert_active_window_to_db(self, item, previous_item):
        #create connection and cursor
        self.conn = sqlite3.connect('performance_monitor.db')
        self.c = self.conn.cursor()
        # create table if not exist
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS
            table_window(process_name TEXT, window_title TEXT, start_time REAL, end_time REAL  )
        ''')
        # check if previous window need end_time record
        if previous_item :
            self.c.execute("""
                UPDATE table_window
                SET end_time=? WHERE
                start_time=?
                """,
                (previous_item[3],previous_item[2])
                )
        # save and commit
        try:
            self.c.execute(
                '''INSERT INTO table_window(process_name, window_title, start_time, end_time)
                VALUES ( ?, ?, ?, ?)''',
                (item[0], item[1], item[2], item[3])
            )
        except Exception as e:
            print(e)
        # commit and close connection
        self.conn.commit()
        self.c.close()
        self.conn.close()

    def read_from_db(self):
        #create connection and cursor
        self.conn = sqlite3.connect('performance_monitor.db')
        self.c = self.conn.cursor()
        # find data in database
        self.c.execute("SELECT * FROM table_event WHERE event_type LIKE '%2019-09-13%'")
        # populate list with time
        times = []
        for row in self.c.fetchall():
            times.append(row[1])
        first = times[0][14:16]
        last = times[len(times)-1][14:16]
        print('first is : {}, Last is : {}'.format(first, last))

        x = times[0][14:16]
        main_list = []
        temp_list = []
        for i in times:
            if i[14:16] == x :
                temp_list.append(i)
            else:
                main_list.append(temp_list)
                temp_list = []
                temp_list.append(i)
                x = i[14:16]
        for i in main_list:
            print('{} in minute {}'.format(len(i), i[0:16]))
        # close db
        self.c.close()
        self.conn.close()

db_manager = DBManager()
