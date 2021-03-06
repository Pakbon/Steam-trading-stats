"""Posting stats on steam profile
"""
import requests
import functions
import json
import shelve
import logging
import traceback

steam = functions.load_id()

if "logging" not in steam or steam['logging'] is None:
    log_level = logging.NOTSET
elif steam[ "logging" ] in (
    "CRITICAL",
    "DEBUG",
    "ERROR",
    "FATAL",
    "INFO",
    "WARN",
    "WARNING",
    "NOTSET",
):
    log_level = getattr( logging, steam[ "logging" ] )
else:
    raise ValueError( "Unknown logging level %r" % (
        steam[ "logging" ],
    ))
log_level = getattr(logging, steam['logging'])
logging.basicConfig(filename='displaystats.log', level=log_level, format=' %(asctime)s - %(levelname)s- %(message)s')


def main():
        logging.debug('log start')
        stats, boosterpacks = getdata()
        profilepost(stats, boosterpacks)
        logging.debug('log end')

def getdata():
    'data to be shown on profile'
    stats = functions.read_sql('stats', where="date=\'{}\'".format(functions.Yday.date()))
    boosterpacks = functions.read_sql('boosterpack', where="date=\'{}\'".format(functions.Yday.date()))
    return stats, boosterpacks

def profilepost(stats, boosterpacks):
    with open('x.json') as file:
        payload = json.loads(file.read())
    payload['rgShowcaseConfig[8][0][title]'] = 'Statistics for {}'.format(functions.Yday.date())
    payload['rgShowcaseConfig[8][0][notes]'] += 'Trades completed: [b]{}[/b]'.format(stats[0]['daily_trades'])
    payload['rgShowcaseConfig[8][0][notes]'] += '\nUnique accounts traded with: [b]{}[/b]'.format(stats[0]['unique_accounts'])
    payload['rgShowcaseConfig[8][0][notes]'] += '\nAverage cards per trade: [b]{}[/b]'.format(stats[0]['average_cards_per_trade'])
    payload['rgShowcaseConfig[8][0][notes]'] += '\nMost cards in one trade: [b]{}[/b]'.format(stats[0]['highest_cards_per_trade'])
    payload['rgShowcaseConfig[8][0][notes]'] += '\nMost traded set by cards: [b]{}[/b]'.format(stats[0]['most_traded_set'][:-13].decode('utf-8'))
    payload['rgShowcaseConfig[8][0][notes]'] += '\n2nd most traded set: [b]{}[/b]'.format(stats[0]['second_most_traded_set'][:-13].decode('utf-8'))
    payload['rgShowcaseConfig[8][0][notes]'] += '\n\nMisc:'
    payload['rgShowcaseConfig[8][0][notes]'] += '\nBoosterpacks received: [b]{}[/b]'.format(len(boosterpacks))
    '''
    try:
        loadfile = shelve.open('paydaytwo.shv')
        payload['rgShowcaseConfig[8][0][notes]'] += '\nTimes commented on Payday 2 news: [b]{}[/b]'.format(loadfile[functions.Yday.date().strftime('%Y-%m-%d')])
    except KeyError:
        payload['rgShowcaseConfig[8][0][notes]'] += '\nTimes commented on Payday 2 news: [b]0[/b]'
    '''
    creds = functions.login(steam['bot'],steam['username'],steam['password'])
    payload['sessionID'] = creds.cookies.get('sessionid', domain='steamcommunity.com')
    url = 'https://steamcommunity.com/id/{}/edit'.format(steam['vanityurl'])
    creds.post(url,data=payload, headers=functions.header)

if __name__ == '__main__':
    try:
        main()
    except:
        logging.warning('Exception ocurred')
        logging.warning(traceback.format_exc())
    