import threading, operator

def poll(self, event):
    poll.onnow = False
    winners = []
    maxkey = max(iter(poll.votes.items()), key=operator.itemgetter(1))[0]
    for key,value in list(poll.votes.items()):
        if value == poll.votes[maxkey]:
            winners.append(key)
    s = "s"
    if poll.votes[maxkey] == 1:
        s = ""
    if len(winners) > 1:
        event.output = "[Poll ended] %s : %s are tied with %s vote%s!" % (poll.question, ", ".join(winners), poll.votes[maxkey], s)  
    else: 
        event.output = "[Poll ended] %s : %s is the winner with %s vote%s!" % (poll.question, maxkey, poll.votes[maxkey], s)  
    self.bot_say(event)
poll.onnow = False
poll.users = []
poll.votes = {}
poll.question = ''

def poll_parser(self, event):
    if poll.onnow and event.input.lower() in poll.votes:
        if event.hostmask in poll.users:
            event.output = "You have already voted!"
        else:
            poll.users.append(event.hostmask)
            poll.votes[event.input.lower()] += 1
            event.output = "Vote: '%s' registered" % event.input
        
        event.source = event.nick
        event.notice = True
        return event
    else:
        return None
poll_parser.lineparser = True

def new_poll(self, event):
    if poll.onnow:
        event.source = event.nick
        event.notice = True
        event.output = "There is already a poll currently voting. You can not start a new one until the current one finishes."
        return event
    
    poll.users = []
    poll.votes = {}
    
    badsyntax = False
    if event.input == "" or len(event.input.split(" ")) < 1:
        badsyntax = True
    else:
        pollmins = event.input.split(" ")[0]
        if pollmins.isdigit(): 
            question = event.input[len(pollmins) + 1:]
            pollmins = min(int(pollmins), 5)
        else:
            pollmins = 1
            question = event.input
            
        if question.find("options:") != -1:
            options = question[question.find("options:") + 8:].strip()
            for option in options.split(","):
                option = option.strip().lower()
                poll.votes[option] = 0
            question = question[0:question.find("options:")]
        else:
            poll.votes = {"yes!" : 0, "no!" : 0}
            options = "Yes!, No!"
        
        if question and pollmins:
            poll.question = question
            event.output = "[Poll by %s] %s\nYou have %s minute(s) to vote. Possible poll options: %s" % (event.nick, question, str(pollmins), options)
        else:
            badsyntax = True
                  
    if badsyntax:
        event.source = event.nick
        event.notice = True
        event.output = "Bad syntax\n" + new_poll.helptext
    else:
        poll.onnow=True
        t=threading.Timer(60 * pollmins, poll, [self, event])
        t.start()
        
    return event
new_poll.command = "!poll"
new_poll.helptext = "Usage: !poll [<minutes>] <poll question> [options: <options>]\nExample: !poll 2 Should I go to bed?\nCreates a 2 minute long yes or no poll for the channel\nExample #2: !poll 2 What should I eat? options: pizza!, chicken!, burger!\nCreates a 2 minute poll with custom vote options"

