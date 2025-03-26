# Azure VM Start/Stop Automation with Email Notification

This Azure Automation Runbook automates the start and stop actions of Azure Virtual Machines (VMs) based on tags. It integrates with the **SendGrid API** to send email notifications to specified recipients after each action (VM start/stop) is performed.

The runbook retrieves the **SendGrid API key** from Azure Automation's **Credential store** to send email notifications about VM actions.

## Prerequisites

Before using this runbook, ensure the following:

1. **Azure Automation Account**: You need an **Azure Automation Account** to run the script.
2. **SendGrid Account**: Create a **SendGrid** account, and generate an **API key**.
3. **Azure Automation Credential**: Store your **SendGrid API key** in Azure Automation as a credential named `sendgrid_key`.
4. **VMs with Tags**: Your VMs should have tags that include a `tag_name` and `tag_value` for identification.

## Setup Instructions

### Step 1: Create the SendGrid API Credential in Azure Automation

1. Go to your **Azure Automation Account** in the Azure portal.
2. Navigate to **Shared Resources** > **Credentials**.
3. Click **+ Add a credential** and enter the following:
   - **Name**: `sendgrid_key`
   - **Username**: `api` (this is a placeholder for the SendGrid API key)
   - **Password**: Your **SendGrid API Key**
4. Click **Create** to save the credential.

### Step 2: Edit the Runbook Script

In the runbook, modify the following variables:
- `sender_email`: Replace with your verified sender email address in SendGrid.
- `subscription_id`: Replace with your Azure subscription ID.

```python
sender_email = "sender@address.com"  # Replace with your sender email
subscription_id = ""  # Provide your subscription ID
