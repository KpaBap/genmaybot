import cherrypy
import threading
import traceback
from inspect import isfunction
from botmodules.web_auth import AuthController, require, member_of, name_is
import time

class RestrictedArea:

    # all methods in this controller (and subcontrollers) is
    # open only to members of the admin group

    _cp_config = {
        'auth.require': [member_of('admin')]
    }

    @cherrypy.expose
    def index(self):
        return """This is the admin only area."""

#generic object to handle the return values from bot functions
class Emptyobject:
    def __init__(self):
        return

class Root:


    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True
    }

    def __init__(self,bot): #make a reference to the main bot object
        self.bot = bot
        self.auth = AuthController(self.bot)
        

    

    restricted = RestrictedArea()

    @cherrypy.expose
    @require()
    def index(self):
        return """

        <center>
        <a href="/commands" target="output">Commands</a>&nbsp;&nbsp;&nbsp;
        <a href="/botconfig" target="output">Bot Config</a>&nbsp;&nbsp;&nbsp;
        <a href="/event_log" target="output">Event log</a>&nbsp;&nbsp;&nbsp;
        <a href="/debug_log" target="output">Debug log</a>&nbsp;&nbsp;&nbsp;
        <a href="/bot_obj" target="output">Bot Object</a>&nbsp;&nbsp;&nbsp;
       <br><br>
       <iframe name="output" width="1280px" height="1024px"></iframe>

        """
    @cherrypy.expose
    @require()
    def bot_obj(self):
        
        output="<pre>"
        obj_val=""
        
        botobjects = self.bot.__dict__
        for obj_name in botobjects.keys():
            try:
                for key in botobjects[obj_name].keys():
                    if key.find("__") != 0:                        
                        obj_val += "<br />\t\t%s -> %s" % (key, str(botobjects[obj_name][key]).replace("<","&lt;").replace(">","&gt;"))
            except:
                #hack to find the wotd lineparser if it exists
                if isinstance(botobjects[obj_name],list): 
                    for func in botobjects[obj_name]:
                        if str(func).find("wotd") != -1:
                            obj_val += "<br />\t\t%s ->" % (str(func).replace("<","&lt;").replace(">","&gt;"))
                            for attrib in func.__dict__:
                                obj_val += "<br />\t\t\t%s = %s" % (attrib, func.__dict__[attrib])
                        else:
                            obj_val += "<br />\t\t%s" % (str(func).replace("<","&lt;").replace(">","&gt;"))
                        # end hack
                else:
                    obj_val = str(botobjects[obj_name]).replace("<","&lt;").replace(">","&gt;")
            
            output+= "<b>%s</b> -> %s <br />" %(obj_name, obj_val)
            obj_val=""
        return output

    @cherrypy.expose
    @require()
    def event_log(self):
        return "<pre>"+open(self.bot.botconfig['misc']['event_log'],"r").read()+"</pre>"

    @cherrypy.expose
    @require()
    def debug_log(self):
        return "<pre>"+open(self.bot.botconfig['misc']['debug_log'],"r").read()+"</pre>"


    @cherrypy.expose
    def commands(self):
        commandlist = ""

        for command in self.bot.bangcommands:
            try: 
                helptext = self.bot.bangcommands[command].helptext
                helptext = helptext.replace("\n","<br>")
            except:
                helptext=""

            commandlist+= "<p>%s - %s</p>" % (command,helptext)

        return commandlist

    @cherrypy.expose
    def do_command(self, cmd=None):
        try:        
            cmd = "!"+cmd
            if self.bot.bangcommands[cmd].webExposed:
                return self.bot.bangcommands[cmd](None, None,True) #Arguments are self, e, web_call
        except:
            print (traceback.format_exc())
            return "Invalid command."

        

    @cherrypy.expose
    @require()
    def botconfig(self):
        output=""

        for section in self.bot.botconfig:
                output+="[%s]<br>" % section
                for item in self.bot.botconfig[section]:
                    output+="%s=%s<br>" % (item,self.bot.botconfig[section][item])

        return output



    # This is only available if the user name is joe _and_ he's in group admin
    @cherrypy.expose
    @require(name_is("joe"))
    @require(member_of("admin"))   # equivalent: @require(name_is("joe"), member_of("admin"))
    @staticmethod
    def only_for_joe_admin():
        return """Hello Joe Admin - this page is available to you only"""


def __init__(bot):
    ##Disable cherrypy logging to stdout, bind to all IPs, start in a separate thread
    cherrypy.config.update({'engine.autoreload_on': True})
    cherrypy.log.screen=False
    
    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': int(bot.botconfig['webui']['port']),
                       })
    cherrypy.tree.mount(Root(bot),"")
    #wait a little bit for other instances to finish starting
    time.sleep(1.5)
    if not cherrypy.server.running:
        thread = threading.Thread(target=cherrypy.server.start,)
        thread.start()
