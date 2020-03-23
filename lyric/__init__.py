#  -*- coding:utf-8 -*-

"""Library to restfully handle Honeywell Home Assistant API calls."""

import logging
import os
import time
import urllib.parse

import requests
from requests.auth import HTTPBasicAuth
from requests.compat import json
from requests_oauthlib import OAuth2Session

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://api.honeywell.com/v2/"
AUTHORIZATION_BASE_URL = "https://api.honeywell.com/oauth2/authorize"
TOKEN_URL = "https://api.honeywell.com/oauth2/token"
REFRESH_URL = TOKEN_URL


class lyricDevice(object):
    """Class definition for Lyric devices."""

    def __init__(self, deviceId, location, lyric_api, local_time=False):
        """Intializes and configures lyricDevice class."""

        self._deviceId = deviceId
        self._location = location
        self._locationId = self._location.locationId
        self._lyric_api = lyric_api
        self._local_time = local_time

    def __repr__(self):
        """Debug string representation."""

        return "<%s: %s>" % (self.__class__.__name__, self._repr_name)

    def _set(self, endpoint, data, **params):
        """Setter Magic Method."""

        params["locationId"] = self._location.locationId
        print(self._lyric_api._post(endpoint, data, **params))
        self._lyric_api._bust_cache_all()

    @property
    def id(self):
        """Return id."""

        return self._deviceId

    @property
    def device(self):
        """Return device."""

        return self._lyric_api._device(self._locationId, self._deviceId)

    @property
    def name(self):
        """Return Name."""

        if "name" in self.device:
            return self.device.get("name")
        else:
            return self.userDefinedDeviceName

    @property
    def _repr_name(self):
        """Return User Defined Name."""

        return self.userDefinedDeviceName

    @property
    def deviceClass(self):
        """Return class."""

        return self.device.get("deviceClass")

    @property
    def deviceType(self):
        """Return Device Type."""

        return self.device.get("deviceType")

    @property
    def deviceID(self):
        """Return Device ID."""

        return self.device.get("deviceID")

    @property
    def userDefinedDeviceName(self):
        """Return User Defined Name."""

        return self.device.get("userDefinedDeviceName")


