# -*- coding:utf-8 -*-

import os
import time
import requests
from requests.compat import json
from requests_oauthlib import OAuth2Session
import urllib.parse

BASE_URL = 'https://api.honeywell.com/v2/'
AUTHORIZATION_BASE_URL = 'https://api.honeywell.com/oauth2/authorize'
TOKEN_URL = 'https://api.honeywell.com/oauth2/token'
REFRESH_URL = TOKEN_URL

class lyricBase(object):
    def __init__(self, deviceId, locationId, lyric_api, local_time=False):
        self._deviceId = deviceId
        self._locationId = locationId
        self._lyric_api = lyric_api
        self._local_time = local_time

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._repr_name)

    def _set(self, endpoint, data, **params):
        self._lyric_api._post(self, endpoint, data, params)
        #self._lyric_api._bust_cache(cache_key)

    @property
    def id(self):
        return self._deviceId

    @property
    def name(self):
        return self._lyric_api._device(self._locationId, self._deviceId)['name']

    @property
    def _repr_name(self):
        return self.name

class Location(object):
    def __init__(self, locationId, lyric_api, local_time=False):
        self._locationId = locationId
        self._lyric_api = lyric_api
        self._local_time = local_time

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._repr_name)

    @property
    def id(self):
        return self._locationId

    @property
    def locationId(self):
        return self._locationId

    @property
    def name(self):
        return self._lyric_api._location(self._locationId)['name']
        #return self._location['name']

    @property
    def _repr_name(self):
        return self.name
    
    @property
    def _devices(self):
        return self._lyric_api._devices(self._locationId)

    @property
    def _thermostats(self):
        return self._lyric_api._devices_type('thermostats', self._locationId)
    
    @property
    def _waterLeakDetectors(self):
        return self._lyric_api._devices_type('waterLeakDetectors', self._locationId)
    
    @property
    def devices(self):
        if 'deviceID' in self._devices[0]:
            return [Device(device['deviceID'], self._locationId, self._lyric_api, 
                           self._local_time)
                    for device in self._devices]

    @property
    def thermostats(self):
        if 'deviceID' in self._thermostats[0]:
            return [Thermostat(thermostat['deviceID'], self._locationId, 
                               self._lyric_api, self._local_time)
                    for thermostat in self._thermostats]

    @property
    def waterLeakDetectors(self):
        if 'deviceID' in self._waterLeakDetectors[0]:
            return [WaterLeakDetector(waterLeakDetector['deviceID'], 
                                      self._locationId, self._lyric_api, 
                                      self._local_time)
                    for waterLeakDetector in self._waterLeakDetectors]

class Device(lyricBase):
    @property
    def displayedOutdoorHumidity(self):
        return self._lyric_api._device(self._locationId, self._deviceId)['displayedOutdoorHumidity']

    #@fan.setter
    #def fan(self, value):
    #    self._set('device', {'fan_mode': 'auto'})

class Thermostat(lyricBase):
    @property
    def displayedOutdoorHumidity(self):
        return self._lyric_api._device(self._locationId, self._deviceId)['displayedOutdoorHumidity']

    @property
    def indoorTemperature(self):
        return self._lyric_api._device(self._locationId, self._deviceId)['indoorTemperature']

    @property
    def outdoorTemperature(self):
        return self._lyric_api._device(self._locationId, self._deviceId)['outdoorTemperature']

    @property
    def indoorHumidity(self):
        if 'indoorHumidity' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['indoorHumidity']

    @property
    def indoorHumidityStatus(self):
        if 'indoorHumidityStatus' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['indoorHumidityStatus']

class WaterLeakDetector(lyricBase):
    @property
    def displayedOutdoorHumidity(self):
        return self._lyric_api._device(self._locationId, self._deviceId)['displayedOutdoorHumidity']

