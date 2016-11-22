import re
import sqlite3
import urllib.request
import urllib.parse

#Handles !quote
g_irc_output = ""

def __init__(self):
	
	conn = sqlite3.connect(quote.db)
	c = conn.cursor()
	result = c.execute("CREATE TABLE IF NOT EXISTS Quotes (quote TEXT)")
	conn.commit()
	c.close()

# --- Commands in this module

def quote(self, event):
	command_handler(event, "quote")
	return event

quote.command = "!quote"
quote.helptext = "Use \"" + quote.command + "\" for look up, and \"" + quote.command + " add <quote>\" to create a new one, and \"" + quote.command + " search <string> to search for one"

quote.db = "quote.sqlite"
quote.addcmd = "add"
quote.searchcmd = "search"
quote.irc_output = ""
quote.last_quote = ""

# --- End commands

def command_handler(event, command):
	
	nick_offset = 0
	arg_offset = 0
	val_offset = 1

	nick = event.nick
	irc_input = event.input

	set_function_dict = {'quote':store_string}
	get_function_dict = {'quote':get_string}
	search_function_dict = {'quote':search_string}


	#split the user input along word (whitespace) boundary into list 
	#EX: "set http://url1 http://url2 http://url3"
	words = irc_input.split()

	if(arg_is_present(words)):

		# ADD <VAL>
		# "add I'm a hero"
		if(is_add_arg(words, arg_offset)):
			if not (set_function_dict[command](words[val_offset:], command)):
				add_to_irc_output("\nFailed to add duplicate quote")
		
		elif(is_search_arg(words, arg_offset)):
			search_function_dict[command](words[val_offset:], command)

		# ADD
		# EX: "add"
		elif(is_arg_without_val(words, arg_offset)):
			# This eval should be safe, possible values of command are hard coded above.
			add_to_irc_output(eval(command).helptext)

		# GET <VAL>
		# EX: "lance_armstrong"
		else:
			add_to_irc_output(eval(command).helptext)

	# GET
	# EX: ""
	else:
		get_function_dict[command](command)

	flush_and_reset_irc_output(event)

	return event

def arg_is_present(words):
	return len(words)

def is_add_arg(words, offset):
	return(len(words) >= 2 and words[offset] == quote.addcmd)

def is_search_arg(words, offset):
	return(len(words) >= 2 and words[offset] == quote.searchcmd)

def is_arg_without_val(words, offset):
	return(len(words) == 1 and words[offset] == quote.addcmd)

def store_string(words, command):
	string = ""
	space = " "
	
	#Stringify lists, dont mess with strings
	if not isinstance(words, str):
		for word in words:
			string += word
			string += space
			#print("DEBUG: adding " + word)
	else:
		string = words

	add_to_irc_output("\nStoring " + command + ": " + string)

	if not (sql_insert_or_update(command, string)):
		return 0
	
	return 1

	
def search_string(words, command):
	search_string = ""
	space = " "
	
	#Stringify lists, dont mess with strings
	if not isinstance(words, str):
		for word in words:
			search_string += word
			search_string += space
			#print("DEBUG: adding " + word)
	else:
		search_string = words

	#Didnt find one
	string = sql_search_value_from_command(command, search_string)
	if string == None:
		add_to_irc_output("\n" + command + " not found")

	#Found one
	else:
		add_to_irc_output("\n" + command + ": " + string)
	
	quote.last_quote = string
	return 1

def get_string(command):

	#Didnt find one
	string = sql_get_random_value_from_command(command)
	if string == None:
		add_to_irc_output("\n" + command + " not found")

	#Found one
	else:
		while(string == quote.last_quote):
			print("DEBUG: Same as last quote, fetch another one")
			string = sql_get_random_value_from_command(command)

		add_to_irc_output("\n" + command + ": " + string)
	
	quote.last_quote = string
	return 1


def sql_insert_or_update(table, value):

	conn = sqlite3.connect(quote.db)
	c = conn.cursor()

	#New user
	query = "SELECT %s from Quotes WHERE Quote=?" % table
	result = c.execute(query, (value,)).fetchone() 
	#result = c.execute("SELECT quote FROM Quotes WHERE quote=?", (value,)).fetchone() 
	if result == None:
		# Not a duplicate quote (hahah) insert it
		print("DEBUG: New quote, inserting: " + value)

		query = "INSERT INTO Quotes (%s) VALUES (?)" % table
		result = c.execute(query, (value,))

		if not result:
			print("DEBUG: Failed to insert value")

		conn.commit()

		print("Current db state: ")
		for row in c.execute("SELECT * FROM Quotes"):
			print(row)

		c.close()
	else:
		return 0
	
	return 1

def sql_get_random_value_from_command(table):

	conn = sqlite3.connect(quote.db)
	c = conn.cursor()

	query = "SELECT %s FROM Quotes ORDER BY RANDOM() LIMIT 1" % table
	value = c.execute(query).fetchone()
	c.close()
	
	if value == None:
		return 0;
	
	return value[0]

def sql_search_value_from_command(table, search_string):

	conn = sqlite3.connect(quote.db)
	c = conn.cursor()
	search_string = search_string.strip()
	search_string = '%' + search_string + '%'
	query = "SELECT %s FROM Quotes WHERE %s LIKE ? ORDER BY RANDOM() LIMIT 1" % (table, table)
	value = c.execute(query, (search_string,)).fetchone()
	c.close()
	if value == None:
		return 0;
	
	return value[0]

def add_to_irc_output(output):
	
	quote.irc_output += output

def flush_and_reset_irc_output(event):
	
	event.output = quote.irc_output
	quote.irc_output = ""