class Location(object):
    """Store Location Information."""

    def __init__(self, locationId, lyric_api, local_time=False):
        """Initialize and setup Location class."""

        self._locationId = locationId
        self._lyric_api = lyric_api
        self._local_time = local_time

    def __repr__(self):
        """Print helpful debug information."""

        return "<%s: %s>" % (self.__class__.__name__, self._repr_name)

    @property
    def id(self):
        """Return id."""

        return self._locationId

    @property
    def locationId(self):
        """Return Location ID."""

        return self._locationId

    @property
    def location(self):
        """Return Location."""

        return self._lyric_api._location(self._locationId)

    @property
    def locationID(self):
        """Return Location ID."""

        return self.location.get("locationID")

    @property
    def name(self):
        """Return name."""

        return self.location.get("name")

    @property
    def _repr_name(self):
        """Return name."""

        return self.name

    @property
    def streetAddress(self):
        """Return street address."""

        return self.location.get("streetAddress")

    @property
    def city(self):
        """Return city."""

        return self.location.get("city")

    @property
    def state(self):
        """Return state."""

        return self.location.get("state")

    @property
    def country(self):
        """Return country."""

        return self.location.get("country")

    @property
    def zipcode(self):
        """Return zipcode."""

        return self.location.get("zipcode")

    @property
    def timeZone(self):
        """Return timezone."""

        return self.location.get("timeZone")

    @property
    def daylightSavingTimeEnabled(self):
        """Return daylight savings time enabled."""

        return self.location.get("daylightSavingTimeEnabled")

    @property
    def geoFenceEnabled(self):
        """Return geofencing enabled."""

        return self.location.get("geoFenceEnabled")

    @property
    def geoFences(self):
        """Return geofences."""

        return self.location.get("geoFences")

    @property
    def geoFence(self, index=0):
        """Return specific geofence."""

        if self.geoFences and len(self.geoFences) >= index + 1:
            return self.geoFences[index]

    @property
    def geoOccupancy(self):
        """Return geo Occupancy."""

        if "geoOccupancy" in self.geoFence:
            return self.geoFence.get("geoOccupancy")

    @property
    def withInFence(self):
        """Return user in fence."""

        if "withinFence" in self.geoOccupancy:
            return self.geoOccupancy.get("withinFence")

    @property
    def outsideFence(self):
        """Return user out of fence."""

        if "outsideFence" in self.geoOccupancy:
            return self.geoOccupancy.get("outsideFence")

    @property
    def _users(self):
        """Return Users."""

        return self._lyric_api._users(self._locationId)

    @property
    def _devices(self, forceGet=False):
        """Return devices."""

        return self._lyric_api._devices(self._locationId, forceGet)

    @property
    def _thermostats(self):
        """Return thermostats."""

        return self._lyric_api._devices_type("thermostats", self._locationId)

    @property
    def _waterLeakDetectors(self):
        """Return water leak dectectors."""

        return self._lyric_api._devices_type("waterLeakDetectors", self._locationId)

    @property
    def users(self):
        """Return Users."""

        return [
            User(user.get("userID"), self, self._lyric_api, self._local_time)
            for user in self._users
        ]

    @property
    def devices(self):
        """Return devices."""

        devices = []
        for device in self._devices:
            if device["deviceType"] == "Thermostat":
                devices.append(
                    Thermostat(
                        device["deviceID"], self, self._lyric_api, self._local_time
                    )
                )
            elif device["deviceType"] == "Water Leak Detector":
                devices.append(
                    WaterLeakDetector(
                        device["deviceID"], self, self._lyric_api, self._local_time
                    )
                )
            else:
                devices.append(
                    Device(device["deviceID"], self, self._lyric_api, self._local_time)
                )
        return devices

    @property
    def thermostats(self):
        """Return thermostats."""

        thermostats = []
        for device in self._devices:
            if device["deviceType"] == "Thermostat":
                thermostats.append(
                    Thermostat(
                        device["deviceID"], self, self._lyric_api, self._local_time
                    )
                )
        return thermostats

    @property
    def waterLeakDetectors(self):
        """Return water leak detectors."""

        waterLeakDetectors = []
        for device in self._devices:
            if device["deviceType"] == "Water Leak Detector":
                waterLeakDetectors.append(
                    WaterLeakDetector(
                        device["deviceID"], self, self._lyric_api, self._local_time
                    )
                )
        return waterLeakDetectors


class User(object):
    """Class definition for User object."""

    def __init__(self, userId, location, lyric_api, local_time=False):
        """Configure User object."""

        self._location = location
        self._locationId = self._location.locationId
        self._userId = userId
        self._lyric_api = lyric_api
        self._local_time = local_time

    def __repr__(self):
        """Print out helpful debug."""

        return "<%s: %s>" % (self.__class__.__name__, self._repr_name)

    @property
    def id(self):
        """Return ID."""

        return self._userId

    @property
    def name(self):
        """Return name."""

        return self.username

    @property
    def _repr_name(self):
        """Return name."""

        return self.username

    @property
    def user(self):
        """Return user."""

        return self._lyric_api._user(self._locationId, self._userId)

    @property
    def userID(self):
        """Return userID."""

        return self.user.get("userID")

    @property
    def username(self):
        """Return username."""

        return self.user.get("username")

    @property
    def firstname(self):
        """Return firstname."""

        return self.user.get("firstname")

    @property
    def lastname(self):
        """Return lastname."""

        return self.user.get("lastname")

    @property
    def created(self):
        """Return created."""

        return self.user.get("created")

    @property
    def deleted(self):
        """Return deleted."""

        return self.user.get("deleted")

    @property
    def activated(self):
        """Return activated."""

        return self.user.get("activated")

    @property
    def connectedHomeAccountExists(self):
        """Return connected home account exists."""

        return self.user.get("connectedHomeAccountExists")


