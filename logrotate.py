'''weekly log folder rotation
'''

import os
import csv
import shutil
import datetime
from time import sleep

logfolder = os.getcwd() + '/log'
stats = '/stats.csv'
boosterpack = '/boosterpack.csv'
files = {'stats' : os.getcwd()+'/log/stats.csv', 'boosterpack' : os.getcwd()+'/log/boosterpack.csv'}

def main():
    rename()
    recreate()

def placeholder():
    today = datetime.date.today()
    week = today.isocalendar()[1]
    os.chdir('./log')
    files = os.listdir()
    
    for entry in files:
        if not 'week' in entry:
            with open(entry, 'r') as file:
                first_line = file.readline()
            shutil.move(entry, 'week{}_{}'.format(week, entry))
            with open(entry, 'a') as file:
                file.write(first_line)

def rename():
    #get ISO weeknumber. Week starts on monday
    today = datetime.date.today()
    week = today.isocalendar()[1]
    shutil.move('{}/stats.csv'.format(logfolder),'{}/week{}_stats.csv'.format(logfolder, week))

def recreate():
    #create a new csv file
    with open('{}/stats.csv'.format(logfolder), 'a') as file:
        file.write('date,total trades,daily trades,avg per trade,med per trade,mode per trade, highest per trade, most traded set name, most traded set count, second highest name, second highest count\n')

if __name__ == '__main__':
    placeholder()
