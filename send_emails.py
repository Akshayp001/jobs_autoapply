import mimetypes
import smtplib
import ssl
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import creds

# Define ANSI color codes
COLOR_GREEN = '\033[92m'
COLOR_RED = '\033[91m'
COLOR_BLUE = '\033[94m'
COLOR_YELLOW = '\033[93m' # Added yellow for warnings/skips
COLOR_END = '\033[0m' # Reset color

# Define the path for the sent emails storage file
SENT_EMAILS_FILE = "sent_emails.json"

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

# Get SMTP server details from config
SMTP_SERVER = config.get("smtp_server")
SMTP_PORT = config.get("smtp_port")
# Get email credentials from creds.py (assuming it exists and has these functions)
SMTP_USERNAME = creds.getSMTPUsername()
SMTP_PASSWORD = creds.getSMTPPassword()
# Get default resume path from config
DEFAULT_RESUME_PATH = config.get("default_resume_path")

def load_emails(job_position):
    """Loads email addresses from the job position-specific JSON file."""
    filename = f"linkedin_posts_{job_position.replace(' ', '_')}.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Return a list of unique emails, handling cases where 'allemails' key might be missing
            return list(set(data.get('allemails', [])))
    except FileNotFoundError:
        print(f"{COLOR_RED}Error: {filename} not found. Please run the scraper for '{job_position}' first or use --apply-only with an existing file.{COLOR_END}")
        return []
    except json.JSONDecodeError:
        print(f"{COLOR_RED}Error: Could not decode JSON from {filename}. File might be corrupted.{COLOR_END}")
        return []
    except Exception as e:
        print(f"{COLOR_RED}Error loading emails from {filename}: {str(e)}{COLOR_END}")
        return []

def load_sent_emails():
    """Loads the list of already sent emails from a JSON file."""
    if not os.path.exists(SENT_EMAILS_FILE):
        return []
    try:
        with open(SENT_EMAILS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"{COLOR_RED}Error: Could not decode JSON from {SENT_EMAILS_FILE}. File might be corrupted. Starting with an empty list.{COLOR_END}")
        return []
    except Exception as e:
        print(f"{COLOR_RED}Error loading sent emails from {SENT_EMAILS_FILE}: {str(e)}{COLOR_END}")
        return []

def save_sent_emails(sent_emails_list):
    """Saves the list of sent emails to a JSON file."""
    try:
        with open(SENT_EMAILS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(set(sent_emails_list)), f, ensure_ascii=False, indent=2) # Save unique emails
    except Exception as e:
        print(f"{COLOR_RED}Error saving sent emails to {SENT_EMAILS_FILE}: {str(e)}{COLOR_END}")


def add_attachment(msg, filepath):
    """Adds an attachment to the email message."""
    if not filepath or not os.path.isfile(filepath):
        print(f"{COLOR_RED}Attachment file not found or path not specified: {filepath}{COLOR_END}")
        return

    # Guess the MIME type of the file
    mime_type, _ = mimetypes.guess_type(filepath)
    if mime_type is None:
        mime_type = 'application/octet-stream' # Default to binary if type cannot be guessed

    main_type, sub_type = mime_type.split('/', 1)

    try:
        # Open the file in binary mode and create a MIMEBase part
        with open(filepath, "rb") as attachment:
            part = MIMEBase(main_type, sub_type)
            part.set_payload(attachment.read())

        # Encode the attachment in base64
        encoders.encode_base64(part)
        # Add header to specify the filename
        filename = os.path.basename(filepath)
        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
        # Attach the part to the message
        msg.attach(part)
        print(f"{COLOR_BLUE}Attached: {filename}{COLOR_END}")
    except Exception as e:
        print(f"{COLOR_RED}Error adding attachment {filepath}: {str(e)}{COLOR_END}")


