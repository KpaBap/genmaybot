#! /usr/bin/env python
#
#To run this bot use the following command:
#
#  python genmaybot.py irc.0id.net "#chan" Nickname
#


import irc.bot
import ssl
import time, imp
import sys, os, socket, configparser, threading, traceback

socket.setdefaulttimeout(5)

mainself = None

class Py3Bot(irc.bot.SingleServerIRCBot):

    def __init__(self, channel, nickname, server, port=6667, use_ssl=False):
        global mainself
        mainself = self
        if use_ssl:
            ssl_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
            irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname, 15, connect_factory=ssl_factory)
        else:
            irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname, 15)
        self.channel = channel
        self.doingcommand = False
        self.botnick = nickname

        self.commandaccesslist = {}
        self.commandcooldownlast = {}

        self.spam = {}

        self.load_config()
        print(self.loadmodules())

    def load_config(self):
        config = configparser.ConfigParser()
        try:
            cfgfile = open('genmaybot.cfg')
        except IOError:
            print("You need to create a .cfg file using the example")
            sys.exit(1)

        config.readfp(cfgfile)
        self.botconfig = config
        self.botadmins = config["irc"]["botadmins"].split(",")
        self.error_log = simpleLogger(config['misc']['error_log'])
        self.event_log = simpleLogger(config['misc']['event_log'])

        sys.stdout = self.event_log
        sys.stderr = self.error_log

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_kick(self, c, e):
        #attempt to rejoin any channel we're kicked from
        if e.arguments[0][0:len(c.get_nickname())] == c.get_nickname():
            c.join(e.target)

    def on_disconnect(self, c, e):
        print("DISCONNECT: " + str(e.arguments))
        
        
    def on_welcome(self, c, e):
        c.privmsg("NickServ", "identify " + self.botconfig['irc']['identpassword'])
        c.oper(self.botconfig['irc']['opernick'], self.botconfig['irc']['operpassword'])
        c.join(self.channel)
        self.alerts(c)
        self.irccontext = c
        c.who(c.get_nickname())
        
       
    
    def on_youreoper(self, c, e):
        print ("I'm an IRCop bitches!")
        
    
    def on_whoishostline(self, c, e):
         try:
            
            self.whoisIP_reply_handler(self, self.whoisIP_sourceEvent, e.arguments()[1].split()[-1],"",True)
         except:
            pass #No whois host line reply handler


    def on_pubmsg(self, c, e):
        self.process_line(c, e)

    def on_privmsg(self, c, e):
        line = e.arguments[0]
        from_nick = e.source.split("!")[0]
        command = line.split(" ")[0].lower()

        if command in self.admincommands and self.isbotadmin(from_nick):
            self.admincommand = line
            c.who(from_nick)

        self.process_line(c, e, True)

    def on_whoreply(self, c, e):
        nick = e.arguments[4]
        
        # The bot does a whois on itself to find its cloaked hostname after it connects
        # This if statement handles that situation and stores the data accordingly        
        if nick == c.get_nickname():
            self.realname = e.arguments[1]
            self.hostname = e.arguments[2]
            #The protocol garbage before the real message is 
            #:<nick>!<realname>@<hostname> PRIVMSG <target> :
            return
        
        line = self.admincommand
        command = line.split(" ")[0]
        self.admincommand = ""
        try:
            if e.arguments[5].find("r") != -1 and line != "":
                say = self.admincommands[command](line, nick, self, c)
                say = say.split("\n")
                for line in say:
                    c.privmsg(nick, line)

        except Exception as inst:
            traceback.print_exc()
            print("admin exception: " + line + " : " + str(inst))

    def process_line(self, c, ircevent, private = False):
        if self.doingcommand:
            return
        self.doingcommand = True

        line = ircevent.arguments[0]
        from_nick = ircevent.source.split("!")[0]
        hostmask = ircevent.source[ircevent.source.find("!")+1:]
        command = line.split(" ")[0].lower()
        args = line[len(command)+1:].strip()
        if private:
            linesource = from_nick
        else:
            linesource = ircevent.target

        e = None
        etmp = []


        try:
            #commands names are defined by the module as function.command = "!commandname"
            if command in self.bangcommands and (self.commandaccess(command) or from_nick in self.botadmins):
                e = self.botEvent(linesource, from_nick, hostmask, args)
                e.botnick = c.get_nickname() #store the bot's nick in the event in case we need it.

                if linesource in self.channels and hasattr(self.bangcommands[command], 'privateonly'):
                    self.doingcommand = False
                    return
                etmp.append(self.bangcommands[command](self, e))

            #lineparsers take the whole line and nick for EVERY line
            #ensure the lineparser function is short and simple. Try to not to add too many of them
            #Multiple lineparsers can output data, leading to multiple 'say' lines
            for command in self.lineparsers:
                e = self.botEvent(linesource, from_nick, hostmask, line)
                e.botnick = c.get_nickname()  # store the bot's nick in the event in case we need it.
                if linesource in self.channels and hasattr(command, 'privateonly'):
                    continue
                etmp.append(command(self, e))

            firstpass = True
            for e in etmp:
                if e and e.output:
                    self.botSay(e)

        except Exception as inst:
            traceback.print_exc()
            print(line + " : " + str(inst))
            pass

        self.doingcommand = False
        return

    def botSay(self, botevent):
        try:
            if botevent.output:
                for line in botevent.output.split("\n"):
                    line = self.tools['decode_htmlentities'](line)
                    if botevent.notice:
                        self.irccontext.notice(botevent.source, line)
                    else:
                        self.irccontext.privmsg(botevent.source, line)
        except Exception as inst:
            print("bot failed trying to say " + str(botevent.output) + "\n" + str(inst))
            traceback.print_exc()

    def loadmodules(self):
        self.tools = vars(imp.load_source("tools", "./botmodules/tools.py"))

        filenames = []
        for fn in os.listdir('./botmodules'):
            if fn.endswith('.py') and not fn.startswith('_'):
                filenames.append(os.path.join('./botmodules', fn))

        self.bangcommands = {}
        self.admincommands = {}
        self.botalerts = []
        self.lineparsers = []

        for filename in filenames:
            name = os.path.basename(filename)[:-3]
            try:
                module = imp.load_source(name, filename)
            except Exception as inst:
                print("Error loading module " + name + " : " + str(inst))
            else:
                try:
                    vars(module)['__init__'](self)
                except:
                    pass
                for name, func in vars(module).items():
                    if hasattr(func, 'command'):
                        command = str(func.command)
                        self.bangcommands[command] = func
                    elif hasattr(func, 'admincommand'):
                        command = str(func.admincommand)
                        self.admincommands[command] = func
                    elif hasattr(func, 'alert'):
                        self.botalerts.append(func)
                    elif hasattr(func, 'lineparser'):
                        self.lineparsers.append(func)

        commands, botalerts, lineparsers, admincommands = "", "", "", ""

        if self.bangcommands:
            commands = 'Loaded command modules: %s' % list(self.bangcommands.keys())
        else:
            commands = "No command modules loaded!"
        if self.botalerts:
            botalerts = 'Loaded alerts: %s' % ', '.join((command.__name__ for command in self.botalerts))
        if self.lineparsers:
            lineparsers = 'Loaded line parsers: %s' % ', '.join((command.__name__ for command in self.lineparsers))
        if self.admincommands:
            admincommands = 'Loaded admin commands: %s' % list(self.admincommands.keys())
        return commands + "\n" + botalerts + "\n" + lineparsers + "\n" + admincommands

    def isbotadmin(self, nick):
        return nick in self.botadmins

    def commandaccess(self, command):
        if "all" in self.commandaccesslist:
            command = "all"
        if command in self.commandaccesslist:
            if type(self.commandaccesslist[command]) == int:
                if time.time() - self.commandcooldownlast[command] < self.commandaccesslist[command]:
                    return False
                else:
                    self.commandcooldownlast[command] = time.time()
                    return True
            elif self.commandaccesslist[command] == "Disabled":
                return False
        else: #if there's no entry it's assumed to be enabled
            return True

    def isspam(self, user, nick):

        if not (user in self.spam):
            self.spam[user] = {}
            self.spam[user]['count'] = 0
            self.spam[user]['last'] = 0
            self.spam[user]['first'] = 0
            self.spam[user]['limit'] = 15

        self.spam[user]['count'] += 1
        self.spam[user]['last'] = time.time()

        if self.spam[user]['count'] == 1:
            self.spam[user]['first'] = time.time()

        if self.spam[user]['count'] > 1:
            self.spam[user]['limit'] = (self.spam[user]['count'] - 1) * 15

            if not ((self.spam[user]['last'] - self.spam[user]['first']) > self.spam[user]['limit']):
                bantime = self.spam[user]['limit'] + 15
                print("%s : %s band %s seconds" % (time.strftime("%d %b %Y %H:%M:%S", time.localtime()), nick, bantime))
                return True
            else:
                self.spam[user]['first'] = 0
                self.spam[user]['count'] = 0
                self.spam[user]['limit'] = 15
                return False

    def alerts(self, context):
        try:
            for command in self.botalerts:
                say = command()
                if say:
                    for channel in self.channels:
                        context.privmsg(channel, say)
        except Exception as inst:
            print("alerts: " + str(inst))
            pass

        self.t = threading.Timer(60, self.alerts, [context])
        self.t.start()

    class botEvent:
        def __init__(self, source, nick, hostmask, inpt, output="", notice=False):
            self.source = source
            self.nick = nick
            self.input = inpt
            self.output = output
            self.notice = notice
            self.hostmask = hostmask


