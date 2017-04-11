# -*- coding: UTF-8 -*-

import urllib.request, urllib.parse, urllib, xml.dom.minidom
import json, time, re
try:
    import botmodules.userlocation as user
except ImportError:
    user = None


def set_wwokey(line, nick, self, c):
    self.botconfig["APIkeys"]["wwoAPIkey"] = line[7:]
    with open('genmaybot.cfg', 'w') as configfile:
        self.botconfig.write(configfile)
set_wwokey.admincommand = "wwokey"

def set_fiokey(line, nick, self, c):
    self.botconfig["APIkeys"]["forecastIO_APIkey"] = line[14:]
    with open('genmaybot.cfg', 'w') as configfile:
        self.botconfig.write(configfile)
set_fiokey.admincommand = "forecastiokey"

def google_geocode(self, address):
    gapikey = self.botconfig["APIkeys"]["shorturlkey"] #This uses the same Google API key as URL shortener
    address = urllib.parse.quote(address)

    url = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}"
    url = url.format(address, gapikey)


    try:
        request = urllib.request.Request(url, None, {'Referer': 'http://irc.00id.net'})
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as err:
        self.logger.exception("Exception in google_geocode:")

    try:
        results_json = json.loads(response.read().decode('utf-8'))
        status = results_json['status']

        if status != "OK":
            raise

        city, state, country, poi = "","","", ""
        
        for component in results_json['results'][0]['address_components']:
            if 'locality' in component['types']:
                city = component['long_name']
            elif 'point_of_interest' in component['types'] or 'natural_feature' in component['types']:
                poi = component['long_name']
            elif 'administrative_area_level_1' in component['types']:
                state = component['short_name']
            elif 'country' in component['types']:
                if component['short_name'] != "US":                
                    country = component['long_name']
                else:
                    country = False

        if not city:
            city = poi #if we didn't find a city, maybe there was a POI or natural feature entry, so use that instead

        if not country: #Only show the state if in the US
            country == ""
        elif country != "Canada" and city:               #We don't care about provinces outside of the US and Canada, unless the city name is empty
            state = ""

        if city:
            formatted_address = "{}{}{}".format(city,"" if not state else ", " + state,"" if not country else ", " + country)
        elif state:
            formatted_address = "{}{}".format(state,"" if not country else ", " + country)
        else:
            formatted_address = "{}".format("" if not country else country)
        
        
        lng = results_json['results'][0]['geometry']['location']['lng']
        lat = results_json['results'][0]['geometry']['location']['lat']


        
    except:
        self.logger.exception("Failed to geocode location using Google API:")

        return
    
    return formatted_address, lat, lng, country

def bearing_to_compass(bearing):
    dirs = {}        
    dirs['N'] = (348.75, 11.25)
    dirs['NNE'] = (11.25, 33.75)
    dirs['NE'] = (33.75, 56.25)
    dirs['ENE'] = (56.25, 78.75)
    dirs['E'] = (78.75, 101.25)
    dirs['ESE'] = (101.25, 122.75)
    dirs['SE'] = (123.75, 146.25)
    dirs['SSE'] = (146.25, 168.75)
    dirs['S'] = (168.75, 191.25)
    dirs['SSW'] = (191.25, 213.75)
    dirs['SW'] = (213.75, 236.25)
    dirs['WSW'] = (236.25, 258.75)
    dirs['W'] = (258.75, 281.25)
    dirs['WNW'] = (281.25, 303.75)
    dirs['NW'] = (303.75, 326.25)
    dirs['NNW'] = (326.25, 348.75)

    for direction in dirs:
        min, max = dirs[direction]
        if bearing >= min and bearing <= max:
            return direction
        elif bearing >= dirs['N'][0] or bearing <= dirs['N'][1]:
            return "N"

def bearing_to_arrow(bearing):
    directions = {
        "↓": (337.5, 22.5),
        "↘︎": (292.5, 337.5),
        "→": (247.5, 292.5),
        "↗︎": (202.5, 247.5),
        "↑": (157.5, 202.5),
        "↖︎": (112.5 ,157.5),
        "←": (67.5, 112.5),
        "↙︎": (22.5, 67.5)
    }
    for direction in directions:
        min, max = directions[direction]
        if bearing >= min and bearing <= max:
            return direction
        elif bearing >= directions['↓'][0] or bearing <= directions['↓'][1]:
            return '↓'

def weather_summary_to_icon(icon):

    icons = {
        "cloudy": "\U00002601",
        "partly-cloudy-day": "\U0001F324",
        "clear-day": "️\U00002600",
        "clear-night": "\U0001F319",
        "rain": "\U0001F327",
        "snow": "\U00002744",
        "wind": "\U0001F4A8",
        "fog": "\U0001F32B"

    }

    try:
        return icons[icon]
    except KeyError:

        return ""

