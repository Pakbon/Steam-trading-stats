'''even more stats to datamine
primarily for logging boosters'''

import requests
import json
import csv
import re
from bs4 import BeautifulSoup as bs
from steam import webauth
from time import sleep


import functions

steam = functions.load_id()

def main():
    ProfileGames = profile()
    BoosterData = boosterpack()
    #writecsv(ProfileGames, BoosterData)
    sql(ProfileGames, BoosterData)

def profile():
    'get profile level, eligible games, returns eligible games, level and steamid in dict'
    with open('accounts.csv') as accounts:
        readcsv = csv.reader(accounts)
        data = list(readcsv)
        ProfileGames = {}
    for line in data:
        session = csvlogin(line)
        store = session.get('https://store.steampowered.com/stats/', headers=functions.header)
        soup = bs(store.text,'html.parser')
        s = soup.select('.submenuitem')
        regex = re.compile(r'(/id/|/profiles/)\w+')#finds /id/vanityurl or /profiles/steam64
        for links in s:
            match = regex.search(str(links))
            if match:
                break
        #check if vanityurl and resolve
        if 'id' in match.group():
            steamid = requests.get('https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={}&vanityurl={}'.format(steam['apikey'],match.group()[4:]), headers=functions.header)
            steamid = steamid.json()['response']['steamid']
        else:
            steamid = match.group()[10:]
        #get profile level
        level = requests.get('http://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key={}&steamid={}'.format(steam['apikey'], steamid))
        level = level.json()['response']['player_level']
        eligible = session.get('https://steamcommunity.com{}/ajaxgetboostereligibility/'.format(match.group()))
        soup = bs(eligible.text,'html.parser')
        games = soup.select('.booster_eligibility_game')
        games = len(games)
        ProfileGames[line[0]] = {'eligible' : games, 'level' : level, 'steamid' : steamid }
    return ProfileGames
        
def boosterpack():
    'counts boosterpacks recieved per profile'
    url = 'https://steamcommunity.com/inventory/{}/753/6?count=20'.format(steam["steam64"])
    inventory = requests.get(url)
    inventory = inventory.json()
    regex = re.compile(r'.*Booster Pack')
    BoosterData = {}
    for items in inventory['descriptions']:
        found = regex.search(items['name'])
        if found:
            name = items['name']
            boosterclassid = items['classid']
            appid = items['market_fee_app']
            #compare with yesterdays trades
            tradedictio = functions.tradedata()
            for trades in tradedictio['response']['trades']:
                try: #trades with nothing received throws error
                    if trades['assets_received'][0]['classid'] == boosterclassid:
                        #came from bot:
                        steamid = trades['steamid_other']
                        if steamid not in steam['exceptions']:
                            #this is a donation, skip
                            continue
                    else: #came from own
                        steamid = steam['steam64']
                except: #safe to skip and continue
                    continue
            
            #using steamspy api to get owner info
            steamspy = 'http://steamspy.com/api.php?request=appdetails&appid={}'.format(appid)
            steamspy_answer = requests.get(steamspy, headers=functions.header)
            steamspy_answer = steamspy_answer.json()
            owners = steamspy_answer['owners']
            regowners = re.compile(r'(\d+(,\d+)*)')
            owners_min, owners_max = regowners.findall(owners)[0][0], regowners.findall(owners)[1][0]
            owners_min, owners_max = owners_min.replace(',',''), owners_max.replace(',','')

            BoosterData[name] = {'received' : steamid, 'minowners' : owners_min, 'maxowners' : owners_max}
        
        else:
            #no boosters left, break from for loop
            break
    return BoosterData


def csvlogin(line):
    user = webauth.WebAuth(line[1], line[2])
    twofaurl = '{}2fa%20{}'.format(steam['asfcommand'], line[0])
    twofa = requests.post(twofaurl,data='')
    twofa = twofa.json()['Result'][-5:]
    steamsession = user.login(twofactor_code=twofa)
    steamsession.headers.update(functions.header)
    return steamsession


def writecsv(ProfileGames, BoosterData):
    with open('log/extraprofile.csv', 'a', newline='') as log:
        writer = csv.writer(log)
        for profile, stats in ProfileGames.items():
            writer.writerow([functions.Yday.strftime("%Y-%m-%d"), profile, stats['steamid'], stats['level'], stats['eligible']])
    with open('log/extraboosterdata.csv', 'a', newline='') as log:
        writer = csv.writer(log)
        if BoosterData:
            for boosters, data in BoosterData.items():
                writer.writerow([functions.Yday.strftime("%Y-%m-%d"), boosters, data['received'], data['minowners'], data['maxowners']])
        
def sql(ProfileGames, BoosterData):
    #write data to profile_games table
    for bot, stats in ProfileGames.items():
        functions.write_sql('profile_games', 'date, bot, steamid, eligible_games, level', "\'{}\', \'{}\', \'{}\', \'{}\', \'{}\'".format(functions.Yday, bot, stats['steamid'], stats['eligible'], stats['level']))

    #write data to boosterpacks_extra
    for bp, data in BoosterData.items():
        functions.write_sql('boosterpacks_extra', 'date, recv_steamid, min_owners, max_owners, name', "\'{}\', \'{}\', \'{}\', \'{}\', \'{}\'".format(functions.Yday, data['received'], data['minowners'], data['maxowners'], bp[:-13]))

if __name__ == '__main__':
    main()
