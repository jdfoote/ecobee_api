# ecobee_api
Checks my RSS feed for peak savings alerts and changes my ecobee to adjust.

In order to use this, you will need to create a developer account and an app on ecobee.com.

Then, create an ecobee_auth.json file that looks like this:

{'client_id': API_KEY_FROM_ECOBEE}


Then, run setup.py, log into the thermostat you want to control, and enter the PIN displayed in the terminal.

Once this runs, the app will get a new auth token and put it into ecobee_auth.json.

I realized that I accidentally pushed my key file, so I revoked the keys and left it up as an example of how this should look
