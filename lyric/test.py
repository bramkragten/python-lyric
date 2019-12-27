#  -*- coding:utf-8 -*-

"""Battery of tests for lyric module."""

from . import lyric as lyric_local

client_id = r""
client_secret = r""

redirect_uri = "https://hass.deproducties.com/api/lyric"
app_name = "Sample"
token_cache_file = "token.txt"

lapi = lyric_local.Lyric(
    client_id=client_id,
    client_secret=client_secret,
    token_cache_file=token_cache_file,
    redirect_uri=redirect_uri,
    app_name=app_name,
)

if lapi._token is None:
    print(lapi.getauthorize_url)

print(lapi._locations)

for location in lapi.locations:
    print(location)
    print(location.id)
    print(location.name)
    print(location.city)
    print(location.geoFences)
    print(location.geoFences[0]["geoOccupancy"]["withinFence"])

    for user in location.users:
        print(user)
        print(user.id)
        print(user.name)
        print(user.firstname)
        print(user.lastname)

    for device in location.devices:
        print(device)
        print(device.id)
        print(device.name)
        print(device.deviceType)
        print(device.indoorTemperature)
        print(device.temperatureSetpoint)
        device.temperatureSetpoint = 18

    for thermostat in location.thermostats:
        print(thermostat)
        print(thermostat.id)
        print(thermostat.name)
        print(thermostat.deviceType)
        print(thermostat.outdoorTemperature)
        print(thermostat.indoorHumidityStatus)
        print(thermostat.temperatureSetpoint)

    for waterLeakDetector in location.waterLeakDetectors:
        print(waterLeakDetector)
        print(waterLeakDetector.id)
        print(waterLeakDetector.name)
        print(waterLeakDetector.deviceType)
