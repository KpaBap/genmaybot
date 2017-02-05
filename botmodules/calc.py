import urllib.request, urllib.error, urllib.parse, urllib, json, re, traceback

def google_convert(self, e):
    #google calculator
    term = e.input
    nick = e.nick
    
    if nick in google_convert.lastresult:
        term = term.replace("ANS", google_convert.lastresult[nick])
    url = "http://www.google.com/ig/calculator?q=%s" % urllib.parse.quote(term)
    result = ""

    response = urllib.request.urlopen(url).read()
    response = response.decode('unicode-escape')
    response = response.replace("\xa0",",")
    response = re.sub("([a-z]+):", '"\\1" :', response)
    response = response.replace("<sup>","^(")
    response = response.replace("</sup>",")")
    response = response.replace("&#215;","x")
    response = json.loads(response)
    if not response['error']:
        result = "%s = %s" % (response['lhs'],response['rhs'])
        google_convert.lastresult[nick] = str(response['rhs'])
        e.output = result

    
    return e
#google_convert.command = "!c"
#google_convert.lastresult = {}
#google_convert.helptext = "Usage: !c <calculator or conversion query>\nExample: !c 42 fathoms per second to mph\nSends a query to Google Calculator and returns the result.\nCan also be used for currency exchange conversions: !c 1USD to CAD"