def send_emails(job_position):
    """Sends emails to scraped addresses for a specific job position, avoiding duplicates."""
    recipients = load_emails(job_position) # Pass job_position to load_emails
    sent_emails_list = load_sent_emails()
    initial_sent_count = len(sent_emails_list)

    # Filter out emails that have already been sent
    recipients_to_send = [email for email in recipients if email not in sent_emails_list]
    total_to_send = len(recipients_to_send)
    skipped_count = len(recipients) - total_to_send

    if total_to_send == 0:
        print(f"{COLOR_BLUE}No new email addresses found to send to for '{job_position}' position.{COLOR_END}")
        if skipped_count > 0:
             print(f"{COLOR_BLUE}{skipped_count} emails skipped as they were already sent.{COLOR_END}")
        return

    print(f"{COLOR_BLUE}Found {len(recipients)} total unique email addresses.{COLOR_END}")
    print(f"{COLOR_BLUE}Skipping {skipped_count} emails that were already sent.{COLOR_END}")
    print(f"{COLOR_BLUE}Attempting to send to {total_to_send} new unique email addresses for '{job_position}' position.{COLOR_END}")


    # Get job specific configuration
    job_config = config["job_positions"].get(job_position)
    if not job_config:
        print(f"{COLOR_RED}Error: Configuration for job position '{job_position}' not found in config.json. Cannot send emails.{COLOR_END}")
        return

    # Get email details from job specific configuration, with fallbacks
    email_subject = job_config.get("email_subject", "Application for Position")
    email_body = job_config.get("email_body", "Dear Hiring Manager,\n\nPlease find my resume attached.\n\nSincerely,\nApplicant")
    attachment_path = job_config.get("resume_path", DEFAULT_RESUME_PATH)

    # Create a default SSL context
    context = ssl._create_unverified_context() # Note: _create_unverified_context is used here for simplicity, but for production, a verified context is recommended.

    sent_count = 0
    failed_count = 0
    failed_emails = []

    try:
        # Connect to the SMTP server and login
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            print(f"\n{COLOR_BLUE}Connecting to SMTP server...{COLOR_END}")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            print(f"{COLOR_GREEN}Successfully authenticated with SMTP server.{COLOR_END}\n")

            # Send email to each recipient
            for idx, receiver in enumerate(recipients_to_send, 1):
                try:
                    # Create the email message
                    msg = MIMEMultipart()
                    msg['From'] = SMTP_USERNAME
                    msg['To'] = receiver
                    msg['Subject'] = email_subject
                    msg.attach(MIMEText(email_body, 'plain'))

                    # Add attachment if specified
                    if attachment_path:
                        add_attachment(msg, attachment_path)

                    # Send the email
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ({idx}/{total_to_send}) Sending to {receiver}...", end=" ")
                    server.sendmail(SMTP_USERNAME, receiver, msg.as_string())
                    sent_count += 1
                    sent_emails_list.append(receiver) # Add to the list of sent emails
                    print(f"{COLOR_GREEN}SUCCESS{COLOR_END}")

                except Exception as e:
                    # Handle errors for individual emails
                    failed_count += 1
                    failed_emails.append(receiver)
                    print(f"{COLOR_RED}FAILED - {str(e)}{COLOR_END}")

    except Exception as e:
        # Handle fatal SMTP connection or login errors
        print(f"\n{COLOR_RED}Fatal SMTP error: {str(e)}{COLOR_END}")
        # Save the list of sent emails even if a fatal error occurs
        save_sent_emails(sent_emails_list)
        return

    # Save the updated list of sent emails
    save_sent_emails(sent_emails_list)

    # Generate and print the email campaign report
    print(f"\n\n{COLOR_BLUE}=== Email Campaign Report ==={COLOR_END}")
    print(f"{COLOR_BLUE}Job Position: {job_position}{COLOR_END}")
    print(f"{COLOR_BLUE}Total unique emails found: {len(recipients)}{COLOR_END}")
    print(f"{COLOR_BLUE}Emails skipped (already sent): {skipped_count}{COLOR_END}")
    print(f"{COLOR_BLUE}Attempted to send to: {total_to_send}{COLOR_END}")
    print(f"{COLOR_GREEN}Successfully sent in this run: {sent_count}{COLOR_END}")
    print(f"{COLOR_RED}Failed attempts in this run: {failed_count}{COLOR_END}")
    print(f"{COLOR_BLUE}Total emails sent historically: {len(sent_emails_list)}{COLOR_END}")


    if failed_emails:
        print(f"\n{COLOR_RED}Failed addresses in this run:{COLOR_END}")
        for email in failed_emails:
            print(f"{COLOR_RED} - {email}{COLOR_END}")

    print(f"\n{COLOR_BLUE}=== Campaign completed ==={COLOR_END}")

# Example usage if the script is run directly
if __name__ == "__main__":
    # This block is for testing the email sender independently
    # In the main application, send_emails is called from main.py
    # You would need to ensure linkedin_posts.json exists with emails for this to work
    print(f"{COLOR_BLUE}Running email sender in standalone mode for 'Flutter Developer'...{COLOR_END}")
    send_emails("Flutter Developer")
