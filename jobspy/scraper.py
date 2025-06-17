import csv
from jobspy import scrape_jobs
import json
import os

# Define ANSI color codes
COLOR_GREEN = '\033[92m'
COLOR_RED = '\033[91m'
COLOR_BLUE = '\033[94m'
COLOR_END = '\033[0m' # Reset color

# Load configuration from config.json
def load_config(config_path="../config.json"):
    """Loads configuration from a JSON file."""
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{COLOR_RED}Error: Configuration file not found at {config_path}{COLOR_END}")
        exit()
    except json.JSONDecodeError:
        print(f"{COLOR_RED}Error: Could not decode JSON from {config_path}{COLOR_END}")
        exit()

config = load_config()

def scrape_jobspy(job_position, results_wanted=100, hours_old=72, location="india"):
    """
    Scrapes job listings from various sites using the jobspy library.

    Args:
        job_position (str): The target job position (used to get keywords from config).
        results_wanted (int): The maximum number of results to scrape.
        hours_old (int): The maximum age of job postings in hours.
        location (str): The location to search for jobs.

    Returns:
        pandas.DataFrame: A DataFrame containing the scraped job data.
    """
    print(f"{COLOR_BLUE}Starting job scraping using jobspy for: {job_position}{COLOR_END}")

    # Get job specific configuration to potentially use keywords
    job_config = config["job_positions"].get(job_position)
    search_term = job_position # Default search term

    if job_config and job_config.get("keywords"):
        # Use keywords from config if available for a more targeted search
        search_term = " ".join(job_config["keywords"])
        print(f"{COLOR_BLUE}Using keywords for jobspy search: {search_term}{COLOR_END}")
    else:
        print(f"{COLOR_BLUE}Using job position for jobspy search: {search_term}{COLOR_END}")


    try:
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google", "bayt", "naukri"],
            search_term=search_term,
            # google_search_term=f"{search_term} jobs in {location}", # Optional: more specific Google search
            location=location,
            results_wanted=results_wanted,
            hours_old=hours_old,
            country_indeed='india', # Assuming India based on previous code
            # linkedin_fetch_description=True # gets more info such as description, direct job url (slower)
            # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"], # Example proxies
        )
        print(f"{COLOR_GREEN}Found {len(jobs)} jobs.{COLOR_END}")
        # print(jobs.head()) # Optional: print head of dataframe

        # Define the filename based on the job position
        filename = f"jobspy_jobs_{job_position.replace(' ', '_')}.csv"

        # Save the results to a CSV file
        jobs.to_csv(filename, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
        print(f"{COLOR_GREEN}Job data saved to {filename}{COLOR_END}")

        return jobs

    except Exception as e:
        print(f"{COLOR_RED}An error occurred during jobspy scraping: {str(e)}{COLOR_END}")
        return None

# Example usage if the script is run directly
if __name__ == "__main__":
    # This block is for testing the jobspy scraper independently
    job_position_to_scrape = "Flutter Developer" # Default for testing
    print(f"{COLOR_BLUE}Running jobspy scraper in standalone mode for '{job_position_to_scrape}'...{COLOR_END}")
    scrape_jobspy(job_position_to_scrape)
