"""
Usage: ingest_missing.py <event_url> <particle_url>

This script will grab dates missing from data ingestion and then it will use the playback command to ingest them.
Provide the event_url and particle_url. 

Arguments:
    event_url    
    particle_url

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
import list_missing_dates
from subprocess import call
from datetime import datetime, timedelta


"""
Get the driver from the cabled_drivers_list.txt file
"""
def get_driver(refdes):
    drivers_conf_git_link = "https://raw.githubusercontent.com/ooi-integration/ingestion-csvs/master/cabled_drivers_list.txt"
    driver_conf_raw = str(requests.get(drivers_conf_git_link).text)

    driver_conf_raw = driver_conf_raw.split('\n')

    for line in driver_conf_raw:
        if refdes in line:
            return line.split()[1]

    return None

"""
Get the reader type from the cabled_drivers_list.txt file
"""
def get_reader_type(refdes):
    drivers_conf_git_link = "https://raw.githubusercontent.com/ooi-integration/ingestion-csvs/master/cabled_drivers_list.txt"
    driver_conf_raw = str(requests.get(drivers_conf_git_link).text)

    driver_conf_raw = driver_conf_raw.split('\n')
    first_pass = False
    reader = []

    for line in driver_conf_raw:
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

"""
    Only get cabled assemblies.
    Table provided by the cabled_drivers_list.txt file.
""" 
def get_cabled_assembly(refdes):
    assembly_set = {'lj01c', 'lv01a', 'lv03a', 'mj01c', 'mj03c', 
                    'mj03f', 'pc03a', 'pd03a', 'sf03a', 'lj01a', 
                    'lj01d', 'lv01b', 'mj01a', 'mj03a', 'mj03d', 
                    'pc01a', 'pd01a', 'sf01a', 'lj01b', 'lj03a', 
                    'lv01c', 'mj01b', 'mj03b', 'mj03e', 'pc01b', 
                    'pd01b', 'sf01b'}
    assembly = refdes.split('-')[1]
    if assembly in assembly_set:
        return assembly
    else:
        return None

"""
    Obtain a list of the missing dates.
"""
def date_list(firstDate, secondDate):
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
    startDate = datetime.strptime(startDate, '%Y-%m-%d').date()
    endDate = datetime.strptime(endDate, '%Y-%m-%d').date()
    delta = endDate - startDate

    # Get all dates in between startDate and endDate (inclusive)
    # to remove startDate and endDate, range(1, delta.days)
    for i in range(delta.days + 1):
        tempDate = startDate + timedelta(days = i)
        tempDate = tempDate.strftime('%Y-%m-%d').replace('-','')
        missing_dates_list.append(tempDate)

    return missing_dates_list

"""
    This function will organize the missing dates into nested dictionaries.
    This will make it easier to put together the directory glob with the missing dates.
    Format of raw date is YYYYMMDD
"""
def organize_dates(missing_dates):
    year = ''
    years_dict = {}
    years = []
    month = ''
    months_dict = {}
    months = []
    day = ''
    days_dict = {}
    days = []

    # This will organize the dates into nested dictionaries
    """
        {YYYY :
                {MM :
                    {D :
                        [D, D, D ,D]
                    }
                }
                {MM :
                    {D :
                        [D, D, D ,D]
                    }
                }
        }
    """
    for i, date in enumerate(missing_dates):
        temp_year = date[0] + date[1] + date[2] + date[3]
        temp_month = date[4] + date[5]
        # Just get first digit of the day
        temp_day = date[6]

        if not year:
            year = temp_year
            month = temp_month
            day = temp_day

        elif year != temp_year or i >= len(missing_dates) - 1:
            days.append(date[7])
            days_dict[day] = days
            months_dict[month] = days_dict
            years_dict[year] = months_dict

            # The year has now changed, then so does the month and the day
            del days_dict
            days_dict = {}
            day = temp_day
            del days
            days = []
            year = temp_year
            del years
            years = []
            del months_dict
            months_dict = {}
            del months
            months = []
            month = temp_month
            day = temp_day
            
        
        if year == temp_year:
            if month == temp_month:
                if day == temp_day:
                    days.append(date[7])
                elif day != temp_day:
                    # The month has not changed in this case, so the very last day of the month
                    # will not change. In the clase where the month does change, so does the day.
                    # That day change will be made in the following elif statement
                    days_dict[day] = days
                    day = temp_day
                    del days
                    days = []
                    days.append(date[7])

            elif month != temp_month:
                # In the case where the month has changed. So day, also needs to change.
                if day != temp_day:
                    days_dict[day] = days
                    day = temp_day
                    del days
                    days = []
                    days.append(date[7])
                
                months_dict[month] = days_dict

                month = temp_month
                del days_dict
                days_dict = {}
                
    return years_dict

"""
    Get the dates in the correct format.
    Future considerations would be to shrink the size of this even further.
