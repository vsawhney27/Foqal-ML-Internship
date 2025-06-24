from database import insert_jobs
from sources.wellfound import collect_jobs  # or whatever your function is called

# Scrape jobs
jobs = collect_jobs()

# Insert into database
insert_jobs(jobs)