def get_weather(self, e):

    try:
        location = e.location
    except:
        location = e.input
    
    if location and user.get_location(location):
        location = user.get_location(location) #allow looking up by nickname
    
    if location == "" and user:
        location = user.get_location(e.nick)

    # Try weather functions in order
    forecast_io(self,  e, location)
    
    if not e.output:
        get_wwo(self, location, e)
    if not e.output:
        return get_weather2(self, e)
        
    return e

get_weather.waitfor_callback = False
get_weather.command = "!w"
get_weather.helptext = """Usage: \002!w <location>\002
Example: !w hell, mi
Shows weather info from a few different providers.
Use \002!setlocation <location>\002 to save your location"""
   
def forecast_io(self,e, location=""):
    apikey = self.botconfig["APIkeys"]["forecastIO_APIkey"]
    self.logger.debug("Entered Forecast.IO function. Location {} or {}".format(location, e.input))
    if location == "":
        location = e.input
    if location == "" and user:
        location = user.get_location(e.nick)
  
    address, lat, lng, country = google_geocode(self,location)

    url = "https://api.forecast.io/forecast/{}/{},{}"
    url = url.format(apikey, lat, lng)

    try:
        request = urllib.request.Request(url, None, {'Referer': 'http://irc.00id.net'})
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as err:
        self.logger.exception("Exception in forecast_io:")

    #try:
    results_json = json.loads(response.read().decode('utf-8'))
    timezone_offset = results_json['offset']    
    current_conditions = results_json['currently']


    temp = current_conditions['temperature']
    humidity = int(100*current_conditions['humidity'])
    precip_probability = current_conditions['precipProbability']
    current_summary = current_conditions['summary']
    summary_icon = weather_summary_to_icon(current_conditions['icon'])
    
    wind_speed = int(round(current_conditions['windSpeed'], 0))
    wind_speed_kmh = int(round(wind_speed * 1.609, 0))

    wind_direction = current_conditions['windBearing']
    wind_arrow = bearing_to_arrow(wind_direction)
    wind_direction = bearing_to_compass(wind_direction)


    cloud_cover = int(100*current_conditions['cloudCover'])
    
    feels_like = current_conditions['apparentTemperature']

    min_temp = int(round(results_json['daily']['data'][0]['temperatureMin'],0))

    min_temp_c = int(round((min_temp - 32)*5/9,0)) 
        
    max_temp = int(round(results_json['daily']['data'][0]['temperatureMax'],0))

    max_temp_c = int(round((max_temp - 32)*5/9,0))
        
    if feels_like != temp:
        if country:
            feels_like = " / Feels like: %s°C" % (int(round((feels_like- 32)*5/9,0)))
        else:
            feels_like = " / Feels like: %s°F" % (int(round(feels_like,0)))
    
    else:
        feels_like = ""
        
    temp_c = int(round((temp - 32)*5/9,0))
    temp = int(round(temp,0))

    # If the minute by minute outlook isn't available, grab the hourly
    try:
        outlook = "%s %s " % (results_json['minutely']['summary'], results_json['daily']['summary'])
    except:
        outlook = "%s %s" % (results_json['hourly']['summary'], results_json['daily']['summary'])


    if not country: #If we're in the US, use Fahrenheit, otherwise Celsius    
        output = "{} / {} {} / {}°F{} / Humidity: {}% / Wind: {} {} at {} mph / Cloud Cover: {}% / High: {}°F Low: {}°F / Outlook: {}"
        e.output = output.format(address, current_summary, summary_icon, temp,
                          feels_like, humidity, wind_arrow,
                          wind_direction, wind_speed,
                          cloud_cover, max_temp, min_temp, outlook)
    else: #Outside of the US
        outlookt = re.search("(-?\d+)°F", outlook)
        if outlookt:
            try:
                tmp = int(outlookt.group(1))
                tmpstr = "{}°C".format(int(round((tmp - 32)*5/9,0)))
                outlook = re.sub("-?\d+°F", tmpstr, outlook)
            except:
                pass

        output = "{} / {} {} / {}°C{} / Humidity: {}% / Wind: {} {} at {} km/h / Cloud Cover: {}% / High: {}°C Low: {}°C / Outlook: {}"
        e.output = output.format(address, current_summary, summary_icon, temp_c,
                          feels_like, humidity, wind_arrow, wind_direction,
                          wind_speed_kmh, cloud_cover, max_temp_c,
                          min_temp_c, outlook)
    return e


forecast_io.command = "!fio"

