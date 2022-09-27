# -*- coding: utf-8 -*-
"""Scraping IMDb tv series.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PVmWl7mg_ktR9ZB93l6Re3knkslnF8fZ
"""

'''
For this project, I will scrape the over 240,000 TV series on IMDb. 

Features I am interested in include: title, release date, country, rating, number of voters, and award wins and nominations. 

To do this, I'll be using the web-scraping framework, scrapy. 

Below are the steps I'll take:
1. Import packages for web scraping, data cleaning, and, possibly, analysis.
   - scrapy
   - pandas
   - seaborn
   - matplotlib

2. Create the web scraping spider

3. Start the scrape
'''

"""1. Import packages"""
# Import scrapy for web scraping
import scrapy

# Import the items where we'll store each movie variable
from .. import items

#from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings


# Solve the ReactorAlreadyInstalled issue by using CrawlerRunner... 
# instead of CrawlerProcess
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
import sys


'''
# For celery
from multiprocessing import Process
from config import celery_app
'''


"""2. The Web Scraping begins

"""

# Assign the IMDb TV series url to the variable, tv_series_url
tv_series_url = 'https://www.imdb.com/search/title/?title_type=tv_series&count=250'

# Write a scrapy spider to crawl IMDb for TV series
class IMDb_TV_Scraper(scrapy.Spider):
  name = "imdb_scraper"
  allowed_domains = ['imdb.com']  # Stops the crawler from leaving imdb.com
  start_urls = [tv_series_url]

  # start_requests method to capture the HTML code of the results page
  def start_requests(self):
    yield scrapy.Request(url = tv_series_url,
                         callback = self.parse_results_page)
    
  # 1. parsing method to loop through result pages
  def parse_results_page(self, response):
    '''
    This loops through every movie result on a results page 
    and accesses the movie page via the movie URL,
    THEN moves to the next results page.
    '''
    # For each movie on a result page, get the link to the movie page
    title_headers = response.css('h3.lister-item-header')
    title_links = title_headers.xpath('./a/@href')
    links_to_follow = title_links.getall()
    
    # For each result on the results page, follow the URL to the movie page
    for url in links_to_follow:
      yield response.follow(url = url,
                            callback = self.parse_movie_page)
      
    # Go to the next page(s) and parse as well
    next_page = response.css('a.lister-page-next.next-page::attr(href)').get()
    if next_page is not None:
        yield response.follow(next_page, callback=self.parse_results_page)
  
  
  # Method to scrape data from the movie page
  def parse_movie_page(self, response):
    '''
    This scrapes the movie page, extracting movie title, global rating, 
    number of voters, release date, country, award wins and nominations, and creators
    '''
    tv_series = items.IMDbItem()

    # Scrape movie features employing XPATH or CSS notation
    tv_series['title'] = response.xpath('//div[contains(@class,"sc-80d4314-1 fbQftq")]/h1/text()').extract_first()
    tv_series['global_rating'] = response.css('div.sc-7ab21ed2-2.kYEdvH > span.sc-7ab21ed2-1.jGRxWM::text').extract_first()
    tv_series['num_of_voters'] = response.xpath('//div[contains(@class,"sc-7ab21ed2-0 fAePGh")]/div[contains(@class,"sc-7ab21ed2-3 dPVcnq")]/text()').extract_first()
    tv_series['release_date'] = response.css('div.sc-f65f65be-0.ktSkVi ul.ipc-inline-list.ipc-inline-list--show-dividers.ipc-inline-list--inline.ipc-metadata-list-item__list-content.base a::text').extract_first()
    tv_series['country'] = response.css('div.sc-f65f65be-0.ktSkVi ul.ipc-inline-list.ipc-inline-list--show-dividers.ipc-inline-list--inline.ipc-metadata-list-item__list-content.base a::text').extract()[1]
    tv_series['award_wins_nominations'] = response.css('div.sc-fcdc3619-0.YgLMu.base ul.ipc-inline-list.ipc-inline-list--show-dividers.ipc-inline-list--inline.ipc-metadata-list-item__list-content.base span::text').extract()
    tv_series['creators'] = response.css('ul.sc-36c36dd0-9.fEgKYH a.ipc-metadata-list-item__list-content-item--link::text').extract()

    yield tv_series


"""Start the Scrape!!"""
# Using Crawler Runner
configure_logging({'LOG_FORMAT' : '%(levelname)s: %(message)s'})
runner = CrawlerRunner(get_project_settings())

if 'twisted.internet.reactor' in sys.modules:
    del sys.modules['twisted.internet.reactor']
    
d = runner.crawl(IMDb_TV_Scraper)
d.addBoth(lambda _: reactor.stop())
reactor.run() # the script will block here until the crawling is over




'''
# lengthen limits for celery to prevent crawler being terminated
SCRAPING_TASK_SOFT_TIME_LIMIT = 30 # mins
SCRAPING_TASK_HARD_TIME_LIMIT = 60 # mins

@celery_app.task(soft_time_limit=SCRAPING_TASK_SOFT_TIME_LIMIT, time_limit=SCRAPING_TASK_HARD_TIME_LIMIT)
'''
"""
def run_scraper_task():
    '''
    Running scrapy in a Celery task
    '''
    
    p = Process(target=run_scrapy)
    p.start()
    p.join()
"""
