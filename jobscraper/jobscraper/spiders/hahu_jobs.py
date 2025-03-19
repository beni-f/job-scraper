import scrapy
from jobscraper.items import JobscraperItem

class HahuJobsSpider(scrapy.Spider):
    name = "hahu_jobs"
    allowed_domains = ["hahu.jobs"]
    start_urls = ["http://hahu.jobs/jobs"]

    def parse(self, response):
        jobs = response.css('div[itemtype="https://schema.org/JobPosting"]')
        for job in jobs:
            item = JobscraperItem()
            item['source'] = 'hahu_jobs'
            item['job_url'] = job.css('div > a[itemprop="url"]::attr(href)').get()
            item['job_title'] = job.css('div > h3[itemprop="title"]::text').get()
            item['recruiter'] = job.css('div > p.line-clamp-2::text').get()
            item['job_description'] = job.css('div > p[itemprop="description"]::text').get()
            item['category'] = job.css('div > p[itemprop="occupationalCategory"]::text').get()
            item['location'] = job.css('div > p > span[itemprop="addressRegion"]::text').get()
            item['level_of_experience'] = job.css('div > p[itemprop="experienceRequirements"]::text').get()
            item['date_posted'] = job.css('div > span > span[itemprop="datePosted"]::text').get()
            item['job_deadline'] = job.css('div > span > span[itemprop="validThrough"]::text').get()
            yield item

        next_page = response.xpath('//div/div[2]/div[2]/div[1]/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div[3]/a/@href').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(
                url= next_page_url,
                callback=self.parse,
            )
