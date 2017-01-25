#! /usr/bin/env python3
#
# To run this bot use the following command:
#
# python genmaybot.py irc.0id.net "#chan" Nickname
#

# look in to !seen functionality
# |- on_join, on_part, on_kick, on_nick, on_quit
# |---use on_whoreply to confirm the users are who their nick is?
# |---check who is in the channel when the bot joins?
# | db: users_table: user UNQ | cur-nick | cur-inchannel BOOL | last action | last-timestamp | <user_aliases> | <user_knownhostmasks>
# | db: user_aliases: user | alternick (allow wildcards in alternick)
# | db: user_knownhostmasks: user | hostmask
# (hostmask might be username | hostmask where username@hostmask
#
# random descision maker?
# test comment please ignore


from irc.bot import SingleServerIRCBot
import time
import imp
import sys
import os
import socket
import configparser
import threading
import traceback

socket.setdefaulttimeout(5)


class TestBot(SingleServerIRCBot):

    def __init__(self, channel, nickname, server, port=6667):
        SingleServerIRCBot.__init__(
            self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.doingcommand = False
        self.botnick = nickname

        self.commandaccesslist = {}
        self.commandcooldownlast = {}

        self.spam = {}

        self.load_config()
        print(self.loadmodules())

        self.keepalive_nick = "OperServ"
        self.alive = True

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
        
        if self.botconfig['irc']['keepalive_timeout'] == "":
            self.botconfig['irc']['keepalive_timeout'] = 120

        sys.stdout = self.event_log
        sys.stderr = self.error_log

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

        c.privmsg("NickServ", "RECOVER %s %s" %
                  (self.botnick, self.botconfig['irc']['identpassword']))

    def on_kick(self, c, e):
        # attempt to rejoin any channel we're kicked from
        if e.arguments[0][0:6] == c.get_nickname():
            c.join(e.target)

    def on_disconnect(self, c, e):
        print("DISCONNECT: " + str(e.arguments))

    def on_welcome(self, c, e):
        c.privmsg(
            "NickServ", "identify " + self.botconfig['irc']['identpassword'])
        c.oper(self.botconfig['irc']['opernick'],
               self.botconfig['irc']['operpassword'])
        c.join(self.channel)
        self.alerts(c)
        self.nick_recover(c)
        self.irccontext = c
        c.who(c.get_nickname())

        self.last_keepalive = time.time()

        self.keepalive(c)

    def on_youreoper(self, c, e):
        print("I'm an IRCop bitches!")

    def on_ison(self, c, e):

        # strip out extraneous space at the end
        ison_reply = e.arguments[0][:-1]

        # print ("Got ISON reply: %s" % e.arguments[0])

        if ison_reply == self.keepalive_nick:
            self.last_keepalive = time.time()
            self.alive = True

    def keepalive(self, irc_context):
        if time.time() - self.last_keepalive > int(self.botconfig['irc']['keepalive_timeout']):
            if not self.alive:
                print("%s: I think we are dead, reconnecting." %
                      time.strftime("%m/%d/%y %H:%M:%S", time.localtime()))
                self.jump_server()
                self.alive = True
                return
            print("%s: Keepalive reply not received, sending request" %
                  time.strftime("%m/%d/%y %H:%M:%S", time.localtime()))
            irc_context.ison([self.keepalive_nick])
            self.alive = False
        else:
            # Send ISON command on configured nick
            irc_context.ison([self.keepalive_nick])
            pass

        self.keepaliveTimer = threading.Timer(
            30, self.keepalive, [irc_context])
        self.keepaliveTimer.start()

    def on_whoishostline(self, c, e):
        try:

            self.whoisIP_reply_handler(
                self, self.whoisIP_sourceEvent, e.arguments[1].split()[-1], "", True)
        except:
            pass  # No whois host line reply handler

    def on_pubmsg(self, c, e):
        self.process_line(c, e)

    def on_privnotice(self, c, e):
        from_nick = e.source.split("!")[0]
        line = e.arguments[0].strip()

        if from_nick == "NickServ":
            if line.find("This nickname is registered and protected.") != -1:
                c.privmsg(
                    "NickServ", "identify " + self.botconfig['irc']['identpassword'])
            # These are responses from NickServ when running the RECOVER
            # command
            elif line.find("Ghost with your nick has been killed.") != -1 or line.find("No one is using your nick, and services are not holding it.") != -1:
                c.nick(self.botconfig['irc']['nick'])

        if from_nick.find(".") == -1:  # Filter out server NOTICEs
            self.mirror_pm(c, from_nick, line, "NOTICE")

    def on_ctcp(self, c, e):
        SingleServerIRCBot.on_ctcp(self, c, e)
        if not e.arguments[0] == "ACTION":  # ignore /me messages
            from_nick = e.source.split("!")[0]
            line = " ".join(e.arguments)
            self.mirror_pm(c, from_nick, line, "CTCP")

    def on_privmsg(self, c, e):
        from_nick = e.source.split("!")[0]
        line = e.arguments[0].strip()
        command = line.split(" ")[0]

        if command in self.admincommands and self.isbotadmin(from_nick):
            self.admincommand = line
            c.whois([from_nick])
		
        # Mirror the PM to the list of admin nicks
        self.mirror_pm(c, from_nick, line, "PM")

        # This sends the PM onward for processing through command parsers
        self.process_line(c, e, True)

    def mirror_pm(self, context, from_nick, line, msgtype="PM"):

        output = "%s: [%s] %s" % (msgtype, from_nick, line)

        try:
            for nick in self.pm_monitor_nicks:
                context.privmsg(nick, output)
        except:
            return

    def on_whoisregnick(self, c, e):
        nick = e.arguments[0]
        line = self.admincommand
        command = line.split(" ")[0]
        self.admincommand = ""
        try:
            if e.arguments[1].find("registered") != -1 and line != "":
                say = self.admincommands[command](line, nick, self, c)
                say = say.split("\n")
                for line in say:
                    c.privmsg(nick, line)

        except Exception as inst:
            traceback.print_exc()
            print("admin exception: " + line + " : " + str(inst))

    def on_whoreply(self, c, e):
        nick = e.arguments[4]

        # The bot does a whois on itself to find its cloaked hostname after it connects
        # This if statement handles that situation and stores the data
        # accordingly
        if nick == c.get_nickname():
            self.realname = e.arguments[1]
            self.hostname = e.arguments[2]
            # The protocol garbage before the real message is
            #:<nick>!<realname>@<hostname> PRIVMSG <target> :
            return


    def process_line(self, c, ircevent, private=False):
        if self.doingcommand:
            return
        self.doingcommand = True

        line = ircevent.arguments[0]
        from_nick = ircevent.source.split("!")[0]
        hostmask = ircevent.source[ircevent.source.find("!") + 1:]
        command = line.split(" ")[0].lower()
        args = line[len(command) + 1:].strip()

        notice = False

        try:
            notice = hasattr(self.bangcommands[command], 'privateonly')
        except:
            pass

        if private or notice:
            linesource = from_nick
        else:
            linesource = ircevent.target

        e = None
        etmp = []

        try:
            # commands names are defined by the module as function.command =
            # "!commandname"
            if command in self.bangcommands and (self.commandaccess(command) or from_nick in self.botadmins):
                e = self.botEvent(linesource, from_nick, hostmask, args)
                # store the bot's nick in the event in case we need it.
                e.botnick = c.get_nickname()

                etmp.append(self.bangcommands[command](self, e))

            # lineparsers take the whole line and nick for EVERY line
            # ensure the lineparser function is short and simple. Try to not to add too many of them
            # Multiple lineparsers can output data, leading to multiple 'say'
            # lines
            for command in self.lineparsers:
                e = self.botEvent(linesource, from_nick, hostmask, line)
                # store the bot's nick in the event in case we need it.
                e.botnick = c.get_nickname()
                etmp.append(command(self, e))

            firstpass = True
            for e in etmp:
                if e and e.output:
                    if firstpass and not e.source == e.nick and not e.nick in self.botadmins:
                        if self.isspam(e.hostmask, e.nick):
                            break
                        firstpass = False
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
            print("bot failed trying to say " +
                  str(botevent.output) + "\n" + str(inst))
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
                        if func.lineparser:
                            self.lineparsers.append(func)

        commands, botalerts, lineparsers, admincommands = "", "", "", ""

        if self.bangcommands:
            commands = 'Loaded command modules: %s' % list(
                self.bangcommands.keys())
        else:
            commands = "No command modules loaded!"
        if self.botalerts:
            botalerts = 'Loaded alerts: %s' % ', '.join(
                (command.__name__ for command in self.botalerts))
        if self.lineparsers:
            lineparsers = 'Loaded line parsers: %s' % ', '.join(
                (command.__name__ for command in self.lineparsers))
        if self.admincommands:
            admincommands = 'Loaded admin commands: %s' % list(
                self.admincommands.keys())
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
        else:  # if there's no entry it's assumed to be enabled
            return True

    def isspam(self, user, nick):
        # Set the number of allowed lines to whatever is in the .cfg file
        allow_lines = int(self.botconfig['irc']['spam_protect_lines'])

        # Clean up ever-growing spam dictionary
        cleanupkeys = []
        for key in self.spam:
            # anything older than 24 hours
            if (time.time() - self.spam[key]['last']) > (24 * 3600):
                cleanupkeys.append(key)
        for key in cleanupkeys:
            self.spam.pop(key)
        # end clean up job

        if not (user in self.spam):
            self.spam[user] = {}
            self.spam[user]['count'] = 0
            self.spam[user]['last'] = 0
            self.spam[user]['first'] = 0
            self.spam[user]['limit'] = 30

        self.spam[user]['count'] += 1
        self.spam[user]['last'] = time.time()

        if self.spam[user]['count'] <= allow_lines:
            self.spam[user]['first'] = time.time()
            return False

        if self.spam[user]['count'] > allow_lines:
            self.spam[user]['limit'] = (self.spam[user]['count'] - 1) * 15

            if not ((self.spam[user]['last'] - self.spam[user]['first']) > self.spam[user]['limit']):
                bantime = self.spam[user]['limit'] + 15
                print("%s : %s band %s seconds" % (
                    time.strftime("%d %b %Y %H:%M:%S", time.localtime()), nick, bantime))
                return True
            else:
                self.spam[user]['first'] = 0
                self.spam[user]['count'] = 1
                self.spam[user]['limit'] = 30
                return False

    def nick_recover(self, context):
        # Check if our nickname is different than configured for some reason
        if context.get_nickname() != self.botconfig['irc']['nick']:

            # Try to recover using NickServ
            context.privmsg("NickServ", "RECOVER %s %s" %
                            (self.botconfig['irc']['nick'], self.botconfig['irc']['identpassword']))
            # The actual nick renaming happens when NickServ tells us the nick
            # has been recovered.

        # Start a timer thread to keep checking and tryng to recover our
        # nickname
        self.nick_recover_thread = threading.Timer(
            5, self.nick_recover, [context])
        self.nick_recover_thread.start()

    def alerts(self, context):
        try:
            for command in self.botalerts:
                if command.alert:  # check if alert is actually enabled
                    say = command()
                    if say:
                        for channel in self.channels:
                            if channel != '#bopgun' and channel != '#fsw':
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
    # print sys.argv

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
            try:
                port = int(port)
            except:
                port = 6667
            channel = config['irc']['channels']
        else:
            print(
                "Usage: bot.py <server[:port]> <channel> <nickname> \nAlternatively configure the server in the .cfg")
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

    bot = TestBot(channel, nickname, server, port)
    bot.start()

# this bullshit is necessary because sys.stdout doesn't write the file
# continuously


class simpleLogger():

    def __init__(self, logfile):
        self.logfile = logfile
        open(logfile, "w").write("")  # clear out any previous contents

    def write(self, logtext):
        logfile = open(self.logfile, "a")
        logfile.write(logtext)
        logfile.close()
        return 0

    def flush(self):
        return 0


if __name__ == "__main__":
    main()
