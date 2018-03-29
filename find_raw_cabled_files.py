"""
Usage:
    find_raw_cabled_files.py <reference_designator>
    find_raw_cabled_files.py [-l] <reference_designator> 

This script will find the driver, reader type, and the files associated with this reference designator. This is for cabled data.
Without using the -l option, the script will only output the file glob to save space. With -l, the entire list of files will put listed.

Example: python find_raw_cabled_files.py RS01SLBS-LJ01A-05-HPIESA101
         python find_raw_cabled_files.py -l RS01SLBS-LJ01A-05-HPIESA101

Arguments:
    reference_designator

Options:
    -h --help
    -l --list_files     list out cabled files for specific reference designator
    -v                  verbose mode
    -q                  quiet mode
"""

import os
import glob

from docopt import docopt
import numpy as mp
import pandas as pd


def request_cabled_raw():
    url = "https://raw.githubusercontent.com/ooi-integration/ingestion-csvs/master/cabled_drivers_list.txt"
    df = pd.read_csv(url, sep='\s{2,}', engine='python', dtype=str)
    df.loc[df['Type'] == 'None', ['Type']] = df['Reference Designator']
    df.loc[df['Reference Designator'] == df['Type'], ['Reference Designator']] = df['Reference Designator'].shift(1)
    return df


def cabled_dir(refdes):
    """
    Only get cabled assemblies.
    Table provided by the cabled_drivers_list.txt file.
    """ 
    main_dir = '/rsn_cabled/rsn_data/DVT_Data'
    directory = '/'.join([main_dir, refdes.split('-')[1].lower(), ''])

    if os.path.isdir(directory):
        return directory


def get_driver_and_type(refdes, df):
    """
    Get both driver and reader type
    """
    driver = df.loc[df['Reference Designator'] == refdes]['Driver'].iloc[0]
    reader = []

    df = df[df['Reference Designator'] == refdes]

    for i in df.index:
        if df['Type'].loc[i] != 'nan':
            reader.append(df['Type'].loc[i])

    return (driver, reader)


def main():
    arg = docopt(__doc__)
    if arg['<reference_designator>']:
        refdes = arg['<reference_designator>']
        df = request_cabled_raw()
        
        try:
            cabled_directory = cabled_dir(refdes)
        except IndexError:
            print "Invalid Reference Designator Format"
            return
        
        if cabled_directory and not df.loc[df['Reference Designator'] == refdes].empty:
            inst = refdes.split('-')[3]
            driver, reader_type = get_driver_and_type(refdes, df)
            file_path = cabled_directory + inst + '*'
            glob_directory = glob.glob(file_path)

            if glob_directory:
                print "Reference Designator: " + refdes
                print "Driver: " + driver
                print "Reader Type(s):",

                # Separate reader type with commas, no comma for last type 
                for reader in reader_type:
                    if reader != reader_type[-1]:
                        print reader + ',',
                    else:
                        print reader
                            
                print "File glob: " + file_path

                # Option to list out all the files available
                if arg['--list_files']:
                    for path in glob_directory:
                        print path
            else:
                print "There are no files available." 
        else:
            print "This is not a valid cabled reference designator or it does not exist in the directory."
    
    
if __name__ == "__main__":
    main()


