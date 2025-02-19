# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobscraperItem(scrapy.Item):
    job_url = scrapy.Field()
    recruiter = scrapy.Field()
    job_title = scrapy.Field()
    job_description = scrapy.Field()
    date_posted = scrapy.Field()
