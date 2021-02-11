import requests
import json

BASE_URL = 'https://api.ecobee.com/'

auth_file = './ecobee_auth.json'

with open(auth_file, 'r') as f:
    auth = json.load(f)
    print(auth)

r = requests.get(BASE_URL + 'authorize',
        params = {'response_type': 'ecobeePin',
            'client_id': auth['client_id']})

if r.status_code == 200:
    print(f"Go to ecobee.com, log in, and enter the following PIN under apps: {r.json()['ecobeePin']}")
    auth_token = r.json()['code']


ready = None
while ready!= 'y':
    ready = input("Once you've entered the PIN, type 'y'")

r2 = requests.post(BASE_URL + 'token',
        params = {'grant_type': 'ecobeePin',
            'code': auth_token,
            'client_id': auth['client_id'],
            'ecobee_type': 'jwt'})
if r2.status_code == 200:
    content = r2.json()
    print(content)
    auth['refresh_token'] = content['refresh_token']
    auth['access_token'] = content['access_token']
    with open(auth_file, 'w') as f:
        json.dump(auth, f)
else:
    print(r2.text)
