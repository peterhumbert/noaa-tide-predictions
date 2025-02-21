import glob
import itertools
import json
from multiprocessing import Pool
import os
import sys
import requests
import time

"""
Downloading .csv files with tide predictions has the format below. Default
interval seems to be 6 minutes for harmonic stations. Have tested a
1-year fetch.

GET https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?
    begin_date=20250221&end_date=20250225&station=9441187&
    product=predictions&datum=MLLW&time_zone=lst_ldt&
    units=english&format=json

Valid formats are json, csv, and xml. The csv format downloads a
.csv file.
"""

URL_TEMPLATE = ("https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?"
                  "begin_date={begin_date}&end_date={end_date}&station={stnid}&"
                  "product=predictions&datum=MLLW&time_zone=lst_ldt&"
                  "units=english&format=csv")



ALL_REGION_IDS =[
    # 1393, # California (only harmonic fetched)
    # 1409, # Oregon
    # 1415, # Washington
    # 1391, # Alaska
    # 1401, # Maine
    # 1405, # New Hampshire
    # 1403, # Massachusetts
    # 1411, # Rhode Island
    # 1394, # Connecticut
    # 1407, # New York
    # 1406, # New Jersey
    # 1395, # Delaware
    # 1410, # Pennsylvania
    # 1402, # Maryland
    # 1414, # Virginia
    # 1396, # Washington DC
    # 1408, # North Carolina
    # 1412, # South Carolina
    # 1398, # Georgia
    # 1397, # Florida
    # 1392, # Alabama
    # 1404, # Mississippi
    # 1400, # Louisiana
    # 1413, # Texas
    # 1542, # Northern Marianas Islands
    # 1848, # Palau
    # 1543, # Federated States of Micronesia
    # 1544, # Marshall Islands
    # 1399, # Hawaii
    # (1484, "kiribati"), # Kiribati
    # (1775, "tokelau"), # Tokelau
    # (1771, "american-samoa"), # American Samoa
    # (1482, "french-polynesia"), # French Polynesia
    # (1752, "cook-islands"), # Cook Islands
    # (1483, "fiji"), # Fiji
    # (1535, "bermuda"), # Bermuda Islands
    # (1536, "bahamas"), # Bahamas
    # (1537, "cuba"), # Cuba
    # (1538, "jamaica"), # Jamaica
    # (1539, "haiti-dr"), # Haiti and Dominican Republic
    # (1540, "pr"), # Puerto Rico
    # (1541, "antilles-vi")  # Lesser Antilles and Virgin Islands 
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


def get_year_data(stn, year, progress=True):
    """
    Fetch a single year of data for a single station.

    Parameters
    ----------
    stn : dict
        Station definition from the NOAA API
    year : int
        The 4-digit year
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
    stn_name = stn["geoGroupName"]
    filename = f"{year} {stn_name} {stn_id} Tidal Data.csv"
    filename = filename.replace("/", "---")
    if progress:
        print(f"Working on {stn_id} for {year}")
    begin_date = f"{year}0101"
    end_date = f"{year}1231"
    url = URL_TEMPLATE.format(stnid=stn_id, begin_date=begin_date, end_date=end_date)
    if stn["stationType"] == "S":
        url += "&interval=hilo"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Response text {response.text}")
        return None, filename
    folder_path = os.path.join("data", stn["state"])
    path = os.path.join(folder_path, filename)
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(response.text)
    return response.text, filename


def skip(stn_id, state, year):
    """
    Determines whether a fetch can be skipped because data corresponding to the
    given station, year, and month already exists.

    Parameters
    ----------
    stn_id : int
        NOAA station ID
    state : str
        2-letter state abbreviation
    year : int
        The 4-digit year

    Returns
    -------
    bool
        Whether the fetch can be skipped
    """
    return len(
        glob.glob(
            os.path.join(
                "data",
                state,
                f"{year}*{stn_id}*.csv"
            )
        )
    ) > 0


if __name__ == "__main__":
    t_end = None
    if len(sys.argv) > 1:
        t0 = time.time()
        t_end = float(sys.argv[1])*3600 + t0
    region_ids = ALL_REGION_IDS
    failed = []
    for region_id, state in region_ids:
        folder_path = os.path.join("data", state)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        stns = get_region_stations(region_id, station_type="both")
        for stn in stns:
            stn["state"] = state
        with open(os.path.join(folder_path, "stations.json"), "w") as f:
            f.write(json.dumps(stns))
        start_year = 2025
        end_year = 2029 # inclusive
        years = range(start_year, end_year + 1)
        fetches = itertools.product(stns, years)
        fetches = [(stn, year) for stn, year in fetches if not skip(
            stn["stationId"], stn["state"], year)]
        with Pool(4) as p:
            results = p.starmap(get_year_data, fetches)
        for data, filename in results:
            if data is None:
                failed.append(filename)
    print("DONE")
    print("The following fetches failed:")
    for i in failed:
        print(i)