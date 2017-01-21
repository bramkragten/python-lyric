import lyric

client_id = r'j9ShGaDTsOWlykvAeJCNcMpO76gGwGq6'
client_secret = r'vtt3qfspAhzgLLyU'

redirect_uri = 'https://hass.deproducties.com:8123/lyric'
app_name = 'Sample'
token_cache_file = 'token.txt'

lapi = lyric.Lyric(client_id=client_id, client_secret=client_secret, 
                   token_cache_file=token_cache_file, 
                   redirect_uri=redirect_uri, app_name=app_name)

if lapi._token is None:
    print(lapi.getauthorize_url)

location = lapi.locations[0]

print (lapi._locations)

print(location.locationID)
print(location.devices[0].displayedOutdoorHumidity)

print(location.thermostats)
print(location.waterLeakDetectors)

print (lapi._locations)

print(location.locationID)
print(location.devices[0].displayedOutdoorHumidity)

print(location.thermostats)
print(location.waterLeakDetectors)
