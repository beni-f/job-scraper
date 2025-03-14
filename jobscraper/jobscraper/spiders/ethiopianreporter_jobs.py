import scrapy
from jobscraper.items import JobscraperItem


class EthiopianreporterJobsSpider(scrapy.Spider):
    name = "ethiopianreporter_jobs"
    allowed_domains = ["www.ethiopianreporterjobs.com"]
    start_urls = ["https://www.ethiopianreporterjobs.com/jobs-in-ethiopia/"]

    def parse(self, response):
        jobs = response.css('div.-wrap > article')

        for job in jobs:
            item = JobscraperItem()
            item['source'] = 'ethiopianreporter_jobs'
            item['job_url'] = job.css('a::attr(href)').get()
            item['job_title'] = job.css('h3.loop-item-title > a::text').get()
            item['recruiter'] = job.css('span.job-company > a > span::text').get()
            item['location'] = job.css('span.job-location > a > em::text').get()

            yield scrapy.Request(
                url=item['job_url'],
                callback=self.parse_job_details,
                meta={'item': item}
            )
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield scrapy.Request(
                url=next_page,
                callback=self.parse
            )

    
    def parse_job_details(self, response):
        item = response.meta['item']

        item['category'] = response.css('span.job-category > a::text').getall()
        item['level_of_experience'] = response.css('span.value-_noo_job_field_year_experience::text').get()
        item['job_description'] = response.css('div[itemprop="description"] > ul > li::text').getall()
        item['date_posted'] = response.css('span.value-_noo_job_field_date_posted::text').get()
        item['job_deadline']= response.css('span.value-_noo_job_field_dead_line::text').get()

        yield item
