# -*- coding:utf-8 -*-

import os
import time
import requests
#import json
from requests.compat import json
from requests_oauthlib import OAuth2Session
import urllib.parse

BASE_URL = 'https://api.honeywell.com/v2/'
AUTHORIZATION_BASE_URL = 'https://api.honeywell.com/oauth2/authorize'
TOKEN_URL = 'https://api.honeywell.com/oauth2/token'
REFRESH_URL = TOKEN_URL

class lyricDevice(object):
    def __init__(self, deviceId, locationId, lyric_api, local_time=False):
        self._deviceId = deviceId
        self._locationId = locationId
        self._lyric_api = lyric_api
        self._local_time = local_time

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._repr_name)

    def _set(self, endpoint, data, **params):
        params['locationId'] = self._locationId
        print(self._lyric_api._post(endpoint, data, **params))
        self._lyric_api._bust_cache_all()

    @property
    def id(self):
        return self._deviceId

    @property
    def name(self):
        if 'name' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['name']
        else:
            return self.userDefinedDeviceName

    @property
    def _repr_name(self):
        return self.userDefinedDeviceName

    @property
    def deviceClass(self):
        return self._lyric_api._device(self._locationId, self._deviceId)['deviceClass']

    @property
    def deviceType(self):
        return self._lyric_api._device(self._locationId, self._deviceId)['deviceType']

    @property
    def deviceID(self):
        return self._lyric_api._device(self._locationId, self._deviceId)['deviceID']

    @property
    def userDefinedDeviceName(self):
        return self._lyric_api._device(self._locationId, self._deviceId)['userDefinedDeviceName']

