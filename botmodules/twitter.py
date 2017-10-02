#stupid fucking twitter api authentication just to fucking read a fucking public timeline, what the fuck.
import json
import urllib, urllib.request, urllib.parse
import datetime
import base64
import re


def __init__(self):
  
  try:
    auth = "%s:%s" % (self.botconfig["APIkeys"]["twitterConsumerKey"], self.botconfig["APIkeys"]["twitterConsumerSecret"])
    auth = "Basic ".encode() + base64.b64encode(auth.encode())

    body = "grant_type=client_credentials".encode()
    headers = {"Authorization": auth, "Content-Type" : "application/x-www-form-urlencoded;charset=UTF-8"}
    url = "https://api.twitter.com/oauth2/token"
    req = urllib.request.Request(url, body, headers)
    response = urllib.request.urlopen(req)
    response = json.loads(response.read().decode('utf-8'))
    read_timeline.holyshitbearstoken = response['access_token']
    self.logger.debug(read_timeline.holyshitbearstoken)
  except Exception as inst:
      self.logger.debug(inst)

def read_timeline (user):
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=%s&count=1" % user
    opener = urllib.request.build_opener()
    opener.addheaders = [('Authorization', 'Bearer ' + read_timeline.holyshitbearstoken)]
    response = opener.open(url).read().decode('utf-8')
    tweet = json.loads(response)
    updated = datetime.datetime.strptime(tweet[0]['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
    ago = round((datetime.datetime.utcnow() - updated).seconds/60)
    text = tweet[0]['user']['screen_name'] + ": " + tweet[0]['text']
    text = re.sub(r"\r\n|\n|\r", " ", text)
    return text, updated, ago

def latest_breaking(self, e):
    text, updated, ago = read_timeline('breakingnews')
    e.output =  "%s (%s minutes ago) " % (text, ago)
    return e
latest_breaking.command = "!breaking"
latest_breaking.helptext = "Usage: !breaking\nShows the latest breaking news alert"

def latest_tweet(self, e):
    text, updated, ago = read_timeline(e.input)
    e.output =  "%s (%s minutes ago) " % (text, ago)
    return e
latest_tweet.command = "!lasttweet"

def trump_tweet(self, e):
  e.input = "realDonaldTrump"
  return latest_tweet(self, e)
trump_tweet.command = "!trump"

def breaking_alert(self):
    #returns a new breaking news only if it hasn't returned it before
      try:
        description, updated, ago = read_timeline('breakingnews')

        if not breaking_alert.lastcheck:
            breaking_alert.lastcheck = updated
        if updated > breaking_alert.lastcheck:
            breaking_alert.lastcheck = updated
            return description
      except Exception as inst:
          self.logger.debug("breakinglert: " + str(inst))

breaking_alert.lastcheck = ""
breaking_alert.alert = False
