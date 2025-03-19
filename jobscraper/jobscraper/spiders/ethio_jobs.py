import scrapy
import json
from jobscraper.items import JobscraperItem
from urllib.parse import urlparse, parse_qs

class EthioJobsSpider(scrapy.Spider):
    name = "ethio_jobs"
    allowed_domains = ["ethiojobs.net"]
    start_urls = ["https://ethiojobs.net/jobs"]

    def parse(self, response):
        item = JobscraperItem()
        script_tag = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()

        if script_tag:
            try:
                data = json.loads(script_tag)
                jobs = data.get('props', {}).get('pageProps', {}).get('jobs', {}).get('data', [])

                current_url = urlparse(response.url)
                query_params = parse_qs(current_url.query)
                current_page_number = query_params.get("page", [1])[0]

                for job in jobs:
                    item['source'] = 'ethio_jobs'
                    item['job_url'] = job.get('slug')
                    item['job_title'] = job.get('title') 
                    item['job_description'] = job.get('job_desription')
                    item['recruiter'] = job.get('company', {}).get('name')
                    item['location'] = job.get('state', 'N/A')
                    item['date_posted'] = job.get('date_published')
                    item['job_deadline'] = job.get('date_expiry')

                    item['category'] = []

                    catalogs = job.get('catalogs', [])
                    for cat in catalogs:
                        name = cat.get('name')
                        item['category'].append(name)
                    yield item

                queries = (
                    data.get('props', {})
                    .get('pageProps', {})
                    .get('initialState', {})
                    .get('api', {})
                    .get('queries', {})
                )

                query_key = f'getPaginatedJob({{"candidateId":"","isFeatured":false,"page":{current_page_number}}})'
                paginated_job_data = queries.get(query_key, {}).get('data', {})
                links = paginated_job_data.get('meta', {}).get('links', [{}])
                url = links[-1].get('url')

                if url:
                    parsed_url = urlparse(url)
                    query_params = parse_qs(parsed_url.query)
                    page_number = query_params.get("page", [None])[0]

                    if page_number and page_number.isdigit():
                        next_page_url = f"https://ethiojobs.net/jobs?page={page_number}"
                        yield scrapy.Request(
                            url=next_page_url,
                            callback=self.parse
                        )
                    else:
                        self.logger.info("No valid page number found in the URL.")
                else:
                    self.logger.info("No next page URL found.")

            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing JSON: {e}")
        else:
            self.logger.error("JSON data not found in the response.")