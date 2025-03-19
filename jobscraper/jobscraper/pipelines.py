# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime
import re


class JobscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        source = adapter.get('source')

        if source == 'ethio_jobs':
            self.clean_ethio_jobs_item(adapter)
        elif source == 'hahu_jobs':
            self.clean_hahu_jobs_item(adapter)
        elif source == 'geez_jobs':
            self.clean_geez_jobs_item(adapter)

        return item
    
    def clean_ethio_jobs_item(self, adapter):
        adapter['date_posted'] = datetime.strptime(adapter['date_posted'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
        adapter['job_deadline'] = datetime.strptime(adapter['job_deadline'], "%Y-%m-%dT%H:%M:%S.%fZ").date()



    def clean_hahu_jobs_item(self, adapter):
        adapter['job_url'] = 'http://hahu.jobs/jobs' + adapter['job_url']
        adapter['date_posted'] = datetime.fromisoformat(adapter['date_posted'].rstrip('Z'))
        adapter['job_deadline'] = datetime.strptime(adapter['job_deadline'], '%Y-%m-%d').date()

    def clean_geez_jobs_item(self, adapter):
        adapter['job_url'] = 'https://geezjobs.com' + adapter['job_url']

        if adapter['level_of_experience'].strip().replace('*', '') == '':
            adapter['level_of_experience'] = "N/A"
        else:
            adapter['level_of_experience'] = adapter['level_of_experience'].strip()

        adapter['job_deadline'] = self.clean_job_deadline_for_geez_jobs(adapter['job_deadline'])
        adapter['date_posted'] = self.clean_date_posted_for_geez_jobs(adapter['date_posted'])

    def clean_job_deadline_for_geez_jobs(self, job_deadline_str):
        match = re.search(r"(\w+), (\d+)/(\d+)", job_deadline_str)
        if match:
            month, day, year = match.groups()
            deadline_date = datetime.strptime(f"{month} {day}, {year}", "%B %d, %Y")
            return deadline_date.strftime("%Y-%m-%d")
        return None
        
    def clean_date_posted_for_geez_jobs(self, date_posted_str):
        match = re.search(r"(Today|Yesterday|\d+ (weeks?|days?) ago)", date_posted_str)
        if match:
            return match.group(1).strip()