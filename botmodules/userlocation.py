import sqlite3, urllib.parse, urllib.request, json


def set_location(self, e):
    
    conn = sqlite3.connect('userlocations.sqlite')
    c = conn.cursor()
    result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='userlocations';").fetchone()
    if not result:
        c.execute('''create table userlocations(user text UNIQUE ON CONFLICT REPLACE, location text)''')
        
    c.execute("""insert into userlocations values (?,?)""", (e.nick, e.input))
    
    conn.commit()
    c.close()

set_location.command = "!setlocation"
set_location.helptext = "Usage: !setlocation <location>\nExample: !setlocation hell, mi\nSaves your geographical location in the bot.\nUseful for the location based commands (!sunset, !sunrise, !w).\nOnce your location is saved you can use those commands without an argument."
    
def get_location(nick):
    conn = sqlite3.connect('userlocations.sqlite')
    c = conn.cursor()
    result = c.execute("SELECT location FROM userlocations WHERE UPPER(user) = UPPER(?)", [nick]).fetchone()
    if result:
        return result[0]
    else:
        return ""
    


def get_geo_ip_location(self, e="", ip="", nick="", whois_reply=False, callback=""):
# This function gets called twice so we need to account for the different calls
# It gets called once by a server side event
# then again when the server responds with the whois IP information
    ##import pdb; pdb.set_trace()
    if callback:
        get_geo_ip_location.callback = callback

    if whois_reply and get_geo_ip_location.callback:

        #we're basically doing a fake call to the original requestor function
        #We set the <arg> portion of !command <arg> to give it expected input
        # GeoIP URL is http://freegeoip.net/json/<ip>
        
        get_geo_ip_location.callback.waitfor_callback=False
        ##import pdb; pdb.set_trace()
        e.location = get_geo_ip(ip)
        response = get_geo_ip_location.callback(self, e)
        self.bot_say(response) #since this is a callback, we have to say the line ourselves
        
    elif whois_reply:
        e.output = get_geo_ip(ip)
        self.bot_say(e)
    elif not callback:
        try: 
            #Try to look up an IP address that was given as a command arugment
            #If that fails, fall back to whois info    
            if e.input:
                e.output = get_geo_ip(e.input)
                self.bot_say(e)
                return
            else:
                request_whois_ip(self, get_geo_ip_location, nick, e)
        except:
            pass
    else:
        request_whois_ip(self, get_geo_ip_location, nick, e)
    
get_geo_ip_location.command = "!geoip"
get_geo_ip_location.callback = None
get_geo_ip_location.helptext = "Looks up your IP address and attempts to return a location based on it."

def get_geo_ip(ip):
    location = get_geo_ip_netimpact(ip)
    if location:
        return location
    #import pdb; pdb.set_trace()
    location = get_geo_ip_free(ip)
    if location:
        return location

    
def get_geo_ip_free(ip):
    ip = urllib.parse.quote(ip)
    
    url = "http://freegeoip.net/json/{}".format(ip)

    response = urllib.request.urlopen(url).read().decode('utf-8')

    try:
        response = urllib.request.urlopen(url).read().decode('utf-8')
        geoip = json.loads(response)
    except:
        return False

    if geoip['city']:
        return "%s, %s" % (geoip['city'], geoip['region_name'])
    else:
        return False

def get_geo_ip_netimpact(ip):

#http://api.netimpact.com/qv1.php?key=WdpY8qgDVuAmvgyJ&qt=geoip&d=json&q=<ip>
    ip = urllib.parse.quote(ip)

    url = "http://api.netimpact.com/qv1.php?key=WdpY8qgDVuAmvgyJ&qt=geoip&d=json&q={}".format(ip)
    try:
        response = urllib.request.urlopen(url).read().decode('utf-8')
        geoip = json.loads(response)[0]
    except:
        return False

    if geoip:
        return "%s, %s, %s" % (geoip[0], geoip[1], geoip[2])
    else:
        return False


def request_whois_ip(self, reply_handler, nick="", e=""):
    #import pdb; pdb.set_trace()
# This function sends the whois request and registers the response handler    
# We also need to store the source event that triggered the whois request     
# So we can respond back to it properly
# Or if we are internally getting whois info, we don't need to know about the source event

    if nick:
        self.irccontext.whois([nick])
    elif e:
        self.irccontext.whois([e.nick])
    else:
        return
    self.whoisIP_reply_handler = reply_handler
    self.whoisIP_sourceEvent = e

