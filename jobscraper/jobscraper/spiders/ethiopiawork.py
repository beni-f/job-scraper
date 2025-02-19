import scrapy
from jobscraper.items import JobscraperItem

class EthiopiaworkSpider(scrapy.Spider):
    name = "ethiopiawork"
    allowed_domains = ["www.ethiopiawork.com"]
    start_urls = ["https://www.ethiopiawork.com/job-vacancies-search-ethiopia"]

    def parse(self, response):
        jobs = response.css('div.card-job')
        for job in jobs:
            item = JobscraperItem()
            item['job_url'] = job.css('div > h3 > a::attr(href)').get()
            item['job_title'] = job.css('div > h3 > a::text').get()
            item['recruiter'] = job.css('div > a.company-name::text').get()
            item['job_description'] = job.css('div > div > p::text').get()
            requirement_details = job.css('div > div > ul > li')
            print(requirement_details)
            item['date_posted'] = job.css('div > div > time::text').get()
            yield item

        next_page = response.css('li.pager-next > a::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(
                url= next_page_url,
                callback=self.parse,
            )
