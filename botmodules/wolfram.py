import urllib, urllib.request, urllib.error, urllib.parse, xml.dom.minidom, socket, traceback, re
import random
try:
    import botmodules.userlocation as user
except:
    pass


def get_wolfram(self, e):
    #query 'input' on wolframalpha and get the plaintext result back
    try:
        location = e.location
    except:
        location = ""
    
    if e.input.find("bmi") != -1:
        e.output = "Eat the whole cake, you deserve it."
        return e
    
    if location == "" and user:
        location = user.get_location(e.nick)

            
    location = urllib.parse.quote(location)
            
    socket.setdefaulttimeout(30)
    url = "http://api.wolframalpha.com/v2/query?appid=%s&format=plaintext&input=%s&location=%s" % (self.botconfig["APIkeys"]["wolframAPIkey"], urllib.parse.quote(e.input), location)
    dom = xml.dom.minidom.parse(urllib.request.urlopen(url))
    socket.setdefaulttimeout(10)

    if dom.getElementsByTagName("queryresult")[0].getAttribute("success") == "false":
        try:
            related = dom.getElementsByTagName("relatedexample")[0].getAttribute("input")
            e.input = related
            return get_wolfram(self, e)
        except Exception as inst:
            traceback.print_exc()
            self.logger.debug("!wolframrelated " + e.input + " : " + str(inst))
            result = self.bangcommands["!error"](self, e).output
            e.output = result
            return e
    else:
        try:
            query = dom.getElementsByTagName("plaintext")[0].childNodes[0].data
            try:
                result = dom.getElementsByTagName("plaintext")[1].childNodes[0].data
            except:
                result = self.bangcommands["!error"](self, e).output

            output = query.replace("\n", " || ") + " :: " + result.replace("\n", " || ")

            if e.nick == 'epon':
            #Just for epon
                final = ""
                for char in output:
                    final += re.sub(r'[0-9]', str(int(random.random()*10)), char)
                output = final
            
                e.output = 'LOL MATHS: ' + output
            else:
                e.output = output
            return e
        except Exception as inst:
            traceback.print_exc()
            self.logger.debug("!wolfram " + e.input + " : " + str(inst))
            result = self.bangcommands["!error"](self, e).output
            e.output = result
            return e
            
get_wolfram.waitfor_callback = False
get_wolfram.command = "!wolfram"
get_wolfram.helptext = "Usage: !wolfram <query>\nExample: !wolfram population of New York City\nPerforms a query through Wolfram|Alpha and returns the first result"


def calc_wolfram (self, e):
    return get_wolfram(self, e)
calc_wolfram.command = "!c"
get_wolfram.helptext = "Calculator alias for !wolfram"

def wolfram_time(self, e):
    if e.input:
        location = user.get_location(e.input)
        if location:
            e.input = "current time in %s" % location
            return get_wolfram(self, e)
    else:
        location = user.get_location(e.nick)
        if location:
            e.input = "current time in %s" % location
            return get_wolfram(self, e)
            
wolfram_time.command = "!time"
wolfram_time.helptext = "Usage: !time to get your local time, !time <nick> to get someone else's local time"
