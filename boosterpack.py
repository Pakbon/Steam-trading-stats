import re
import requests
import json
import csv
import datetime
import logging
import traceback

from bs4 import BeautifulSoup as bs

import functions

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
logging.basicConfig(filename='boosterpack.log', level=log_level, format=' %(asctime)s - %(levelname)s- %(message)s')
print(type(log_level))

def main():
    logging.debug('log start')
    boosteramount = boosterpacks()
    if boosteramount > 0:
        extract()
    logging.debug('log end')
        

def boosterpacks():
    'count boosterpacks'
    #get inventory
    url = 'https://steamcommunity.com/inventory/{}/753/6?count=10'.format(steam["steam64"])
    inventory = requests.get(url)
    inventory = inventory.json()

    #find boosterpacks in inventory
    regex = re.compile(r'.*Booster Pack')
    logging.debug('looking for boosterpacks in inventory')
    boosteramount = 0
    for items in inventory['descriptions']:
        logging.debug('Item type of item: {}'.format(items['type']))
        steamid = ''
        if items['classid'] == '667924416': #gems break the script and can be safely skipped
            continue
        found = regex.search(items['name'])
        if found:
            boosteramount += 1
            logging.debug('Found boosterpack {} in inventory'.format(items['market_fee_app']))
            #find account it came from
            boosterclassid = items['classid']
            logging.debug('boosterpack classid = {}'.format(boosterclassid))
            boosterappid = items['market_fee_app']
            tradehist = functions.tradedata()
            tradelist = [trades for trades in tradehist['response']['trades'] if trades['steamid_other'] in str(steam['exceptions'])if 'assets_received' in trades]
            logging.debug('Looking in trades for boosterpack')
            for trades in tradelist:
                for assets in trades['assets_received']:
                    if assets['classid'] == boosterclassid:
                        steamid = trades['steamid_other']
                        logging.debug('Found in trades: steam64={}'.format(steamid))
                        break
                    else:
                        continue
                break
            if not steamid:
                logging.debug('Not found in trades, boosterpack dropped from main bot')
                steamid = steam['steam64']

            #amount of owners of the game
            steamspy = 'http://steamspy.com/api.php?request=appdetails&appid={}'.format(boosterappid)
            steamspy_answer = requests.get(steamspy, headers=functions.header)
            steamspy_answer = steamspy_answer.json()
            game_name = steamspy_answer['name']
            game_name = game_name.replace("\'", "")
            owners = steamspy_answer['owners']
            regowners = re.compile(r'(\d+(,\d+)*)')
            owners_min, owners_max = regowners.findall(owners)[0][0], regowners.findall(owners)[1][0]
            owners_min, owners_max = owners_min.replace(',',''), owners_max.replace(',','')
        
            #stats of account boosterpack dropped from
            with open('accounts.json') as accounts:
                accounts = json.loads(accounts.read())
                level = requests.get('http://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key={}&steamid={}'.format(steam['apikey'], steamid))
                level = level.json()['response']['player_level']    
                session = functions.login(accounts[steamid]['bot'], accounts[steamid]['username'], accounts[steamid]['password'])
                try:
                    vanityurl = accounts[steamid]['vanityurl']
                    url = 'https://steamcommunity.com/id/{}/ajaxgetboostereligibility/'.format(vanityurl)
                except KeyError:
                    url = 'https://steamcommunity.com/profiles/{}/ajaxgetboostereligibility/'.format(steamid)
                eligible = session.get(url)
                soup = bs(eligible.text,'html.parser')
                games = soup.select('.booster_eligibility_game')
                games = len(games)
            
            #how many accounts own this game
            asfapi = '{}oa%20{}'.format(steam['asfcommand'], boosterappid)
            resp = requests.post(asfapi, data='')
            resp = resp.json()
            regex = re.compile(r'(?<=<ASF>\s).*(?=/.*\sbots)')
            bot_owns = regex.search(resp['Result'])
            bot_owns = bot_owns.group()

            #write data to sql
            logging.debug('Writing to SQL, values: {},{},{},{},{},{},{}'.format(game_name, owners_min, owners_max, steamid, level, games, bot_owns))
            columns = 'date, boosterpack, min_owners, max_owners, received_from, level, eligible_games, owned_on_bots'
            values = "\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\'".format(functions.Tday, game_name, owners_min, owners_max, steamid, level, games, bot_owns)
            functions.write_sql('boosterpack', columns, values)

        else: #no boosterpacks left
            logging.debug('no boosterpacks left')
            break    
    return boosteramount

def extract():
    'unpacks boosterpacks via ASF'
    logging.debug('unpacking boosterpack')
    asfapi = '{}unpack%20{}'.format(steam["asfcommand"], steam["bot"])
    resp = requests.post(asfapi, data='')
    resp = resp.json()
    if resp['Success']:	
        return 0
    else:
        return 1

if __name__ == '__main__':
    try:
        main()
    except:
        logging.warning('Exception ocurred')
        logging.warning(traceback.format_exc())
