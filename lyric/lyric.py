# -*- coding:utf-8 -*-

import os
import time
from requests.compat import json
from requests_oauthlib import OAuth2Session
import urllib.parse

CLIENT_ID = r'j9ShGaDTsOWlykvAeJCNcMpO76gGwGq6'
CLIENT_SECRET = r'vtt3qfspAhzgLLyU'

BASE_URL = 'https://api.honeywell.com/v2/'
AUTHORIZATION_BASE_URL = 'https://api.honeywell.com/oauth2/authorize'
TOKEN_URL = 'https://api.honeywell.com/oauth2/token'
REFRESH_URL = TOKEN_URL

class lyricBase(object):
    def __init__(self, device, lyric_api, local_time=False):
        self._device = device
        self._lyric_api = lyric_api
        self._local_time = local_time

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._repr_name)

    def _set(self, endpoint, data, **params):
        self._lyric_api._post(self, endpoint, data, params)
        self._lyric_api._bust_cache()

    @property
    def id(self):
        return self._device['deviceID']

    @property
    def name(self):
        return self._device['name']

    @property
    def _repr_name(self):
        return self.name

class Location(object):
    def __init__(self, location, lyric_api, local_time=False):
        self._location = location
        self._lyric_api = lyric_api
        self._local_time = local_time

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._repr_name)

    @property
    def id(self):
        return self._location['locationID']

    @property
    def name(self):
        return self._location['name']

    @property
    def _repr_name(self):
        return self.name
    
    @property
    def locationID(self):
        return self.id
    
    @property
    def _devices(self):
        return self._lyric_api._devices(self.locationID)

    @property
    def _thermostats(self):
        return self._lyric_api._devices_type('thermostats', self.locationID)
    
    @property
    def _waterLeakDetectors(self):
        return self._lyric_api._devices_type('waterLeakDetectors', self.locationID)
    
    @property
    def devices(self):
        return [Device(device, self, self._local_time)
                for device in self._devices]

    @property
    def thermostats(self):
        return [Thermostat(thermostat, self, self._local_time)
                for thermostat in self._thermostats]

    @property
    def waterLeakDetectors(self):
        return [WaterLeakDetector(waterLeakDetector, self, self._local_time)
                for waterLeakDetector in self._waterLeakDetectors]

class Device(lyricBase):
    @property
    def displayedOutdoorHumidity(self):
        return self._device['displayedOutdoorHumidity']

    #@fan.setter
    #def fan(self, value):
    #    self._set('device', {'fan_mode': 'auto'})

class Thermostat(lyricBase):
    @property
    def displayedOutdoorHumidity(self):
        return self._device['displayedOutdoorHumidity']

class WaterLeakDetector(lyricBase):
    @property
    def displayedOutdoorHumidity(self):
        return self._device['displayedOutdoorHumidity']

class Lyric(object):
    def __init__(self, cache_ttl=270,
                 user_agent='python-lyric/0.1',
                 token=None, token_cache_file=None,
                 local_time=False, app_name=None, redirect_uri=None):
        self._app_name=app_name
        self._redirect_uri=redirect_uri
        self._token = token;
        self._token_cache_file = token_cache_file;
        self._cache_ttl = cache_ttl
        self._cache = (None, 0)
        self._local_time = local_time
        self._user_agent = user_agent
        
        self._lyricAuth()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def _token_saver(self, token):
        self._token = token
        if self._token_cache_file is not None:
                with os.fdopen(os.open(self._token_cache_file,
                                       os.O_WRONLY | os.O_CREAT, 0o600),
                               'w') as f:
                    json.dump(token, f)
    
    def _lyricAuth(self):
        if (self._token_cache_file is not None and
                    self._token is None and
                    os.path.exists(self._token_cache_file)):
                with open(self._token_cache_file, 'r') as f:
                    self._token = json.load(f)
    
        if self._token is not None:
            self._lyricApi = OAuth2Session(CLIENT_ID, token=self._token, 
                                  auto_refresh_url=REFRESH_URL, 
                                  token_updater=self._token_saver)
        else:
            self._lyricApi = OAuth2Session(CLIENT_ID, redirect_uri=self._redirect_uri, 
                                  auto_refresh_url=REFRESH_URL, 
                                  token_updater=self._token_saver)
        
            authorization_url, state = self._lyricApi.authorization_url(
                    AUTHORIZATION_BASE_URL, app=self._app_name)
            
            print ('Please go to %s and authorize access.' % authorization_url)
            authorization_response = input('Enter the full response url')
            
            headers = {'Authorization': 'Basic ajlTaEdhRFRzT1dseWt2QWVKQ05jTXBPNzZnR3dHcTY6dnR0M3Fmc3BBaHpnTEx5VQ==', 'Accept': 'application/json'}
            
            token = self._lyricApi.fetch_token(
                    TOKEN_URL, headers=headers, 
                    authorization_response=authorization_response)
        
            self._token_saver(token)
    
    def _get(self, endpoint, **params):
        params['apikey'] = CLIENT_ID
        query_string = urllib.parse.urlencode(params)
        url = BASE_URL + endpoint + '?' + query_string
        response = self._lyricApi.get(url, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint, data, **params):
        params['apikey'] = CLIENT_ID
        query_string = urllib.parse.urlencode(params)
        url = BASE_URL + endpoint + '?' + query_string
        response = self._lyricApi.post(url, json=data, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        #response.raise_for_status()
        return response.status_code
            
    @property
    def _locations(self):
        value, last_update = self._cache
        now = time.time()

        if not value or now - last_update > self._cache_ttl:
            value = self._get('locations')
            self._cache = (value, now)

        return value

    def _devices(self, locationID):
        value = self._get('devices', locationId=locationID)
        return value

    def _devices_type(self, deviceType, locationID):
        value = self._get('devices/' + deviceType, locationId=locationID)
        return value

    def _bust_cache(self):
        self._cache = (None, 0)

    @property
    def locations(self):
        return [Location(location, self, self._local_time)
                for location in self._locations]