def get_wwo(self, location, e):
    # WWO weather of place specified in 'zip'
    # http://www.worldweatheronline.com/free-weather-feed.aspx
    
    location = urllib.parse.quote(location)
    
    #End callback handling code
    url = "http://api.worldweatheronline.com/free/v1/weather.ashx?" \
          "q={}&format=json&num_of_days=1&includeLocation=yes&key={}".format(location,
                                                                             self.botconfig["APIkeys"]["wwoAPIkey"])

    response = urllib.request.urlopen(url).read().decode('utf-8')
    weather = json.loads(response)
    weatherdata = weather["data"]

    if 'error' not in weatherdata:
    
        country = weatherdata['nearest_area'][0]['country'][0]['value']
        
        if country == "United States Of America" or country == "Canada" or country == "USA":
            country = ""
        elif country == "United Kingdom":
            country = ", UK"
        else: 
            country = ", " + country

        try:
            region = ", " + weatherdata['nearest_area'][0]['region'][0]['value']
        except:
            region = ""
        
        city = "%s%s%s" % (weatherdata['nearest_area'][0]['areaName'][0]['value'], region, country)
        desc = weatherdata['current_condition'][0]['weatherDesc'][0]['value']
        temp = "{}°F {}°C".format(weatherdata['current_condition'][0]['temp_F'],
                                  weatherdata['current_condition'][0]['temp_C'])
        humidity = "%s%%" % (weatherdata['current_condition'][0]['humidity'])
        high = "{}°F {}°C".format(weatherdata['weather'][0]['tempMaxF'], weatherdata['weather'][0]['tempMaxC'])
        low = "{}°F {}°C".format(weatherdata['weather'][0]['tempMinF'], weatherdata['weather'][0]['tempMinC'])
        outlook = weatherdata['weather'][0]['weatherDesc'][0]['value']

        if int(weatherdata['current_condition'][0]['cloudcover']) > 5:
            cloudcover = "Cloud Cover: %s%% / " % (weatherdata['current_condition'][0]['cloudcover'])
        else:
            cloudcover = ""

        if float(weatherdata['current_condition'][0]['precipMM']) > 0:
            precip = "Precipitation: %s mm / " % (weatherdata['current_condition'][0]['precipMM'])
        else:
            precip = ""

        if int(weatherdata['current_condition'][0]['visibility']) < 10:
            visibility = "Visibility: %skm / " % (weatherdata['current_condition'][0]['visibility'])
        else: 
            visibility = ""
            
        if int(weatherdata['current_condition'][0]['windspeedMiles']) > 0:
            wind = "Wind: %s at %s mph (%s km/h) / " % (weatherdata['current_condition'][0]['winddir16Point'],
                                                        weatherdata['current_condition'][0]['windspeedMiles'],
                                                        weatherdata['current_condition'][0]['windspeedKmph'])
        else:
            wind = ""

        message = "{} / {} / {} / Humidity: {} / {}{}{}{}High: {} - Low: {} Outlook: {}".format(city,
                                                                                                desc,
                                                                                                temp,
                                                                                                humidity,
                                                                                                visibility,
                                                                                                wind,
                                                                                                cloudcover,
                                                                                                precip,
                                                                                                high,
                                                                                                low,
                                                                                                outlook)
        e.output = message
        return e
    else:
        return False




def get_weather2(self, e):
    #wunderground weather of place specified in 'zipcode'
    zipcode = e.input
    if zipcode == "" and user:
        zipcode = user.get_location(e.nick)

    url = "http://api.wunderground.com/auto/wui/geo/WXCurrentObXML/index.xml?query=" + urllib.parse.quote(zipcode)
    dom = xml.dom.minidom.parse(urllib.request.urlopen(url))
    city = dom.getElementsByTagName('display_location')[0].getElementsByTagName('full')[0].childNodes[0].data
    if city != ", ":
        temp_f = dom.getElementsByTagName('temp_f')[0].childNodes[0].data
        temp_c = dom.getElementsByTagName('temp_c')[0].childNodes[0].data
        try:
            condition = dom.getElementsByTagName('weather')[0].childNodes[0].data
        except:
            condition = ""
        try:
            humidity = "Humidity: " + str(dom.getElementsByTagName('relative_humidity')[0].childNodes[0].data)
        except:
            humidity = ""
        try:
            wind = "Wind: " + str(dom.getElementsByTagName('wind_string')[0].childNodes[0].data)
        except:
            wind = ""

        degree_symbol = chr(176)
        chanmsg = "%s / %s / %s%sF %s%sC / %s / %s" % (city,
                                                       condition,
                                                       temp_f,
                                                       degree_symbol,
                                                       temp_c,
                                                       degree_symbol,
                                                       humidity,
                                                       wind)
        e.output = chanmsg
        return e
    else:
        if user:
            ziptry = user.get_location(e.input)
            if ziptry:
                e.nick = e.input
                e.input = ""
                return get_weather(self, e)
            else:
                return None

get_weather2.command = "!wu"
get_weather2.helptext = """Usage: \002!wu <location>\002
Example: !wu hell, mi
Shows weather info from wunderground.com.
Use \002!setlocation <location>\002 to save your location"""
