import random
import urllib.request, urllib.error, urllib.parse
from datetime import datetime, timedelta

def error_generator(self, e):
    firstword = firstwords[random.randint(0, len(firstwords) - 1)]
    secondword = secondwords[random.randint(0, len(secondwords) - 1)]
    thirdword = secondwords[random.randint(0, len(thirdwords) - 1)]
    rand5 = random.randint(0, 3)
    fourthword = fourthwords[rand5]
    heading = ("Error: ", "Problem: ", "Warning: ", "Signal: ")
    e.output = "%s%s %s %s %s" % (heading[rand5], firstword, secondword, thirdword, fourthword)
    return e

error_generator.command = "!error"
error_generator.helptext = "Usage: !error\nGenerates a random scary-sounding error message"

firstwords = ["Temporary", "Intermittant", "Partial", "Redundant", "Total",
                "Multiplexed", "Inherent", "Duplicated", "Dual-Homed", "Synchronous",
                "Bidirectional", "Serial", "Asynchronous", "Multiple", "Replicated",
                "Non-Replicated", "Unregistered", "Non-Specific", "Generic", "Migrated",
                "Localised", "Resignalled", "Dereferenced", "Nullified", "Aborted",
                "Serious", "Minor", "Major", "Extraneous", "Illegal", "Insufficient",
                "Viral", "Unsupported", "Outmoded", "Legacy", "Permanent", "Invalid",
                "Deprecated", "Virtual", "Unreportable", "Undetermined", "Undiagnosable",
                "Unfiltered", "Static", "Dynamic", "Delayed", "Immediate", "Nonfatal",
                "Fatal", "Non-Valid", "Unvalidated", "Non-Static", "Unreplicatable",
                "Non-Serious"]

secondwords = ["Array", "Systems", "Hardware", "Software", "Firmware",
                "Backplane", "Logic-Subsystem", "Integrity", "Subsystem", "Memory",
                "Comms", "Integrity", "Checksum", "Protocol", "Parity", "Bus", "Timing",
                "Synchronisation", "Topology", "Transmission", "Reception", "Stack",
                "Framing", "Code", "Programming", "Peripheral", "Environmental",
                "Loading", "Operation", "Parameter", "Syntax", "Initialisation",
                "Execution", "Resource", "Encryption", "Decryption", "File",
                "Precondition", "Authentication", "Paging", "Swapfile", "Service",
                "Gateway", "Request", "Proxy", "Media", "Registry", "Configuration",
                "Metadata", "Streaming", "Retrieval", "Installation", "Library", "Handler"]

thirdwords = ["Interruption", "Destabilisation", "Destruction",
                "Desynchronisation", "Failure", "Dereferencing", "Overflow", "Underflow",
                "NMI", "Interrupt", "Corruption", "Anomoly", "Seizure", "Override",
                "Reclock", "Rejection", "Invalidation", "Halt", "Exhaustion", "Infection",
                "Incompatibility", "Timeout", "Expiry", "Unavailability", "Bug",
                "Condition", "Crash", "Dump", "Crashdump", "Stackdump", "Problem",
                "Lockout"]

fourthwords = ["Error", "Problem", "Warning", "Signal", "Flag"]


def mba_generator(self, e):
    verb = verbs[random.randint(0, len(verbs) - 1)]
    adjective = adjectives[random.randint(0, len(adjectives) - 1)]
    noun = nouns[random.randint(0, len(nouns) - 1)]
    e.output = "%s %s %s" % (verb, adjective, noun)
    return e

mba_generator.command = "!mba"
mba_generator.helptext = "Usage: !mba\nGenerates random corporate jargon"


def development_generator(self, e):
    verb = seng_thirdwords[random.randint(0, len(seng_thirdwords) - 1)]
    adjective = seng_firstwords[random.randint(0, len(seng_firstwords) - 1)]
    noun = seng_secondwords[random.randint(0, len(seng_secondwords) - 1)]
    e.output = "%s %s %s" % (verb, adjective, noun)
    return e


development_generator.command = "!developers"
development_generator.helptext = "Usage: !developers\nGenerates random programming engineering bullshit"

