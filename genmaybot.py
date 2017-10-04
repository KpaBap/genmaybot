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
import irc
import time
import importlib
import sys
import os
import socket
import configparser
import threading
import traceback
import textwrap
import logging, logging.handlers
from jaraco.stream import buffer
import html


# We need this in order to catch whois reply from a registered nick.
irc.events.numeric["307"] = "whoisregnick"
socket.setdefaulttimeout(5)


class TestBot(SingleServerIRCBot):

    def __init__(self, channel, nickname, server, port=6667):
        SingleServerIRCBot.__init__(
            self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.doingcommand = False

        self.connection.buffer_class = buffer.LenientDecodingLineBuffer

        self.botnick = nickname
        self.logger = logging.getLogger(self.botnick)
        self.logger.info("Connecting with nickname ({}) to server {}:{}".format(self.botnick, server, port))

        self.commandaccesslist = {}
        self.commandcooldownlast = {}

        self.spam = {}

        self.load_config()
        self.logger.info(self.loadmodules())

        self.admincommand = None


        self.alive = True

    def load_config(self):
        config = configparser.ConfigParser()
        try:
            cfgfile = open('genmaybot.cfg')
        except IOError:
            logging.exception("You need to create a .cfg file using the example")
            sys.exit(1)

        config.read_file(cfgfile)
        self.botconfig = config
        self.botadmins = config["irc"]["botadmins"].split(",")
        self.botadmin_webui_tokens = {}
        # Tokens for the web UI
        for admin in self.botadmins:
            self.botadmin_webui_tokens[admin] = None

        self.logger.info("Bot admins: {}".format(self.botadmins))
        if self.botconfig['irc']['keepalive_timeout'] == "":
            self.botconfig['irc']['keepalive_timeout'] = 120

        if self.botconfig['irc']['keepalive_nick'] == "":
            self.botconfig['irc']['keepalive_nick'] = "OperServ"


    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

        c.privmsg("NickServ", "RECOVER %s %s" %
                  (self.botnick, self.botconfig['irc']['identpassword']))

    def on_kick(self, c, e):
        # attempt to rejoin any channel we're kicked from
        if e.arguments[0][0:6] == c.get_nickname():
            self.logger.info("Kicked from ({}) attempting to rejoin...".format(e.target))
            c.join(e.target)

    def on_disconnect(self, c, e):
        self.logger.info("DISCONNECT: " + str(e.arguments))

    def on_welcome(self, c, e):
        c.privmsg(
            "NickServ", "identify " + self.botconfig['irc']['identpassword'])
        self.logger.info("Identifying with NickServ...")

        c.oper(self.botconfig['irc']['opernick'],
               self.botconfig['irc']['operpassword'])
        self.logger.info("Attempting to become IRCop...")

        if self.channel:
            self.logger.info("Joining channel: ({})".format(self.channel))
        c.join(self.channel)


        self.alerts(c)
        self.nick_recover(c)
        self.irccontext = c
        c.who(c.get_nickname())

        self.last_keepalive = time.time()

        self.keepalive(c)

    def on_youreoper(self, c, e):
        self.logger.info("I'm an IRCop bitches!")

    def on_ison(self, c, e):

        # strip out extraneous space at the end
        ison_reply = e.arguments[0][:-1]

        self.logger.debug("Got ISON reply: {}".format(e.arguments[0]))

        if ison_reply == self.botconfig['irc']['keepalive_nick']:
            self.last_keepalive = time.time()
            self.alive = True

    def keepalive(self, irc_context):
        if time.time() - self.last_keepalive > int(self.botconfig['irc']['keepalive_timeout']):
            if not self.alive:
                self.logger.info("I think we are dead, reconnecting.")
                self.jump_server()
                self.alive = True
                return
            self.logger.info("Keepalive reply not received, sending request")
            irc_context.ison([self.botconfig['irc']['keepalive_nick']])
            self.alive = False
        else:
            # Send ISON command on configured nick
            irc_context.ison([self.botconfig['irc']['keepalive_nick']])

        self.keepaliveTimer = threading.Timer(
            3, self.keepalive, [irc_context])
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
                self.logger.info("NickServ requested identification.")
                c.privmsg(
                    "NickServ", "identify " + self.botconfig['irc']['identpassword'])
            # These are responses from NickServ when running the RECOVER
            # command
            elif line.find("Ghost with your nick has been killed.") != -1 or line.find("No one is using your nick, and services are not holding it.") != -1:
                self.logger.info("Nickname successfully recovered.")
                c.nick(self.botconfig['irc']['nick'])

        if from_nick.find(".") == -1:  # Filter out server NOTICEs
            self.mirror_pm(c, from_nick, line, "NOTICE")

    def on_ctcp(self, c, e):
        super(TestBot, self).on_ctcp(c, e)
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
                self.split_privmsg(context, nick, output)
        except:
            return

    def on_whoisregnick(self, c, e):
        nick = e.arguments[0]
        if not self.admincommand:
            return
        line = self.admincommand
        command = line.split(" ")[0]
        self.admincommand = ""
        try:
            if e.arguments[1].find("registered") != -1 and line != "":
                say = self.admincommands[command](line, nick, self, c)
                say = say.split("\n")
                for line in say:
                    self.split_privmsg(c, nick, line)

        except Exception:
            self.logger.exception("Admin command: ({}) Exception:".format(command))
    def on_whoreply(self, c, e):
        nick = e.arguments[4]

        # The bot does a whois on itself to find its cloaked hostname after it connects
        # This if statement handles that situation and stores the data
        # accordingly
        if nick == c.get_nickname():
            self.realname = e.arguments[1]
            self.hostname = e.arguments[2]
            # The protocol garbage before the real message is
            # :<nick>!<realname>@<hostname> PRIVMSG <target> :
            return

    def process_line(self, c, ircevent, private=False):
        if self.doingcommand:
            self.logger.debug("Got a command while processing a previous one.")
            return
        self.doingcommand = True

        line = ircevent.arguments[0]
        from_nick = ircevent.source.split("!")[0]
        hostmask = ircevent.source[ircevent.source.find("!") + 1:]
        command = line.split(" ")[0].lower()
        args = line[len(command) + 1:].strip()
        
        if "ducky" in hostmask.lower() or "ucky" in from_nick.lower():
            return
        
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
                e = self.Botevent(linesource, from_nick, hostmask, args)
                # store the bot's nick in the event in case we need it.
                e.botnick = c.get_nickname()
                self.logger.debug("Got command ({}) from nick ({})".format(command, from_nick))

                etmp.append(self.bangcommands[command](self, e))
                self.logger.debug("Command: ({}) Output: ({})".format(command, e.output))

            # lineparsers take the whole line and nick for EVERY line
            # ensure the lineparser function is short and simple. Try to not to add too many of them
            # Multiple lineparsers can output data, leading to multiple 'say'
            # lines
            for command in self.lineparsers:
                e = self.Botevent(linesource, from_nick, hostmask, line)
                # store the bot's nick in the event in case we need it.
                e.botnick = c.get_nickname()
                try:
                    etmp.append(command(self, e))
                except:
                    self.logger.exception("Line parser: ({}) Exception:".format(command))

            firstpass = True
            for e in etmp:
                if e and e.output:
                    if firstpass and not e.source == e.nick and not e.nick in self.botadmins:
                        if self.isspam(e.hostmask, e.nick):
                            bantime = self.spam[e.hostmask]['limit'] + 15
                            output = "You've been ignored for {} seconds. Slow your roll and try again later.".format(bantime)
                            self.irccontext.notice(e.nick, output)
                            break
                        firstpass = False

                    self.bot_say(e)

        except:
            self.logger.exception("Command: ({}) Exception:".format(command))
            try:
                e = self.bangcommands["!error"](self, e)
            except:
                e.output = "Command failed: {}".format(sys.exc_info())

            self.bot_say(e)


        self.doingcommand = False
        return

    def split_privmsg(self, client, nick, output):
        output_max_length = 510 - len("PRIVMSG %s :" % nick)
        for line in textwrap.wrap(output, output_max_length):
            client.privmsg(nick, line)

    def bot_say(self, botevent):
        try:
            if botevent.output:
                for line in botevent.output.split("\n"):
                    line = html.unescape(line)
                    if botevent.notice:
                        self.irccontext.notice(botevent.source, line)
                    else:
                        self.irccontext.privmsg(botevent.source, line)
        except Exception:
            self.logger.exception("Bot failed trying to say: ({}) Exception: ({}) ".format(botevent.output))


    def loadmodules(self):

        tools_spec = importlib.util.spec_from_file_location("tools", "./botmodules/tools.py")
        self.tools = importlib.util.module_from_spec(tools_spec)
        tools_spec.loader.exec_module(self.tools)
        try:
            self.tools.__init__(self)
            self.tools = vars(self.tools)
        except:
            self.logger.exception("Could not initialize tools.py:")


        filenames = []
        for fn in os.listdir('./botmodules'):
            if fn.endswith('.py') and not fn.startswith('_') and fn.find("tools.py") == -1:
                filenames.append(os.path.join('./botmodules', fn))

        self.logger.debug("Module files found: {}".format(filenames))

        self.bangcommands = {}
        self.admincommands = {}
        self.botalerts = []
        self.lineparsers = []

        for filename in filenames:
            name = os.path.basename(filename)[:-3]
            try:
                spec = importlib.util.spec_from_file_location(name, filename)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except Exception:
                self.logger.exception("Error loading module: {} Exception:".format(name))
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
                    elif hasattr(func, 'lineparser') and func.lineparser:
                        self.lineparsers.append(func)

        commands, botalerts, lineparsers, admincommands = "", "", "", ""

        if self.bangcommands:
            commands = 'Loaded command modules: %s' % list(
                self.bangcommands.keys())
        else:
            commands = "No command modules loaded!"
        if self.botalerts:
            botalerts = 'Loaded alerts: %s' % ', '.join(
                command.__name__ for command in self.botalerts)
        if self.lineparsers:
            lineparsers = 'Loaded line parsers: %s' % ', '.join(
                command.__name__ for command in self.lineparsers)
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

        if not user in self.spam:
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

            time_since_first_line = self.spam[user]['last'] - self.spam[user]['first']
            if time_since_first_line < self.spam[user]['limit']:
                bantime = self.spam[user]['limit'] + 15
                self.logger.info("Nick ({}) ignored for {} seconds. {} lines received in {} seconds".format(nick,
                                                                                                             bantime,
                                                                                                             self.spam[user]['count'],
                                                                                                             time_since_first_line))
                return True
            else:
                self.spam[user]['first'] = 0
                self.spam[user]['count'] = 1
                self.spam[user]['limit'] = 30
                return False

    def nick_recover(self, context):
        # Check if our nickname is different than configured for some reason
        if context.get_nickname() != self.botconfig['irc']['nick']:
            self.logger.info("Trying to recover nickname from NickServ")
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
                                self.split_privmsg(context, channel, say)
        except Exception:
            self.logger.exception("Alert: ({}) Exception:".format(command))

        self.t = threading.Timer(60, self.alerts, [context])
        self.t.start()

    class Botevent:

        def __init__(self, source, nick, hostmask, inpt, output="", notice=False):
            self.source = source
            self.nick = nick
            self.input = inpt
            self.output = output
            self.notice = notice
            self.hostmask = hostmask


def main():
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    root_logger = logging.getLogger('')
    root_logger.addHandler(console)
    root_logger.setLevel(logging.DEBUG)
    retries = 0

    if len(sys.argv) != 4:

        config = configparser.ConfigParser()
        try:
            cfgfile = open('genmaybot.cfg')
        except IOError:
            root_logger.exception("You need to create a .cfg file using the example")
            sys.exit(1)

        config.read_file(cfgfile)
        DEBUG_LOG_FILENAME = config['misc']['debug_log']
        EVENT_LOG_FILENAME = config['misc']['event_log']
        if config['misc']['spawn_failure_retries'] == "":
            config['misc']['spawn_failure_retries'] = 2


        if not DEBUG_LOG_FILENAME or not EVENT_LOG_FILENAME:
            root_logger.error("Please configure debug and event log filenames in the config file. Using defaults for now.")
            config['misc']['debug_log'] = "bot_debug.log"
            config['misc']['event_log'] = "bot_event.log"
            DEBUG_LOG_FILENAME = config['misc']['debug_log']
            EVENT_LOG_FILENAME = config['misc']['event_log']


        debug_log_handler = logging.handlers.RotatingFileHandler(
            DEBUG_LOG_FILENAME, maxBytes=2*(1024**2), backupCount=20)
        event_log_handler = logging.handlers.RotatingFileHandler(
            EVENT_LOG_FILENAME, maxBytes=2*(1024**2), backupCount=20)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s", datefmt='%m-%d %H:%M:%S')

        debug_log_handler.setLevel(logging.DEBUG)
        event_log_handler.setLevel(logging.INFO)
        debug_log_handler.setFormatter(formatter)
        event_log_handler.setFormatter(formatter)

        root_logger.addHandler(debug_log_handler)
        root_logger.addHandler(event_log_handler)

        root_logger.info("\n----------------------- START OF BOT PROCESS -----------------------\n")

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
                root_logger.exception("Error: Erroneous port.")
                sys.exit(1)
        else:
            port = 6667
        channel = sys.argv[2]
        nickname = sys.argv[3]
    while retries <= int(config['misc']['spawn_failure_retries']):
        retries += 1
        try:
            bot = TestBot(channel, nickname, server, port)
            bot.start()
        except OSError:
            root_logger.exception("Something went horribly wrong while trying to spawn the bot (try #{}):".format(retries))

    root_logger.error("Could not recover. Exiting process.")
    os._exit(1) #JUST DIE ALREADY

if __name__ == "__main__":
    try:
        main()
    except:
        logging.exception("Exception in main thread, big trouble:")
        sys.exit(1)
