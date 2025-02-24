import calendar
from datetime import date
import itertools
import os
import requests
import scrapy


class BasicNOAASpider(scrapy.Spider):
    name  = "baseclass"

    def __init__(self, name = None, **kwargs):
        super().__init__(name, **kwargs)
        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)

    @property
    def save_dir(self):
        return f"data-{self.name}"
    
    def get_stations(self):
        response = requests.get(self.stations_url)
        return response.json()["stations"]
    
    def start_requests(self):
        stations = self.get_stations()
        for station in stations:
            station_id = station["id"]
            args = dict(station_id=station_id)
            url = self.url.format(**args)
            yield scrapy.Request(url=url, 
                                 callback=self.parse, cb_kwargs=args)
            
    def parse(self, response, station_id):
        save_path = os.path.join(
            self.save_dir, f"{station_id}.json")
        with open(save_path, "w") as f:
            f.write(response.text)

class TimeSeriesNOAASpider(BasicNOAASpider):
    TIME_DATA_MONTHLY = "monthly"
    TIME_DATA_ANNUAL =  "annual"
    url = ""
    stations_url = ""
    start_year = 1990
    time_type = TIME_DATA_MONTHLY
    
    def get_time_periods(self) -> tuple[date, date]:
        time_periods = []
        if self.time_type == self.TIME_DATA_MONTHLY:
            years = range(self.start_year, 2025) # exclude 2025
            months = (list(itertools.product(years, range(1, 13)))
                            + [(2025, 1), (2025, 2)])
            for year, month in months:
                _, days = calendar.monthrange(year, month)
                time_periods.append(
                    (date(year, month, 1), date(year, month, days)))
        else:
            years = range(self.start_year, 2026)
            time_periods = [(date(year, 1, 1), date(year, 12, 31))
                            for year in years]
        return time_periods

    def start_requests(self):
        stations = self.get_stations()
        time_periods = self.get_time_periods()
        for station in stations:
            station_id = station["details"]["id"]
            for time_period in time_periods:
                begin = time_period[0].strftime("%Y%m%d")
                end = time_period[1].strftime("%Y%m%d")
                args = dict(begin=begin, end=end, station_id=station_id)
                url = self.url.format(**args)
                yield scrapy.Request(url=url, 
                                     callback=self.parse, cb_kwargs=args)

    def parse(self, response, begin, end, station_id):
        save_path = os.path.join(
            self.save_dir, f"{begin}-{end}-{station_id}.json")
        with open(save_path, "w") as f:
            f.write(response.text)