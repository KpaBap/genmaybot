import json, urllib.request, urllib.error, urllib.parse, re, botmodules.tools as tools

def gwiki(bot, e):
      url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=site:wikipedia.org+' + urllib.parse.quote(e.input)
      request = urllib.request.Request(url, None, {'Referer': 'http://irc.00id.net'})
      response = urllib.request.urlopen(request)

      results_json = json.loads(response.read().decode('utf-8'))
      results = results_json['responseData']['results']
      regexstring = "wikipedia.org/wiki/"
      result = results[0]
      m = re.search(regexstring,result['url'])   
      if m:
         url = result['url']
         url = tools.shorten_url(url.replace('%25','%'))

         content = tools.decode_htmlentities(tools.remove_html_tags(result['content']))
         content = re.sub('\s+', ' ', content)
         content = content.replace("...", "")

         e.output = "%s [ %s ]" % (content, url)
      return e
    
gwiki.command = "!gwiki"
gwiki.helptext = "!gwiki <query> - attempts to look up what you want to know on wikipedia using google's synopsis context"