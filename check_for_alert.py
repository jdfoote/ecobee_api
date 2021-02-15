#!/usr/bin/python3

import requests
import re
#import sethold
from datetime import datetime, timedelta, timezone
import json
import feedparser
import pytz

future_holds_file = '/home/pi/ecobee_api/future_events.json'


def main():
    feed = feedparser.parse('https://notifier.in/rss/kbh1nnsaukm97yjdk5if41epxaprmrs6.xml')
    for entry in feed.entries:
        entry_date = get_date(entry.published)
        if entry_date < datetime.now(pytz.timezone('US/Eastern')) - timedelta(days=1):
            continue
        else:
            if re.match('.*Alert.*[tT]omorrow', entry.title):
                to_add = get_settings(entry_date + timedelta(days=1))
                save_changes(to_add)
            else:
                print("No alert for the post '{entry.title}'")



def get_date(s):
    dt = datetime.strptime(s, '%a, %d %b %Y %H:%M:%S %z')
    return dt.astimezone(pytz.timezone('US/Eastern'))



def get_settings(date):
    '''Takes in the date, and figures out which hours to turn off.
    In Summer, this is noon - 6, in winter it's 6-1300 and 1800-2100.
    In both cases, an hour before turning off, either cool down or heat up to help compensate'''
    datestring = date.strftime('%Y-%m-%d')
    if date.month >= 4 and date.month <= 9:
        result = [
            {'date': datestring,
                'start_time' : '11:00:00',
                'end_time': '12:00:00',
                'type': 'prep'},
            {'date': datestring,
                'start_time' : '12:00:00',
                'end_time': '19:00:00',
                'type': 'saving'},
            {'date': datestring, # Resume the regular program at 6
                'start_time': '18:00:00',
                'end_time' : '19:00:00',
                'type': 'resume'}]
    else:
        result = [
            {'date': datestring,
                'start_time' : '04:00:00',
                'end_time': '06:00:00',
                'type': 'prep'},
            {'date': datestring,
                'start_time' : '06:00:00',
                'end_time': '15:00:00', # Hold until 3, so that it doesn't automatically adjust before it's time
                'type': 'saving'},
            {'date': datestring, # Resume the regular program at 1
                'start_time': '13:00:00',
                'end_time' : '14:00:00',
                'type': 'resume'},
            {'date': datestring,
                'start_time' : '17:00:00',
                'end_time': '18:00:00',
                'type': 'prep'},
            {'date': datestring,
                'start_time' : '18:00:00',
                'end_time': '23:00:00',
                'type': 'saving'
            },
            {'date': datestring, # Resume the regular program at 9
                'start_time': '21:00:00',
                'end_time' : '22:00:00',
                'type': 'resume'}
        ]
    return result


def save_changes(holds):
    try:
        with open(future_holds_file, 'r') as f:
            curr_holds = json.load(f)
    except (json.decoder.JSONDecodeError, FileNotFoundError) as e:
        curr_holds = []
    # check if this date has already been added
    if holds[0]['date'] not in [x['date'] for x in curr_holds]:
        curr_holds += holds
    with open(future_holds_file, 'w') as f:
        print("Adding some new holds")
        json.dump(curr_holds, f)


if __name__ == '__main__':
    main()
