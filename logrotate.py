'''weekly log folder rotation
'''

import os
import csv
import shutil
import datetime


def rotate():
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

if __name__ == '__main__':
    rotate()
