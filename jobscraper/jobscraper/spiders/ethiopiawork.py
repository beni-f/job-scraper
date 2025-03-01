import scrapy
from jobscraper.items import JobscraperItem

class EthiopiaworkSpider(scrapy.Spider):
    name = "ethiopiawork"
    allowed_domains = ["www.ethiopiawork.com"]
    start_urls = ["https://www.ethiopiawork.com/job-vacancies-search-ethiopia"]

    def parse(self, response):
        jobs = response.css('div.card-job')
        for job in jobs:
            details = job.css('div.card-job-detail > ul > li > strong::text').getall()

            item = JobscraperItem()
            item['source'] = 'ethiopiawork'
            item['job_url'] = job.css('div > h3 > a::attr(href)').get()
            item['job_title'] = job.css('div > h3 > a::text').get()
            item['recruiter'] = job.css('div > a.company-name::text').get()
            item['job_description'] = job.css('div > div > p::text').get()
            item['location'] = details[3]
            item['level_of_experience'] = details[1]
            item['date_posted'] = job.css('div > div > time::text').get()
            
            yield scrapy.Request(
                url=f"https://www.ethiopiawork.com{item['job_url']}",
                callback=self.parse_skills,
                meta={'item': item}
            )

        next_page = response.css('li.pager-next > a::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(
                url= next_page_url,
                callback=self.parse,
            )

    def parse_skills(self, response):
        item = response.meta['item']

        item['category'] = response.css('li.suitcase > span::text').get()
        item['job_deadline'] = ''

        yield item