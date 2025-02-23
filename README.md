## Background

This repo contains code to augment the ongoing efforts to preserve data hosted on government websites. The code is focused on accessing data through the NOAA API. Ongoing efforts include:

* Archive Team's End Of Term crawl
  * Details here: https://wiki.archiveteam.org/index.php/US_Government
  * Searchable here: https://web.archive.org/collection-search/EndOfTerm2024WebCrawls
  * Example: https://web.archive.org/collection-search/EndOfTerm2024WebCrawls/8454049 shows limited results, say, a given station's [Physical Oceanography](#physical-oceanography) data.
  * See also: https://www.reddit.com/r/DataHoarder/comments/1ihalfe/how_you_can_help_archive_us_government_data_right/
* Data.gov Archive from the Harvard Law Scool Library's Library Innovation Lab 
  * Details here: https://lil.law.harvard.edu/blog/2025/02/06/announcing-data-gov-archive/
  * Example: This archive [only crawls the top level](https://www.reddit.com/r/DataHoarder/comments/1ijhybf/harvards_library_innovation_lab_just_released_all/), so while [an entry](https://source.coop/harvard-lil/gov-data/collections/data_gov/coastal-meteorological-and-water-temperature-data-from-national-water-level-observation-network) exists for https://www.ncei.noaa.gov/data/oceans/ndbc/co-ops/, it doesn't include the actual data.
  * See also:  (includes a description of how this is a shallow crawl)

The data scraped by this codebase will be registered with https://www.datarescueproject.org/ and uploaded to DataLumos.

## Tide Predictions

Tide predictions for future dates were pulled to preserve access to such data without relying on paid
vendors.

> [!CAUTION]
> The NOAA website includes the following disclaimer:
>
> *Disclaimer: The predictions from NOAA Tide Predictions are based upon the latest information available as of the date of your request.*

However, the NOAA website also expressly notes that tide predictions up to 2 years in the future are made available. 
> NOAA Tide Predictions allows users of the Tides and Currents website (http://tidesandcurrents.noaa.gov) to generate tide predictions for up to 2 years in the past or future, at any of 3000+ locations around the United States. 

This seems to refer to how Annual Prediction Tide Tables are available for 2023 through 2027 (inclusive) as of February 2025.

Similar agencies -- such as the Port of London Authority -- offer predictions up to 5 years in the future.
> ...the web based predictions are generated in house by the PLA using Geotide to give predictions for up to 5 years in advance and for all tide stations

### Supporting information from the NOAA website

The NOAA FAQ (https://tidesandcurrents.noaa.gov/faq.html) provides relevant information about accuracy and availability. This information is partially duplicated below for convenience; the complete FAQ has been archived.

#### Q: How accurate are the tide predictions?

The accuracy of the tide predictions is different for each location. Periodically, we do a comparison of the predicted tides versus the observed tides for a calendar year. The information generated is compiled in a Tide Prediction Accuracy Table. We work to ensure that the predictions are as accurate as possible. However, we can only predict the astronomical tides; water level changes created by the gravity of the Moon, and the relative motions of the Earth, Sun and Moon. We cannot predict the effect that wind, rain, freshwater runoff, and other short-term meteorological events will have on the tides.

In general, predictions for stations along the outer coast are more accurate than those for stations farther inland; such as along rivers, or inbays or other estuaries. Inland stations tend to have a stronger non-tidal influence; that is, they are more susceptible to the effects of wind and other meteorological effects than stations along the outer coast. An example of an inland station that is difficult to predict is Baltimore, Maryland. This station is located at the northern end of Chesapeake Bay. Winds that blow along the length of the bay have been known to cause water levels to be 1-2 feet above or below the predicted tides.

Stations in relatively shallow water, or with a small tidal range, are also highly susceptible to meteorological effects, and thus, difficult to accurately predict. At these stations, short-term weather events can completely mask the astronomical tides. Many of the stations along the western Gulf of Mexico fall into this category. An example is Galveston, Texas. This station is in a bay that is relatively shallow and has a small opening to the sea. At this station it is possible for meteorological events to delay or accelerate the arrival of the predicted tides by an hour or more.

#### Q: I can only get a short time period of data from your website and data services. How can I get a longer time series of data?

All of our online data services have limitations on the amount (length) of data which can be retrieved through a single data query. These limitations are necessary to prevent large data requests from slowing or preventing data access to our customers.

The data length limitation are based on the interval of the data being retrieved.

    6-Minute interval data is limited to 1 month
    Hourly interval data is limited to 1 year
    Daily Means (Great Lakes only) is limited to 10 years
    High/Low Tides or Max/Min currents are limited to 1 year
    Monthly Means water level data is limited to 200 years

There are no exceptions to these limitations.

The only available means to retrieve a longer data series of data would be to use one of the [Web Services](https://tidesandcurrents.noaa.gov/web_services_info.html) which we offer to retrieve data using a query system, and repeat that query as needed in order to compile the length of data required.

### Datum validation

NOAA data was cross-referenced against the Jeppesen tide chart posted at Kalaloch for July 2023 -- both for Destruction Island. They matched to roughly +/-0.1 ft with the NOAA data using the datum MLLW.

### API issue with subordinate stations

API requests must explicitly include the `interval` for subordinate stations. For example:
```
https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions&begin_date=20230630&end_date=20230801&datum=MLLW&station=9440574&time_zone=lst_ldt&units=english&interval=hilo&format=json
```

## Physical Oceanography

Physical Oceanography data is available at https://www.ncei.noaa.gov/data/oceans/ndbc/co-ops/ (via https://catalog.data.gov/dataset/coastal-meteorological-and-water-temperature-data-from-national-water-level-observation-network), but that data only spans 2013-2024, inclusive. Further, it appears that neither of the ongoing efforts listed above have captured the actual data. The data is in `netCDF4` format and includes the following parameters:

* time
* wind_speed
* wind_speed_qc
* wind_speed_detail_qc
* wind_speed_release
* wind_direction
* wind_direction_qc
* wind_direction_detail_qc
* wind_direction_release
* wind_gust
* wind_gust_qc
* wind_gust_detail_qc
* wind_gust_release
* air_pressure_at_sea_level
* air_pressure_at_sea_level_qc
* air_pressure_at_sea_level_detail_qc
* air_pressure_at_sea_level_release
* air_temperature
* air_temperature_qc
* air_temperature_detail_qc
* air_temperature_release
* sea_surface_temperature (see [Water Temperatures](#water-temperatures) for more information)
* sea_surface_temperature_qc
* sea_surface_temperature_detail_qc
* sea_surface_temperature_release

## Water Temperatures

This data set is partially included in the [Physical Oceanography](#physical-oceanography) data set (where temperatures are stored in Kelvin), but temperature data exists for years prior to the period covered by Physical Oceanography.