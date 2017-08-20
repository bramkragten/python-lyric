# -*- coding:utf-8 -*-

import os
import time
import logging
import requests
#import json
from requests.compat import json
from requests_oauthlib import OAuth2Session, TokenUpdated
from oauthlib.oauth2 import TokenExpiredError
import urllib.parse

_LOGGER = logging.getLogger(__name__)

BASE_URL = 'https://api.honeywell.com/v2/'
AUTHORIZATION_BASE_URL = 'https://api.honeywell.com/oauth2/authorize'
TOKEN_URL = 'https://api.honeywell.com/oauth2/token'
REFRESH_URL = TOKEN_URL

class lyricDevice(object):
    def __init__(self, deviceId, location, lyric_api, local_time=False):
        self._deviceId = deviceId
        self._location = location
        self._locationId = self._location.locationId
        self._lyric_api = lyric_api
        self._local_time = local_time

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._repr_name)

    def _set(self, endpoint, data, **params):
        params['locationId'] = self._location.locationId
        print(self._lyric_api._post(endpoint, data, **params))
        self._lyric_api._bust_cache_all()

    @property
    def id(self):
        return self._deviceId

    @property
    def name(self):
        if 'name' in self._lyric_api._device(self._location.locationId, self._deviceId):
            return self._lyric_api._device(self._location.locationId, self._deviceId)['name']
        else:
            return self.userDefinedDeviceName

    @property
    def _repr_name(self):
        return self.userDefinedDeviceName

    @property
    def deviceClass(self):
        return self._lyric_api._device(self._location.locationId, self._deviceId)['deviceClass']

    @property
    def deviceType(self):
        return self._lyric_api._device(self._location.locationId, self._deviceId)['deviceType']

    @property
    def deviceID(self):
        return self._lyric_api._device(self._location.locationId, self._deviceId)['deviceID']

    @property
    def userDefinedDeviceName(self):
        return self._lyric_api._device(self._location.locationId, self._deviceId)['userDefinedDeviceName']

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
    def locationID(self):
        return self._lyric_api._location(self._locationId)['locationID']

    @property
    def name(self):
        return self._lyric_api._location(self._locationId)['name']

    @property
    def _repr_name(self):
        return self.name

    @property
    def streetAddress(self):
        return self._lyric_api._location(self._locationId)['streetAddress']

    @property
    def city(self):
        return self._lyric_api._location(self._locationId)['city']

    @property
    def state(self):
        return self._lyric_api._location(self._locationId)['state']

    @property
    def country(self):
        return self._lyric_api._location(self._locationId)['country']

    @property
    def zipcode(self):
        return self._lyric_api._location(self._locationId)['zipcode']

    @property
    def timeZone(self):
        return self._lyric_api._location(self._locationId)['timeZone']

    @property
    def daylightSavingTimeEnabled(self):
        return self._lyric_api._location(self._locationId)['daylightSavingTimeEnabled']

    @property
    def geoFenceEnabled(self):
        if 'geoFenceEnabled' in self._lyric_api._location(self._locationId):
            return self._lyric_api._location(self._locationId)['geoFenceEnabled']

    @property
    def geoFences(self):
        if 'geoFences' in self._lyric_api._location(self._locationId):
            return self._lyric_api._location(self._locationId)['geoFences']

    @property
    def geoFence(self, index=0):
        if self.geoFences and len(self.geoFences) >= index+1:
            return self.geoFences[index]

    @property
    def geoOccupancy(self):
        if 'geoOccupancy' in self.geoFence:
            return self.geoFence['geoOccupancy']

    @property
    def withInFence(self):
        if 'withinFence' in self.geoOccupancy:
            return self.geoOccupancy['withinFence']

    @property
    def outsideFence(self):
        if 'outsideFence' in self.geoOccupancy:
            return self.geoOccupancy['outsideFence']
        
    @property
    def _users(self):
        return self._lyric_api._users(self._locationId)

    @property
    def _devices(self, forceGet=False):
        return self._lyric_api._devices(self._locationId, forceGet)

    @property
    def _thermostats(self):
        return self._lyric_api._devices_type('thermostats', self._locationId)

    @property
    def _waterLeakDetectors(self):
        return self._lyric_api._devices_type('waterLeakDetectors', self._locationId)

    @property
    def users(self):
        return [User(user['userID'], self, self._lyric_api, self._local_time)
                for user in self._users]

    @property
    def devices(self):
        devices = []
        for device in self._devices:
            if device['deviceType'] == 'Thermostat':
                devices.append(Thermostat(device['deviceID'], self,
                                    self._lyric_api, self._local_time))
            elif device['deviceType'] == 'Water Leak Detector':
                devices.append(WaterLeakDetector(device['deviceID'], self,
                                    self._lyric_api, self._local_time))
            else:
                devices.append(Device(device['deviceID'], self,
                                    self._lyric_api, self._local_time))
        return devices

    @property
    def thermostats(self):
        thermostats = []
        for device in self._devices:
            if device['deviceType'] == 'Thermostat':
                thermostats.append(Thermostat(device['deviceID'], self,
                                    self._lyric_api, self._local_time))
        return thermostats

    @property
    def waterLeakDetectors(self):
        waterLeakDetectors = []
        for device in self._devices:
            if device['deviceType'] == 'Water Leak Detector':
                waterLeakDetectors.append(WaterLeakDetector(device['deviceID'], self,
                                    self._lyric_api, self._local_time))
        return waterLeakDetectors

