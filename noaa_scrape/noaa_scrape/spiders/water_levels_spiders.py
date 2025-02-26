from .noaa_data_api_spider import BasicNOAASpider


class HarmonicConstituentsSpider(BasicNOAASpider):
    name = "harmonicconstituents"
    url = (
        "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/"
        "stations/{station_id}/harcon.json"
    )
    stations_url = (
        "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?"
        "type=harcon&expand=details&units=english"
    )

class MonthlyMeanWaterLevelSpider(BasicNOAASpider):
    name = "monthlymeanwaterlevel"
    url = (
        "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?"
        "begin_date=19000222&end_date=20250225&station={station_id}&"
        "product=monthly_mean&datum=STND&time_zone=gmt&units=english&format=json"
    )
    stations_url = (
        "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?"
        "type=waterlevels&units=english"
    )

