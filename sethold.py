#!/usr/bin/python3

import json
import requests
import urllib
import random
from datetime import datetime

BASE_URL = 'https://api.ecobee.com/'
auth_file = '/home/pi/ecobee_api/ecobee_auth.json'
future_holds_file = '/home/pi/ecobee_api/future_events.json'

def main():
    activate_holds(future_holds_file)



def refresh_tokens():

    with open(auth_file, 'r') as f:
        auth = json.load(f)

    r = requests.post(BASE_URL + 'token',
            params = {'grant_type': 'refresh_token',
                'code': auth['refresh_token'],
                'client_id': auth['client_id'],
                'ecobee_type': 'jwt'})
    r.raise_for_status()
    if r.status_code == 200:
        content = r.json()
        auth['refresh_token'] = content['refresh_token']
        auth['access_token'] = content['access_token']
        #auth['expiry'] = content['
        with open(auth_file, 'w') as f:
            json.dump(auth, f)
        return content['access_token']
    else:
        raise(f"Refresh failed with {r.status_code}")

def get_events(token):

    headers = {"Authorization": f"Bearer {token}",
 'Content-Type': 'text/json'}
    r = requests.get('https://api.ecobee.com/1/thermostat', headers=headers, params='format=json&body={"selection":{"selectionType":"registered","selectionMatch":"","includeEvents":true}}')
    if r.status_code == 200:
        return r.json()['thermostatList'][0]['events']


def make_call(params):

    token = refresh_tokens()

    r = requests.post(BASE_URL + '1/thermostat',
              params = {'format': 'json'},
              headers = {"Authorization": f"Bearer {token}"},
              json = params)
    return r

def resume_program():

    params = {"selection": {
		"selectionType":"registered",
		"selectionMatch":""
	      },
	      "functions": [
		{
		  "type":"resumeProgram",
		  "params":{
		    "resumeAll":false}}]}
    r = make_call(params)
    if r.status_doe == 200:
        print("Resuming regular program")
    

def set_hold(start_date,
        start_time,
        end_time,
        hold_type,
        ):
    if hold_type == 'prep':
        heatHoldTemp = 700
        coldHoldTemp = 720
    elif hold_type == 'saving':
        heatHoldTemp = 610
        coldHoldTemp = 800
    else:
        raise("hold_type must be one of {prep, saving}")



    selection_params = {"selection": {
    "selectionType":"registered",
    "selectionMatch":"" },
  "functions": [{
      "type":"setHold",
      "params":{
        "name": hold_type + str(random.randint(1,1000)),
        "startDate": start_date,
        "startTime": start_time,
        "endDate": start_date,
        "endTime": end_time,
        "holdType":"dateTime",
        "heatHoldTemp": heatHoldTemp,
        "coolHoldTemp": coldHoldTemp}}]}

    r = make_call(selection_params)
    if r.status_code == 200:
        print(f"Setting temp range to {heatHoldTemp/10}-{coldHoldTemp/10} degrees, starting at {start_time} on {start_date}")
    else:
        print("could not set temperature successfully")
        print(r.content)


def activate_holds(upcoming_holds_file):
    curr_dt = datetime.now()
    with open(upcoming_holds_file, 'r') as f:
        upcoming = json.load(f)
        to_save = []
        for hold in upcoming:
            curr_start = datetime.strptime(f"{hold['date']} {hold['start_time']}", "%Y-%m-%d %H:%M:%S")
            curr_end = datetime.strptime(f"{hold['date']} {hold['end_time']}", "%Y-%m-%d %H:%M:%S")
            if curr_start < curr_dt:
                if curr_end > curr_dt:
                    print("Running")
                    if hold['type'] == 'resume':
                        resume_progam()
                    else:
                        set_hold(start_date = hold['date'],
                                start_time = hold['start_time'],
                                end_time = hold['end_time'],
                                hold_type = hold['type'])
                else:
                    continue
            else:
                to_save.append(hold)
    with open(upcoming_holds_file, 'w') as f:
        json.dump(to_save, f)


if __name__ == '__main__':
    main()
