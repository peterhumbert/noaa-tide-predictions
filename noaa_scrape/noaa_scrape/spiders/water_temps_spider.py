from .noaa_data_api_spider import TimeSeriesNOAASpider


class WaterTempSpider(TimeSeriesNOAASpider):
    name = "watertemp"
    url = (
        "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?"
        "begin_date={begin}&end_date={end}&station={station_id}&"
        "product=water_temperature&datum=STND&time_zone=gmt&"
        "units=english&format=json"
    )
    stations_url = (
        "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?"
        "type=watertemp&expand=details&units=english"
    )
    start_year = 1990
    time_type = TimeSeriesNOAASpider.TIME_DATA_MONTHLY
        