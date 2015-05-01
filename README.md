# ingestion-csvs
A definitive collection of calibration and ingestion parameter data for all platforms.

The repository is organized by platform. Each platform directory contains two types of data files.
 * Calibration sheets in Excel format.
 * Ingestion parameter sheets in CSV format.

Filenames adhere to the following conventions:
 * Calibration sheets are named **Omaha_Cal_Info_PLATFORM_XXXXX_.xlsx**, where:
   * PLATFORM is the platform name (e.g. CP02PMCI).
   * XXXXX is the five digit deployment number (e.g. 00001).
 * Ingestion parameter sheets are named **PLATFORM_SXXXXX_ingest.csv**, where:
   * PLATFORM is the platform name.
   * S is the source of data (e.g. D for telemetered, R for recovered).
   * XXXXX is the five-digit deployment number (e.g. 00001).
 
A **Platform Parameters Checklist** Excel spreadsheet is also included in the repository to help keep track of the sheets that are available and the sheets that still need to be created.

## Ingestion Parameter Sheets (CSV Files)
The ingestion parameter sheets require 4 columns of data:
| Column Name          | Description |
| -------------------- | - |
| uframe_route         | The name of the ingestion queue that the EDEX application will pull the files from. |
| filename_mask        | A filename mask that points to the files to be ingested. Can include UNIX style wildcards (*, ?). |
| reference_designator | The reference designator associated with the files to be ingested. |
| data_source          | An indication of whether the data is telemetered or recovered. |

Lines can be commented out in the CSV file by placing a pound-sign # at the beginning of the line, or at the beginning of any cell in the line. It's recommended to place it in the uframe_route column. When a line in the CSV file is commented out, the ingestion script will ingore that line completely.

Extra columns, such as "notes" or "status," can be included in the CSV files. The ingestion script will ignore these columns completely. Feel free to annotate CSV files with extra columns of data as necessary.

