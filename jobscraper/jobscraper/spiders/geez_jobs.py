import scrapy
from jobscraper.items import JobscraperItem

class GeezJobsSpider(scrapy.Spider):
    name = "geez_jobs"
    allowed_domains = ["geezjobs.com"]
    start_urls = ["https://geezjobs.com/search-jobs"]

    def parse(self, response):
        jobs = response.css('div.clients-page')

        for job in jobs:
            item = JobscraperItem()

            detail_list = job.css('ul > li::text').getall()
            date = job.css('ul.down-ul > li').getall()

            item['job_url'] = ''
            item['job_title'] = job.css('div.job-link > a > h4::text').get()
            item['recruiter'] = job.css('ul > li > a::text').get()
           
            item['job_description'] = job.css('p::text').get()
            item['location'] = detail_list[2]
            item['level_of_experience'] = detail_list[1]
            item['category'] = job.css('ul.tags-v1 > li > a::text').getall()
            item['date_posted'] = date[0]
            item['job_deadline'] = date[1]

            yield item

        total_pages = len(response.css('ul.pagination > li'))
        base_url = 'https://geezjobs.com/search-jobs?page={}'

        for page_number in range(2, total_pages + 1):
            url = base_url.format(page_number)
            yield scrapy.Request(url=url, callback=self.parse)