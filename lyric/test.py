import lyric

code = 'Ko9QCRxK'
returnurl = 'http://hass.deproducties.com:8123/api/lyric/'

lapi = lyric.Lyric(code)#, returnurl)

print(lapi.locations)

#for location in lapi.locations:
#    print('Location %s' % location.name)
##    print '    Away: %s' % structure.away
##    print '    Devices:'
##
##    for device in structure.devices:
##        print '        Device: %s' % device.name
##        print '            Temp: %0.1f' % device.temperature
##
### Access advanced structure properties:
##for structure in napi.structures:
##    print 'Structure   : %s' % structure.name
##    print ' Postal Code                    : %s' % structure.postal_code
##    print ' Country                        : %s' % structure.country_code
##    print ' dr_reminder_enabled            : %s' % structure.dr_reminder_enabled
##    print ' emergency_contact_description  : %s' % structure.emergency_contact_description
##    print ' emergency_contact_type         : %s' % structure.emergency_contact_type
##    print ' emergency_contact_phone        : %s' % structure.emergency_contact_phone
##    print ' enhanced_auto_away_enabled     : %s' % structure.enhanced_auto_away_enabled
##    print ' eta_preconditioning_active     : %s' % structure.eta_preconditioning_active
##    print ' house_type                     : %s' % structure.house_type
##    print ' hvac_safety_shutoff_enabled    : %s' % structure.hvac_safety_shutoff_enabled
##    print ' num_thermostats                : %s' % structure.num_thermostats
##    print ' measurement_scale              : %s' % structure.measurement_scale
##    print ' renovation_date                : %s' % structure.renovation_date
##    print ' structure_area                 : %s' % structure.structure_area
##
### Access advanced device properties:
##    for device in structure.devices:
##        print '        Device: %s' % device.name
##        print '        Where: %s' % device.where
##        print '            Mode     : %s' % device.mode
##        print '            Fan      : %s' % device.fan
##        print '            Temp     : %0.1fC' % device.temperature
##        print '            Humidity : %0.1f%%' % device.humidity
##        print '            Target   : %0.1fC' % device.target
##        print '            Away Heat: %0.1fC' % device.away_temperature[0]
##        print '            Away Cool: %0.1fC' % device.away_temperature[1]
##        print '            Eco      : %s' % device.eco
##
##        print '            hvac_ac_state         : %s' % device.hvac_ac_state
##        print '            hvac_cool_x2_state    : %s' % device.hvac_cool_x2_state
##        print '            hvac_heater_state     : %s' % device.hvac_heater_state
##        print '            hvac_aux_heater_state : %s' % device.hvac_aux_heater_state
##        print '            hvac_heat_x2_state    : %s' % device.hvac_heat_x2_state
##        print '            hvac_heat_x3_state    : %s' % device.hvac_heat_x3_state
##        print '            hvac_alt_heat_state   : %s' % device.hvac_alt_heat_state
##        print '            hvac_alt_heat_x2_state: %s' % device.hvac_alt_heat_x2_state
##        print '            hvac_emer_heat_state  : %s' % device.hvac_emer_heat_state
##
##        print '            online                : %s' % device.online
##        print '            last_ip               : %s' % device.last_ip
##        print '            local_ip              : %s' % device.local_ip
##        print '            last_connection       : %s' % device.last_connection
##
##        print '            error_code            : %s' % device.error_code
##        print '            battery_level         : %s' % device.battery_level
##
### The Nest object can also be used as a context manager
##with nest.Nest(username, password) as napi:
##    for device in napi.devices:
##        device.temperature = 23
##
### Weather data is also available under structure or device
### The api is the same from either
##
##structure = napi.structures[0]
##time_str = structure.weather.current.datetime.strftime('%Y-%m-%d %H:%M:%S')
##print 'Current Weather at %s:' % time_str
##print '    Condition: %s' % structure.weather.current.condition
##print '    Temperature: %s' % structure.weather.current.temperature
##print '    Humidity: %s' % structure.weather.current.humidity
##print '    Wind Dir: %s' % structure.weather.current.wind.direction
##print '    Wind Azimuth: %s' % structure.weather.current.wind.azimuth
##print '    Wind Speed: %s' % structure.weather.current.wind.kph
##
### NOTE: Hourly forecasts do not contain a "contidion" its value is `None`
###       Wind Speed is likwise `None` as its generally not reported
##print 'Hourly Forcast:'
##for f in structure.weather.hourly:
##    print '    %s:' % f.datetime.strftime('%Y-%m-%d %H:%M:%S')
##    print '        Temperature: %s' % f.temperature
##    print '        Humidity: %s' % f.humidity
##    print '        Wind Dir: %s' % f.wind.direction
##    print '        Wind Azimuth: %s' % f.wind.azimuth
##
##
### NOTE: Daily forecasts temperature is a tuple of (low, high)
##print 'Daily Forcast:'
##for f in structure.weather.daily:
##    print '    %s:' % f.datetime.strftime('%Y-%m-%d %H:%M:%S')
##    print '    Condition: %s' % structure.weather.current.condition
##    print '        Low: %s' % f.temperature[0]
##    print '        High: %s' % f.temperature[1]
##    print '        Humidity: %s' % f.humidity
##    print '        Wind Dir: %s' % f.wind.direction
##    print '        Wind Azimuth: %s' % f.wind.azimuth
##    print '        Wind Speed: %s' % structure.weather.current.wind.kph
##
##
### NOTE: By default all datetime objects are timezone unaware (UTC)
###       By passing `local_time=True` to the `Nest` object datetime objects
###       will be converted to the timezone reported by nest. If the `pytz`
###       module is installed those timezone objects are used, else one is
###       synthesized from the nest data
##napi = nest.Nest(username, password, local_time=True)
##print napi.structures[0].weather.current.datetime.tzinfo