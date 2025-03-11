import os

import pandas as pd

for region in os.listdir("data"):
    region_path = os.path.join("data", region)
    consolidated_data = {}
    for filename in os.listdir(region_path):
        file_path = os.path.join(region_path, filename)
        if filename != "stations.json":
            data = pd.read_csv(file_path)
            station_id = filename.split(" ")[-3]
            data["Station ID"] = station_id
            year = filename[:4]
            if consolidated_data.get(year) is not None:
                consolidated_data[year] = pd.concat([consolidated_data[year], data])
            else:
                consolidated_data[year] = data
    for year in consolidated_data:
        consolidated_data[year].to_csv(os.path.join("data", f"{region}-{year}.csv"), index=False)