class Location(object):
    # locationID    Integer    Unique LocationID for a user's location.
    # name    String    User-defined name of location
    # streetAddress    String    User-defined street address of location
    # city    String    User-defined city of location
    # state    String    User-defined US State
    # country    String    Country of location
    # zipcode    Integer    User-defined Zip Code of location

    # device.deviceClass    String    Class of Device, currently "Thermostat" or "LeakDetector"
    # device.deviceType    String    Type of device, currently "Thermostat" or "Water Leak Detector"
    # device.deviceID    String    Unique deviceID
    # device.userDefinedDeviceName    String    User-defined device name
    # device.name    String    Name
    # device.units    String    Measurement units for temperature readings. Celcius or Fahrenheit
    # device.indoorTemperature    Decimal    Current indoor temperature reading. Measured in whole numbers for F and half-degree increments for C.
    # device.outdoorTemperature    Decimal    Current outdoor temperature reading. Measured in whole numbers for F and half-degree increments for C.
    # device.allowedModes    Array    Currently allowed mode settings for the Thermostat
    # device.deadband    Decimal    Required distance between heat and cool setpoints in AutoChangeover mode.
    # device.hasDualSetpointStatus    Boolean    Indicates if the thermostat maintains seperate heat and cool setpoints
    # device.minHeatSetpoint    Decimal    Minimum allowed heat setpoint
    # device.maxHeatSetpoint    Decimal    Maximum allowed heat setpoint
    # device.minCoolSetpoint    Decimal    Minimum allowed cool setpoint
    # device.maxCoolSetpoint    Decimal    Maximum allowed cool setpoint
    # device.changeableValues    Object    List of values/settings that can be changed on the thermostat. Used in POST requests.
    # device.smartAway    Object    Settings that will take effect when nobody is home (via Geofencing). Null when reported means smart away is not available.
    # device.indoorHumidity    Decimal    Indoor humidity rating as a percentage
    # device.indoorHumidityStatus    String    Status of humidity sensor. Measured, NotAvailable, or SensorFault.
    # device.isAlive    Boolean    Is the device alive
    # device.isUpgrading    Boolean    Is the device currently running a firmware update true/false
    # device.isProvisioned    Boolean    True if the device has completed provisioning and is communicating with Honeywell servers
    # device.settings    Object    Secondary settings for the device
    # device.settings.homeSetPoints    Object    Listing of current home mode setpoints
    # device.settings.awaySetPoints    Object    Listing of current away mode settings
    # device.settings.hardwareSettings    Object    List of current hardware settings (e.g., screen brightness, volume)
    # device.settings.fan    Object    Shows current available modes and changeable settings for the fan
    # device.settings.fan.allowedModes    Array    Currently available fan settings
    # device.settings.fan.changeableValues    Object    Current fan setting, structure is used in POST change requests
    # device.settings.temperatureMode    Object    Temperature reading and adjusment settings
    # device.settings.temperatureMode.feelsLike    Boolean    Indicates if the 'Feels Like' feature is enabled
    # device.settings.temperatureMode.air    Boolean    Indicates if Adaptive Intelligent Recovery is enabled
    # device.settings.specialMode    Object    Special mode settings
    # device.settings.specialMode.autoChangeoverActive    Boolean    Indicates if Auto mode is active. Not sent if the setting does not exist.
    # device.settings.specialMode.emergencyHeatActive    Boolean    Indicates if Emergency Heat is active and device is capable. Not sent if not enabled on device.
    # device.macID    String    The unique MACID of the device
    # device.scheduleStatus    String    The running status of the schedule.
    # device.allowedTimeIncrements    Integer    Allowed time increments, used when setting the schedule or temporary hold changes. In minutes.
    # device.thermostatVersion    String    Current thermostat firmware version for Water Leak Detector
    # device.waterPresent    Boolean    Is water currently detected
    # device.currentSensorReadings    Object    Object showing current sensor readings
    # device.currentSensorReadings.time    String    Timestamp of current sensor reading
    # device.currentSensorReadings.temperature    Decimal    Temperature reading, always in celcius units.
    # device.currentSensorReadings.humidity    Decimal    Current humidity reading as a percentage
    # device.currentAlarms    Array    Array with individual objects for each current alarm. Contains type of alert and time created.
    # device.lastCheckin    DateTime    Date and timestamp of the last time the device checked-in to Honeywell servers.
    # device.lastdeviceettingUpdatedOn    DateTime    Date and time stamp of the last device setting change request
    # device.batteryRemaining    Integer    Battery life remaining as a percentage
    # device.isRegistered    Boolean    True/false if the device is registered
    # device.hasDeviceCheckedIn    Boolean    True/false if the device has checked-in to Honeywell servers.
    # device.isDeviceOffline    Boolean    True/false if the device is offline.
    # device.firstFailedAttemptTime    DateTime    First failed communication attempt time.
    # device.failedConnectionAttempts    Integer    Number of failed connection attempts
    # device.wifiSignalStrength    Integer    WiFi signal strength in db
    # device.isFirmwareUpdateRequired    Boolean    Does the device require a firmware update
    # device.time    DateTime    Current device time.
    # device.devicesettings    Object    Object containing device settings
    # device.devicesettings.temp    Object    Temperature limit settings for alerts
    # device.devicesettings.humidity    Object    Humidity limit settings for alerts
    # device.devicesettings.userDefinedName    String    User defined device name
    # device.devicesettings.buzzerMuted    Boolean    Buzzer muted true/false
    # device.devicesettings.checkinPeriod    Integer    User set device check-in/reporting period for periodic readings
    # device.devicesettings.currentSensorReadPeriod    Integer    Sensor reading period in minutes
    # device.displayedOutdoorHumidity    Integer    Outdoor humidity value displayed in mobile app
    # device.currentSchedulePeriod    Object    Current schedule period information
    # device.currentSchedulePeriod.day    String    Currently running schedule period day
    # device.currentSchedulePeriod.period    String    Currently running schedule period for the day. Home, Away, Wake or Sleep.
    # device.scheduleCapabilities    Object    Information for schedule capabilities of the device.
    # device.scheduleCapabilities.availableScheduleTypes    Array    List of available scheduling options for the device.
    # device.scheduleCapabilities.schedulableFan    Boolean    Shows if the fan is capable of being scheduled.
    # device.scheduleType    Object    Detail on currently selected schedule type.
    # device.scheduleType.scheduleType    String    Currently selected schedule type. Would follow the values in device.scheduleCapabilities.availableScheduleTypes.
    # device.scheduleType.scheduleSubType    String    Currently selected schedule subtype.

    # user    Array    User information
    # user.userID    Integer    Unique UserID
    # user.username    String    User's username to login, usually an email address
    # user.firstname    String    User's first name
    # user.lastname    String    user last name
    # user.created    Unix Timestamp    Date and time account was created in epoch format
    # user.deleted    Unix Timestamp    Date and time account was deleted, negative number if not deleted
    # user.activated    Boolean    True/false if user has been activated
    # user.connectedHomeAccountExists    Boolean
    # timeZone    String    Time Zone of the location
    # daylightSavingTimeEnabled    Boolean    Is DST enabled for this location
    # geoFences    Array    Shows configuration of user-defined geofences from our application
    # geoFenceEnabled    Boolean    Is geofencing used by the user?

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
    def geoFences(self):
        return self._lyric_api._location(self._locationId)['geoFences']

    @property
    def geoFenceEnabled(self):
        return self._lyric_api._location(self._locationId)['geoFenceEnabled']

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
        return [User(user['userID'], self._locationId, self._lyric_api, self._local_time)
                for user in self._users]

    @property
    def devices(self):
        if 'deviceID' in self._devices[0]:
            devices = []
            for device in self._devices:
                if device['deviceType'] == 'Thermostat':
                    devices.append(Thermostat(device['deviceID'], self._locationId,
                                       self._lyric_api, self._local_time))
                elif device['deviceType'] == 'Water Leak Detector':
                    devices.append(WaterLeakDetector(device['deviceID'], self._locationId,
                                       self._lyric_api, self._local_time))
                else:
                    devices.append(Device(device['deviceID'], self._locationId,
                                       self._lyric_api, self._local_time))
            return devices

    @property
    def thermostats(self):
        if 'deviceID' in self._devices[0]:
            devices = []
            for device in self._devices:
                if device['deviceType'] == 'Thermostat':
                    devices.append(Thermostat(device['deviceID'], self._locationId,
                                       self._lyric_api, self._local_time))
            return devices

    @property
    def waterLeakDetectors(self):
        if 'deviceID' in self._devices[0]:
            devices = []
            for device in self._devices:
                if device['deviceType'] == 'Water Leak Detector':
                    devices.append(WaterLeakDetector(device['deviceID'], self._locationId,
                                       self._lyric_api, self._local_time))
            return devices

