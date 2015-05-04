import os, sys
import logging, logging.config
import csv
from StringIO import StringIO
from glob import glob

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)-7s | %(asctime)s | %(name)-8s | %(message)s',
            },
        'raw': {
            'format': '%(message)s',
            },
        },
    'handlers': {
        'file_handler': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'filename': "csv_validation.log",
            'mode': 'w',
            },
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
            'formatter': 'raw',
            'stream': 'ext://sys.stdout',
            },
        },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['file_handler', 'stream_handler', ],
            'propagate': False,
            },
        },
    })

log = logging.getLogger('Main')

def get_csvs(filepath):
    all_files = []
    for root, dirs, files in os.walk("."):
        all_files += ["/".join([root, f]) for f in files if f.endswith(".csv")]
    return all_files

def commented(row):
    ''' Check to see if the row is commented out. Any field that starts with # indictes 
        a comment.'''
    return bool([v for v in row.itervalues() if v.startswith("#")])

def file_mask_has_files(row):
    ''' Check to see if any files are found that match the file mask. '''
    return bool(len(glob(row["filename_mask"])))

def file_mask_has_deployment_number(row):
    ''' Check to see if a deployment number can be parsed from the file mask. '''
    try:
        deployment_number = int([
            n for n 
            in row['filename_mask'].split("/") 
            if len(n)==6 and n[0] in ('D', 'R', 'X')
            ][0][1:])
    except:
        return False
    return True

def ingest_queue_matches_data_source(row):
    ''' Check to see if the ingestion route matches the data source specification. '''
    return row['uframe_route'].split("_")[-1] == row['data_source']

log.info("Verifying local CSVs.")

csv_files = get_csvs(".")

for f in csv_files:
    reader = csv.DictReader(open(f))
    log.info("")
    log.info("Validating CSV file: %s" % f) 
    parameters = [r for r in reader if not commented(r)]
    for i, row in enumerate(parameters):
        try:
            if not file_mask_has_files(row):
                log.warning(
                    "%-2s: No files found for %s (%s)." % (i + 2, row["filename_mask"], f))
            if not file_mask_has_deployment_number(row):
                log.warning(
                    "%-2s: Can't parse Deployment Number from %s (%s)." % (i + 2, row["filename_mask"], f))
            if not ingest_queue_matches_data_source(row):
                log.warning(
                    "%-2s: UFrame Route doesn't match Data Source: %s, %s" % (
                        i + 2, row['uframe_route'], row['data_source']))
        except Exception:
            log.exception(f)