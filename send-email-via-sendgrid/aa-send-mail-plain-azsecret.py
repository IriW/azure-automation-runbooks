#!/usr/bin/env python3

import requests
import json
import automationassets
from automationassets import AutomationAssetNotFound
import sys

sender_email = "sender@address.com" # Replace with sender email
recipient_email = "recipient@address.com" # Replace with recipient email

# Retrieve SendGrid API key from Azure Automation Credential
try:
    creds = automationassets.get_automation_credential("sendgrid_key")
    SENDGRID_API_KEY = creds["password"]  # the API key secret
except AutomationAssetNotFound:
    print("Credential not found")
    sys.exit(1)

def send_email_via_api():
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "personalizations": [
            {
                "to": [{"email": recipient_email}],
                "subject": "Test Email from Azure Automation Account (DEV)"
            }
        ],
        "from": {"email": sender_email},
        "content": [{"type": "text/plain", "value": "This is a test email from SendGrid."}]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 202:
        print("Email sent successfully!")
    else:
        print(f"Failed to send email: {response.status_code}, {response.text}")

send_email_via_api()
