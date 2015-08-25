import os
import shutil
from glob import glob

# Sort Calibration Sheets
for f in [x for x in glob("*.xlsx") if x.startswith("Omaha")]:
    platform_name = f.split("_")[3]
    if not os.path.exists("./%s" % platform_name):
        shutil.os.mkdir(platform_name)
    shutil.copy(f, platform_name)
    os.remove(f)

# Sort Ingestion Parameter Sheets
for f in [x for x in glob("*.csv")]:
    platform_name = f.split("_")[0]
    if not os.path.exists("./%s" % platform_name):
        shutil.os.mkdir(platform_name)
    shutil.copy(f, platform_name)
    os.remove(f)

# Sort Ingestion Parameter Template Sheets
for f in [x for x in glob("*.xlsx")]:
    platform_name = f.split("_")[0]
    if not os.path.exists("./%s" % platform_name):
        shutil.os.mkdir(platform_name)
    shutil.copy(f, platform_name)
    os.remove(f)

