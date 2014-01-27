FarmSubsidy.org Scrapers
========================

[FarmSubsidy](http://farmsubsidy.openspending.org/) is a website that collects the payment data of the Common Agriculture Policy (CAP) which represents about a third of the EU budget. It was run by a group of journalists and activists for the past years. In 2013 the [OpenSpending project](http://openspending.org/) of the [Open Knowledge Foundation](http://okfn.org/) took over responsibility of the website.

The FarmSubsidy data is mostly scraped from member state websites. The old scrapers were working well, but were running in costly and proprietary software. This year we need Free and Open Source scrapers and this repository will collect these scrapers and coordinate the effort.

Please have a look at the [member state scraper issues](https://github.com/openspending/farmsubsidy-scrapers/issues?labels=memberstate&page=1&state=open). If you can help provide a scraper that would be awesome.


Background Information
----------------------

If you need an introduction to the topic, you can have a look at the [Wikipedia article](https://en.wikipedia.org/wiki/Common_Agricultural_Policy) about EU agricultural policiy or at the [CAP website from the European Commision](http://ec.europa.eu/agriculture/cap-funding/index_en.htm). The wikipedia article is quite long, for an introduction to the structure of the subsidies just read the [The CAP today](https://en.wikipedia.org/wiki/Common_Agricultural_Policy#The_CAP_today) section.

The main thing you have to know, is that European agricultural subsidies are divided into two funds. *The European Agricultural Guarantee Fund (EAGF)* ([Wikipedia](https://en.wikipedia.org/wiki/European_Agricultural_Guarantee_Fund)) is for direct payments for farmers (majority of payments) and for measures to respond to market disturbances. You will find these two posts separately distinguished in the data provided.

The second fund is the *European Agricultural Fund for Rural Development (EAFRD)* ([Wikipedia](https://en.wikipedia.org/wiki/European_Agricultural_Fund_for_Rural_Development)).


Data Format
-----------

General exchange format will be CSV. [Past data is available at data.farmsubsidy.org](http://data.farmsubsidy.org/).

Requirements for scrapers are not yet determined. A likely format is just a unix program that outputs scraped CSV.