class User(object):
    # User information
    # user.userID    Integer    Unique UserID
    # user.username    String    User's username to login, usually an email address
    # user.firstname    String    User's first name
    # user.lastname    String    user last name
    # user.created    Unix Timestamp    Date and time account was created in epoch format
    # user.deleted    Unix Timestamp    Date and time account was deleted, negative number if not deleted
    # user.activated    Boolean    True/false if user has been activated
    # user.connectedHomeAccountExists    Boolean
    def __init__(self, userId, locationId, lyric_api, local_time=False):
        self._locationId = locationId
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
        return self._lyric_api._user(self._locationId, self._userId)['userID']

    @property
    def username(self):
        return self._lyric_api._user(self._locationId, self._userId)['username']

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
    # deviceClass    String    Class of Device, currently "Thermostat" or "LeakDetector"
    # deviceType    String    Type of device, currently "Thermostat" or "Water Leak Detector"
    # deviceID    String    Unique deviceID
    # userDefinedDeviceName    String    User-defined device name
    # name    String    Name
    # units    String    Measurement units for temperature readings. Celcius or Fahrenheit
    # indoorTemperature    Decimal    Current indoor temperature reading. Measured in whole numbers for F and half-degree increments for C.
    # outdoorTemperature    Decimal    Current outdoor temperature reading. Measured in whole numbers for F and half-degree increments for C.
    # allowedModes    Array    Currently allowed mode settings for the Thermostat
    # deadband    Decimal    Required distance between heat and cool setpoints in AutoChangeover mode.
    # hasDualSetpointStatus    Boolean    Indicates if the thermostat maintains seperate heat and cool setpoints
    # minHeatSetpoint    Decimal    Minimum allowed heat setpoint
    # maxHeatSetpoint    Decimal    Maximum allowed heat setpoint
    # minCoolSetpoint    Decimal    Minimum allowed cool setpoint
    # maxCoolSetpoint    Decimal    Maximum allowed cool setpoint
    # changeableValues    Object    List of values/settings that can be changed on the thermostat. Used in POST requests.
    # changeableValues.mode    String    Current running mode. Will match values in allowedModes.
    # changeableValues.heatSetpoint    Integer    Current heat setpoint.
    # changeableValues.coolSetpoint    Integer    Current cool setpoint.
    # changeableValues.thermostatSetpointStatus    String    Current status of setpoint. NoHold means running schedule. TemporaryHold means holding current temp until nextPeriodTime. PermanentHold means holding current setpoint until next end-user action.
    # changeableValues.nextPeriodTime    String    Signifies time of next schedule change, or time when any temporary hold expires. 00:00:00-23:45:00
    # changeableValues.endHeatSetpoint    Integer
    # changeableValues.endCoolSetpoint    Integer
    # changeableValues.heatCoolMode    String    Signifies current running mode, usually used to tell last running state when Auto mode is enabled and active.
    # operationStatus    Object    Details around operation status of the equipment.
    # operationStatus.mode    String    Current running (relay status) of the equipment.
    # operationStatus.fanRequest    Boolean    Current running (relay status) of the fan.
    # operationStatus.circulationFanRequest    Boolean    Current running (relay status) of the fan circulate mode.
    # smartAway    Object    Settings that will take effect when nobody is home (via Geofencing). Null when reported means smart away is not available.
    # indoorHumidity    Decimal    Indoor humidity rating as a percentage
    # indoorHumidityStatus    String    Status of humidity sensor. Measured, NotAvailable, or SensorFault.
    # isAlive    Boolean    Is the device alive
    # isUpgrading    Boolean    Is the device currently running a firmware update true/false
    # isProvisioned    Boolean    True if the device has completed provisioning and is communicating with Honeywell servers
    # settings    Object    Secondary settings for the device
    # settings.homeSetPoints    Object    Listing of current home mode setpoints
    # settings.awaySetPoints    Object    Listing of current away mode settings
    # settings.hardwareSettings    Object    List of current hardware settings (e.g., screen brightness, volume)
    # settings.fan    Object    Shows current available modes and changeable settings for the fan
    # settings.fan.allowedModes    Array    Currently available fan settings
    # settings.fan.changeableValues    Object    Current fan setting, structure is used in POST change requests
    # settings.temperatureMode    Object    Temperature reading and adjusment settings
    # settings.temperatureMode.feelsLike    Boolean    Indicates if the 'Feels Like' feature is enabled
    # settings.temperatureMode.air    Boolean    Indicates if Adaptive Intelligent Recovery is enabled
    # settings.specialMode    Object    Special mode settings
    # settings.specialMode.autoChangeoverActive    Boolean    Indicates if Auto mode is active. Not sent if the setting does not exist.
    # settings.specialMode.emergencyHeatActive    Boolean    Indicates if Emergency Heat is active and device is capable. Not sent if not enabled on
    # macID    String    The unique MACID of the device
    # scheduleStatus    String    The running status of the schedule.
    # allowedTimeIncrements    Integer    Allowed time increments, used when setting the schedule or temporary hold changes. In minutes.
    # thermostatVersion    String    Current thermostat firmware version for Water Leak Detector
    # isRegistered    Boolean    True/false if the device is registered
    # devicesettings    Object    Object containing device settings
    # displayedOutdoorHumidity    Integer    Outdoor humidity value displayed in mobile app
    # currentSchedulePeriod    Object    Current schedule period information
    # currentSchedulePeriod.day    String    Currently running schedule period day
    # currentSchedulePeriod.period    String    Currently running schedule period for the day. Home, Away, Wake or Sleep.
    # scheduleCapabilities    Object    Information for schedule capabilities of the
    # scheduleCapabilities.availableScheduleTypes    Array    List of available scheduling options for the
    # scheduleCapabilities.schedulableFan    Boolean    Shows if the fan is capable of being scheduled.
    # scheduleType    Object    Detail on currently selected schedule type.
    # scheduleType.scheduleType    String    Currently selected schedule type. Would follow the values in scheduleCapabilities.availableScheduleTypes.
    # scheduleType.scheduleSubType    String    Currently selected schedule subtype.

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

        if 'AutoChangeover' in self.changeableValues:
            if AutoChangeover is None:
                AutoChangeover = self.changeableValues['AutoChangeover']

        data = {
            'mode': mode,
            'heatSetpoint': heatSetpoint,
            'coolSetpoint': coolSetpoint
        }

        if 'thermostatSetpointStatus' in self.changeableValues:
            data['thermostatSetpointStatus'] = thermostatSetpointStatus
        if 'AutoChangeover' in self.changeableValues:
            data['AutoChangeover'] = AutoChangeover
        if nextPeriodTime is not None:
            data['nextPeriodTime'] = nextPeriodTime

        self._set('devices/thermostats/' + self._deviceId, data=data)

    @property
    def away(self):
        if self._lyric_api._location(self._locationId)['geoFenceEnabled']:
            return (self._lyric_api._location(self._locationId)['geoFences'][0]['geoOccupancy']['withinFence'] == 0)
    
    @property
    def vacationHold(self):
        return self._lyric_api._device(self._locationId, self._deviceId)['vacationHold']['enabled']

    @property
    def where(self):
        return self._lyric_api._location(self._locationId)['name']

    @property
    def units(self):
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
    def temperatureSetpoint(self, setpoint, mode=None):
        if mode is None:
            if setpoint < self.indoorTemperature and self.can_cool:
                mode = 'Cool';
            else:
                mode = 'Heat';

        if mode=='Cool':
            self.updateThermostat(mode=mode, coolSetpoint=setpoint, thermostatSetpointStatus='TemporaryHold')

        if mode=='Heat':
            self.updateThermostat(mode=mode, heatSetpoint=setpoint, thermostatSetpointStatus='TemporaryHold')

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
        if ('settings' in self._lyric_api._device(self._locationId, self._deviceId)) & ('fan' in self.settings):
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
        if 'scheduleType' in self._lyric_api._device(self._locationId, self._deviceId):
            return self._lyric_api._device(self._locationId, self._deviceId)['scheduleType']['scheduleType']

    @property
    def scheduleSubType(self):
        if ('scheduleType' in self._lyric_api._device(self._locationId, self._deviceId)) & ('scheduleSubType' in self._lyric_api._device(self._locationId, self._deviceId)['scheduleType']):
            return self._lyric_api._device(self._locationId, self._deviceId)['scheduleType']['scheduleSubType']

    # #changeableValues    Object    List of values/settings that can be changed on the thermostat. Used in POST requests.
    # changeableValues.mode    String    Current running mode. Will match values in allowedModes.
    # changeableValues.heatSetpoint    Integer    Current heat setpoint.
    # changeableValues.coolSetpoint    Integer    Current cool setpoint.
    # changeableValues.thermostatSetpointStatus    String    Current status of setpoint. NoHold means running schedule. TemporaryHold means holding current temp until nextPeriodTime. PermanentHold means holding current setpoint until next end-user action.
    # changeableValues.nextPeriodTime    String    Signifies time of next schedule change, or time when any temporary hold expires. 00:00:00-23:45:00
    # changeableValues.endHeatSetpoint    Integer
    # changeableValues.endCoolSetpoint    Integer
    # changeableValues.heatCoolMode    String    Signifies current running mode, usually used to tell last running state when Auto mode is enabled and active.
    #
    # #operationStatus    Object    Details around operation status of the equipment.
    # operationStatus.mode    String    Current running (relay status) of the equipment.
    # operationStatus.fanRequest    Boolean    Current running (relay status) of the fan.
    # operationStatus.circulationFanRequest    Boolean    Current running (relay status) of the fan circulate mode.
    #
    # #settings    Object    Secondary settings for the device
    # settings.homeSetPoints    Object    Listing of current home mode setpoints
    # settings.awaySetPoints    Object    Listing of current away mode settings
    # settings.hardwareSettings    Object    List of current hardware settings (e.g., screen brightness, volume)
    # settings.fan    Object    Shows current available modes and changeable settings for the fan
    # settings.fan.allowedModes    Array    Currently available fan settings
    # settings.fan.changeableValues    Object    Current fan setting, structure is used in POST change requests
    # settings.temperatureMode    Object    Temperature reading and adjusment settings
    # settings.temperatureMode.feelsLike    Boolean    Indicates if the 'Feels Like' feature is enabled
    # settings.temperatureMode.air    Boolean    Indicates if Adaptive Intelligent Recovery is enabled
    # settings.specialMode    Object    Special mode settings
    # settings.specialMode.autoChangeoverActive    Boolean    Indicates if Auto mode is active. Not sent if the setting does not exist.
    # settings.specialMode.emergencyHeatActive    Boolean    Indicates if Emergency Heat is active and device is capable. Not sent if not enabled on
    #
    # #currentSchedulePeriod    Object    Current schedule period information
    # currentSchedulePeriod.day    String    Currently running schedule period day
    # currentSchedulePeriod.period    String    Currently running schedule period for the day. Home, Away, Wake or Sleep.
    #
    # #scheduleCapabilities    Object    Information for schedule capabilities of the
    # scheduleCapabilities.availableScheduleTypes    Array    List of available scheduling options for the
    # scheduleCapabilities.schedulableFan    Boolean    Shows if the fan is capable of being scheduled.
    #
    # #scheduleType    Object    Detail on currently selected schedule type.
    # scheduleType.scheduleType    String    Currently selected schedule type. Would follow the values in scheduleCapabilities.availableScheduleTypes.
    # scheduleType.scheduleSubType    String    Currently selected schedule subtype.

