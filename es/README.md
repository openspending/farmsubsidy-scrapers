Scraper for Spain
=========================


#### Introduction

It seems that the easiest way to access the EAGF & EAFRD data is through the [FEGA eAdministration][1] page

Right now the information is available for 2010, 2011 and 2012

[1]: https://www.sede.fega.gob.es/EfeSde/es/buscador_transparencia/index.jsp

#### Script description

The script expects a year as an input parameter and scrapes the data for that year into a CSV file inside the data folder (automatically created)

The nomenclature of the output file starts with the year and then the script name, i.e.: 2012scrapeFEGAdata.csv for 2012

If some unexpected behaviour is found the script logs the details inside the logs folder (automatically created)

#### Script requirements

Ruby script
* require 'csv' 
* require 'mechanize'
* require 'fileutils'
* require 'unicode_utils' # For internationalization issues

Rake file
* require 'pty' # To buffer out the stdout

#### Execution of the script

* To run the script

    $ rake scrape:subsidies[2012]


