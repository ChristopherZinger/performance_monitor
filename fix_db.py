import sqlite3
import numpy as np
import pandas as pd
from db_manager import db_manager
import datetime
import sqlalchemy
from sqlalchemy import create_engine
import math

'''
This is most likely one time script, to rewrite old db to new format.
table names will be changed
table colums names will be changed and rearanged and added
Test if new db has correct data
'''

# get all db to pd.dataFrame
start = datetime.datetime.now()
conn = sqlite3.connect('old_performance_monitor.db')
df = pd.read_sql( "SELECT * FROM table_event" ,conn)
start2 = datetime.datetime.now()
df = df.rename({'event_type': 'event_direction', 'key_name': 'event_name'}, axis='columns')


# create and rearrange columns
df['event_x'] = None
df['event_y'] = None
df['event_type'] = 'KEY'
df = df[['event_type', 'event_name', 'event_direction','event_x', 'event_y', 'event_time']]


# rewrite db by segments to avoid memory errors
factor = 100000

engine = create_engine('sqlite:///new_performance_monitor.db')
for i in range(math.ceil(df.shape[0]/factor)):
    df_temp = df[i*factor:(i+1)*factor]
    df_temp.to_sql(
        name='table_event',
        con=engine,
        if_exists='append',
        index=False,
    )
    print(i* factor, ': saved')

conn.close()

conn_new = sqlite3.connect('new_performance_monitor.db')
conn_old = sqlite3.connect('old_performance_monitor.db')
c_new = conn_new.cursor()
c_old = conn_old.cursor()



# check if ther is no mistakes in rewriting the db
c_new.execute("""
    SELECT  * FROM table_event WHERE rowid=?
    """,(1,))
c_old.execute("""
    SELECT  * FROM table_event WHERE rowid=?
    """,(1,))

new_row = c_new.fetchone()
old_row = c_old.fetchone()

if (
        (
            old_row[0] != new_row[5]
        ) or
        (
            old_row[1] != new_row[2]
        )or
        (
            old_row[2] != new_row[1]
        )

    ):
    print( "new  :   old")
    print(new_row[5], ' : ', old_row[0])
    print(new_row[2], ' : ', old_row[1])
    print(new_row[1], ' : ', old_row[2])

print('rest good')
