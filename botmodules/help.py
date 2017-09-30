def commands_help(bot, e):
  command = e.input

  if command == "":
    help="The following bot commands are available:\n"
    for command in bot.bangcommands:
      help+=command + "   "
    help+="\nUse !help <command> to get more detailed info on each command"
    if len(help)>= 460:
      help = help[0:460] + "\n" + help[460:]
    e.output = help
    
  elif command in bot.bangcommands and hasattr(bot.bangcommands[command],"helptext"):
    help = bot.bangcommands[command].helptext

    if hasattr(bot.bangcommands[command],"privateonly"):
      help+="\nNote: This command works only in a private message to the bot"
    e.output = help

  else:
    e.output = "Incorrect command or no help available." 
    
  return e 
    
    
    
#    if hasattr(bot.bangcommands[command],"helptext"):        
#      help += "%s:\t\t" % command
#      help += bot.bangcommands[command].helptext

#      
#      help+="\n"  
  

  
commands_help.command = "!help" 
commands_help.privateonly = True
commands_help.helptext="Usage: !help <command> or !help\n!help: Shows a list of available bot commands\n!help <command>: get more detailed info on each command"

