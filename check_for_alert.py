import requests
import re
#import sethold
from datetime import datetime, timedelta
import json
import feedparser

future_holds_file = './future_events.json'


def main():
    feed = feedparser.parse('http://emails2rss.appspot.com/rss?id=36e69f0b0d17404aa40a7eb032bb6a3c0c1c')
    for entry in feed.entries:
        entry_date = get_date(entry.published)
        if entry_date < datetime.now() - timedelta(days=1):
            continue
        else:
            if re.match('.*Flex Savings Option Alert for Tomorrow', entry.title):
                to_add = get_settings(entry_date + timedelta(days=1))
                save_changes(to_add)
            else:
                print("No alert for the post '{entry.title}'")



def get_date(s):
    return datetime.strptime(s, '%a, %d %b %Y %H:%M:%S %Z')


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
                'end_time': '18:00:00',
                'type': 'saving'}]
    else:
        result = [
            {'date': datestring,
                'start_time' : '04:30:00',
                'end_time': '06:00:00',
                'type': 'prep'},
            {'date': datestring,
                'start_time' : '06:00:00',
                'end_time': '13:00:00',
                'type': 'saving'},
            {'date': datestring,
                'start_time' : '17:00:00',
                'end_time': '18:00:00',
                'type': 'prep'},
            {'date': datestring,
                'start_time' : '18:00:00',
                'end_time': '21:00:00',
                'type': 'saving'
            }
        ]
    return result


def save_changes(holds):
    with open(future_holds_file, 'r') as f:
        try:
            curr_holds = json.load(f)
        except json.decoder.JSONDecodeError:
            curr_holds = []
        curr_holds += holds
    with open(future_holds_file, 'w') as f:
        json.dump(curr_holds, f)


if __name__ == '__main__':
    main()
