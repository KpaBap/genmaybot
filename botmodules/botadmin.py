import time, sys, traceback
import threading, sqlite3
import requests
import uuid

def __init__(self):
    self.pm_monitor_nicks = []
    
    conn = sqlite3.connect('admins.sqlite')
    sqlcur = conn.cursor()
    result = sqlcur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_info';").fetchone()
    
    if not result: #if table is not found
        sqlcur.execute('''create table admin_info(nick text UNIQUE ON CONFLICT REPLACE, pm_monitor_enabled integer)''')
        conn.commit()
    else:
        sqlcur.execute("SELECT nick FROM admin_info WHERE pm_monitor_enabled = ?", [True])
        for nick in sqlcur.fetchall():
            self.pm_monitor_nicks.append(nick[0])
    
    
def who_partyline(line, nick, self, c): #Returns a list of users who have joined the party line
    try:
        output = ", ".join(self.pm_monitor_nicks)
        if output:
            return "Admins online: %s" % output
    except:
        return "No one is online at the moment."
        
        
who_partyline.admincommand = "who"

def monitor_pm(line,nick,self,c):
    conn = sqlite3.connect('admins.sqlite')
    sqlcur = conn.cursor()
    result = sqlcur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_info';").fetchone()
    
    if not result: #if table is not found
        sqlcur.execute('''create table admin_info(nick text UNIQUE ON CONFLICT REPLACE, pm_monitor_enabled integer)''')
        conn.commit()


    if line.split(" ")[1] == "on":
        try:
            if nick in self.pm_monitor_nicks:
                return "PM monitoring already enabled. 'monitorpm off' to disable."
            else:
                self.pm_monitor_nicks.append(nick)
                
                sqlcur.execute("INSERT OR REPLACE INTO admin_info (nick, pm_monitor_enabled) VALUES (?, ?)", [nick, True])
                conn.commit()
                
                for mon_nick in self.pm_monitor_nicks:
                    c.privmsg(mon_nick, "%s joined the party line." % nick)
                return "Enabled PM monitoring. All PMs will be mirrored to you."	
        except: # Initialize monitor nick list if it doesn't exist
            self.pm_monitor_nicks = []
            self.pm_monitor_nicks.append(nick)
            
            sqlcur.execute("INSERT OR REPLACE INTO admin_info (nick, pm_monitor_enabled) VALUES (?, ?)", [nick, True])
            conn.commit()
            
            return "Enabled PM monitoring. All PMs will be mirrored to you. You're the first one on the party line."	


    elif line.split(" ")[1] == "off":
        try:
            if nick in self.pm_monitor_nicks:
                self.pm_monitor_nicks.remove(nick)
                
                sqlcur.execute("UPDATE admin_info SET pm_monitor_enabled = ? WHERE nick = ?", [False, nick])
                conn.commit()
                
                for mon_nick in self.pm_monitor_nicks:
                    c.privmsg(mon_nick, "%s left the party line." % nick)
                return "Disabled PM monitoring."
            else:
                return "PM monitoring is not enabled for you. 'monitorpm on' to enable."
        except: #PM monitoring was NEVER enabled
            return "PM monitoring is not enabled for you. 'monitorpm on' to enable."
    else:
        return "Usage: monitorpm on|off - mirrors all PMs sent to the bot to you"

monitor_pm.admincommand="monitorpm"

#test commit
def manual_spamban(line, nick, self, c):
    try:
        command, hostmask, minutes = line.split(" ")
        if int(minutes) < 2:
            minutes = 2
    except:
        return "Command format is: spamban user@host <number of minutes to ban>"
    self.spam[hostmask] = {}
    bancount = (int(minutes)*60)/15
    self.spam[hostmask]['count'] = bancount
    self.spam[hostmask]['last'] = time.time()
    self.spam[hostmask]['first'] = time.time()
    self.spam[hostmask]['limit'] = 0
    self.logger.info("Spam ban of ({}) for {} min, requested by admin ({})".format(hostmask, minutes, nick))
    return "Banned hostmask <{}> for {} minutes".format(hostmask, minutes)

