import lyric

client_id = r''
client_secret = r''

redirect_uri = 'https://hass.deproducties.com:8123/lyric'
app_name = 'Sample'
token_cache_file = 'token.txt'

lapi = lyric.Lyric(client_id=client_id, client_secret=client_secret,
                   token_cache_file=token_cache_file,
                   redirect_uri=redirect_uri, app_name=app_name)

if lapi._token is None:
    print(lapi.getauthorize_url)

location = lapi.locations[0]

print(location.name)

print(location.thermostats[0].id)

print(location.thermostats[0].displayedOutdoorHumidity)
print(location.thermostats[0].indoorTemperature)
print(location.thermostats[0].outdoorTemperature)
print(location.thermostats[0].indoorHumidityStatus)
