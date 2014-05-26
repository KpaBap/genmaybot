import urllib.request, urllib.error, urllib.parse, urllib, re, botmodules.tools as tools
try: import botmodules.userlocation as user
except: pass

def google_sunrise(self, e):
    #returns the next sunrise time and time from now of the place specified
    #This callback handling code should be able to be reused in any other function


    try:
        location = e.location
    except:
        location = e.input
        
    if location == "" and user:
        location = user.get_location(e.nick)


    
    
    #End callback handling code
    e.output = google_sun(self, location, "Sunrise", e.nick)
    return e
    
google_sunrise.waitfor_callback = False
google_sunrise.command = "!sunrise"
google_sunrise.helptext = "Usage: !sunrise <location>\nExample: !sunrise las vegas, nv\nShows the time of sunrise at a given location\nUse !setlocation <location> to save your location\nThen, using !sunrise without arguments will always show sunrise at your location"
    
def google_sunset(self, e):

    #returns the next sunset time and time from now of the place specified
    #This callback handling code should be able to be reused in any other function


    try:
        location = e.location
    except:
        location = e.input
        
    if location == "" and user:
        location = user.get_location(e.nick)

        
    
    #End callback handling code
    
    e.output = google_sun(self, location, "Sunset", e.nick)
    return e
    
google_sunset.waitfor_callback = False
google_sunset.command = "!sunset"
google_sunset.helptext = "Usage: !sunset <location>\nExample: !sunset las vegas, nv\nShows the time of sunset at a given location\nUse !setlocation <location> to save your location\nThen, using !sunset without arguments will always show sunset at your location"

def google_sun(self, location, sun, nick):
    if location == "" and user:
       location = user.get_location(nick)
    location = urllib.parse.quote(location)
    url = "https://www.google.com/search?hl=en&client=opera&hs=6At&rls=en&q=%s+%s&aq=f&aqi=g1&aql=&oq=&gs_rfai=" % (sun, location)
    request = urllib.request.Request(url, None, {})
    request.add_header('User-Agent', "Opera/9.80 (Windows NT 6.0; U; en) Presto/2.2.15 Version/10.10")
    request.add_header('Range', "bytes=0-40960")
    response = urllib.request.urlopen(request).read().decode('utf-8')
    
    f = open("file.txt","w")
    f.write(response)
    f.close()

    m = re.search('(vk_bk vk_ans\"\> )(.*?)( \<\/div\>\s+)(.*?)(\s*? \<\/div\> )',response)
    
    try:
      settime = m.group(2)
      setlocation = m.group(4)

      #add math to calculate how long ago or how long until
      #miltime = time.strftime("%H:%M",time.strptime(settime,"%I:%M %p"))


      result = "%s: %s" % (setlocation, settime)
   
      #print result
    except:
      pass
      return

    return tools.remove_html_tags(result)
