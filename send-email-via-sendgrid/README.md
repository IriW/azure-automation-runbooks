# Send Email via SendGrid

This repository contains Python scripts to send emails using the SendGrid API from an Azure Automation environment.
To make any of those production-ready, make sure to replace hardcoded values such as Subscription ID, key etc. by variables.

## Files

- `aa-send-mail-multiplerecepients.py`: Script to send an email to multiple recipients using SendGrid.
- `aa-send-mail-plain-azsecret.py`: Script to send an email to a single recipient using SendGrid.
- `aa-send-mail-plain.py`: Script to send an email to a single recipient using SendGrid with Sendgrid Key as plain text in runbook.

## Prerequisites

1. **Azure Automation Account**: You need an Azure Automation account to run the script.
2. **SendGrid Account**: Create a SendGrid account and generate an API key.
3. **Azure Automation Credential**: Store your **SendGrid API key** securely in Azure Automation as a credential named `sendgrid_key`.
4. **Recipient Email(s)**: The email addresses of the recipients must be set in the `recipient_emails` variable in the runbooks.
5. **Sender Email**: The email addresses of the sender must be set in the `sender_email` variable in the runbooks.

## Usage
## Setup Instructions

1. **Create Azure Automation Credential** (if not yet done):
    - Go to your **Azure Automation Account** in the Azure portal.
    - Navigate to **Shared Resources** > **Credentials**.
    - Click **+ Add a credential** and add your SendGrid API key with the following:
        - **Name**: `sendgrid_key`
        - **Username**: `api` (placeholder value)
        - **Password**: Your **SendGrid API Key**
    - Click **Create** to save the credential.

2. **Edit Runbook(s)**:
    - Replace `sender_email` with your verified sender email in SendGrid.
    - Replace `recipient_emails` with the email addresses of the recipients (separate them with semicolons if sending to multiple recipients).

3. **Run the Script**:
    - This script will retrieve the SendGrid API key from Azure Automation's credential store and send a test email.
    - If the email is sent successfully, you'll see a success message in the logs.

