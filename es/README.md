Scraper for Spain
=========================


#### Introduction

It seems that the easiest way to access the EAGF & EAFRD data is through the [FEGA eAdministration][1] page

Right now the information is available for 2010, 2011 and 2012

[1]: https://www.sede.fega.gob.es/EfeSde/es/buscador_transparencia/index.jsp

#### Script description

The script expects a year as an input parameter and scrapes the data for that year into a CSV file inside the data folder (automatically created)

All texts are uppercased, names, address, town, etc.

The nomenclature of the output file is payment_YEAR.csv, i.e.: payment_2013.csv for 2013

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

    $ rake scrape:subsidies[2013]


