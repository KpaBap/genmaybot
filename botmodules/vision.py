# -*- coding: utf-8 -*-
import re
import json
import urllib

from botmodules.url import last_link

def set_msvisionkey(line, nick, self, c):
  self.botconfig["APIkeys"]["msvisionkey"] = line[11:]
  with open('genmaybot.cfg', 'w') as configfile:
      self.botconfig.write(configfile)
set_msvisionkey.admincommand = "msvisionkey"

def url_is_image(url):
    url = re.search(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>])*\))+(?:\(([^\s()<>])*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))", url)
    #http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    if url:
        url = url.group(0)
        req = urllib.request.Request(url, method="HEAD")
        resp = urllib.request.urlopen(req)
        if "image" in resp.getheader("Content-Type"):
          return True
        else: 
          return False
    else:
        return False


def image_vision(self, e):
    key = self.botconfig["APIkeys"]["msvisionkey"]
    
    class Tmp():
        pass
    tmpevent = Tmp()
    tmpevent.output = ""
    #print ("Vision input ({})".format(e.input))
    if e.input:
      url = e.input
    else:
      url = last_link("", tmpevent).output
    
    if not url_is_image(url):
      return e
    
    values = json.dumps({"url": url})
    self.logger.debug(values)
    request_url = "https://api.projectoxford.ai/vision/v1.0/analyze?visualFeatures=Description,Adult"
    headers = {'Ocp-Apim-Subscription-Key' : key,
               'Content-Type': 'application/json'}
    req = urllib.request.Request(request_url, values.encode(), headers)
    response = urllib.request.urlopen(req)
    results = json.loads(response.read().decode('utf-8'))

    self.logger.debug(results)

    caption = results["description"]["captions"][0]["text"]
    capconfidence = int(results["description"]["captions"][0]["confidence"] * 100)

    adult = results["adult"]["isAdultContent"]
    racy = results["adult"]["isRacyContent"]

    adultstring = ""
    if adult:
       aconfidence = results["adult"]["adultScore"]
       adultstring += " NSFW - {}% confidence".format(int(aconfidence * 100))
    elif racy:
      aconfidence = results["adult"]["racyScore"]
      adultstring += " NSFWish - {}% confidence".format(int(aconfidence * 100))

    e.output = '"{}" - {}% confidence{}'.format(caption, capconfidence, adultstring)

    return e
image_vision.command = "!vision"
