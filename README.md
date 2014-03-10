FarmSubsidy.org Scrapers
========================

[FarmSubsidy](http://farmsubsidy.openspending.org/) is a website that collects the payment data of the Common Agriculture Policy (CAP) which represents about a third of the EU budget. It was run by a group of journalists and activists for the past years. In 2013 the [OpenSpending project](http://openspending.org/) of the [Open Knowledge Foundation](http://okfn.org/) took over responsibility of the website.

The FarmSubsidy data is mostly scraped from member state websites. The old scrapers were working well, but were running in costly and proprietary software. This year we need Free and Open Source scrapers and this repository will collect these scrapers and coordinate the effort.

Please have a look at the [member state scraper issues](https://github.com/openspending/farmsubsidy-scrapers/issues?labels=memberstate&page=1&state=open). If you can help provide a scraper that would be awesome.


Developer Documentation
-----------------------

More extensive developer documentation is just being build up at http://farmsubsidy.readthedocs.org.

Background Information
----------------------

If you need an introduction to the topic, you can have a look at the [Wikipedia article](https://en.wikipedia.org/wiki/Common_Agricultural_Policy) about EU agricultural policiy or at the [CAP website from the European Commision](http://ec.europa.eu/agriculture/cap-funding/index_en.htm). The wikipedia article is quite long, for an introduction to the structure of the subsidies just read the [The CAP today](https://en.wikipedia.org/wiki/Common_Agricultural_Policy#The_CAP_today) section.

The main thing you have to know, is that European agricultural subsidies are divided into two funds. *The European Agricultural Guarantee Fund (EAGF)* ([Wikipedia](https://en.wikipedia.org/wiki/European_Agricultural_Guarantee_Fund)) is for direct payments for farmers (majority of payments) and for measures to respond to market disturbances. You will find these two posts separately distinguished in the data provided.

The second fund is the *European Agricultural Fund for Rural Development (EAFRD)* ([Wikipedia](https://en.wikipedia.org/wiki/European_Agricultural_Fund_for_Rural_Development)).


Data Sources
------------

Data is provided on a country-by-country basis. Mostly you will find a web form where you can filter the data by things like year, amount or the region and get back an HTML table with the single payments. Sometimes data is also provided in a downloadable format.

Here are some examples:

* [Belgium](http://www.belpa.be/pub/EN/data.html) (just hit *search* button)
* [UK](http://cap-payments.defra.gov.uk/) (get data by searching for amount > 1.000.000)
* [Germany](http://www.agrar-fischerei-zahlungen.de/Suche) (get data by searching for EGFL > 1.000.000)
* [Slovenia](http://www.arsktrp.gov.si/si/o_agenciji/informacije_javnega_znacaja/prejemniki_sredstev/prejemniki_sredstev/) (get data by selecting a sum and search)

To make things more fun, you often have local abbreviations for the names of the funds (e.g. *ELER* in german for the *EAFRD* fund). One tip: sometimes Google Translate (use Google Chrome for direct translation) can help to translate even the abbreviation back on the local sites. You can (normally) also distinguish the two funds by - like said above - having two posts for the *EAGF* and only one for the *EAFRD*.


Data Format
-----------

General exchange format will be CSV. [Past data is available at data.farmsubsidy.org](http://data.farmsubsidy.org/).

Requirements for scrapers are not yet determined. A likely format is just a unix program that outputs scraped CSV.

