import calendar
from calendar import monthrange
import glob
import json
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
    "units=standard&timezone=LST/LDT&datum=MLLW&interval={interval}&"
    "clock=12hour&type=txt&annual=false")


ALL_REGION_IDS =[
    # 1393, # California (only harmonic fetched)
    # 1409, # Oregon
    # 1415, # Washington
    1391, # Alaska
    1401, # Maine
    1405, # New Hampshire
    1403, # Massachusetts
    1411, # Rhode Island
    1394, # Connecticut
    1407, # New York
    1406, # New Jersey
    1395, # Delaware
    1410, # Pennsylvania
    1402, # Maryland
    1414, # Virginia
    1396, # Washington DC
    1408, # North Carolina
    1412, # South Carolina
    1398, # Georgia
    1397, # Florida
    1392, # Alabama
    1404, # Mississippi
    1400, # Louisiana
    1413, # Texas
    1542, # Northern Marianas Islands
    1848, # Palau
    1543, # Federated States of Micronesia
    1544, # Marshall Islands
    1399, # Hawaii
    1484, # Kiribati
    1775, # Tokelau
    1771, # American Samoa
    1482, # French Polynesia
    1752, # Cook Islands
    1483, # Fiji
    1535, # Bermuda Islands
    1536, # Bahamas
    1537, # Cuba
    1538, # Jamaica
    1539, # Haiti and Dominican Republic
    1540, # Puerto Rico
    1541  # Lesser Antilles and Virgin Islands 
]


def get_region_stations(region_id, station_type="harmonic"):
    """
    Fetch a list of stations for a given region.

    Parameters
    ----------
    region_id : int
        NOAA region ID
    station_type : {"harmonic", "subordinate", "both"}, optional
        Whether to limit the output to only harmonic stations, only subordinate
        stations, or both. Defaults to "harmonic".

    Returns
    -------
    list[dict]
        List of station definitions from the NOAA API
    """
    response = requests.get(f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/geogroups/{region_id}/children.json")
    if response.status_code != 200:
        raise Exception(f"Response code {response.status_code}")
    data = response.json()["stationList"]
    if station_type == "harmonic":
        data = [i for i in data if i["stationType"] == "R"]
    elif station_type == "subordinate":
        data = [i for i in data if i["stationType"] == "S"]
    else:
        data = [i for i in data if i["stationType"] in ("S", "R")]
    return data


def get_month_data(stn, year, month, progress=True):
    """
    Fetch a single month of data for a single station.

    Parameters
    ----------
    stn : dict
        Station definition from the NOAA API
    year : int
        The 4-digit year
    month : int
        The 1- or 2-digit month, where the value 1 corresponds to January
    progress : bool, optional
        Whether or not to print a statement describing the fetch, by default True

    Returns
    -------
    tuple[str, str]
        The text (data) of the fetch and corresponding filename

    Raises
    ------
    IndexError
        When the station name cannot be determined from the server response
    """
    stn_id = stn["stationId"]
    interval = "6" if stn["stationType"] == "R" else "hilo"
    if progress:
        print(f"Working on {stn_id} for {month}/{year}")
    _, last_day_of_month = monthrange(year, month)
    bdate = f"{year}{str(month).zfill(2)}01"
    edate = f"{year}{str(month).zfill(2)}{last_day_of_month}"
    url = URL_TEMPLATE.format(stnid=stn_id, bdate=bdate, edate=edate, interval=interval)
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Response text {response.text}")
        return None, None
    try:
        station_name = [i for i in response.text.split("\n") if "StationName" in i][0][12:].strip()
    except IndexError as e:
        print(response.url)
        return None, None
    filename = f"{calendar.month_name[month]} {year} {station_name}, {stn_id} Tidal Data.txt"
    filename = filename.replace("/", "---")
    return response.text, filename


def skip(stn_id, year, month):
    """
    Determines whether a fetch can be skipped because data corresponding to the
    given station, year, and month already exists.

    Parameters
    ----------
    stn_id : int
        NOAA station ID
    year : int
        The 4-digit year
    month : int
        The 1- or 2-digit month, where the value 1 corresponds to January

    Returns
    -------
    bool
        Whether the fetch can be skipped
    """
    return len(
        glob.glob(
            os.path.join(
                "data",
                f"{calendar.month_name[month]} {year}*{stn_id} Tidal Data.txt"
            )
        )
    ) > 0


if __name__ == "__main__":
    region_ids = [
        (1391, "ak"),
        (1401, "me"),
        (1399, "hi")
    ]
    for region_id, state in region_ids:
        folder_path = os.path.join("data", state)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        stns = get_region_stations(region_id, station_type="harmonic")
        with open(os.path.join(folder_path, "stations.json"), "w") as f:
            f.write(json.dumps(stns))
        start_year = 2025
        end_year = 2029 # inclusive
        years = range(start_year, end_year + 1)
        months = range(1, 12 + 1)
        failed = []
        for stn in stns:
            for year in years:
                for month in months:
                    if not skip(stn["stationId"], year, month):
                        try:
                            data, filename = get_month_data(stn, year, month)
                            path = os.path.join(folder_path, filename)
                            if not os.path.exists(path):
                                with open(path, "w") as f:
                                    f.write(data)
                        except (IndexError, TypeError):
                            failed.append((stn, year, month))
    print("DONE")
    print("The following fetches failed:")
    for i in failed:
        print(i)