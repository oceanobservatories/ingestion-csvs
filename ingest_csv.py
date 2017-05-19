#!/usr/bin/env python
import sys
import glob
import csv
import re
from ingest_file import ingest_files


DEPLOYMENT_PATTERN = re.compile(r'.*/[DR](\d{5})/.*')


def deployment_number(mask):
    match = re.match(DEPLOYMENT_PATTERN, mask)
    return int(match.group(1))


def read_csvs(ingest_csv):
    with open(ingest_csv, 'rb') as csvfile:

        reader = csv.reader(csvfile)
        for route, mask, designator, method in reader:
            if route == 'uframe_route': continue  # header line
            if not len(route): continue  # empty line
            if route[0] == '#': continue  # comment line
            filenames = glob.glob(mask)
            ingest_files(route, designator, method, deployment_number(mask), filenames)


if __name__ == '__main__':
    csvs = sys.argv[1:]

    for csv_file in csvs:
        print '----- processing ', csv_file, ' -----'
        read_csvs(csv_file)