class Lyric(object):
    def __init__(self, client_id, client_secret, cache_ttl=270,
                 user_agent='python-lyric/0.1',
                 token=None, token_cache_file=None,
                 local_time=False, app_name=None, redirect_uri=None):
        self._client_id = client_id
        self._client_secret = client_secret
        self._app_name=app_name
        self._redirect_uri=redirect_uri
        self._token = token;
        self._token_cache_file = token_cache_file
        self._cache_ttl = cache_ttl
        self._cache = {'locations': (None, 0)}
        self._local_time = local_time
        self._user_agent = user_agent
        
        if token is None and token_cache_file is None and redirect_uri is None:
            print('You need to supply a token or a cached token file,'
            'or define a redirect uri')
        else:
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
    
    @property
    def authorized(self):
        self._lyricApi.authorized
    
    @property
    def getauthorize_url(self):
        self._lyricApi = OAuth2Session(self._client_id, 
                                       redirect_uri=self._redirect_uri, 
                                       auto_refresh_url=REFRESH_URL, 
                                       token_updater=self._token_saver)
    
        authorization_url, state = self._lyricApi.authorization_url(
                AUTHORIZATION_BASE_URL, app=self._app_name)
        
        return authorization_url
    
    def authorization_response(self, authorization_response):
        auth = requests.auth.HTTPBasicAuth(self._client_id, self._client_secret) 
        headers = {'Accept': 'application/json'}
        
        token = self._lyricApi.fetch_token(
                TOKEN_URL, headers=headers, auth=auth,
                authorization_response=authorization_response)
    
        self._token_saver(token)

    def authorization_code(self, code, state):
        auth = requests.auth.HTTPBasicAuth(self._client_id, self._client_secret) 
        headers = {'Accept': 'application/json'}
        
        token = self._lyricApi.fetch_token(
                TOKEN_URL, headers=headers, auth=auth,
                code=code, state=state)
    
        self._token_saver(token)
    
    def _lyricAuth(self):
        if (self._token_cache_file is not None and
                    self._token is None and
                    os.path.exists(self._token_cache_file)):
                with open(self._token_cache_file, 'r') as f:
                    self._token = json.load(f)
    
        if self._token is not None:
            self._lyricApi = OAuth2Session(self._client_id, token=self._token, 
                                           auto_refresh_url=REFRESH_URL, 
                                           token_updater=self._token_saver)
#         else:
#             self._lyricApi = OAuth2Session(self._client_id, 
#                                            redirect_uri=self._redirect_uri, 
#                                            auto_refresh_url=REFRESH_URL, 
#                                            token_updater=self._token_saver)
#         
#             authorization_url, state = self._lyricApi.authorization_url(
#                     AUTHORIZATION_BASE_URL, app=self._app_name)
#             
#             print ('Please go to %s and authorize access.' % authorization_url)
#             authorization_response = input('Enter the full response url')
#             
#             auth = requests.auth.HTTPBasicAuth(self._client_id, 
#                                                self._client_secret) 
#             headers = {'Accept': 'application/json'}
#             
#             token = self._lyricApi.fetch_token(
#                     TOKEN_URL, headers=headers, auth=auth,
#                     authorization_response=authorization_response)
#         
#             self._token_saver(token)
    
    def _get(self, endpoint, **params):
        params['apikey'] = self._client_id
        query_string = urllib.parse.urlencode(params)
        url = BASE_URL + endpoint + '?' + query_string
        response = self._lyricApi.get(url, client_id=self._client_id, 
                                      client_secret=self._client_secret)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint, data, **params):
        params['apikey'] = self._client_id
        query_string = urllib.parse.urlencode(params)
        url = BASE_URL + endpoint + '?' + query_string
        response = self._lyricApi.post(url, json=data, client_id=self._client_id, 
                                       client_secret=self._client_secret)
        #response.raise_for_status()
        return response.status_code
    
    def _checkCache(self, cache_key):
        if cache_key in self._cache:
            cache = self._cache[cache_key]
        else:
            cache = (None, 0)
            
        return cache
    
    def _location(self, locationId):
        for location in self._locations:
            if location['locationID'] == locationId:
                return location
        
    @property
    def _locations(self):
        cache_key = 'locations'
        value, last_update = self._checkCache(cache_key)
        now = time.time()

        if not value or now - last_update > self._cache_ttl:
            value = self._get('locations')
            self._cache[cache_key] = (value, now)

        return value
    
    def _device(self, locationId, deviceId):
        for device in self._devices(locationId):
            if device['deviceID'] == deviceId:
                return device
    
    def _devices(self, locationId):
        cache_key = 'devices-%s' %locationId
        value, last_update = self._checkCache(cache_key)
        now = time.time()

        if not value or now - last_update > self._cache_ttl:
            value = self._get('devices', locationId=locationId)
            self._cache[cache_key] = (value, now)

        return value

    def _device_type(self, locationId, deviceType, deviceId):
        for device in self._devices_type(deviceType, locationId):
            if device['deviceID'] == deviceId:
                return device

    def _devices_type(self, deviceType, locationId):
        cache_key = 'devices_type-%s-%s' % (deviceType, locationId)
        value, last_update = self._checkCache(cache_key)
        now = time.time()

        if not value or now - last_update > self._cache_ttl:
            value = self._get('devices/' + deviceType, locationId=locationId)
            self._cache[cache_key] = (value, now)

        return value

    def _bust_cache_all(self):
        self._cache = {'locations': (None, 0)}

    def _bust_cache(self, cache_key):
        self._cache[cache_key] = (None, 0)

    @property
    def locations(self):
        return [Location(location['locationID'], self, self._local_time)
                for location in self._locations]
