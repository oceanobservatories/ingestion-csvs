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
import requests
import re
import glob
import list_missing_dates
from subprocess import call
from datetime import datetime, timedelta

g_cabled_drivers_raw = []

def request_cabled_raw():
    drivers_conf_git_link = "https://raw.githubusercontent.com/ooi-integration/ingestion-csvs/master/cabled_drivers_list.txt"
    return str(requests.get(drivers_conf_git_link).text).split('\n')
    
def get_driver(refdes):
    """
    Get the driver from the cabled_drivers_list.txt file
    """
    global g_cabled_drivers_raw

    for line in g_cabled_drivers_raw:
        if refdes in line:
            return line.split()[1]

    return None

def get_reader_type(refdes):
    """
    Get the reader type from the cabled_drivers_list.txt file
    """
    global g_cabled_drivers_raw
    first_pass = False
    reader = []

    for line in g_cabled_drivers_raw:
        if refdes in line:
            first_pass = True
            reader.append(line.split()[2])
        elif first_pass: 
            if line.split()[0] != 'datalog' and \
                line.split()[0] != 'chunky' and \
                line.split()[0] != 'ascii':
                first_pass = False
                break
            else:
                reader.append(line.split()[0])
    return reader

def is_cabled(refdes):
    """
    Only get cabled assemblies.
    Table provided by the cabled_drivers_list.txt file.
    """ 
    global g_cabled_drivers_raw

    for line in g_cabled_drivers_raw:
        if refdes in line:
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
        global g_cabled_drivers_raw
        g_cabled_drivers_raw = request_cabled_raw()
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