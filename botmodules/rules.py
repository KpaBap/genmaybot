import random
rules = { 1: "Obey the Rules", 2: "Lead by example", 3: "Guide the uninitiated",
          4: "It's all about the bike", 5: "Harden the fuck up",
          6: "Free your mind and your legs will follow.",
          7: "Tan lines should be cultivated and kept razor sharp.",
          8: "Saddles, bars, and tires shall be carefully matched.",
          9: "If you are out riding in bad weather, it means you are a badass."
          " Period.", 10: "It never gets easier, you just go faster.",
          11: "Family does not come first. The bike does.", 12: "The correct "
          "number of bikes to own is n+1.", 13: "If you draw race number 13, "
          "turn it upside down.", 14: "Shorts should be black.",
          15: "Black shorts should also be worn with leader's jerseys.",
          16: " Respect the jersey.", 17: "Team kit is for "
          "members of the team.", 18: "Know what to wear. "
          "Don't suffer kit confusion.", 19: "Introduce Yourself.",
          20: "There are only three remedies for pain.",
          21: "Cold weather gear is for cold weather.", 22: "Cycling " 
          "caps are for cycling.", 23: "Tuck only after reaching "
          "Escape Velocity.", 24: "Speeds and distances shall be referred "
          "to and measured in kilometers.", 25: "The bikes on top "
          "of your car should be worth more than the car.",
          26: "Make your bike photogenic.", 27: "Shorts and socks "
          "should be like Goldilocks.", 28: "Socks can be any damn "
          "colour you like.", 29: "No European Posterior Man-Satchels.",
          30: "No frame-mounted pumps.", 31: "Spare tubes, multi-tools "
          "and repair kits should be stored in jersey pockets.",
          32: "Humps are for camels: no hydration packs.", 33: "Shave "
          "your guns", 34: "Mountain bike shoes and pedals have their "
          "place. On a mountain bike.", 35: "No visors on the road.",
          36: "Eyewear shall be cycling specific.", 37: "The arms of the "
          "eyeware shall always be placed over the helmet straps.",
          38: "Don't Play Leap Frog.", 39: "Never ride without your "
          "eyewear.", 40: "Tires are to be mounted with the label centered "
          "over the valve stem.", 41: "Quick-release levers are to "
          "be carefully positioned", 42: "A bike race shall never be "
          "preceded with a swim and/or followed by a run.",
          43: "Don't be a jackass.", 44: "Position matters",
          45: "Slam your stem.", 46: "Keep your bars level.", 47: "Drink "
          "Tripels, don't ride triples", 48: "Saddles must be level and "
          "pushed back", 49: "Keep the rubber side down.", 50: "Facial "
          "hair is to be carefully regulated.",
          51: "Livestrong wristbands are like cockrings for your arms.",
          52: "Drink in Moderation.", 53: "Keep your kit clean and new.",
          54: "No aerobars on road bikes.", 55: "Earn your turns.",
          56: "Espresso or macchiato only.", 57: "No stickers.",
          58: "Support your local bike shop.", 59: "Hold your line",
          60: "Ditch the washer-nut and valve-stem cap.",
          61: "Like your guns, saddles should be smooth and hard.",
          62: "You shall not ride with earphones.", 63: "Point in the "
          "direction you're turning.", 64: "Cornering confidence "
          "increases with time and experience.", 65: "Maintain and "
          "respect your machine.", 66: "No mirrors.",
          67: "Do your time in the wind.", 68: "Rides are to be measured "
          "by quality, not quantity.", 69: "Cycling shoes and bicycles "
          "are made for riding.",70: "The purpose of competing is to win.",
          71: "Train Properly.", 72: "Legs speak louder than words.", 
          73: "Gear and brake cables should be cut to optimum length.",
          74: "V Meters or small computers only.", 75: "Race numbers are "
          "for races", 76: "Helmets are to be hung from your stem.",
          77: "Respect the earth; don't litter.", 78: "Remove unnecessary "
          "gear.", 79: "Fight for your town lines.", 80: "Always be "
          "Casually Deliberate.", 81: "Don't talk it up", 82: "Close the "
          "gap", 83: "Be self-sufficient.", 84: "Follow the Code.",
          85: "Decend like a Pro.", 86: "Don't half-wheel.", 87: "The Ride "
          "Starts on Time. No exceptions.", 88: "Don't surge.", 89: "Pronounce "
          "it Correctly.", 90: "Never Get Out of the Big Ring.", 91: "No Food "
          "On Training Rides Under Four Hours.", 92: "No Sprinting From the "
          "Hoods", 93: "Descents are not for recovery. Recovery Ales "
          "are for Recovery", 94: "Use the correct tool for the job, "
          "and use the tool correctly.", 95: "Never lift your bike over your "
          "head."
 }


def get_rule(self, e):
    if e.input:
        try:
            rule_num = int(e.input)
        except ValueError:
            rule_num = 0

        ## Valid Rule
        if rule_num > 0 and rule_num <= len(rules):
            e.output = "Rule %d: %s" % (rule_num, rules[rule_num])

        ## Invalid Rule
        else:
            e.output = "Invalid rule ID. Please enter 1-%s" % str(len(rules))

    ## Random Rule
    else:
        rule_num = random.randint(1,len(rules))
        e.output = "Rule %d: %s" % (rule_num, rules[rule_num])

    return e


get_rule.command = "!rule"
get_rule.helptext = "!rule <RuleID> : Shows the corresponding velominati rule."
