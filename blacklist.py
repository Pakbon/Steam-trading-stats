'''auto blacklisting of abusers'''

import requests
import shelve
import datetime

import functions

steam = functions.load_id()

def main():
    if not steam['blacklist']:
        return

    blcount = steam['blacklistcount']
    bldays = steam['blacklistdays']
    find_abusers(blcount)
    
def find_abusers(blcount):
    'find abusers'
    tradehist = functions.tradedata()
    for trades in tradehist['response']['trades']:
        if trades['steamid_other'] in steam['exceptions']:
            continue
        try:
            trades['assets_given']
            if len(trades['assets_received']) >= blcount:
                counter = {}
                for items in trades['assets_received']:
                    try:
                        counter[items['classid']] += 1
                    except KeyError: #key doesn't exist. Create it.
                        counter[items['classid']] = 1
                highkey = max(counter, key=counter.get)
                if counter[highkey] >= blcount:
                    #BANHAMMER
                    ban_him(trades['steamid_other'],highkey, counter[highkey], trades['tradeid'])
                    
        except KeyError:
            #no items given in this trade
            continue

def ban_him(steamid, classid, count, tradeid):
    #save to savefile first
    savefile = shelve.open('blacklist.shv')
    if steamid not in savefile:
        savefile[steamid] = {'tradeid' : tradeid, classid : count}
        
        #write to sql
        date = datetime.datetime.now()
        date = date.replace(microsecond = 0)
        table = 'banned'
        column = 'datetime, steamid, offending_item, count, trade_id'
        value = "\'{}\',\'{}\',\'{}\',\'{}\',\'{}\'".format(date, steamid, classid, count, tradeid )
        functions.write_sql(table, column, value)
        
        #blacklist with asf
        url = '{}bladd%20{}%20{}'.format(steam["asfcommand"], steam["bot"],steamid)    
        requests.post(url, data='')

if __name__ == "__main__":
    main()