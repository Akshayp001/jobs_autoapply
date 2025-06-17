import json
import argparse
from scrap import scrape_linkedin
from send_emails import send_emails

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

# Main execution block
import json
import argparse
from scrap import scrape_linkedin
from send_emails import send_emails, load_sent_emails, save_sent_emails

# Define ANSI color codes
COLOR_GREEN = '\033[92m'
COLOR_RED = '\033[91m'
COLOR_BLUE = '\033[94m'
COLOR_YELLOW = '\033[93m' # Added yellow for warnings/skips
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

# Main execution block
if __name__ == "__main__":
    # Set up argument parser for command-line arguments
    parser = argparse.ArgumentParser(description="Automated job search and email campaign tool.")
    parser.add_argument("--position", required=True, help="The target job position (must match a key in config.json).")
    parser.add_argument("--apply", action="store_true", help="Set this flag to send emails after scraping.")
    parser.add_argument("--apply-only", action="store_true", help="Set this flag to skip scraping and only send emails to available addresses.")

    args = parser.parse_args()

    target_job_position = args.position
    send_emails_flag = args.apply
    apply_only_flag = args.apply_only

    # Load configuration
    config = load_config()

    # Validate if the specified job position exists in the configuration
    if target_job_position not in config.get("job_positions", {}):
        print(f"{COLOR_RED}Error: Job position '{target_job_position}' not found in config.json.{COLOR_END}")
        print(f"{COLOR_BLUE}Available job positions:{COLOR_END}")
        for pos in config.get("job_positions", {}).keys():
            print(f"{COLOR_BLUE}- {pos}{COLOR_END}")
        exit()

    print(f"{COLOR_BLUE}Starting job search for: {target_job_position}{COLOR_END}")

    scraped_data = None
    # Step 1: Scrape LinkedIn for emails unless --apply-only flag is set
    if not apply_only_flag:
        print(f"\n{COLOR_BLUE}Running LinkedIn scraper...{COLOR_END}")
        scraped_data = scrape_linkedin(target_job_position)
        print(f"{COLOR_GREEN}LinkedIn scraping complete.{COLOR_END}")
    else:
        print(f"\n{COLOR_YELLOW}Scraping skipped (--apply-only flag is set).{COLOR_END}")

    # Step 2: Send emails to collected addresses if --apply flag is set
    if send_emails_flag or apply_only_flag: # Send emails if either --apply or --apply-only is set
        # If apply_only, load emails from the existing file
        if apply_only_flag and not scraped_data:
             # Need to load emails if scraping was skipped
             # The send_emails function already loads from linkedin_posts.json, so no need to load here
             pass # send_emails will handle loading

        print(f"\n{COLOR_BLUE}Running email sender...{COLOR_END}")
        # The send_emails function will load emails from linkedin_posts.json
        send_emails(target_job_position)
        print(f"{COLOR_GREEN}Email sending complete.{COLOR_END}")

    else:
        print(f"\n{COLOR_BLUE}Email sending skipped (--apply flag not set and --apply-only flag not set).{COLOR_END}")


    print(f"\n{COLOR_BLUE}Job search and email campaign finished.{COLOR_END}")
