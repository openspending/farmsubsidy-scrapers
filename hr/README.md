# Scraper for Croatia

## Website

[Isplate APPRRR](<http://isplate.apprrr.hr/>)

## Usage
 
Run the commands from the top-level scrapy directory. 

To check Scrapy Contracts:

    scrapy check croatia
    
To collect information for a particular year (defaults to 2015):

    crawl -a year=2014 croatia
    
Data is available from 2014. Results are dumped into an S3 bucket. Remember to set environmental variables: [see Scrapy docs](http://doc.scrapy.org/en/latest/topics/feed-exports.html#topics-feed-storage-s3).