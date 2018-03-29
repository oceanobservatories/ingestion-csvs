"""
Usage: ingest_missing.py <event_url> <particle_url> <server>

This script will grab dates missing from data ingestion and then it will use the playback command to ingest them.
Provide the event_url and particle_url. 

Example: python ingest_missing.py qpid://guest/guest@uframe-test?queue=Ingest.instrument_events qpid://guest/guest@uframe-test?queue=Ingest.instrument_particles uframe-test

Arguments:
    event_url    
    particle_url
    server          This is where the reference designator information is stored.

Options:
    -h --help
    -v       verbose mode
    -q       quiet mode
"""

from docopt import docopt
import sys
import time
import numpy as np
import pandas as pd
import re
import glob
import list_missing_dates
from subprocess import call
from datetime import datetime, timedelta

class Cabled:
    cabled_drivers_raw = None


def request_cabled_raw():
    url = "https://raw.githubusercontent.com/ooi-integration/ingestion-csvs/master/cabled_drivers_list.txt"
    df = pd.read_csv(url, sep='\s{2,}', engine='python', dtype=str)
    df.loc[df['Type'] == 'None', ['Type']] = df['Reference Designator']
    df.loc[df['Reference Designator'] == df['Type'], ['Reference Designator']] = 'None'
    return df
    
def get_driver(refdes):
    """
    Get the driver from the cabled_drivers_list.txt file
    """
    return Cabled.cabled_drivers_raw.loc[Cabled.cabled_drivers_raw['Reference Designator'] == refdes]['Driver'][0]

def get_reader_type(refdes):
    """
    Get the reader type from the cabled_drivers_list.txt file
    """
    first_pass = False
    reader = []

    df = Cabled.cabled_drivers_raw[Cabled.cabled_drivers_raw['Reference Designator'] == refdes]

    for i in df.index:
        if df['Type'].loc[i] != 'nan':
            reader.append(df['Type'].loc[i])

    # for line in Cabled.cabled_drivers_raw:
    #     if refdes in line:
    #         first_pass = True
    #         reader.append(line.split()[2])
    #     elif first_pass: 
    #         if line.split()[0] != 'datalog' and \
    #             line.split()[0] != 'chunky' and \
    #             line.split()[0] != 'ascii':
    #             first_pass = False
    #             break
    #         else:
    #             reader.append(line.split()[0])
    print reader
    return reader

def is_cabled(refdes):
    """
    Only get cabled assemblies.
    Table provided by the cabled_drivers_list.txt file.
    """ 
    if not Cabled.cabled_drivers_raw.loc[Cabled.cabled_drivers_raw['Reference Designator'] == refdes].empty:
        return True
    else:
        return False

def date_list(firstDate, secondDate):
    """
    Obtain a list of the missing dates.
    """
    startDate = 0
    endDate = 0
    missing_dates_list = []

    if firstDate < secondDate:
        startDate = firstDate
        endDate = secondDate
    else:
        startDate = secondDate
        endDate = firstDate

    # Working with the dates, getting the times between the start date and end date
    startDate = datetime.strptime(startDate, '%Y-%m-%d %H:%M:%S')
    endDate = datetime.strptime(endDate, '%Y-%m-%d %H:%M:%S')
    
    date_times = [startDate.strftime('%Y%m%dT%H')]
    date_time = startDate
    
    while date_time < endDate:
        date_time += timedelta(hours=1)
        date_times.append(date_time.strftime('%Y%m%dT%H'))

    return date_times

def playback(refdes, event_url, particle_url, missing_dates):
    """
    Put together the directory glob and other options for the playback command.
    This will then playback cabled data.
    """
    main_directory = '/rsn_cabled/rsn_data/DVT_Data'
    driver = get_driver(refdes)
    reader_list = get_reader_type(refdes)
    node = refdes.split('-')[1].lower()
    instrument = refdes.split('-')[3]

    for reader in reader_list:
        for date in missing_dates:
            directory = '/'.join([main_directory, node, instrument])
            directory += '*'.join(['', date, ''])

            # Check to see if this particular file exists before executing callback
            if glob.glob(directory):
                playback_command = ' '.join(['playback', reader, driver, refdes, event_url, particle_url, directory])
                call(playback_command, shell=True)

def main(args):
    if args['<event_url>'] and args['<particle_url>'] and args['<server>']:
        Cabled.cabled_drivers_raw = request_cabled_raw()
        event_url = args['<event_url>']
        particle_url = args['<particle_url>']
        server = args['<server>']
        refdes_list = list_missing_dates.get_refdes_list(server)
        missing_data_dict = {}
        
        for refdes in refdes_list:
            if is_cabled(refdes):
                missing_data_list = list_missing_dates.get_missing_data_list(refdes, server) # returns tuple
                if missing_data_list:
                    missing_data_dict[refdes] = missing_data_list
        
        for refdes, missing_dates in missing_data_dict.iteritems():
            for date in missing_dates:
                dates = date_list(date[0], date[1])
                playback(refdes, event_url, particle_url, dates)

if __name__ == "__main__":
    args = docopt(__doc__)
    main(args)