import sqlite3
import numpy as np
import pandas as pd
import time
import datetime
import re
import matplotlib.pyplot as plt


def get_week():
    print('Enter number of the week: ')
    while True:
        week_nr = input()
        print('Enter Year: ')
        year = input()
        try:
            week_nr=int(week_nr)
            year=int(year)
            break
        except:
            print('Week and year number have to be integer. Try again (week): ')
    return year, week_nr

def convert_timestamp_table_to_date_and_time(df, timestamp_table, new_date_table, new_time_table):
    def tryconvert(timestamp, timeordate):
        try:
            if timeordate=='date':
                return datetime.datetime.fromtimestamp(timestamp).date()
            return datetime.datetime.fromtimestamp(timestamp).time()
        except Exception as e:
            return None

    df[new_date_table] = df[timestamp_table].apply(
        lambda timestamp: tryconvert(timestamp,  'date')
    )
    df[new_time_table] = df[timestamp_table].apply(
        lambda timestamp: tryconvert(timestamp,  'time')
    )
    return df.drop([timestamp_table,], axis=1)

def timestamp_to_datetime(df, timestamp_table, datetime_table):
    def tryconvert(timestamp):
        try:
            return datetime.datetime.fromtimestamp(timestamp)
        except Exception as e:
            return None
    df[datetime_table] = df[timestamp_table].apply(
        lambda timestamp: tryconvert(timestamp)
    )
    return df

def weekly_key_activity():
    year, week_nr = get_week()
    # generate the week
    week_query = '{}-W{}'.format(year, week_nr)
    monday = datetime.datetime.strptime(week_query + '-1', "%Y-W%W-%w").date()
    week = [monday,]
    for day in range(6):
        week.append(
            week[-1] + datetime.timedelta(days=1)
        )

    #read from db
    conn = sqlite3.connect('performance_monitor.db')
    df = pd.read_sql( """
        SELECT * FROM table_event
        WHERE event_direction='up' AND
        event_type='KEY'
        """ ,conn)
    conn.close()
    print(df.columns )

    # manupulate data
    df['event_date'] = df['event_time'].apply(
        lambda x: datetime.datetime.fromtimestamp(x).date()
    )
    df['event_time'] = df['event_time'].apply(
        lambda x: datetime.datetime.fromtimestamp(x).time()
    )

    week_events = { 'event_date': week, 'event_count': [] }
    for day in week:
        week_events['event_count'].append(
            df.loc[df['event_date'] == day].count()['event_name']
        )
    new_df = pd.DataFrame.from_dict(week_events)

    # PLOT
    plt.close('all')
    new_df.plot(
        x='event_date',
        y='event_count',
        kind='bar',
        title='chart title',
    )
    plt.show()


    # print('week events: ',week_events)
    return
    # Render Data
    x_labels = [ 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun' ]

    df.plot(
        x='x',
        y='y',
        kind='scatter',
        title='chart title',
        )

def weekly_sortware_usate():
    # get week
    # pull data from db
    conn = sqlite3.connect('performance_monitor.db')
    df = pd.read_sql("""
        SELECT * FROM table_window
        """, conn)

    df['delta_time']=None

    df_delta = pd.DataFrame(columns=['process_name', 'delta_time'])

    for index, row in df.iterrows():
        df.loc[index, 'delta_time'] =  df.loc[index, 'end_time'] - df.loc[index, 'start_time']

    df['delta_time'] = df.end_time.fillna(0) - df.start_time.fillna(0) # calcualte time of windows active
    df.loc[ df['delta_time']<0, 'delta_time' ] = 0 # zero if data is missing

    # df.loc[ df['end_time'] == None , 'delta_time'] = 0
    df = df.groupby('process_name').sum().sort_values('delta_time')
    print(
        df.drop(columns=['end_time', 'start_time'])
    )
    plot = df.plot(
        y='delta_time',
        figsize=(15, 15),
        title='Softwere usage [%]',
        kind='pie',
        fontsize= 6,
        startangle=90,
        autopct='%1.1f%%',

        )
    plt.show()


def main():
    #weekly_key_activity()
    weekly_sortware_usate()

if __name__ == '__main__':
    main()