"""
def glob_dates(organize_dates):
    date_glob = '{'
    
    for i, (year, months_dict) in enumerate(organize_dates.iteritems()):
        date_glob += year + '{'
        for j, (month, days_dict) in enumerate(months_dict.iteritems()):
            date_glob += month + '{'
            first_day = True

            for k, (day, ones_list) in enumerate(days_dict.iteritems()):
                if first_day:
                    date_glob += day + '['
                    first_day = False
                    
                for ones in ones_list:
                    date_glob += ones
                    first_day = True
                if k < len(days_dict) - 1:
                    date_glob += '],'
                else:
                    date_glob +=']'

            if j < len(months_dict) - 1:
                date_glob += '},'
            else:
                date_glob += '}'

        if i < len(organize_dates) - 1:
            date_glob += '},'
        else:
            date_glob += '}'
    date_glob += '}'
    return date_glob

"""
    This is the main function to get the dates into their specified
    directory glob format. This will be used for the playback command.
"""
def get_dir_glob(missing_dates_dict):
    base_dir = '/rsn_cabled/rsn_data/DVT_Data/'
    directory = ''
    instrument = ''
    missing_dates = []
    playback_dict = {}

    for key, date_tup_list in missing_dates_dict.iteritems():
        firstDate = ''
        secondDate = ''
        
        refdes = key
        assembly = get_cabled_assembly(refdes.lower())
        instrument = refdes.split('-')[3]

        directory = base_dir + assembly + '/' + instrument + '*'

        for first, second in date_tup_list:
            firstDate = first
            secondDate = second
            missing_dates += date_list(firstDate, secondDate)

        organized_dates = organize_dates(missing_dates)
        dates_glob = glob_dates(organized_dates)
        directory_glob = directory + dates_glob + '*'
        playback_dict[refdes] = directory_glob

    return playback_dict

"""
    Put together the directory glob and other options for the playback command.
    This will then playback cabled data.
"""
def playback(directory, refdes, event_url, particle_url):
    driver = get_driver(refdes)
    reader_list = get_reader_type(refdes)

    playback_command = 'playback ' + driver + ' ' + refdes + ' ' + event_url + particle_url + directory

    for reader in reader_list:
        playback_command = 'playback ' + reader + ' ' + driver + ' ' + refdes + ' ' + event_url + particle_url + directory
        print playback_command + '\n'
        call(playback_command, shell=True)

def main(args):

    if args['<event_url>'] and args['<particle_url>']:
        event_url = args['<event_url>'] + ' '
        particle_url = args['<particle_url>'] + ' '
        print "Getting list of Reference Designators"
        refdes_list = list_missing_dates.get_refdes_list()
        missing_data_dict = {}
        
        print "Assembling each date to the specific reference designator"
        for refdes in refdes_list:
            assembly = get_cabled_assembly(refdes.lower())
            if assembly:
                missing_data_list = list_missing_dates.get_missing_data_list(refdes) # returns tuple
                if missing_data_list:
                    missing_data_dict[refdes] = missing_data_list
            
        
        playback_dict = get_dir_glob(missing_data_dict)

        for refdes, directory_glob in playback_dict.iteritems():
            playback(directory_glob, refdes, event_url, particle_url)
    

if __name__ == "__main__":
    args = docopt(__doc__)
    print(args)
    main(args)