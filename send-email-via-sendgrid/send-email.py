#!/usr/bin/env python3

import requests
import json
import automationassets
from automationassets import AutomationAssetNotFound
import sys

sender_email = automationassets.get_automation_variable("sender_email")

# Retrieve SendGrid API key from Azure Automation Credential
try:
    creds = automationassets.get_automation_credential("sendgrid_key")
    SENDGRID_API_KEY = creds["password"]  # the API key secret
except AutomationAssetNotFound:
    print("Credential not found")
    sys.exit(1)

def send_email_via_api():
    recipient_emails = automationassets.get_automation_variable("recipient_emails")
    # Split the string by semicolon and remove any extra spaces
    to_emails = [{"email": email.strip()} for email in recipient_emails.split(";")]
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "personalizations": [
            {
                "to": to_emails,
                "subject": "Test Email from Azure Automation Account"
            }
        ],
        "from": {"email": sender_email},
        "content": [{"type": "text/plain", "value": "This is a test email from SendGrid."}]
    }

    # Send the POST request to SendGrid API
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check if the email was sent successfully
    if response.status_code == 202:
        print("Email sent successfully!")
    else:
        print(f"Failed to send email: {response.status_code}, {response.text}")

# Call the function to send the email
send_email_via_api()
