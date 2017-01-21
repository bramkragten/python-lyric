import lyric

redirect_uri = 'https://hass.deproducties.com:8123/lyric'
app_name = 'Sample'
token_cache_file = 'token.txt'

lapi = lyric.Lyric(token_cache_file=token_cache_file, redirect_uri=redirect_uri, app_name=app_name)

location = lapi.locations[0]

print (lapi._locations)

print(location.locationID)
print(location.devices[0].displayedOutdoorHumidity)

print(location.thermostats)
print(location.waterLeakDetectors)


