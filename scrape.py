import calendar
from calendar import monthrange
import os
import requests

"""
Downloading .txt files with 6-minute tide predictions has the format...
GET https://tidesandcurrents.noaa.gov/cgi-bin/predictiondownload.cgi?=&
    stnid=9442705&threshold=&thresholdDirection=&bdate=20250501&edate=20250531&
    units=standard&timezone=LST/LDT&datum=MLLW&interval=6&
    clock=12hour&type=txt&annual=false
"""

URL_TEMPLATE = ("https://tidesandcurrents.noaa.gov/cgi-bin/predictiondownload.cgi?=&"
    "stnid={stnid}&threshold=&thresholdDirection=&bdate={bdate}&edate={edate}&"
    "units=standard&timezone=LST/LDT&datum=MLLW&interval=6&"
    "clock=12hour&type=txt&annual=false")

if __name__ == "__main__":
    stnid = 9442705
    years = range(2025, 2029 + 1)
    months = [1]
    # months = [1, 2, 3, 4, 10, 11, 12] # manually pulled peak season months
    for year in years:
        for month in months:
            _, last_day_of_month = monthrange(year, month)
            bdate = f"{year}{str(month).zfill(2)}01"
            edate = f"{year}{str(month).zfill(2)}{last_day_of_month}"
            url = URL_TEMPLATE.format(stnid=stnid, bdate=bdate, edate=edate)
            response = requests.get(url)
            station_name = [i for i in response.text.split("\n") if "StationName" in i][0][12:].strip()
            with open(
                os.path.join(
                    "data", 
                    f"{calendar.month_name[month]} {year} {station_name}, {stnid} Tidal Data.txt"),
                "w") as f:
                f.write(response.text)
