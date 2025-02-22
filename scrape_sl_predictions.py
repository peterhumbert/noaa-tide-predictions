import os
import requests


SL_RISE_PROJECTION_URL = (
    "https://api.tidesandcurrents.noaa.gov/dpapi/prod/webapi/"
    "product/slr_projections.json?units=english&report_year=2022&page={page}"
) # all projection years, all stations/grids, and all scenarios

if __name__ == "__main__":
    page = 1
    total_pages = 99999
    while page <= total_pages:
        url = SL_RISE_PROJECTION_URL.format(page=page)
        response = requests.get(url)
        dir = "sl-data"
        if not os.path.exists(dir):
            os.mkdir(dir)
        if response.status_code == 200:
            filepath = os.path.join(dir, f"page-{page}.json")
            with open(filepath, "w") as f:
                f.write(response.text)
            total_pages = response.json()["totalPages"]
        else:
            print(f"Page {page} failed.")
        page += 1