# Adjectives
seng_firstwords = ["Sequential", "Downwards", "Structural", "Modified", "Extreme", "Up Front", "Waterfall", "Agile", "Critical", "Flawed",
"Top-Down", "Discrete", "Evolutionary", "Initial", "Scrum", "Horizontal", "Usability", "Throwaway", "Rapid", "Incremental", "Extreme", "Reduced", "Insufficient",
"Dynamic", "Business", "Operating", "Rapid", "Object-Oriented", "Iterative", "Unified", "V-Model", "Linear", "Unit", "Spiral", "Daily", "Retrospective", "Epic", "Rockstar"]
# Nouns
seng_secondwords = ["Prototype", "Software", "Critical View", "Requirements Specification", "Model", "Architecture", "Meeting", "Products", "Objectives", "Logic",
"Application", "Environment", "Task", "Deployment", "Process", "Abstraction", "Data Structure", "NoSQL", "Web 2.0", "XML", "XSL", "Memcache", "Cloud", "Cluster",
"Version Control", "Code", "Feedback Loop", "Master", "Stakeholders", "Managers", "Storytime", "User Story", "Programmer"]
# Verbs
seng_thirdwords = ["Design", "Maintenance", "Testing", "Production", "Implementation", "Research", "Conception", "Analysis", "Initiation",
"Programming", "Development", "Review", "Verification", "Replication", "Evaluate", "Integrate", "Sprint", "Backlog Grooming", "Termination"]


def bbnet(self, e):
    if e.nick.lower().startswith('rc'):
        e.output = "lol"
        return e
    
    lols = generatelols()
    if e.nick.lower().startswith('bbnet'):
        e.output = "<%s> !bbnet\n^\n%s" % (e.nick, lols)
    else:
        e.output = lols

    return e 

bbnet.command = "!bbnet"

def generatelols():
    output = ""
    rand = random.randint(2, 10)
    for n in range(0, rand):
        output = "%s%s" % (output, "l")
        output = "%s%s" % (output, "oo" if random.randint(0, 5) == 0 else "o")
    return output

def fortune(self, e):
    e.output = urllib.request.urlopen("http://www.fortunefortoday.com/getfortuneonly.php").read().decode('utf-8').replace('\n', ' ').replace('\r', '').strip()
    return e

fortune.command = "!fortune"
fortune.helptext = "Usage: just fucking type !fortune"


verbs = ["gamify", "aggregate", "architect", "benchmark", "brand", "cultivate", "deliver", "deploy", "disintermediate", "drive",
"e-enable", "embrace", "empower", "enable", "engage", "engineer", "enhance", "envisioneer", "evolve", "expedite",
"exploit", "extend", "facilitate", "generate", "grow", "harness", "implement", "incentivize", "incubate",
"innovate", "integrate", "iterate", "leverage", "matrix", "maximize", "mesh", "monetize", "morph", "optimize",
"orchestrate", "productize", "recontextualize", "redefine", "reintermediate", "reinvent", "repurpose",
"revolutionize", "scale", "seize", "strategize", "streamline", "syndicate", "synergize", "synthesize",
"target", "transform", "transition", "unleash", "utilize", "visualize", "whiteboard"]

adjectives = ["24/365", "24/7", "B2B", "B2C", "back-end", "best-of-breed", "bleeding-edge", "bricks-and-clicks",
"clicks-and-mortar", "collaborative", "compelling", "cross-platform", "cross-media", "customized", "cutting-edge",
"distributed", "dot-com", "dynamic", "e-business", "efficient", "end-to-end", "enterprise", "extensible", "frictionless",
"front-end", "global", "granular", "holistic", "impactful", "innovative", "integrated", "interactive", "intuitive", "killer",
"leading-edge", "magnetic", "mission-critical", "next-generation", "one-to-one", "open-source", "out-of-the-box",
"plug-and-play", "proactive", "real-time", "revolutionary", "rich", "robust", "scalable", "seamless", "sexy", "sticky",
"strategic", "synergistic", "transparent", "turn-key", "ubiquitous", "user-centric", "value-added", "vertical", "viral",
"virtual", "visionary", "web-enabled", "wireless", "world-class", "software-as-a-service"]

nouns = ["action-items", "applications", "architectures", "bandwidth", "channels", "communities", "content", "convergence",
"deliverables", "e-business", "e-commerce", "e-markets", "e-services", "e-tailers", "experiences", "eyeballs",
"functionalities", "infomediaries", "infrastructures", "initiatives", "interfaces", "markets", "methodologies",
"metrics", "mindshare", "models", "networks", "niches", "paradigms", "partnerships", "platforms", "portals", "relationships",
"ROI", "synergies", "web-readiness", "schemas", "solutions", "supply-chains", "systems", "technologies", "users", "vortals",
"web services"]


def goodshit(self, e):
        e.output = "👌👀👌👀👌👀👌👀👌👀 good shit go౦ԁ sHit👌 thats ✔ some good👌👌shit right👌👌there👌👌👌 right✔there ✔✔if i do ƽaү so my self 💯 i say so 💯 thats what im talking about right there right there (chorus: ʳᶦᵍʰᵗ ᵗʰᵉʳᵉ) mMMMMᎷМ💯 👌👌 👌НO0ОଠOOOOOОଠଠOoooᵒᵒᵒᵒᵒᵒᵒᵒᵒ👌 👌👌 👌 💯 👌 👀 👀 👀 👌👌Good shit "
        return e
goodshit.command = "!goodshit"
