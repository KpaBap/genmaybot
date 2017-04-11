import urllib.request, urllib.error, urllib.parse, csv, json# ,locale

def get_stock_quote(self, e):
    # stock quotes from Yahoo Finance
    if not e.input:
        return
      
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent',"Opera/9.10 (YourMom 8.0)")]
    #first runs a search to get a ticker symbol:
    pagetmp = opener.open("https://s.yimg.com/aq/autoc?query=%s&region=CA&lang=en-CA&callback=YAHOO.util.ScriptNodeDataSource.callbacks" % urllib.parse.quote(e.input)).read()
    pagetmp = pagetmp.decode('utf-8')
    pagetmp = pagetmp.replace('YAHOO.util.ScriptNodeDataSource.callbacks({"ResultSet":', "").replace("});", "")
    pagetmp = json.loads(pagetmp)
    #we assume the first result is correct:
    stock = pagetmp['Result'][0]['symbol']
    if stock == "^DJI":
        stock = "INDU"
    pagetmp = opener.open("http://download.finance.yahoo.com/d/quotes.csv?s=%s&f=nl1c1va2j1" % stock)
    quote = pagetmp.read(1024).decode('utf-8')
    opener.close()
    name,price,change,volume,avg_volume,mkt_cap = [r for r in csv.reader([quote])][0]
    if price != "0.00": #assume no price = no result
       name = name.replace('"','')
    
       if change != "N/A":
           change = change + ' ({0:.2%})'.format(float(change)/(float(price) - float(change)))
       if volume != "N/A" and avg_volume != "N/A":
           volume = '{0:n}'.format(int(volume))
           avg_volume = '{0:n}'.format(int(avg_volume))
       
       e.output = "[%s] %s    %s %s | Cap: %s | Volume (Avg): %s (%s)" % (stock,name.strip(),price,change,mkt_cap.strip(),volume,avg_volume)
       return e
   
get_stock_quote.command = "!stock"
get_stock_quote.helptext = "Usage: !stock <ticker symbol>\nExample: !stock GOOG\nShows a quote for the given ticker symbol"

    # http://cliffngan.net/a/13
#a     Ask             a2     Average Daily Volume     a5     Ask Size
#b     Bid             b2     Ask (Real-time)     b3     Bid (Real-time)
#b4     Book Value     b6     Bid Size     c     Change & Percent Change
#c1     Change         c3     Commission     c6     Change (Real-time)
#c8     After Hours Change (Real-time)     d     Dividend/Share     d1     Last Trade Date
#d2     Trade Date     e     Earnings/Share     e1     Error Indication (returned for symbol changed / invalid)
#e7     EPS Estimate Current Year     e8     EPS Estimate Next Year     e9     EPS Estimate Next Quarter
#f6     Float Shares     g     Day's Low     h     Day's High
#j     52-week Low     k     52-week High     g1     Holdings Gain Percent
#g3     Annualized Gain     g4     Holdings Gain     g5     Holdings Gain Percent (Real-time)
#g6     Holdings Gain (Real-time)     i     More Info     i5     Order Book (Real-time)
#j1     Market Capitalization     j3     Market Cap (Real-time)     j4     EBITDA
#j5     Change From 52-week Low     j6     Percent Change From 52-week Low     k1     Last Trade (Real-time) With Time
#k2     Change Percent (Real-time)     k3     Last Trade Size     k4     Change From 52-week High
#k5     Percebt Change From 52-week High     l     Last Trade (With Time)     l1     Last Trade (Price Only)
#l2     High Limit     l3     Low Limit     m     Day's Range
#m2     Day's Range (Real-time)     m3     50-day Moving Average     m4     200-day Moving Average
#m5     Change From 200-day Moving Average     m6     Percent Change From 200-day Moving Average     m7     Change From 50-day Moving Average
#m8     Percent Change From 50-day Moving Average     n     Name     n4     Notes
#o     Open     p     Previous Close     p1     Price Paid
#p2     Change in Percent     p5     Price/Sales     p6     Price/Book
#q     Ex-Dividend Date     r     P/E Ratio     r1     Dividend Pay Date
#r2     P/E Ratio (Real-time)     r5     PEG Ratio     r6     Price/EPS Estimate Current Year
#r7     Price/EPS Estimate Next Year     s     Symbol     s1     Shares Owned
#s7     Short Ratio     t1     Last Trade Time     t6     Trade Links
#t7     Ticker Trend     t8     1 yr Target Price     v     Volume
#v1     Holdings Value     v7     Holdings Value (Real-time)     w     52-week Range
#w1     Day's Value Change     w4     Day's Value Change (Real-time)     x     Stock Exchange
#y     Dividend Yield             
