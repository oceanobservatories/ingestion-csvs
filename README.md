# ingestion-csvs
A definitive collection of calibration and ingestion parameter data for all platforms.

The repository is organized by platform. Each platform directory contains two types of data files.
 * Calibration sheets in Excel format.
 * Ingestion parameter sheets in CSV format.

Filenames follow the following conventions:
 * Calibration sheets are named **Omaha_Cal_Info_PLATFORM_XXXXX_.xlsx**, where:
   * PLATFORM is the platform name (e.g. CP02PMCI).
   * XXXXX is the five digit deployment number (e.g. 00001).
 * Ingestion parameter sheets are named **PLATFORM_SXXXXX_ingest.csv**, where:
   * PLATFORM is the platform name.
   * S is the source of data (e.g. D for telemetered, R for recovered).
   * XXXXX is the five-digit deployment number (e.g. 00001).
 
A **Platform Parameters Checklist** Excel spreadsheet is also included in the repository to help keep track of the sheets that are available and the sheets that still need to be created.
