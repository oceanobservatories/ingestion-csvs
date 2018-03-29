# ingestion-csvs
A definitive collection of calibration and ingestion parameter data for all platforms.

The repository is organized by platform. Each platform directory contains two types of data files.
 * Calibration sheets in Excel format.
 * Ingestion parameter sheets in CSV format.

Filenames adhere to the following conventions:
 * Calibration sheets are named `Omaha_Cal_Info_PLATFORM_XXXXX.xlsx`, where:
   * `PLATFORM` is the platform name (e.g. `CP02PMCI`).
   * `XXXXX` is the five digit deployment number (e.g. `00001`).
 * Ingestion parameter sheets are named `PLATFORM_SXXXXX_ingest.csv`, where:
   * `PLATFORM` is the platform name.
   * `S` is the source of data (e.g. `D` for telemetered, `R` for recovered).
   * `XXXXX` is the five-digit deployment number (e.g. `00001`).
 
A **Platform Parameters Checklist** Excel spreadsheet is also included in the repository to help keep track of the 
sheets that are available and the sheets that still need to be created.

## Ingestion Parameter Sheets (CSV Files)
The ingestion parameter sheets require 4 columns of data:

| Column Name          | Description | 
| -------------------- | ----------- |
| `uframe_route`         | The name of the ingestion queue that the EDEX application will pull the files from. |
| `filename_mask`        | A filename mask that points to the files to be ingested. Can include UNIX style wildcards (*, ?). |
| `reference_designator` | The reference designator associated with the files to be ingested. |
| `data_source`          | An indication of whether the data is telemetered or recovered. |

Lines can be commented out in the CSV file by placing a pound sign # at the beginning of the line, or at the beginning 
of any cell in the line. It's recommended to place the pound sign # in the `uframe_route` column. When a line in the 
CSV file is commented out, the ingestion script will ignore that line completely.

Extra columns, such as "notes" or "status," can be included in the CSV files. The ingestion script will ignore these 
columns completely. Feel free to annotate CSV files with extra columns of data as necessary.

# Utilities

## `ingest_csv.py`

Ingest all files described in one or more ingestion csv files.

This allows a simple way to ingest a large amount of uncabled data by simply providing the list of ingestion CSV files.

Usage: 
`ingest_csv.py` `csv_glob`

For example, to ingest all the uncabled data from the CE02SHSP mooring:

```bash
./ingest_csv.py CE02SHSP/*
```

This uses `ingest_file.py` to process each file glob as defined in the ingestion csv file. 

## `ingest_file.py`

Ingest a set of files for a given reference designator. 

This tool is designed to test ingestion for a particular uncabled instrument stream. It can also be used to patch 
ingestion on production, however Large or continual ingestion should be managed by the ingestion tool currently under 
design by Mark Steiner. 

Usage:
`ingest_file.py` `uframe_route` `reference_designator` `data_source` `deployment number` `filename_mask`

Example:
```
./ingest_file.py Ingest.flort-dj-cspp_recovered CE02SHSP-SP002-07-FLORTJ000 telemetered 2 /omc_data/whoi/OMC/CE02SHSP/R00002/extract/*TRIP.txt
```

## `find_raw_cabled_files`

Find files associated with a specific cabled reference designator.

`find_raw_cabled_files.py` `[-l]` `reference_designator`

Example:
```
python find_raw_cabled_files.py CE04OSPS-SF01B-4B-VELPTD106
```
```
python get_raw_data.py -l CE04OSPS-SF01B-4B-VELPTD106
```


# Monitoring

The file ingest queue can be monitored using the `qpid_stat.py` utility in the ooi-tools repository:
