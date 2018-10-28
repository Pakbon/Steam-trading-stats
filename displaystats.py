"""Posting stats on steam profile
"""
import requests
import functions
import json
import shelve

steam = functions.load_id()

def main():
    stats, boosterpacks = getdata()
    profilepost(stats, boosterpacks)

def getdata():
    'data to be shown on profile'
    stats = functions.read_sql('stats', where="date=\'{}\'".format(functions.Yday.date()))
    boosterpacks = functions.read_sql('boosterpack', where="date=\'{}\'".format(functions.Yday.date()))
    return stats, boosterpacks

#def profilepost(stats):
def profilepost(stats, boosterpacks):
    with open('x.json') as file:
        payload = json.loads(file.read())
    payload['rgShowcaseConfig[8][0][title]'] = 'Stats for {}'.format(functions.Yday.date())
    payload['rgShowcaseConfig[8][0][notes]'] += 'Trades: [b]{}[/b]\n'.format(stats[0]['daily_trades'])
    payload['rgShowcaseConfig[8][0][notes]'] += 'Average cards per trade: [b]{}[/b]\n'.format(stats[0]['average_cards_per_trade'])
    payload['rgShowcaseConfig[8][0][notes]'] += 'Most traded set by cards: [b]{}[/b]\n'.format(stats[0]['most_traded_set'][:-13])
    payload['rgShowcaseConfig[8][0][notes]'] += '2nd most traded set by cards: [b]{}[/b]\n'.format(stats[0]['second_most_traded_set'][:-13])
    payload['rgShowcaseConfig[8][0][notes]'] += '\nBoosterpacks received: [b]{}[/b]\n'.format(len(boosterpacks))
    loadfile = shelve.open('paydaytwo.shv')
    payload['rgShowcaseConfig[8][0][notes]'] += 'Times commented on Payday 2 news: [b]{}[/b]\n'.format(loadfile[functions.Yday.date()])
    
    creds = functions.login(steam['bot'],steam['username'],steam['password'])
    payload['sessionID'] = creds.cookies.get('sessionid', domain='steamcommunity.com')
    url = 'https://steamcommunity.com/id/{}/edit'.format(steam['vanityurl'])
    creds.post(url,data=payload, headers=functions.header)
    

    
if __name__ == '__main__':
    main()
