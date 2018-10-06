import re
import requests
import json
import csv
import datetime

from bs4 import BeautifulSoup as bs

import functions

steam = functions.load_id()

def main():
    #get inventory
    url = 'https://steamcommunity.com/inventory/{}/753/6?count=10'.format(steam["steam64"])
    inventory = requests.get(url)
    inventory = inventory.json()

    #find boosterpacks in inventory
    regex = re.compile(r'.*Booster Pack')
    for items in inventory['descriptions']:
        found = regex.search(items['name'])
        if found:
            #find account it came from
            boosterclassid = items['classid']
            boosterappid = items['market_fee_app']
            tradehist = functions.tradedata()
            for trades in tradehist['response']['trades']:
                try: #trades with nothing received throws error
                    if trades['assets_received'][0]['classid'] == boosterclassid:
                        #came from bot:
                        steamid = trades['steamid_other']
                        if steamid not in steam['exceptions']:
                            #this is a donation, skip
                            continue
                except: #safe to skip and continue
                    continue
            if not steamid: #came from own
                steamid = steam['steam64']

            #amount of owners of the game
            steamspy = 'http://steamspy.com/api.php?request=appdetails&appid={}'.format(boosterappid)
            steamspy_answer = requests.get(steamspy, headers=functions.header)
            steamspy_answer = steamspy_answer.json()
            game_name = steamspy_answer['name']
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
            
            #write data to sql
            columns = 'date, boosterpack, min_owners, max_owners, received_from, level, eligible_games'
            values = "\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\'".format(functions.Yday, game_name, owners_min, owners_max, steamid, level, games)
            functions.write_sql('boosterpack', columns, values)

        else: #no boosterpacks left
            break    

if __name__ == '__main__':
    main()