import scrapy
from jobscraper.items import JobscraperItem

class GeezJobsSpider(scrapy.Spider):
    name = "geez_jobs"
    allowed_domains = ["geezjobs.com", "www.geezjobs.com"]
    start_urls = ["https://geezjobs.com/search-jobs"]

    def parse(self, response):
        jobs = response.css('div.clients-page')

        for job in jobs:
            item = JobscraperItem()

            detail_list = job.css('ul > li::text').getall()

            item['source'] = 'geez_jobs'
            item['job_url'] = job.css('a::attr(href)').get()
            item['job_title'] = job.css('a > h4::text').get()
            item['recruiter'] = job.css('ul > li > a::text').get()
           
            item['job_description'] = job.css('p::text').get()
            item['location'] = detail_list[2]
            item['level_of_experience'] = detail_list[1]
            item['category'] = job.css('ul.tags-v1 > li > a::text').getall()
            item['date_posted'] = job.css('ul.down-ul > li::text').get()
            item['job_deadline'] = job.css('ul.down-ul > li > span::text').get()

            yield scrapy.Request(
                url=response.urljoin(item['job_url']),
                callback=self.parse_job_type,
                meta={'item': item},
                dont_filter=True
            )

        total_pages = len(response.css('ul.pagination > li'))
        base_url = 'https://geezjobs.com/search-jobs?page={}'

        for page_number in range(2, total_pages + 1):
            url = base_url.format(page_number)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse_job_type(self, response):
        item = response.meta['item']

        item['job_type'] = response.css('div.left-inner > div > h5::text').getall()[1]

        yield item