class WaterLeakDetector(lyricDevice):

    # deviceClass    String    Class of Device, currently "Thermostat" or "LeakDetector"
    # deviceType    String    Type of device, currently "Thermostat" or "Water Leak Detector"
    # deviceID    String    Unique deviceID
    # waterPresent    Boolean    Is water currently detected
    # currentSensorReadings    Object    Object showing current sensor readings
    # currentSensorReadings.time    String    Timestamp of current sensor reading
    # currentSensorReadings.temperature    Decimal    Temperature reading, always in celcius units.
    # currentSensorReadings.humidity    Decimal    Current humidity reading as a percentage
    # currentAlarms    Array    Array with individual objects for each current alarm. Contains type of alert and time created.
    # lastCheckin    DateTime    Date and timestamp of the last time the device checked-in to Honeywell servers.
    # lastDeviceSettingUpdatedOn    DateTime    Date and time stamp of the last device setting change request
    # batteryRemaining    Integer    Battery life remaining as a percentage
    # isRegistered    Boolean    True/false if the device is registered
    # hasDeviceCheckedIn    Boolean    True/false if the device has checked-in to Honeywell servers.
    # isDeviceOffline    Boolean    True/false if the device is offline.
    # firstFailedAttemptTime    DateTime
    # failedConnectionAttempts    Integer
    # wifiSignalStrength    Integer    WiFi signal strength in db
    # isFirmwareUpdateRequired    Boolean    Does the device require a firmware update
    # time    DateTime
    # deviceSettings    Object    Object containing device settings
    # deviceSettings.temp    Object    Temperature limit settings for alerts
    # deviceSettings.humidity    Object    Humidity limit settings for alerts
    # deviceSettings.userDefinedName    String    User defined device name
    # deviceSettings.buzzerMuted    Boolean    Buzzer muted true/false
    # deviceSettings.checkinPeriod    Integer    User set device check-in/reporting period for periodic readings
    # deviceSettings.currentSensorReadPeriod    Integer    Sensor reading period in minutes

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

    # #currentSensorReadings    Object    Object showing current sensor readings
    # currentSensorReadings.time    String    Timestamp of current sensor reading
    # currentSensorReadings.temperature    Decimal    Temperature reading, always in celcius units.
    # currentSensorReadings.humidity    Decimal    Current humidity reading as a percentage

    # #deviceSettings    Object    Object containing device settings
    # deviceSettings.temp    Object    Temperature limit settings for alerts
    # deviceSettings.humidity    Object    Humidity limit settings for alerts
    # deviceSettings.userDefinedName    String    User defined device name
    # deviceSettings.buzzerMuted    Boolean    Buzzer muted true/false
    # deviceSettings.checkinPeriod    Integer    User set device check-in/reporting period for periodic readings
    # deviceSettings.currentSensorReadPeriod    Integer    Sensor reading period in minutes

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
            value = self._get('locations')
            self._cache[cache_key] = (value, now)

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
                value = self._get('devices', locationId=locationId)
                self._cache[cache_key] = (value, now)
        else:
            value = self._location(locationId)['devices']

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
        return [Location(location['locationID'], self, self._local_time)
                for location in self._locations]