manual_spamban.admincommand = "spamban"

def kill_bot(line, nick, self, c):
    self.logger.info("Got die command from {}".format(nick))
    message = ""
    if line[4:]:
        message = line[4:]
    c.disconnect(message)
    self.t.cancel()
    sys.exit(0)
kill_bot.admincommand = "die"

def nick(line, nick, self, c):
    c.nick(line[5:])
    output = "Changing nickname to {}, requested by {}".format(line[5:], nick)
    self.logger.info(output)
    return output
nick.admincommand = "nick"

def clear_bans(line, nick, self, c):
    self.logger.info("Admin ({}) cleared bans".format(nick))
    self.spam ={}
    return "All bans cleared"
clear_bans.admincommand = "clearbans"

def reload_modules(line, nick, self, c):
    self.logger.info("Module reload requested by admin ({})".format(nick))
    return self.loadmodules()
reload_modules.admincommand = "reload"


def reload_config(line, nick, self, c):
    self.logger.info("Config reload requested by admin {}".format(nick))
    return self.load_config()
reload_config.admincommand = "reconfig"


def enable_command(line, nick, self, c):
    if len(line.split(" ")) == 2:
        command = line.split(" ")[1]
        if command in self.commandaccesslist:
            del self.commandaccesslist[command]
            self.logger.info("Command ({}) enabled by admin ({})".format(command, nick))
            return command + " Enabled"
        else:
            return command + " not disabled"
enable_command.admincommand = "enable"

def disable_command(line, nick, self, c):
    if len(line.split(" ")) == 2:
        command = line.split(" ")[1]
        self.commandaccesslist[command] = "Disabled"
        self.logger.info("Command ({}) disabled by admin ({})".format(command, nick))
        return command + " Disabled"
disable_command.admincommand = "disable"

def disable_alert(line,nick,self,c):
    if len(line.split(" ")) == 2:
        disable_alert = line.split(" ")[1]
        for alert in self.botalerts:
            if alert.__name__ == disable_alert:
                alert.alert = False
                self.logger.info("Alert ({}) disabled by admin ({})".format(alert, nick))
                return disable_alert + " disabled"
disable_alert.admincommand = "disable_alert"

def enable_alert(line,nick,self,c):
    if len(line.split(" ")) == 2:
        enable_alert = line.split(" ")[1]
        for alert in self.botalerts:
            if alert.__name__ == enable_alert:
                alert.alert = True
                self.logger.info("Alert ({}) disabled by admin ({})".format(alert, nick))
                return disable_alert + " enabled"
enable_alert.admincommand = "enable_alert"


def cooldown_command(line, nick, self, c):
    if len(line.split(" ")) == 3:
        command = line.split(" ")[1]
        cooldown = line.split(" ")[2]
        if cooldown.isdigit():
            cooldown = int(cooldown)
            if cooldown == 0:
                if command in self.commandaccesslist:
                    del self.commandaccesslist[command]
                    self.logger.info("Cooldown for command ({}) disabled by admin ({})".format(command, nick))
                return command + " cooldown disabled"
            else:
                self.commandaccesslist[command] = cooldown
                self.commandcooldownlast[command] = time.time() - cooldown
                self.logger.info("Cooldown for command ({}) set to {} sec by admin ({})".format(command, cooldown, nick))
                return command + " cooldown set to " + str(cooldown) + " seconds (set to 0 to disable)"
        else:
            return "bad format: 'cooldown !wiki 30' (30 second cooldown on !wiki)"
    else:
        return "not enough perameters: cooldown !command ##"
cooldown_command.admincommand = "cooldown"

def command_status(line, nick, self, c):
    if len(line.split(" ")) == 2:
        command = line.split(" ")[1]
        if command in self.commandaccesslist:
            return command + " " + str(self.commandaccesslist[command]) + " (Seconds cooldown if it's a number)"
        else:
            return command + " Enabled"
    elif len(line.split(" ")) == 1:
        return str(list(self.commandaccesslist.items()))

