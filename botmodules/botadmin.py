import time, sys, traceback
import threading, sqlite3

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
    self.spam[user]['last'] = time.time()
    self.spam[user]['first'] = time.time()
    self.spam[user]['limit'] = 0
    return "Banned hostmask <{}> for {} minutes".format(hostmask, minutes)

manual_spamban.admincommand = "spamban"

def kill_bot(line, nick, self, c):
    print("got die command from " + nick)
    message = ""
    if line[4:]:
        message = line[4:]
    c.disconnect(message)
    self.t.cancel()
    sys.exit(0)
kill_bot.admincommand = "die"

def nick(line, nick, self, c):
    print(line)
    print(line[5:])
    c.nick(line[5:])
nick.admincommand = "nick"

def clear_bans(line, nick, self, c):
    print(nick + " cleared bans")
    self.spam ={}
    return "All bans cleared"
clear_bans.admincommand = "clearbans"

def reload_modules(line, nick, self, c):
    return self.loadmodules()
reload_modules.admincommand = "reload"


def reload_config(line, nick, self, c):
    return self.load_config()
reload_config.admincommand = "reconfig"


def enable_command(line, nick, self, c):
    if len(line.split(" ")) == 2:
        command = line.split(" ")[1]
        if command in self.commandaccesslist:
            del self.commandaccesslist[command]
            return command + " Enabled"
        else:
            return command + " not disabled"
enable_command.admincommand = "enable"

def disable_command(line, nick, self, c):
    if len(line.split(" ")) == 2:
        command = line.split(" ")[1]
        self.commandaccesslist[command] = "Disabled"
        return command + " Disabled"
disable_command.admincommand = "disable"

def disable_alert(line,nick,self,c):
	if len(line.split(" ")) == 2:
		disable_alert = line.split(" ")[1]
		for alert in self.botalerts:
			if alert.__name__ == disable_alert:
				alert.alert = False
				return disable_alert + " disabled"
disable_alert.admincommand = "disable_alert"

def enable_alert(line,nick,self,c):
	if len(line.split(" ")) == 2:
		enable_alert = line.split(" ")[1]
		for alert in self.botalerts:
			if alert.__name__ == enable_alert:
				alert.alert = True
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
                return command + " cooldown disabled"
            else:
                self.commandaccesslist[command] = cooldown
                self.commandcooldownlast[command] = time.time() - cooldown
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
            return "Left " + chan
        else:
            return "Not in " + chan
part_chan.admincommand = "part"

def say_cmd(line, nick, self, c):
	if len(line.split(" ")) > 2:
		chan = line.split(" ")[1]
		words = " ".join(line.split(" ")[2:])
		c.privmsg(chan, words)
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
                     return "Earthquake alerts containing '%s' will not be shown." % " ".join(line.split(" ")[1:])
                except:
                    traceback.print_exc()
                    return "Quake module doesn't seem to be loaded."
            else:
                return "Correct syntax: quake-filter [title string]   For example: quake-filter Honshu -> this will disable any quake alerts containing the word Honshu"
quake_filter.admincommand = "quake-filter"


def debug_listthreads(line, nick, self, c):
    print(threading.enumerate())
    return "A list of threads has been printed in the event log"
debug_listthreads.admincommand = "listthreads"
