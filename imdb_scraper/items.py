# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# Create scrapy Item instances for each movie variable we want to scrape from IMDb
class IMDbItem(scrapy.Item):
    title = scrapy.Field()
    global_rating = scrapy.Field()
    num_of_voters = scrapy.Field()
    release_date = scrapy.Field()
    country = scrapy.Field()
    award_wins_nominations = scrapy.Field()
    creators = scrapy.Field()