class User(object):
    def __init__(self, userId, location, lyric_api, local_time=False):
        self._location = location
        self._locationId = self._location.locationId
        self._userId = userId
        self._lyric_api = lyric_api
        self._local_time = local_time

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._repr_name)

    @property
    def id(self):
        return self._userId

    @property
    def name(self):
        return self.username

    @property
    def _repr_name(self):
        return self.username

    @property
    def userID(self):
        return self._lyric_api._user(self._location.locationId, self._userId)['userID']

    @property
    def username(self):
        return self._lyric_api._user(self._location.locationId, self._userId)['username']

    @property
    def firstname(self):
        return self._lyric_api._user(self._locationId, self._userId)['firstname']

    @property
    def lastname(self):
        return self._lyric_api._user(self._locationId, self._userId)['lastname']

    @property
    def created(self):
        return self._lyric_api._user(self._locationId, self._userId)['created']

    @property
    def deleted(self):
        return self._lyric_api._user(self._locationId, self._userId)['deleted']

    @property
    def activated(self):
        return self._lyric_api._user(self._locationId, self._userId)['activated']

    @property
    def connectedHomeAccountExists(self):
        return self._lyric_api._user(self._locationId, self._userId)['connectedHomeAccountExists']

class Device(lyricDevice):
    @property
    def unknownType(self):
        return True

    def properties(self):
        return self._lyric_api._device(self._locationId, self._deviceId)