class Device(lyricDevice):
    """Device class."""

    @property
    def unknownType(self):
        """Return unknown type."""

        return True

    def properties(self):
        """Return properties."""

        return self.device


class Thermostat(lyricDevice):
    """Thermostat Class."""

    def updateThermostat(
        self,
        mode=None,
        heatSetpoint=None,
        coolSetpoint=None,
        AutoChangeover=None,
        thermostatSetpointStatus=None,
        nextPeriodTime=None,
    ):
        """Update Themostate."""

        if mode is None:
            mode = self.operationMode
        if heatSetpoint is None:
            heatSetpoint = self.heatSetpoint
        if coolSetpoint is None:
            coolSetpoint = self.coolSetpoint

        if "thermostatSetpointStatus" in self.changeableValues:
            if thermostatSetpointStatus is None:
                thermostatSetpointStatus = self.thermostatSetpointStatus

        if "autoChangeoverActive" in self.changeableValues:
            if AutoChangeover is None:
                AutoChangeover = self.changeableValues.get("autoChangeoverActive")

        data = {
            "mode": mode,
            "heatSetpoint": heatSetpoint,
            "coolSetpoint": coolSetpoint,
        }

        if "thermostatSetpointStatus" in self.changeableValues:
            data["thermostatSetpointStatus"] = thermostatSetpointStatus
        if "autoChangeoverActive" in self.changeableValues:
            data["autoChangeoverActive"] = AutoChangeover
        if nextPeriodTime is not None:
            data["nextPeriodTime"] = nextPeriodTime

        self._set("devices/thermostats/" + self._deviceId, data=data)

    def updateFan(self, mode):
        """Update Fan."""

        if mode is None:
            mode = self.fanMode

        self._set("devices/thermostats/" + self._deviceId + "/fan", data={"mode": mode})

    @property
    def away(self):
        """Get away status."""

        if self.scheduleType == "Geofence":
            if self._location.geoFenceEnabled:
                return self._location.withInFence == 0
        elif self.scheduleType == "Timed" and self.scheduleSubType == "NA":
            # North America
            return self.currentSchedulePeriod.get("period") == "Away"
        elif self.scheduleType == "Timed" and self.scheduleSubType == "EMEA":
            # Europe, Middle-East, Africa
            return self.currentSchedulePeriod.get("period") == "P3"

    @property
    def vacationHold(self):
        """Return vacation hold."""

        return self.device.get("vacationHold").get("enabled")

    @property
    def where(self):
        """Return location."""

        return self._location.name

    @property
    def units(self):
        """Return units."""

        return self.device.get("units")

    @property
    def indoorTemperature(self):
        """Return indoor temperature."""

        return self.device.get("indoorTemperature")

    @property
    def heatSetpoint(self):
        """Return Heat Setpoint."""

        return self.changeableValues.get("heatSetpoint")

    @property
    def coolSetpoint(self):
        """Return Cool Setpoint."""

        return self.changeableValues.get("coolSetpoint")

    @property
    def thermostatSetpointStatus(self):
        """Return thermostat Set Point."""

        return self.changeableValues.get("thermostatSetpointStatus")

    @thermostatSetpointStatus.setter
    def thermostatSetpointStatus(self, thermostatSetpointStatus):
        """Set Thermostat."""

        self.updateThermostat(thermostatSetpointStatus=thermostatSetpointStatus)

    def thermostatSetpointHoldUntil(
        self, nextPeriodTime, heatSetpoint=None, coolSetpoint=None
    ):
        """Set thermostate hold until point."""

        if nextPeriodTime is None:
            raise ValueError("nextPeriodTime is required")
        self.updateThermostat(
            heatSetpoint=heatSetpoint,
            coolSetpoint=coolSetpoint,
            thermostatSetpointStatus="HoldUntil",
            nextPeriodTime=nextPeriodTime,
        )

    @property
    def nextPeriodTime(self):
        """Return next period time."""

        return self.changeableValues.get("nextPeriodTime")

    @property
    def auto_changeover(self):
        """Return auto change over."""

        return self.changeableValues.get("AutoChangeover")

    @property
    def operationMode(self):
        """Return operation mode."""

        return self.changeableValues.get("mode")

    @operationMode.setter
    def operationMode(self, mode):
        """Set operation mode."""

        self.updateThermostat(mode=mode)

    @property
    def temperatureSetpoint(self):
        """Return temperature set point."""

        if self.operationMode == "Heat":
            return self.changeableValues.get("heatSetpoint")
        else:
            return self.changeableValues.get("coolSetpoint")

    @temperatureSetpoint.setter
    def temperatureSetpoint(self, setpoint):
        """Set temperature set point."""

        if self.thermostatSetpointStatus in ["NoHold", "HoldUntil"]:
            thermostatSetpointStatus = "TemporaryHold"
        else:
            thermostatSetpointStatus = self.thermostatSetpointStatus

        if isinstance(setpoint, tuple):
            self.updateThermostat(
                coolSetpoint=setpoint[0],
                heatSetpoint=setpoint[1],
                thermostatSetpointStatus=thermostatSetpointStatus,
            )
        elif self.operationMode == "Cool":
            self.updateThermostat(
                coolSetpoint=setpoint, thermostatSetpointStatus=thermostatSetpointStatus
            )
        elif self.operationMode == "Heat":
            self.updateThermostat(
                heatSetpoint=setpoint, thermostatSetpointStatus=thermostatSetpointStatus
            )

    @property
    def can_heat(self):
        """Return can heat."""

        return "Heat" in self.allowedModes

    @property
    def can_cool(self):
        """Return can cool."""

        return "Cool" in self.allowedModes

    @property
    def has_fan(self):
        """Return has fan."""

        return True

    @property
    def outdoorTemperature(self):
        """Return outdoor temperature."""

        return self.device.get("outdoorTemperature")

    @property
    def allowedModes(self):
        """Return allowed modes."""

        return self.device.get("allowedModes")

    @property
    def deadband(self):
        """Return deadband."""

        return self.device.get("deadband")

    @property
    def hasDualSetpointStatus(self):
        """Return has dual set points."""

        return self.device.get("hasDualSetpointStatus")

    @property
    def minHeatSetpoint(self):
        """Return min heat set point."""

        return self.device.get("minHeatSetpoint")

    @property
    def maxHeatSetpoint(self):
        """Return max heat setpoint."""

        return self.device.get("maxHeatSetpoint")

    @property
    def minCoolSetpoint(self):
        """Return min cool set point."""

        return self.device.get("minCoolSetpoint")

    @property
    def maxCoolSetpoint(self):
        """Return max cool setpoint."""

        return self.device.get("maxCoolSetpoint")

    @property
    def maxSetpoint(self):
        """Return max setpoint."""

        if self.can_heat:
            return self.maxHeatSetpoint
        else:
            return self.maxCoolSetpoint

    @property
    def minSetpoint(self):
        """Return min setpoint."""

        if self.can_cool:
            return self.minCoolSetpoint
        else:
            return self.minHeatSetpoint

    @property
    def changeableValues(self):
        """Return changeable values."""

        return self.device.get("changeableValues")

    @property
    def operationStatus(self):
        """Return operation status."""

        return self.device.get("operationStatus")

    @property
    def smartAway(self):
        """Return smart away."""

        return self.device.get("smartAway")

    @property
    def indoorHumidity(self):
        """Return indoor humidity."""

        return self.device.get("indoorHumidity")

    @property
    def indoorHumidityStatus(self):
        """Return indoor humidity status."""

        return self.device.get("indoorHumidityStatus")

    @property
    def isAlive(self):
        """Return is alive."""

        return self.device.get("isAlive")

    @property
    def isUpgrading(self):
        """Return is upgrading."""

        return self.device.get("isUpgrading")

    @property
    def isProvisioned(self):
        """Return is provisioned."""

        return self.device.get("isProvisioned")

    @property
    def settings(self):
        """Return settings."""

        return self.device.get("settings")

    @property
    def fanMode(self):
        """Return fan mode."""

        if (
            self.settings
            and "fan" in self.settings
            and "changeableValues" in self.settings.get("fan")
        ):
            return self.settings.get("fan").get("changeableValues").get("mode")

    @fanMode.setter
    def fanMode(self, mode):
        """Set fan mode."""

        self.updateFan(mode)

    @property
    def macID(self):
        """Return MAC id."""

        return self.device.get("macID")

    @property
    def scheduleStatus(self):
        """Return schedule status."""

        return self.device.get("scheduleStatus")

    @property
    def allowedTimeIncrements(self):
        """Return allowed time increment."""

        return self.device.get("allowedTimeIncrements")

    @property
    def thermostatVersion(self):
        """Return thermostat version."""

        return self.device.get("thermostatVersion")

    @property
    def isRegistered(self):
        """Return is registered."""

        return self.device.get("isRegistered")

    @property
    def devicesettings(self):
        """Return device settings."""

        return self.device.get("devicesettings")

    @property
    def displayedOutdoorHumidity(self):
        """Return outdoor humidity."""

        return self.device.get("displayedOutdoorHumidity")

    @property
    def currentSchedulePeriod(self):
        """Return scheduled period."""

        return self.device.get("currentSchedulePeriod")

    @property
    def scheduleCapabilities(self):
        """Return schedule capabilities."""

        return self.device.get("scheduleCapabilities")

    @property
    def scheduleType(self):
        """Return schedule type."""

        if (
            "scheduleType" in self.device
            and "scheduleType" in self.device["scheduleType"]
        ):
            return self.device.get("scheduleType").get("scheduleType")
        elif "schedule" in self.device and "scheduleType" in self.device["schedule"]:
            return self.device.get("schedule").get("scheduleType")

    @property
    def scheduleSubType(self):
        """Return schedule subtype."""

        return self.device.get("scheduleType").get("scheduleSubType")


