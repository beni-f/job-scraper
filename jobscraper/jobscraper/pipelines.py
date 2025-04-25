from itemadapter import ItemAdapter
from datetime import datetime
import re

MASTER_CATEGORY_MAP = {
    # hahu.jobs
    "Business": "Business & Management",
    "Creative Arts": "Creative & Media",
    "Engineering": "Engineering & Manufacturing",
    "Education": "Education & Training",
    "Finance": "Accounting & Finance",
    "Health Care": "Healthcare & Pharmaceutical",
    "Hospitality": "Hospitality & Tourism",
    "ICT": "IT & Technology",
    
    # ethiopiawork.com
    "Accounting, controlling, finance": "Accounting & Finance",
    "Health and social professions": "Healthcare & Pharmaceutical",
    "HR, training": "Human Resources",
    "IT, new technologies": "IT & Technology",
    "Management": "Business & Management",
    "Marketing, communication": "Marketing & Sales",
    "Production, maintenance, quality": "Engineering & Manufacturing",
    "Public buildings and works professions": "Architecture & Construction",
    "Purchases": "Logistics & Supply Chain",
    "R&D, project management": "Research & Development",
    "Sales": "Marketing & Sales",
    "Secretarial work, assistantship": "Administration & Secretarial",
    "Services": "Customer Service",
    "Telemarketing, teleassistance": "Customer Service",
    "Tourism, hotel business and catering": "Hospitality & Tourism",
    "Transport, logistics": "Logistics & Supply Chain",
    
    # ethiojobs.net & geezjobs.com (same categories)
    "Accounting and Finance": "Accounting & Finance",
    "Admin, Secretarial, and Clerical": "Administration & Secretarial",
    "Agriculture": "Agriculture & Environment",
    "Architecture and Construction": "Architecture & Construction",
    "Automotive": "Engineering & Manufacturing",
    "Banking and Insurance": "Banking & Insurance",
    "Business and Administration": "Business & Management",
    "Business Development": "Business & Management",
    "Consultancy and Training": "Project Management & Consulting",
    "Creative Arts": "Creative & Media",
    "Customer Service": "Customer Service",
    "Development and Project Management": "Project Management & Consulting",
    "Economics": "Business & Management",
    "Education": "Education & Training",
    "Engineering": "Engineering & Manufacturing",
    "Environment and Natural Resource": "Agriculture & Environment",
    "Event Management": "Creative & Media",
    "Health Care": "Healthcare & Pharmaceutical",
    "Hotel and Hospitality": "Hospitality & Tourism",
    "Human Resource and Recruitment": "Human Resources",
    "IT, Computer Science and Software Engineering": "IT & Technology",
    "Legal": "Legal Services",
    "Logistics, Transport and Supply Chain": "Logistics & Supply Chain",
    "Management": "Business & Management",
    "FMCG and Manufacturing": "Engineering & Manufacturing",
    "Communications, Media and Journalism": "Creative & Media",
    "Pharmaceutical": "Healthcare & Pharmaceutical",
    "Purchasing and Procurement": "Logistics & Supply Chain",
    "Quality Assurance": "Engineering & Manufacturing",
    "Research and Development": "Research & Development",
    "Retail, Wholesale and Distribution": "Logistics & Supply Chain",
    "Sales and Marketing": "Marketing & Sales",
    "Security": "Social Sciences & Community Services",
    "Technology": "IT & Technology",
    "Social Sciences and Community Service": "Social Sciences & Community Services",
    "Telecommunications": "IT & Technology",
    "Travel and Tourism": "Hospitality & Tourism",
    "Veterinary Services": "Healthcare & Pharmaceutical",
    "Warehouse, Supply Chain and Distribution": "Logistics & Supply Chain",
    "Water and Sanitation": "Social Sciences & Community Services"
}


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
        elif source == 'ethiopiawork':
            self.clean_ethiopia_work(adapter)

        return item
    
    def clean_ethio_jobs_item(self, adapter):
        adapter['date_posted'] = datetime.strptime(adapter['date_posted'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
        adapter['job_deadline'] = datetime.strptime(adapter['job_deadline'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
        adapter['category'] = self.normalize_category(adapter['category'])




    def clean_hahu_jobs_item(self, adapter):
        adapter['job_url'] = 'http://hahu.jobs/jobs' + adapter['job_url']
        adapter['date_posted'] = datetime.fromisoformat(adapter['date_posted'].rstrip('Z'))
        adapter['job_deadline'] = datetime.strptime(adapter['job_deadline'], '%Y-%m-%d').date()
        adapter['category'] = self.normalize_category(adapter['category'])


    def clean_geez_jobs_item(self, adapter):
        adapter['job_url'] = 'https://geezjobs.com' + adapter['job_url']

        if adapter['level_of_experience'].strip().replace('*', '') == '':
            adapter['level_of_experience'] = "N/A"
        else:
            adapter['level_of_experience'] = adapter['level_of_experience'].strip()

        adapter['category'] = self.normalize_category(adapter['category'])
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
        
    def clean_ethiopia_work(self, adapter):
        adapter['job_url'] = 'https://www.ethiopiawork{}'.format(adapter['job_url'])
        adapter['category'] = self.normalize_category(adapter['category'])

    def normalize_category(categories):
        if isinstance(categories, str):
            categories = [categories]
        
        normalized_categories = []
        
        for category in categories:
            if category in MASTER_CATEGORY_MAP:
                normalized_categories.append(MASTER_CATEGORY_MAP[category])
                continue
        
            for pattern, normalized in MASTER_CATEGORY_MAP.items():
                if ':' not in pattern:
                    if pattern.lower() in category.lower():
                        normalized_categories.append(normalized)
                        break
            else:
                normalized_categories.append(category)
        
        return normalized_categories[0] if len(normalized_categories) == 1 else normalized_categories