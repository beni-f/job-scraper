import scrapy
from scrapy_selenium import SeleniumRequest
import time
from jobscraper.items import JobscraperItem
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By



class HarmeeJobsSpider(scrapy.Spider):
    name = "harmee_jobs"
    allowed_domains = ["harmeejobs.com"]
    
    def start_requests(self):
        yield scrapy.Request(
            url="https://harmeejobs.com/jobs/",
            callback=self.parse,
        )

    def parse(self, response):
        item = JobscraperItem()

        jobs = response.css('ul.job-list > li')

        for job in jobs:
            item['source'] = 'harmee_jobs'
            item['job_url'] = job.css('a::attr(href)').get()
            item['job_title'] = job.attrib.get('data-title', None)
            item['recruiter'] = job.attrib.get('data-company', None)
            item['location'] = job.attrib.get('data-address', None)
            
            deadline = job.css('div.listing-date::text').getall()
            item['job_deadline'] = deadline[1] if len(deadline) > 1 else None

            yield scrapy.Request(
                url=item['job_url'],
                callback=self.parse_job_details,
                meta={'item': item},
            )

    def parse_job_details(self, response):
        item = response.meta['item']
        yield item
