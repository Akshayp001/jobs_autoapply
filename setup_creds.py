import os

# Define ANSI color codes
COLOR_GREEN = '\033[92m'
COLOR_RED = '\033[91m'
COLOR_BLUE = '\033[94m'
COLOR_END = '\033[0m' # Reset color

def setup_credentials():
    """Guides the user through setting up the creds.py file."""
    print(f"{COLOR_BLUE}--- Credential Setup ---{COLOR_END}")
    print("This script will help you create the creds.py file to store your login details.")
    print(f"Please provide the following information. This information will be saved locally in {COLOR_BLUE}creds.py{COLOR_END}.")

    linkedin_email = input(f"{COLOR_BLUE}Enter your LinkedIn email: {COLOR_END}")
    linkedin_password = input(f"{COLOR_BLUE}Enter your LinkedIn password: {COLOR_END}")
    smtp_username = input(f"{COLOR_BLUE}Enter your SMTP email address (sending email): {COLOR_END}")
    smtp_password = input(f"{COLOR_BLUE}Enter your SMTP password (app password recommended): {COLOR_END}")

    creds_content = f"""# This file contains your sensitive credentials.
# Keep this file secure and do not share it.

def getEmail():
    return "{linkedin_email}"

def getPassword():
    return "{linkedin_password}"

def getSMTPUsername():
    return '{smtp_username}'

def getSMTPPassword():
    return '{smtp_password}'
"""

    try:
        with open("creds.py", "w") as f:
            f.write(creds_content)
        print(f"{COLOR_GREEN}creds.py created successfully!{COLOR_END}")
        print(f"{COLOR_BLUE}Remember to keep this file secure.{COLOR_END}")
    except IOError as e:
        print(f"{COLOR_RED}Error writing to creds.py: {str(e)}{COLOR_END}")

if __name__ == "__main__":
    setup_credentials()
