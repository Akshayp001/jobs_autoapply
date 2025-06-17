# JobSpy Scraper Module

This module (`scraper.py`) provides functionality to scrape job listings from various online job boards using the `jobspy` library. It is a separate component from the main LinkedIn scraping and email sending workflow, but can be used independently to gather additional job data.

## Usage

To use the `jobspy` scraper, you need to have the project dependencies installed (as described in the main `documentation.md`) and the `config.json` file properly configured.

You can run the `scraper.py` script directly from your terminal:

```bash
python3 jobspy/scraper.py
```

By default, this will scrape for "Flutter Developer" jobs in "india" with a limit of 100 results from the last 72 hours, based on the example usage in the script.

You can modify the `if __name__ == "__main__":` block in `jobspy/scraper.py` to change the default job position, results wanted, hours old, or location for standalone runs.

The `scrape_jobspy` function within `scraper.py` can also be imported and used in other Python scripts if you wish to integrate this functionality into a larger workflow.

The scraped job data will be saved to a CSV file named based on the job position (e.g., `jobspy_jobs_Flutter_Developer.csv`).

## Configuration

The `jobspy` scraper uses the `config.json` file from the project root directory. It specifically looks for the `keywords` associated with a job position under the `"job_positions"` key. If keywords are provided for the specified job position, they will be used as the search term for `jobspy`. Otherwise, the full job position name will be used.

Ensure your `config.json` is set up correctly with the job positions and optional keywords you want to use for scraping.

## Files

-   `jobspy/scraper.py`: The Python script containing the `scrape_jobspy` function and standalone execution logic.
-   `../config.json`: The configuration file used by the scraper.
