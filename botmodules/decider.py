import re, random
def decider(self, e):
    if "red dot" in e.input.lower():  
        self.irccontext.mode(e.source, '+b {}'.format(e.hostmask))
        self.irccontext.kick(e.source, e.nick, "Congratulations! You found the word of the day, courtesy of red dot!")
    regex = "^!bot\s(.*?)\s+or\s+(.*?)[?]*$"
    result = re.search(regex, e.input)
    if result:
        if random.randint(0,1) == 0:
            e.output = e.nick + ": " + result.group(1)
        else:
            e.output = e.nick + ": " + result.group(2)
    return e
decider.lineparser = True
