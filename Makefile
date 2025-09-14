# Foqal Internship ML Project Makefile

.PHONY: help install run-dashboard export-us-mid-market test clean

help:
	@echo "Available targets:"
	@echo "  install              Install Python dependencies"
	@echo "  run-dashboard        Start the Streamlit dashboard"
	@echo "  export-us-mid-market Export filtered US mid-market jobs to parquet"
	@echo "  test                 Run the test suite"
	@echo "  clean                Clean temporary files"

install:
	pip install -r requirements.txt

run-dashboard:
	streamlit run dashboard.py

export-us-mid-market:
	python cli.py export --input scraped_jobs.json --out data/exports/us_mid_market_postings.parquet --only-us-mid-market

test:
	python -m pytest tests/ -v

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/