class Thermostat(lyricDevice):

    def updateThermostat(self, mode=None, heatSetpoint=None, coolSetpoint=None, AutoChangeover=None, thermostatSetpointStatus=None, nextPeriodTime=None):
        if mode is None:
            mode = self.operationMode
        if heatSetpoint is None:
            heatSetpoint = self.heatSetpoint
        if coolSetpoint is None:
            coolSetpoint = self.coolSetpoint

        if 'thermostatSetpointStatus' in self.changeableValues:
            if thermostatSetpointStatus is None:
                thermostatSetpointStatus = self.thermostatSetpointStatus

        if 'autoChangeoverActive' in self.changeableValues:
            if AutoChangeover is None:
                AutoChangeover = self.changeableValues['autoChangeoverActive']

        data = {
            'mode': mode,
            'heatSetpoint': heatSetpoint,
            'coolSetpoint': coolSetpoint
        }

        if 'thermostatSetpointStatus' in self.changeableValues:
            data['thermostatSetpointStatus'] = thermostatSetpointStatus
        if 'autoChangeoverActive' in self.changeableValues:
            data['autoChangeoverActive'] = AutoChangeover
        if nextPeriodTime is not None:
            data['nextPeriodTime'] = nextPeriodTime

        self._set('devices/thermostats/' + self._deviceId, data=data)
        
    @property
    def away(self):
        if self.scheduleType == 'Geofence':
            if self._location.geoFenceEnabled:
                return (self._location.withInFence == 0)
        elif self.scheduleType == 'Timed' and self.scheduleSubType == 'NA': # North America
            return (self.currentSchedulePeriod['period'] == 'Away')
        elif self.scheduleType == 'Timed' and self.scheduleSubType == 'EMEA': # Europe, Middle-East, Africa
            return (self.currentSchedulePeriod['period'] == 'P3')
    
    @property
    def vacationHold(self):
        if 'vacationHold' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['vacationHold']['enabled']

    @property
    def where(self):
        return self._location.name

    @property
    def units(self):
        if 'units' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['units']

    @property
    def indoorTemperature(self):
        if 'indoorTemperature' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['indoorTemperature']

    @property
    def heatSetpoint(self):
        return self.changeableValues['heatSetpoint']

    @property
    def coolSetpoint(self):
        return self.changeableValues['coolSetpoint']

    @property
    def thermostatSetpointStatus(self):
        if 'thermostatSetpointStatus' in self.changeableValues:
            return self.changeableValues['thermostatSetpointStatus']

    @thermostatSetpointStatus.setter
    def thermostatSetpointStatus(self, thermostatSetpointStatus):
        self.updateThermostat(thermostatSetpointStatus=thermostatSetpointStatus)

    def thermostatSetpointHoldUntil(self, nextPeriodTime, heatSetpoint=None, coolSetpoint=None):
        if (nextPeriodTime is None):
            raise ValueError('nextPeriodTime is required')
        self.updateThermostat(heatSetpoint=heatSetpoint, coolSetpoint=coolSetpoint, thermostatSetpointStatus='HoldUntil', nextPeriodTime=nextPeriodTime)

    @property
    def nextPeriodTime(self):
        if 'nextPeriodTime' in self.changeableValues:
            return self.changeableValues['nextPeriodTime']

    @property
    def AutoChangeover(self):
        if 'AutoChangeover' in self.changeableValues:
            return self.changeableValues['AutoChangeover']

    @property
    def operationMode(self):
        if 'mode' in self.changeableValues:
            return self.changeableValues['mode']

    @operationMode.setter
    def operationMode(self, mode):
        self.updateThermostat(mode=mode)

    @property
    def temperatureSetpoint(self):
        if self.operationMode == 'Heat':
            return self.changeableValues['heatSetpoint']
        else:
            return self.changeableValues['coolSetpoint']

    @temperatureSetpoint.setter
    def temperatureSetpoint(self, setpoint):
        
        if self.thermostatSetpointStatus=='NoHold':
            thermostatSetpointStatus = 'TemporaryHold'
        else:
            thermostatSetpointStatus = self.thermostatSetpointStatus

        if isinstance(setpoint, tuple):
        # if self.operationMode=='Auto':
            self.updateThermostat(coolSetpoint=setpoint[0], heatSetpoint=setpoint[1], thermostatSetpointStatus=thermostatSetpointStatus)
        elif self.operationMode=='Cool':
            self.updateThermostat(coolSetpoint=setpoint, thermostatSetpointStatus=thermostatSetpointStatus)
        elif self.operationMode=='Heat':
            self.updateThermostat(heatSetpoint=setpoint, thermostatSetpointStatus=thermostatSetpointStatus)

    @property
    def can_heat(self):
        return ("Heat" in self.allowedModes)

    @property
    def can_cool(self):
        return ("Cool" in self.allowedModes)

    @property
    def has_fan(self):
        return True

    @property
    def outdoorTemperature(self):
        if 'outdoorTemperature' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['outdoorTemperature']

    @property
    def allowedModes(self):
        if 'allowedModes' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['allowedModes']

    @property
    def deadband(self):
        if 'deadband' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['deadband']

    @property
    def hasDualSetpointStatus(self):
        if 'hasDualSetpointStatus' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['hasDualSetpointStatus']

    @property
    def minHeatSetpoint(self):
        if 'minHeatSetpoint' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['minHeatSetpoint']

    @property
    def maxHeatSetpoint(self):
        if 'maxHeatSetpoint' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['maxHeatSetpoint']

    @property
    def minCoolSetpoint(self):
        if 'minCoolSetpoint' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['minCoolSetpoint']

    @property
    def maxCoolSetpoint(self):
        if 'maxCoolSetpoint' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['maxCoolSetpoint']

    @property
    def maxSetpoint(self):
        if self.can_heat:
            return self.maxHeatSetpoint
        else:
            return self.maxCoolSetpoint

    @property
    def minSetpoint(self):
        if self.can_cool:
            return self.minCoolSetpoint
        else:
            return self.minHeatSetpoint
        
    @property
    def changeableValues(self):
        if 'changeableValues' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['changeableValues']

    @property
    def operationStatus(self):
        if 'operationStatus' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['operationStatus']

    @property
    def smartAway(self):
        if 'smartAway' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['smartAway']

    @property
    def indoorHumidity(self):
        if 'indoorHumidity' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['indoorHumidity']

    @property
    def indoorHumidityStatus(self):
        if 'indoorHumidityStatus' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['indoorHumidityStatus']

    @property
    def isAlive(self):
        if 'isAlive' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['isAlive']

    @property
    def isUpgrading(self):
        if 'isUpgrading' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['isUpgrading']

    @property
    def isProvisioned(self):
        if 'isProvisioned' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['isProvisioned']

    @property
    def settings(self):
        if 'settings' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['settings']

    @property
    def fanMode(self):
        if self.settings and 'fan' in self.settings:
            return self.settings["fan"]["changeableValues"]["mode"]

    @property
    def macID(self):
        if 'macID' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['macID']

    @property
    def scheduleStatus(self):
        if 'scheduleStatus' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['scheduleStatus']

    @property
    def allowedTimeIncrements(self):
        if 'allowedTimeIncrements' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['allowedTimeIncrements']

    @property
    def thermostatVersion(self):
        if 'thermostatVersion' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['thermostatVersion']

    @property
    def isRegistered(self):
        if 'isRegistered' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['isRegistered']

    @property
    def devicesettings(self):
        if 'devicesettings' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['devicesettings']

    @property
    def displayedOutdoorHumidity(self):
        if 'displayedOutdoorHumidity' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['displayedOutdoorHumidity']

    @property
    def currentSchedulePeriod(self):
        if 'currentSchedulePeriod' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['currentSchedulePeriod']

    @property
    def scheduleCapabilities(self):
        if 'scheduleCapabilities' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['scheduleCapabilities']

    @property
    def scheduleType(self):
        if 'scheduleType' in self._lyric_api._device(self._locationId, self._deviceId) and 'scheduleType' in self._lyric_api._device(self._locationId, self._deviceId)['scheduleType']:
            return self._lyric_api._device(self._locationId, self._deviceId)['scheduleType']['scheduleType']
        elif 'schedule' in self._lyric_api._device(self._locationId, self._deviceId) and 'scheduleType' in self._lyric_api._device(self._locationId, self._deviceId)['schedule']:
            return self._lyric_api._device(self._locationId, self._deviceId)['schedule']['scheduleType']

    @property
    def scheduleSubType(self):
        if 'scheduleType' in self._lyric_api._device(self._locationId, self._deviceId) and 'scheduleSubType' in self._lyric_api._device(self._locationId, self._deviceId)['scheduleType']:
            return self._lyric_api._device(self._locationId, self._deviceId)['scheduleType']['scheduleSubType']