command_status.admincommand = "status"

def join_chan(line, nick, self, c):
    if len(line.split(" ")) == 2:
        chan = line.split(" ")[1]
        if chan[0:1] != "#":
            return "not a valid channel name"
        if chan in self.channels:
            return "Already in " + chan
        else:
            c.join(chan)
            self.logger.info("Joined channel ({}), requested by admin ({})".format(chan, nick))
            return "Joined " + chan
join_chan.admincommand = "join"

def part_chan(line, nick, self, c):
    if len(line.split(" ")) >= 2:
        chan = line.split(" ")[1]
        message = ""
        if len(line.split(" ")) > 2:
            message = " ".join(line.split(" ")[2:])
        if chan[0:1] != "#":
            return "not a valid channel name: Part #chan part message here"
        if chan in self.channels:
            c.part(chan, message)
            self.logger.info("Left channel ({}), requested by admin ({})".format(chan, nick))
            return "Left " + chan
        else:
            return "Not in " + chan
part_chan.admincommand = "part"

def say_cmd(line, nick, self, c):
    if len(line.split(" ")) > 2:
        chan = line.split(" ")[1]
        words = " ".join(line.split(" ")[2:])
        c.privmsg(chan, words)
        self.logger.info("Said ({}) to ({}), requested by admin ({})".format(chan, words, nick))
        return "Said %s to %s" % (words, chan)
    else:
        return "Correct syntax: say [#channel/nickname] I hate you!"
say_cmd.admincommand="say"

def show_channels(line, nck, self, c):
    return ", ".join(self.channels)
show_channels.admincommand = "channels"

def quake_filter(line, nick, self, c):
    for alert in self.botalerts:
        if alert.__name__ == "quake_alert":
            if len(line.split(" ")) >= 2:
                try:
                     alert.filter = " ".join(line.split(" ")[1:])
                     self.logger.info("Earhtquake alerts containing '{}' will not be shown, requested by admin ({})".format(alert.filter, nick))
                     return "Earthquake alerts containing '%s' will not be shown." % " ".join(line.split(" ")[1:])
                except:
                    self.logger.exception("Quake module doesn't seem to be loaded:")
                    return "Quake module doesn't seem to be loaded."
            else:
                return "Correct syntax: quake-filter [title string]   For example: quake-filter Honshu -> this will disable any quake alerts containing the word Honshu"
quake_filter.admincommand = "quake-filter"


def debug_listthreads(line, nick, self, c):
    self.logger.debug(threading.enumerate())
    return "A list of threads has been printed in the event log"
debug_listthreads.admincommand = "listthreads"

def admin_ui(line, nick, self, irc_context):
    resp = requests.get("https://api.ipify.org")
    if not resp.text or not resp.ok:
        return "Failed to get IP from ipify.org"

    ip = resp.text
    port = self.botconfig['webui']['port']
    self.botadmin_webui_tokens[nick] = str(uuid.uuid4())
    self.logger.info("Admin ({}) requested webUI URL".format(nick))
    return "Admin UI is at http://{}:{}/auth/login?admin={}&token={}".format(ip, port, nick, self.botadmin_webui_tokens[nick])


admin_ui.admincommand="adminui"

def test_all_commands(line, nick, self, irc_context):
    input = " ".join(line.split(" ")[1:])
    from genmaybot import TestBot


    for command in self.bangcommands:
        event = TestBot.Botevent(nick, nick, "testuser@testhost.test", input)
        event.botnick = irc_context.get_nickname()
        try:
            event.output = "Command: {} Input: {} Output: {}\n".format(command, input, self.bangcommands[command](self, event).output)
            self.bot_say(event)
        except:
            self.logger.exception("Command: ({}) Input: ({}) Exception:".format(command, input))
            event.output = "Command: {} Input: {} Exception: {}".format(command, input, sys.exc_info())
            self.bot_say(event)



test_all_commands.admincommand="testall"