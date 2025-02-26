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