class WaterLeakDetector(lyricDevice):
    """Water Leak Detector Class."""

    @property
    def waterPresent(self):
        """Return water present."""

        return self.device.get("waterPresent")

    @property
    def currentSensorReadings(self):
        """Return current sensor reading."""

        return self.device.get("currentSensorReadings")

    @property
    def currentAlarms(self):
        """Return current alarms."""

        return self.device.get("currentAlarms")

    @property
    def lastCheckin(self):
        """Return last checkin."""

        return self.device.get("lastCheckin")

    @property
    def lastDeviceSettingUpdatedOn(self):
        """Return last device setting update on."""

        return self.device.get("lastDeviceSettingUpdatedOn")

    @property
    def batteryRemaining(self):
        """Return battery remaining."""

        return self.device.get("batteryRemaining")

    @property
    def isRegistered(self):
        """Return is registered."""

        return self.device.get("isRegistered")

    @property
    def hasDeviceCheckedIn(self):
        """Return has device checked in."""

        return self.device.get("hasDeviceCheckedIn")

    @property
    def isDeviceOffline(self):
        """Return is device offline."""

        return self.device.get("isDeviceOffline")

    @property
    def firstFailedAttemptTime(self):
        """Return first failed attempt time."""

        return self.device.get("firstFailedAttemptTime")

    @property
    def failedConnectionAttempts(self):
        """Return failed connection attempts."""

        return self.device.get("failedConnectionAttempts")

    @property
    def wifiSignalStrength(self):
        """Return wifi signal strength."""

        return self.device.get("wifiSignalStrength")

    @property
    def isFirmwareUpdateRequired(self):
        """Return is firmware update required."""

        return self.device.get("isFirmwareUpdateRequired")

    @property
    def time(self):
        """Return time."""

        return self.device.get("time")

    @property
    def deviceSettings(self):
        """Return device settings."""

        return self.device.get("deviceSettings")


