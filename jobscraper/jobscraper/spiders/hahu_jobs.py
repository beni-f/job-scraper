import scrapy
from jobscraper.items import JobscraperItem

class HahuJobsSpider(scrapy.Spider):
    name = "hahu_jobs"
    allowed_domains = ["hahu.jobs"]
    start_urls = ["http://hahu.jobs/jobs"]

    def parse(self, response):
        jobs = response.xpath('//div')
        for job in jobs:
            item = JobscraperItem()
            item['job_url'] = jobs.css('div > a[itemprop="url"]::attr(href)').get()
            item['job_title'] = jobs.css('div > h3[itemprop="title"]::text').get()
            item['recruiter'] = jobs.css('div > p.line-clamp-2::tex').get()
            item['job_description'] = jobs.css('div > p[itemprop="description"]::text').get()
            item['category'] = jobs.css('div > p[itemprop="occupationalCategory"]::text')
            item['location'] = jobs.css('div > span[itemprop="addressRegion"]::text')
            item['level_of_experience'] = jobs.css('div > span[itemprop="addressRegion"]::text')
            item['open_positions'] =  jobs.css('div > p[itemprop="totalJobOpenings"]::text')
            item['date_posted'] = jobs.css('div > span > span[itemprop="datePosted"]::text').get()
            item['job_deadline'] = jobs.css('div > span > span[itemprop="validThrough"]::text').get()

