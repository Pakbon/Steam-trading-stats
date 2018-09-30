'''datamining tradingbot stats
'''

import json
import csv
import requests
import statistics
import datetime
import re
from bs4 import BeautifulSoup as bs

import functions

steam = functions.load_id()

def main():
    tradehist = functions.tradedata()
    basestats = stats(tradehist)
    basestats.update(mosttraded(tradehist))
    #misc = other(tradehist)
    #writecsv(basestats)
    sql(basestats)

def stats(tradehist):
    'calculating all kinds of stats about trades. Declined trades are not included in steam api'
    #amount of trades
    dailytrades = len(tradehist['response']['trades'])
    totaltrades = tradehist['response']['total_trades']

    #average, mode, median of amount of items per trade
    data = []
    for trades in tradehist['response']['trades']:
        data += [len(trades['assets_received'])]
    data.sort()
    avg = round(statistics.mean(data), 2)
    med = round(statistics.median(data), 2)
    mode = statistics.mode(data)
    high = max(data) 

    return {'dailytrades':dailytrades, 'totaltrades':totaltrades, 'avg':avg, 'med':med, 'mode':mode, 'high':high}

def mosttraded(tradehist):
    itemid = []
    url = 'https://api.steampowered.com/ISteamEconomy/GetAssetClassInfo/v1/'
    args = '?key={}&appid=753&class_count=7'.format(steam['apikey'])
    for trades in tradehist['response']['trades']:
        if int(trades['steamid_other']) in steam['exceptions']:
            continue
        for items in trades['assets_received']:
            id = items['classid']
            itemid += [int(id)]
    itemid.sort()
    counter = 0
    idargs = ''
    dictio = {}
    for i in itemid: #convert classid to itemset and count them
        idargs += '&classid{}={}'.format(counter, i)
        counter += 1
        if counter == 7:
            r = requests.get(url+args+idargs)
            r = r.json()
            for n in r['result']:
                try:
                    cardset = r['result'][n]['type']
                except:
                    continue
                try:
                    cardset in dictio
                    dictio[cardset] += 1
                except:
                    dictio[cardset] = 1
            counter = 0
            idargs = ''
    highestcount = 0
    highestcountname = ''
    for key, value in dictio.items():
        if value > highestcount:
            secondhighest = highestcount
            secondhighestname = highestcountname
            highestcount = value
            highestcountname = key
        else:
            if value > secondhighest:
                secondhighest = value
                secondhighestname = key
    return {'highestcount':highestcount, 'highestcountname':highestcountname, 'secondhighest':secondhighest, 'secondhighestname':secondhighestname}

def other(tradehist):
    'other stats worth keeping, not directly related to trading'          
    #friends added
    friend = 0
    url = 'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/'
    args = '?key={}&steamid={}&relationship=friend'.format(steam['apikey'], steam['steam64'])
    friendslist = requests.get(url+args)
    if friendslist.status_code != 200:
        raise Exception('Request failed with {}'.format(friendslist.status_code))
    friendslist = friendslist.json()
    for people in friendslist['friendslist']['friends']:
        if people['friend_since'] > functions.YdayUnix:
            friend += 1
    
    #comments posted
    comment = 0
    profile = requests.get('https://steamcommunity.com/id/{}'.format(steam['vanityurl']))
    soup = bs(profile.text, 'html.parser')
    for tag in soup.select('.commentthread_comment_timestamp'):
        if int(tag.attrs['data-timestamp']) > int(functions.YdayUnix):
            comment += 1
    
    #donations received
    donation = 0
    for trades in tradehist['response']['trades']:
        try:
            trades['assets_given']
        except:
            #this is a donation, don't count own profiles(exceptions)
            if int(trades['steamid_other'])not in steam['exceptions']:
                donation += 1
    
    return friend, comment

def writecsv(stats):
    with open('log/stats.csv', 'a', newline='') as log:
        writer = csv.writer(log)
        writer.writerow([functions.Yday.strftime("%Y-%m-%d"), stats['totaltrades'], stats['dailytrades'], stats['avg'], stats['med'],\
        stats['mode'], stats['high'], stats['highestcountname'], stats['highestcount'], stats['secondhighestname'], stats['secondhighest']])

def sql(stats):
    functions.write_sql('stats', \
                        'date, total_trades, daily_trades, average_cards_per_trade, median_cards_per_trade, mode_cards_per_trade, highest_cards_per_trade, most_traded_set, most_traded_count, second_most_traded_set, second_most_traded_count', \
                        "\'{}\', \'{}\', \'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\'" \
                        .format(functions.Yday, stats['totaltrades'], stats['dailytrades'], stats['avg'], stats['med'],stats['mode'], stats['high'], stats['highestcountname'], stats['highestcount'], stats['secondhighestname'], stats['secondhighest']))

if __name__ == '__main__':
    main()