def main():
    #print sys.argv
    use_ssl=False
    if len(sys.argv) != 4:

        config = configparser.ConfigParser()
        try:
            cfgfile = open('genmaybot.cfg')
        except IOError:
            print("You need to create a .cfg file using the example")
            sys.exit(1)

        config.readfp(cfgfile)
        if config['irc']['nick'] and config['irc']['server'] and config['irc']['channels']:
            nickname = config['irc']['nick']
            server, port = config['irc']['server'].split(":", 1)
            if "+" in port:
                use_ssl=True
                port = port[1:]
            try:
                port = int(port)
            except:
                port = 6667
            channel = config['irc']['channels']
        else:
            print("Usage: bot.py <server[:port]> <channel> <nickname> \nAlternatively configure the server in the .cfg")
            sys.exit(1)

    else:
        s = sys.argv[1].split(":", 1)
        server = s[0]
        if len(s) == 2:
            try:
                port = int(s[1])
            except ValueError:
                print("Error: Erroneous port.")
                sys.exit(1)
        else:
            port = 6667
        channel = sys.argv[2]
        nickname = sys.argv[3]

    bot = Py3Bot(channel, nickname, server, port, use_ssl)
    bot.start()

#this bullshit is necessary because sys.stdout doesn't write the file continuously
class simpleLogger():

    def __init__(self,logfile):
        self.logfile = logfile
        open(logfile,"w").write("") ##clear out any previous contents

    def write(self,logtext):
        logfile = open(self.logfile,"a")
        logfile.write(logtext)
        logfile.close()
        return 0

    def flush(self):
        return 0


if __name__ == "__main__":
    main()

