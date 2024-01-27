""" 
Features:
    - log hours 
        - argument for date, default is today
    - clock in and clock out 
    - daily total hours
    - total hours for the week, week starts on monday
    - total hours for last week
    - weekly hours
"""

#TODO: 
#   add revert feature

import pandas as pd
from datetime import date, timedelta, datetime
from time import localtime, strftime
import argparse
import math
import sys
def excepthook(type, value, traceback): print(type, ':', value)

if True:
    csv_path = 'shits/logger_data.csv'
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--date', type=str, default=None) 
    parser.add_argument('-l', '--log', type=str, default=None)
    parser.add_argument('-hr', '--hours', type=float, default=0)
    parser.add_argument('-ci', '--clockin', type=str, default=None)
    parser.add_argument('-co', '--clockout', type=str, default=None)
    parser.add_argument('-tw', '--thisweek', action='store_true')
    parser.add_argument('-lw', '--lastweek', action='store_true')
    parser.add_argument('-wk', '--weeks', type=int, default=0) 
    args = parser.parse_args()
    if not any(vars(args).values()):
        raise ValueError('no arguments given u dumb fuck')



global_df = pd.read_csv(csv_path)
today = date.today()
temp = "6666-06-06"


# add hours
def log_hours(df, log_date, log_type, hours):
    log_date = str(today) if log_date == None else str(log_date)
    row_date, row_t, row_c, row_r, row_sum = df[df['date']==log_date].iloc[0]
    if log_type == "T":
        row_t += hours
    elif log_type == "C":
        row_c += hours
    elif log_type == "R":
        row_r += hours
    row_sum += hours
    df.loc[df['date']==log_date] = [row_date, row_t, row_c, row_r, row_sum]
    # print(strftime("%Y-%m-%d %H:%M", localtime()))
    print(f'\tlogged {hours} {log_type}-hours for {log_date}')

    return df

# clock in
def clock_in(df, clock_type):
    if any(df[df['date']==temp].iloc[0][1:]):
        sys.excepthook = excepthook
        raise EnvironmentError("did not clock out!")

    cur = localtime()
    md = cur.tm_mon + (cur.tm_mday * .01)
    hm = cur.tm_hour + (cur.tm_min * .01)
    df.loc[df['date']==temp] = [temp, cur.tm_year, md, hm, 1]
    cur = strftime("%Y-%m-%d %H:%M", cur)
    print(f'\tclocked in at {cur} for {clock_type}')

    return df

# clock out
def clock_out(df, clock_type):
    if not all(df[df['date']==temp].iloc[0][1:]):
        sys.excepthook = excepthook
        raise EnvironmentError("did not clock in!")
    
    cur = localtime()
    year, md, hm, _ = df[df['date']==temp].iloc[0][1:]
    year = int(year)
    mon = int(math.floor(md))
    day = int((md - mon) * 100)
    hour = int(math.floor(hm))
    min = int((hm - hour) * 100)
    logged_hours = datetime(cur.tm_year, cur.tm_mon, cur.tm_mday, cur.tm_hour, cur.tm_min) - datetime(year, mon, day, hour, min) 
    logged_hours = round(logged_hours.total_seconds()/3600, 3)

    cur = strftime("%Y-%m-%d %H:%M", cur)
    df.loc[df['date']==temp] = [temp, 0, 0, 0, 0]
    print(f'\tclocked in at %d-%d-%d %d:%d for {clock_type}' % (year, mon, day, hour, min))
    print(f'\tclocked out at {cur} for {clock_type}')

    df = log_hours(df, cur[:10], clock_type, logged_hours)

    return df

# display hours
def week_df(df, wk_start):
    delta = min(today - wk_start, timedelta(days=6))
    wk_end = wk_start + delta
    df_wk = pd.DataFrame(df.loc[(df['date'] <= str(wk_end)) & (df['date'] >=str(wk_start))])
    df_wk.index = ['M', 'T', 'W', 'T', 'F', 'S', 'S'][:len(df_wk)]
    df_wk.loc[''] = ['weekly'] + list(df_wk[['T', 'C', 'R', 'sum']].sum().values)
    return df_wk


# display data for the past n weeks
def display_weeks(df, n):
    monday = today - timedelta(days=today.weekday())
    df_wks = week_df(monday)
    df_wks = df_wks[df_wks.index=='']
    df_wks.iloc[0,0] = monday

    for _ in range(n):
        monday -= timedelta(days=7)
        temp = week_df(monday)
        temp = temp[temp.index=='']
        df_wks = pd.concat([temp, df_wks])
        df_wks.iloc[0,0] = monday

    df_wks.set_index('date', inplace=True)
    return df_wks


def main():
    df = global_df.copy()

    if args.log != None:
        if not args.log in ['t', 'c', 'r', 'T', 'C', 'R']:
            sys.excepthook = excepthook
            raise ValueError('invalid type')
        if not args.hours > 0: 
            sys.excepthook = excepthook
            raise ValueError('invalid hours')
        log_hours(df, args.date, args.log.upper(), args.hours)
        df.to_csv(csv_path, index=False)


    elif args.clockin != None:
        if not args.clockin in ['t', 'c', 'r', 'T', 'C', 'R']:
            sys.excepthook = excepthook
            raise ValueError('invalid type')
        clock_in(df, args.clockin.upper())
        df.to_csv(csv_path, index=False)

    elif args.clockout != None:
        if not args.clockout in ['t', 'c', 'r', 'T', 'C', 'R']:
            sys.excepthook = excepthook
            raise ValueError('invalid type')
        clock_out(df, args.clockout.upper())
        df.to_csv(csv_path, index=False)
    
    elif args.thisweek:
        df_wk = week_df(df, today - timedelta(days=today.weekday()))
        df_wk.drop(['date'], axis=1, inplace=True)
        print(df_wk)

    elif args.lastweek:
        df_wk = week_df(df, today - timedelta(days=today.weekday()) - timedelta(days=7))
        df_wk.drop(['date'], axis=1, inplace=True)
        print(df_wk)

    elif args.weeks > 0:
        total_weeks = math.floor((today-(datetime.strptime(global_df.iloc[0][0], '%Y-%m-%d').date())).days/7)
        if total_weeks < args.weeks:
            print('only {} weeks of data!!!!!!!!!!!'.format(total_weeks))
        else:
            print(display_weeks(df, args.weeks))


main()