class Lyric(object):
    """Lyric Class."""

    def __init__(
        self,
        client_id,
        client_secret,
        cache_ttl=270,
        user_agent="python-lyric/0.1",
        token=None,
        token_cache_file=None,
        local_time=False,
        app_name=None,
        redirect_uri=None,
    ):
        """Intializes and configures the Lyric class."""

        self._client_id = client_id
        self._client_secret = client_secret
        self._app_name = app_name
        self._redirect_uri = redirect_uri
        self._token = token
        self._token_cache_file = token_cache_file
        self._cache_ttl = cache_ttl
        self._cache = {}
        self._local_time = local_time
        self._user_agent = user_agent

        if token is None and token_cache_file is None and redirect_uri is None:
            print(
                "You need to supply a token or a cached token file,"
                "or define a redirect uri"
            )
        else:
            self._lyricAuth()

    def __enter__(self):
        """Return Self."""

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Return exit."""

        return False

    def _token_saver(self, token):
        """Token saver."""

        self._token = token
        if self._token_cache_file is not None:
            with os.fdopen(
                os.open(
                    self._token_cache_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600
                ),
                "w",
            ) as f:
                return json.dump(token, f)

    @property
    def token(self):
        """Return token."""

        return self._token

    @property
    def authorized(self):
        """Return authorized."""

        return self._lyricApi.authorized

    @property
    def getauthorize_url(self):
        """Return session."""

        self._lyricApi = OAuth2Session(
            self._client_id,
            redirect_uri=self._redirect_uri,
            auto_refresh_url=REFRESH_URL,
            token_updater=self._token_saver,
        )

        authorization_url, state = self._lyricApi.authorization_url(
            AUTHORIZATION_BASE_URL, app=self._app_name
        )

        return authorization_url

    def authorization_response(self, authorization_response):
        """Get authorized response."""

        auth = HTTPBasicAuth(self._client_id, self._client_secret)
        headers = {"Accept": "application/json"}

        token = self._lyricApi.fetch_token(
            TOKEN_URL,
            headers=headers,
            auth=auth,
            authorization_response=authorization_response,
        )

        self._token_saver(token)

    def authorization_code(self, code, state):
        """Return authorization status."""

        auth = HTTPBasicAuth(self._client_id, self._client_secret)
        headers = {"Accept": "application/json"}

        token = self._lyricApi.fetch_token(
            TOKEN_URL, headers=headers, auth=auth, code=code, state=state
        )

        self._token_saver(token)

    def _lyricAuth(self):
        """Get lyric authorization."""

        if (
            self._token_cache_file is not None
            and self._token is None
            and os.path.exists(self._token_cache_file)
        ):
            with open(self._token_cache_file, "r") as f:
                self._token = json.load(f)

        if self._token is not None:
            # force token refresh
            self._token["expires_at"] = time.time() - 10
            self._token["expires_in"] = "-30"

            self._lyricApi = OAuth2Session(
                self._client_id,
                token=self._token,
                auto_refresh_url=REFRESH_URL,
                token_updater=self._token_saver,
            )

    def _lyricReauth(self):
        """Lyric reauth."""

        if (
            self._token_cache_file is not None
            and self._token is None
            and os.path.exists(self._token_cache_file)
        ):
            with open(self._token_cache_file, "r") as f:
                self._token = json.load(f)

        if self._token is not None:
            auth = HTTPBasicAuth(self._client_id, self._client_secret)
            headers = {"Accept": "application/json"}

            self._lyricApi = OAuth2Session(
                self._client_id,
                token=self._token,
                auto_refresh_url=REFRESH_URL,
                token_updater=self._token_saver,
            )

            token = self._lyricApi.refresh_token(
                REFRESH_URL,
                refresh_token=self._token.get("refresh_token"),
                headers=headers,
                auth=auth,
            )
            self._token_saver(token)

    def _get(self, endpoint, **params):
        """Lyric get request method."""

        params["apikey"] = self._client_id
        query_string = urllib.parse.urlencode(params)
        url = BASE_URL + endpoint + "?" + query_string
        try:
            response = self._lyricApi.get(
                url, client_id=self._client_id, client_secret=self._client_secret
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            _LOGGER.error("HTTP Error Lyric API: %s" % e)
            if e.response.status_code == 401:
                self._lyricReauth()
        except requests.exceptions.RequestException as e:
            # print("Error Lyric API: %s with data: %s" % (e, data))
            _LOGGER.error("Error Lyric API: %s" % e)

    def _post(self, endpoint, data, **params):
        """Lyric post request method."""

        params["apikey"] = self._client_id
        query_string = urllib.parse.urlencode(params)
        url = BASE_URL + endpoint + "?" + query_string
        try:
            response = self._lyricApi.post(
                url,
                json=data,
                client_id=self._client_id,
                client_secret=self._client_secret,
            )
            response.raise_for_status()
            return response.status_code
        except requests.HTTPError as e:
            _LOGGER.error("HTTP Error Lyric API: %s" % e)
            if e.response.status_code == 401:
                self._lyricReauth()
        except requests.exceptions.RequestException as e:
            # print("Error Lyric API: %s with data: %s" % (e, data))
            _LOGGER.error("Error Lyric API: %s with data: %s" % (e, data))

    def _checkCache(self, cache_key):
        """Check cache status."""

        if cache_key in self._cache:
            cache = self._cache[cache_key]
        else:
            cache = (None, 0)

        return cache

    def _bust_cache_all(self):
        """Destroy Cache."""

        self._cache = {}

    def _bust_cache(self, cache_key):
        """Destroy specific cache entry."""

        self._cache[cache_key] = (None, 0)

    def _location(self, locationId):
        """Return location."""

        for location in self._locations:
            if location.get("locationID") == locationId:
                return location

    @property
    def _locations(self):
        """Return locations."""

        cache_key = "locations"
        value, last_update = self._checkCache(cache_key)
        now = time.time()

        if not value or now - last_update > self._cache_ttl:
            new_value = self._get("locations")
            if new_value:
                self._cache[cache_key] = (new_value, now)
                return new_value
            else:
                self._cache[cache_key] = (
                    value,
                    last_update + 5,
                )  # try again in 5 seconds

        return value

    def _user(self, locationId, userId):
        """Return user."""

        for user in self._users(locationId):
            if user.get("userID") == userId:
                return user

    def _users(self, locationId):
        """Return users."""

        value = self._location(locationId).get("users")
        return value

    def _device(self, locationId, deviceId):
        """Return device."""

        for device in self._devices(locationId):
            if device.get("deviceID") == deviceId:
                return device

    def _devices(self, locationId, forceGet=False):
        """Return devices."""

        if forceGet:
            cache_key = "devices-%s" % locationId
            value, last_update = self._checkCache(cache_key)
            now = time.time()

            if not value or now - last_update > self._cache_ttl:
                new_value = self._get("devices", locationId=locationId)
                if new_value:
                    self._cache[cache_key] = (new_value, now)
                    return new_value
        else:
            if self._location(locationId):
                return self._location(locationId).get("devices")
            else:
                return None

        return value

    def _device_type(self, locationId, deviceType, deviceId):
        """Return devices of a specific type."""

        for device in self._devices_type(deviceType, locationId):
            if device.get("deviceID") == deviceId:
                return device

    def _devices_type(self, deviceType, locationId):
        """Return device type."""

        cache_key = "devices_type-%s_%s" % (locationId, deviceType)
        value, last_update = self._checkCache(cache_key)
        now = time.time()

        if not value or now - last_update > self._cache_ttl:
            value = self._get("devices/" + deviceType, locationId=locationId)
            self._cache[cache_key] = (value, now)

        return value

    @property
    def locations(self):
        """Return locations."""

        if self._locations:
            return [
                Location(location["locationID"], self, self._local_time)
                for location in self._locations
            ]
        else:
            return None