class WaterLeakDetector(lyricDevice):

    @property
    def waterPresent(self):
        if 'waterPresent' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['waterPresent']

    @property
    def currentSensorReadings(self):
        if 'currentSensorReadings' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['currentSensorReadings']

    @property
    def currentAlarms(self):
        if 'currentAlarms' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['currentAlarms']

    @property
    def lastCheckin(self):
        if 'lastCheckin' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['lastCheckin']

    @property
    def lastDeviceSettingUpdatedOn(self):
        if 'lastDeviceSettingUpdatedOn' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['lastDeviceSettingUpdatedOn']

    @property
    def batteryRemaining(self):
        if 'batteryRemaining' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['batteryRemaining']

    @property
    def isRegistered(self):
        if 'isRegistered' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['isRegistered']

    @property
    def hasDeviceCheckedIn(self):
        if 'hasDeviceCheckedIn' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['hasDeviceCheckedIn']

    @property
    def isDeviceOffline(self):
        if 'isDeviceOffline' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['isDeviceOffline']

    @property
    def firstFailedAttemptTime(self):
        if 'firstFailedAttemptTime' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['firstFailedAttemptTime']

    @property
    def failedConnectionAttempts(self):
        if 'failedConnectionAttempts' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['failedConnectionAttempts']

    @property
    def wifiSignalStrength(self):
        if 'wifiSignalStrength' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['wifiSignalStrength']

    @property
    def isFirmwareUpdateRequired(self):
        if 'isFirmwareUpdateRequired' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['isFirmwareUpdateRequired']

    @property
    def time(self):
        if 'time' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['time']

    @property
    def deviceSettings(self):
        if 'deviceSettings' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['deviceSettings']


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
        self._cache = {}
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
                                       os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600),
                               'w') as f:
                    json.dump(token, f)

    @property
    def token(self):
        self._token
    
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

    def _get(self, endpoint, **params):
        params['apikey'] = self._client_id
        query_string = urllib.parse.urlencode(params)
        url = BASE_URL + endpoint + '?' + query_string
        try:
            response = self._lyricApi.get(url, client_id=self._client_id,
                                         client_secret=self._client_secret)
            response.raise_for_status()
            return response.json()
        except TokenUpdated as e:
            _LOGGER.debug("Token Updated Lyric API: %s" % e)
            self._token_saver(e.token)
        except TokenExpiredError as e:
            _LOGGER.warning("Token Expired Lyric API: %s" % e)
            token = self._lyricApi.refresh_token(REFRESH_URL) #, **extra
            self._token_saver(token)
            self._get(endpoint, params)
        except requests.HTTPError as e:
            _LOGGER.error("HTTP Error Lyric API: %s" % e)
            if e.response.status_code == 401:
                token = self._lyricApi.refresh_token(REFRESH_URL) #, **extra
                self._token_saver(token)
        except requests.exceptions.RequestException as e:
            # print("Error Lyric API: %s with data: %s" % (e, data))
            _LOGGER.error("Error Lyric API: %s" % e)

    def _post(self, endpoint, data, **params):
        params['apikey'] = self._client_id
        query_string = urllib.parse.urlencode(params)
        url = BASE_URL + endpoint + '?' + query_string
        try:
            response = self._lyricApi.post(url, json=data, client_id=self._client_id,
                                           client_secret=self._client_secret)
            response.raise_for_status()
            return response.status_code
        except TokenUpdated as e:
            _LOGGER.debug("Token Updated Lyric API: %s" % e)
            self._token_saver(e.token)
        except TokenExpiredError as e:
            _LOGGER.warning("Token Expired Lyric API: %s" % e)
            token = self._lyricApi.refresh_token(REFRESH_URL, **extra)
            self._token_saver(token)
            self._post(endpoint, data, params)
        except requests.exceptions.RequestException as e:
            # print("Error Lyric API: %s with data: %s" % (e, data))
            _LOGGER.error("Error Lyric API: %s with data: %s" % (e, data))

    def _checkCache(self, cache_key):
        if cache_key in self._cache:
            cache = self._cache[cache_key]
        else:
            cache = (None, 0)

        return cache

    def _bust_cache_all(self):
        self._cache = {}

    def _bust_cache(self, cache_key):
        self._cache[cache_key] = (None, 0)

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
            new_value = self._get('locations')
            if new_value:
                self._cache[cache_key] = (new_value, now)
                return new_value
            else:
                self._cache[cache_key] = (value, last_update + 5) # try again in 5 seconds

        return value

    def _user(self, locationId, userId):
        for user in self._users(locationId):
            if user['userID'] == userId:
                return user

    def _users(self, locationId):
        value = self._location(locationId)['users']
        return value

    def _device(self, locationId, deviceId):
        for device in self._devices(locationId):
            if device['deviceID'] == deviceId:
                return device

    def _devices(self, locationId, forceGet=False):
        if forceGet:
            cache_key = 'devices-%s' %locationId
            value, last_update = self._checkCache(cache_key)
            now = time.time()

            if not value or now - last_update > self._cache_ttl:
                new_value = self._get('devices', locationId=locationId)
                if new_value:
                    self._cache[cache_key] = (new_value, now)
                    return new_value
        else:
            if self._locations:
                return self._location(locationId)['devices']
            else:
                return None

        return value

    def _device_type(self, locationId, deviceType, deviceId):
        for device in self._devices_type(deviceType, locationId):
            if device['deviceID'] == deviceId:
                return device

    def _devices_type(self, deviceType, locationId):
        cache_key = 'devices_type-%s_%s' % (locationId, deviceType)
        value, last_update = self._checkCache(cache_key)
        now = time.time()

        if not value or now - last_update > self._cache_ttl:
            value = self._get('devices/' + deviceType, locationId=locationId)
            self._cache[cache_key] = (value, now)

        return value

    @property
    def locations(self):
        if (self._locations):
            return [Location(location['locationID'], self, self._local_time)
                    for location in self._locations]
        else:
            return None
