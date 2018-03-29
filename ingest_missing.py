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


import sys
import os
import time
import logging
import glob
import errno
import signal
from subprocess import call
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from docopt import docopt

import list_missing_dates


class Cabled:
    cabled_drivers_raw = None


class TimeoutException(Exception):
    pass
    
    
def timeout_handler(signum, frame):
    raise TimeoutException


def request_cabled_raw():
    url = "https://raw.githubusercontent.com/ooi-integration/ingestion-csvs/master/cabled_drivers_list.txt"
    df = pd.read_csv(url, sep='\s{2,}', engine='python', dtype=str)
    df.loc[df['Type'] == 'None', ['Type']] = df['Reference Designator']
    df.loc[df['Reference Designator'] == df['Type'], ['Reference Designator']] = df['Reference Designator'].shift(1)
    return df
    

def get_driver(refdes):
    """
    Get the driver from the cabled_drivers_list.txt file
    """
    return Cabled.cabled_drivers_raw.loc[Cabled.cabled_drivers_raw['Reference Designator'] == refdes]['Driver'].iloc[0]


def get_reader_type(refdes):
    """
    Get the reader type from the cabled_drivers_list.txt file
    """
    reader = []

    df = Cabled.cabled_drivers_raw[Cabled.cabled_drivers_raw['Reference Designator'] == refdes]

    for i in df.index:
        if df['Type'].loc[i] != 'nan':
            reader.append(df['Type'].loc[i])

    return reader


def is_cabled(refdes):
    """
    Only get cabled assemblies.
    Table provided by the cabled_drivers_list.txt file.
    """ 
    if not Cabled.cabled_drivers_raw.loc[Cabled.cabled_drivers_raw['Reference Designator'] == refdes].empty:
        return True
    return False


def date_list(first_date, second_date):
    """
    Obtain a list of the missing dates.
    """
    start_date = 0
    end_date = 0

    start_date = first_date if first_date < second_date else second_date
    end_date = second_date if first_date < second_date else first_date

    # Working with the dates, getting the times between the start date and end date
    start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    
    date_times = [start_date.strftime('%Y%m%dT%H')]
    date_time = start_date
    
    while date_time < end_date:
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
    signal.signal(signal.SIGALRM, timeout_handler)

    for reader in reader_list:
        for date in missing_dates:
            directory = '/'.join([main_directory, node, instrument])
            directory += '*'.join(['', date, ''])

            # Check to see if this particular file exists before executing callback
            if glob.glob(directory):
                playback_command = ' '.join(['playback', reader, driver, refdes, event_url, particle_url, directory])
                logging.info("%s", playback_command)

                # Some playback reader types may not ingest the data at all.
                # Timeout after 90 seconds and continue to the next reader type or
                # next data.
                signal.alarm(90)    
                try:
                    call(playback_command, shell=True)
                except TimeoutException:
                    logging.warning('%s Took more than 90 seconds. Timing out this ingestion.', playback_command)
                    continue 
                else:
                    signal.alarm(0)


def main():
    arg = docopt(__doc__)
    logging.getLogger().setLevel(logging.INFO)
    
    if arg['<event_url>'] and arg['<particle_url>'] and arg['<server>']:
        Cabled.cabled_drivers_raw = request_cabled_raw()
        event_url = arg['<event_url>']
        particle_url = arg['<particle_url>']
        server = arg['<server>']
        refdes_list = list_missing_dates.get_refdes_list(server)
        missing_data_dict = {}
        
        for refdes in refdes_list:
            if is_cabled(refdes):
                missing_data_list = list_missing_dates.get_missing_data_list(refdes, server) # returns tuple
                if missing_data_list:
                    missing_data_dict[refdes] = missing_data_list
        
        for refdes, missing_dates in missing_data_dict.iteritems():
            for begin, end in missing_dates:
                dates = date_list(begin, end)
                playback(refdes, event_url, particle_url, dates)


if __name__ == "__main__":
    main()