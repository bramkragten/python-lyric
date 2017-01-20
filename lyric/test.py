#import lyric
import os
import requests
from requests.compat import json
from requests_oauthlib import OAuth2Session

client_id = r'j9ShGaDTsOWlykvAeJCNcMpO76gGwGq6'
client_secret = r'vtt3qfspAhzgLLyU'
redirect_uri = 'https://hass.deproducties.com:8123/lyric'
app_name = 'Home Assistant'

base_url = 'https://api.honeywell.com/v2/'
authorization_base_url = 'https://api.honeywell.com/oauth2/authorize'
token_url = 'https://api.honeywell.com/oauth2/token'
refresh_url = token_url

saved_token = None

access_token_cache_file = 'token.txt'

if (access_token_cache_file is not None and
                saved_token is None and
                os.path.exists(access_token_cache_file)):
            with open(access_token_cache_file, 'r') as f:
                saved_token = json.load(f)

def token_saver(token):
    saved_token = token
    if access_token_cache_file is not None:
            with os.fdopen(os.open(access_token_cache_file,
                                   os.O_WRONLY | os.O_CREAT, 0o600),
                           'w') as f:
                json.dump(saved_token, f)

if saved_token is not None:
    oauth = OAuth2Session(client_id, token=saved_token, 
                          auto_refresh_url=refresh_url, 
                          token_updater=token_saver)
else:
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, 
                          auto_refresh_url=refresh_url, 
                          token_updater=token_saver)

    authorization_url, state = oauth.authorization_url(
            authorization_base_url, app=app_name)
    
    print ('Please go to %s and authorize access.' % authorization_url)
    authorization_response = input('Enter the full response url')
    
    headers = {'Authorization': 'Basic ajlTaEdhRFRzT1dseWt2QWVKQ05jTXBPNzZnR3dHcTY6dnR0M3Fmc3BBaHpnTEx5VQ==', 'Accept': 'application/json'}
    
    token = oauth.fetch_token(
            token_url, headers=headers, 
            authorization_response=authorization_response)

    token_saver(token)

response = oauth.get(base_url + 'locations?apikey=' + client_id)
print (response.json())

response = oauth.get(base_url + 'devices?locationId=77713&apikey=' + client_id)
print (response.json())

data = {
    "mode": "Heat",
    "heatSetpoint": 18,
    "coolSetpoint": 30,
    "thermostatSetpointStatus": "TemporaryHold"
    }

response = oauth.post(base_url + 'devices/thermostats/' + 'LCC-00D02DAAF29A?locationId=77713' + '&apikey=' + client_id, json = data)
print (response.status_code)

#except TokenExpiredError as e:
#    token = oauth.refresh_token(token_url, headers=headers)
#    token_saver(token)
