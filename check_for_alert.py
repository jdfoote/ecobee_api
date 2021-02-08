import requests
import re
#import sethold
from datetime import datetime
import json

future_holds_file = './future_events.json'

alert_regex = re.compile('a')

r = requests.get('http://emails2rss.appspot.com/rss?id=36e69f0b0d17404aa40a7eb032bb6a3c0c1c', headers = {'user-agent': 'jdfoote-app/0.0.1'})
print(r.content)


def get_date(text):
# Delete this when regex is fixed
    return datetime.now()


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
                'start_time' : '05:00:00',
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


if r.status_code == 200:
    if re.search(alert_regex, r.text):
        date = get_date(r.text)
        holds = get_settings(date)
        with open(future_holds_file, 'r') as f:
            curr_holds = json.load(f)
            curr_holds += holds
        with open(future_holds_file, 'w') as f:
            json.dump(curr_holds, f)

#        for hold in holds:
#            sethold.set_hold(
#                start_date = hold['date'],
#                start_time= hold['start_time'],
#                end_time = hold['end_time'],
#                hold_type = hold['type'],
#                token = token
#                )
#        print(sethold.get_events(token))
#
