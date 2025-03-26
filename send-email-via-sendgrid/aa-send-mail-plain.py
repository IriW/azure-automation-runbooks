#!/usr/bin/env python3

import requests
import json

sender_email = "sender@address.com" # Replace with sender email
recipient_email = "recipient@address.com" # Replace with recipient email

def send_email_via_api():
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": "Bearer SG.12345678901234567890]",  # Your API key
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
