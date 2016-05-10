Scraper for Austria
=========================

<http://www.transparenzdatenbank.at/>

Scrapy scraper in scrapy_fs directory.


## Some cmd line documentation

    YEAR="2014"
    curl -vv 'http://www.transparenzdatenbank.at/suche' -H 'Origin: http://www.transparenzdatenbank.at' -H 'Accept-Encoding: gzip, deflate' -H 'PAGINATION_CURRENT: 1' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36' -H 'Content-Type: application/json;charset=UTF-8' -H 'Accept-Language: en-US,en;q=0.8,de;q=0.6' -H 'Accept: application/json, text/plain, */*' -H 'Referer: http://www.transparenzdatenbank.at/' -H 'PAGINATION_PER_PAGE: 500000' -H 'Connection: keep-alive' -H 'DNT: 1' --data-binary '{"name":"","betrag_von":"","betrag_bis":"","gemeinde":"","massnahme":null,"jahr":'"$YEAR"',"sort":"name"}' --compressed > "data_$YEAR.json"
    jq length data_2014.json
