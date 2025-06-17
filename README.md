# Automated Job Search and Email Campaign Tool

This project is an automated tool designed to scrape job-related information from LinkedIn and send personalized application or outreach emails.

## Features

- Scrapes LinkedIn posts based on a specified job position and keywords.
- Extracts email addresses from scraped LinkedIn posts.
- Supports sending emails with customizable subjects, bodies, and attachments based on the job position.
- Avoids sending duplicate emails using a local storage file.
- Allows running only the scraping or only the email sending process via command-line arguments.
- Configuration is managed in a central JSON file.


## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
    (Note: Replace `<repository_url>` and `<repository_directory>` with the actual repository details if applicable, otherwise the user already has the files.)

2.  **Set up a Python virtual environment (recommended):**
    ```bash
    python3 -m venv myenv
    source myenv/bin/activate
    ```
    This creates a virtual environment named `myenv` and activates it. You should see `(myenv)` at the beginning of your terminal prompt when the environment is active.

3.  **Install dependencies:**
    Install the required Python packages using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```
    You will also need a compatible WebDriver for Selenium (e.g., ChromeDriver). Download the appropriate version for your Chrome browser and make sure it's in your system's PATH or specify its location.

4.  **Set up credentials (`creds.py`):**
    Run the `setup_creds.py` script to interactively create the `creds.py` file. This file will store your sensitive login details for LinkedIn and your email account.

    ```bash
    python3 setup_creds.py
    ```
    The script will prompt you for your LinkedIn email and password, and your SMTP email address and password. **Keep the generated `creds.py` file secure and do not share it.** (Note: Using an app password for your email provider, like Gmail, is generally more secure than using your main password. Refer to your email provider's documentation for creating app passwords.)

5.  **Configure `config.json`:**
    Update the `config.json` file to define your SMTP server details, default resume path, and configurations for different job positions you want to target. Each job position can have a specific email subject, body, resume path, and a list of keywords for LinkedIn scraping.

    ```json
    {
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 465,
      "default_resume_path": "attachments/resume.pdf",
      "job_positions": {
        "Flutter Developer": {
          "email_subject": "Application for Flutter Developer Position",
          "email_body": "Dear Hiring Manager,\n...\nSincerely,\nYour Name",
          "resume_path": "attachments/flutter_resume.pdf",
          "keywords": ["Flutter", "Dart", "Mobile Developer"]
        },
        "Python Developer": {
          "email_subject": "Application for Python Developer Position",
          "email_body": "Dear Hiring Manager,\n...\nSincerely,\nYour Name",
          "resume_path": "attachments/python_resume.pdf",
          "keywords": ["Python", "Django", "Flask", "Backend Developer"]
        }
        // Add more job positions as needed
      }
    }
    ```

6.  **Place your resume(s):**
    Place your resume PDF file(s) in the `attachments` directory as specified in `config.json`.

## Usage

Run the `main.py` script from your terminal with the following command-line arguments:

```bash
python main.py --position "Your Job Position" [--apply] [--apply-only]
```

-   `--position "Your Job Position"`: **Required**. Specifies the target job position. This must exactly match a key under `"job_positions"` in `config.json`.
-   `--apply`: **Optional**. If included, the script will first scrape LinkedIn for the specified position and then send emails to the collected addresses (excluding those already sent to, as recorded in `sent_emails.json`).
-   `--apply-only`: **Optional**. If included, the script will skip the scraping step and only send emails to the addresses found in the existing position-specific JSON file (e.g., `linkedin_posts_Your_Job_Position.json`) that haven't been sent to before.

**You must include either `--apply` or `--apply-only` to trigger the email sending process.** If neither is included, the script will only perform the scraping (if `--apply-only` is not present).

**Examples:**

-   Scrape for "Flutter Developer" positions and then send emails:
    ```bash
    python main.py --position "Flutter Developer" --apply
    ```

-   Only send emails to already scraped addresses for "Python Developer" (skipping scraping):
    ```bash
    python main.py --position "Python Developer" --apply-only
    ```

-   Only scrape for "React Developer" positions (without sending emails):
    ```bash
    python main.py --position "React Developer"
    ```

## Output

The script will print progress and status messages to the console with color coding for better readability:
- Blue: Informational messages
- Green: Success messages
- Red: Error messages
- Yellow: Warning or skipped actions

## Files

-   `main.py`: The main script to run the application.
-   `scrap.py`: Contains the LinkedIn scraping logic.
-   `send_emails.py`: Contains the email sending logic.
-   `config.json`: Configuration file for the application.
-   `creds.py`: (User-created) Contains sensitive credentials.
-   `creds.py.example`: Example file for `creds.py`.
-   `attachments/`: Directory to store resume files.
-   `attachments/resume.pdf`: Example resume file.
-   `linkedin_posts_[Job Position].json`: (Generated) Stores scraped LinkedIn data for each position.
-   `sent_emails.json`: (Generated) Stores a list of email addresses that have been sent emails.
-   `jobspy/`: Directory containing the `jobspy` scraper module. See `jobspy/README.md` for details on using this module independently.
    -   `jobspy/scraper.py`: The script for scraping job boards using `jobspy`.
    -   `jobspy/README.md`: Documentation for the `jobspy` scraper module.
-   `documentation.md`: This documentation file.
