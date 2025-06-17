import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
from datetime import datetime, timedelta
import creds
import os

# Define ANSI color codes
COLOR_GREEN = '\033[92m'
COLOR_RED = '\033[91m'
COLOR_BLUE = '\033[94m'
COLOR_END = '\033[0m' # Reset color

# Load configuration from config.json
def load_config(config_path="config.json"):
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

def save_cookies(driver):
    """Saves browser cookies to a JSON file."""
    with open("linkedin_cookies.json", "w") as f:
        json.dump(driver.get_cookies(), f)

def load_cookies(driver):
    """Loads browser cookies from a JSON file and adds them to the driver."""
    try:
        with open("linkedin_cookies.json", "r") as f:
            cookies = json.load(f)
            for cookie in cookies:
                # Add domain to cookie if missing (sometimes required by Selenium)
                if 'domain' not in cookie:
                    cookie['domain'] = '.linkedin.com'
                driver.add_cookie(cookie)
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"{COLOR_RED}Error loading cookies: {str(e)}{COLOR_END}")
        return False


def perform_login(driver):
    """Performs login on LinkedIn."""
    driver.get("https://www.linkedin.com/login")
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys(creds.getEmail())
        driver.find_element(By.ID, "password").send_keys(creds.getPassword())
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        # Wait for login to complete by checking for a common element on the homepage
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.global-nav-typeahead__input"))
        )
        save_cookies(driver)
        print(f"{COLOR_GREEN}Login successful. Cookies saved.{COLOR_END}")
    except TimeoutException:
        print(f"{COLOR_RED}Login timeout. Check credentials or 2FA.{COLOR_END}")
    except Exception as e:
        print(f"{COLOR_RED}An error occurred during login: {str(e)}{COLOR_END}")


def scrape_linkedin(job_position):
    """Scrapes LinkedIn posts for a given job position."""
    # Configure browser
    driver = webdriver.Chrome()
    driver.maximize_window()

    # Attempt to reuse existing session using cookies
    driver.get("https://www.linkedin.com")
    if os.path.exists("linkedin_cookies.json") and load_cookies(driver):
        driver.refresh()  # Refresh to apply cookies
        try:
            # Check if session is still valid
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.global-nav-typeahead__input"))
            )
            print(f"{COLOR_GREEN}Session reused successfully.{COLOR_END}")
        except TimeoutException:
            print(f"{COLOR_BLUE}Session expired. Performing fresh login.{COLOR_END}")
            perform_login(driver)
    else:
        print(f"{COLOR_BLUE}No existing session found or cookies invalid. Performing fresh login.{COLOR_END}")
        perform_login(driver)

    # Determine search term based on keywords in config
    job_config = config["job_positions"].get(job_position)
    if job_config and job_config.get("keywords"):
        # Use keywords from config if available
        search_keywords = " AND ".join([f'"{keyword}"' for keyword in job_config["keywords"]])
        search_term = f'{search_keywords} AND "hiring"'
        print(f"{COLOR_BLUE}Using keywords for search: {search_term}{COLOR_END}")
    else:
        # Fallback to using the full job position name
        search_term = f'"{job_position}" AND "hiring"'
        print(f"{COLOR_BLUE}Using job position for search: {search_term}{COLOR_END}")


    # Navigate to target search results page
    search_url = f"https://www.linkedin.com/search/results/content/?keywords={search_term.replace(' ', '%20')}&origin=FACETED_SEARCH&sid=k79&sortBy=%22date_posted%22"
    driver.get(search_url)

    posts_data = []
    processed_posts = set()
    allemails = []
    start_time = datetime.now()
    # Scrape for a fixed duration (e.g., 2 minutes) to avoid infinite loops
    end_time = start_time + timedelta(minutes=2)

    print(f"{COLOR_BLUE}Starting to scrape LinkedIn posts...{COLOR_END}")
    try:
        while datetime.now() < end_time:
            # Scroll down to load more posts
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) # Give time for new content to load

            try:
                # Wait for new posts to appear
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.feed-shared-update-v2"))
                )
            except TimeoutException:
                print(f"{COLOR_BLUE}No new posts loaded after scrolling or end of feed reached.{COLOR_END}")
                break # Exit loop if no new posts load

            # Find all post elements
            posts = driver.find_elements(By.CSS_SELECTOR, "div.feed-shared-update-v2")

            # Process each post
            for post in posts:
                try:
                    post_id = post.get_attribute("data-urn")
                    if post_id in processed_posts:
                        continue # Skip already processed posts
                    processed_posts.add(post_id)

                    # Extract post details
                    name = post.find_element(By.CSS_SELECTOR, "span.update-components-actor__title").text
                    date = post.find_element(By.CSS_SELECTOR, "span.update-components-actor__sub-description").text
                    content = post.find_element(By.CSS_SELECTOR, "div.update-components-text").text

                    # Extract emails from mailto links
                    email_links = post.find_elements(By.CSS_SELECTOR, "a[href^='mailto:']")
                    emails = [link.get_attribute("href").split(":")[1] for link in email_links]
                    allemails.extend(emails) # Add to the overall email list

                    # Extract emails from text content using regex
                    text_emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
                    combined_emails = list(set(emails + text_emails)) # Combine and deduplicate emails for this post

                    # Extract all links from the post
                    all_links = [link.get_attribute("href") for link in post.find_elements(By.CSS_SELECTOR, "a[href]")]

                    # Append extracted data to the list
                    posts_data.append({
                        "name": name,
                        "date": date,
                        "post_text": content,
                        "emails": combined_emails,
                        "links": list(set(all_links)), # Deduplicate links
                        "post_id": post_id
                    })

                except NoSuchElementException:
                    # Skip posts that don't have the expected elements
                    continue
                except Exception as e:
                    print(f"{COLOR_RED}Error processing post {post_id}: {str(e)}{COLOR_END}")


    finally:
        # Close the browser
        driver.quit()
        print(f"{COLOR_BLUE}Browser closed.{COLOR_END}")


    # Save all collected data to a JSON file
    data = {
        'allemails': list(set(allemails)), # Deduplicate final list of all emails
        'posts_data': posts_data
    }

    # Define the filename based on the job position
    filename = f"linkedin_posts_{job_position.replace(' ', '_')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"{COLOR_GREEN}Scraped {len(posts_data)} posts and found {len(data['allemails'])} unique emails in 2 minutes. Data saved to {filename}{COLOR_END}")
    return data

# Example usage if the script is run directly
if __name__ == "__main__":
    # This block is for testing the scraper independently
    # In the main application, scrape_linkedin is called from main.py
    job_position_to_scrape = config["job_positions"].get("Flutter Developer") # Default for testing
    if job_position_to_scrape:
        print(f"{COLOR_BLUE}Running scraper in standalone mode for 'Flutter Developer'...{COLOR_END}")
        scrape_linkedin("Flutter Developer")
    else:
        print(f"{COLOR_RED}Job position 'Flutter Developer' not found in config.json. Cannot run scraper in standalone mode.{COLOR_END}")
