import sqlite3, locale, urllib.request, urllib.error, urllib.parse
try:
    locale.setlocale(locale.LC_ALL, 'English_United States')
except:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def portfolio(self, e):
    args = e.input.upper().split()
    nick = e.nick.upper()


    if len(args) == 4:		# arguments for adding stock
        command,stock,numshares,pricepaid = args
        if command != "ADD":
            return

        e.source = e.nick
        e.notice = True
        e.output = add_stock(nick, stock, numshares, pricepaid)
        return e


    elif len(args) == 2:	# arguments for deleting stock
        command,stock_rowid = args
        if command != "DEL":
            return

        e.source = e.nick
        e.notice = True
        e.output = del_stock(nick, stock_rowid)
        return e

    elif len(args) == 1:	# argument for listing portfolio
        command = args[0]
        if command != "LIST":
            return
        e.source = e.nick
        e.notice = True
        e.output = list_stock(nick,False)

    elif len(args) == 0:
        e.output = list_stock(nick,True)
        return e



    return e

def add_stock(nick,stock,numshares,pricepaid):
    conn = sqlite3.connect('portfolios.sqlite')
    c = conn.cursor()
    result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='portfolios';").fetchone()
    if not result:
        c.execute('''create table portfolios(user text, stock text, numshares real, pricepaid real)''')

    if get_stocks_prices(stock)[0] == "0.00":
        return "Incorrect ticker symbol. Fix it and try again."

    try:
        numshares = float(numshares)
        pricepaid = float(pricepaid)
        if numshares <= 0 or pricepaid < 0:
            raise BaseException
    except:
        return "The number of shares or the price is incorrect. Fix it and try again."



    c.execute("INSERT INTO portfolios VALUES (?,?,?,?)", [nick,stock,numshares,pricepaid])
    conn.commit()
    conn.close()

    return "Added %s shares of %s at $%s." % (numshares, stock, pricepaid)

def del_stock(nick, stock_rowid):
    conn = sqlite3.connect('portfolios.sqlite')
    c = conn.cursor()
    result = c.execute("DELETE FROM portfolios WHERE user = ? AND rowid = ?", [nick, stock_rowid]).rowcount
    conn.commit()
    conn.close()

    if result == 0:
            return "You did something wrong, try again."
    if result == 1:
            return "Deleted portfolio entry #%s" % (stock_rowid)


def list_stock(nick,public):
    stocks = []
    id_counter=0

    #initial portfolio valuations
    init_value=0
    cur_value=0
    stock_gain=0
    stock_perc_gain=0
    portfolio_gain=0
    portfolio_perc_gain=0

    conn = sqlite3.connect('portfolios.sqlite')
    c = conn.cursor()
    try:
        result = c.execute("SELECT rowid, stock, numshares, pricepaid FROM portfolios WHERE user = ?", [nick]).fetchall()
    except:
        return "You're too poor to own stock."


    conn.close()

    return_line="%s%s%s%s%s%s\n" % ("ID".center(5),"Symbol".center(10),"# of Shares".center(15),"Price Paid".center(15), "Current Price".center(15),"Change".center(18))

    if result:
        for stock in result:
            stocks.append(stock[1])

        stock_prices = get_stocks_prices(stocks)


        for stock in result:
            init_value+=stock[2]*stock[3]
            cur_value+=stock[2]*float(stock_prices[id_counter])
            stock_gain=float(stock_prices[id_counter])-stock[3]
            if stock[3] > 0:
                stock_perc_gain= round(float(stock_gain)/stock[3],4)*100
            else:
                stock_perc_gain= float('nan')

            stockgainpct = "%0.2f (%0.2f%%)" % (stock_gain, stock_perc_gain)

            return_line += "%s%s%s%s%s%s\n" % (str(stock[0]).center(5),stock[1].center(10),str(stock[2]).center(15),str(stock[3]).center(15),str(stock_prices[id_counter]).center(15),stockgainpct.center(18))
            id_counter+=1

        portfolio_gain = round(cur_value-init_value,2)
        portfolio_perc_gain= round(float(portfolio_gain)/init_value,4)*100


        return_line+=" "*80+"\n"

        ##only output the value line in a channel, everything else if asked in pm
        if public:
            return_line="Starting Value: %0.2f   Current: %0.2f   Gain: %0.2f (%0.2f%%)" % (init_value, cur_value, portfolio_gain, portfolio_perc_gain)
        else:
            return_line+="Starting Value: %0.2f   Current: %0.2f   Gain: %0.2f (%0.2f%%)" % (init_value, cur_value, portfolio_gain, portfolio_perc_gain)

        return return_line
    else:
        return "You're too poor to own stock."

def get_stocks_prices(stocks):## pass in a list or tuple or a single string
                        ## of stocks and get back their prices in a tuple

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent',"Opera/9.10 (YourMom 8.0)")]

    #if you pass in a string we dont want to insert + signs
    if type(stocks) is not str:
        stocks = "+".join(stocks)

    pagetmp = opener.open("http://download.finance.yahoo.com/d/quotes.csv?s=%s&f=l1" % stocks)
    quote = pagetmp.read(1024).decode("utf-8")

    return quote.split("\r\n")
      


portfolio.command = "!portfolio"
portfolio.helptext = "!portfolio ADD <symbol> <# of shares> <price> - to add stocks to your portfolio \n!portfolio LIST - will list all your stocks and gains\n!portfolio - show only the gains and values\n!portfolio DEL <id> - use the ID number given in !portfolio list"
