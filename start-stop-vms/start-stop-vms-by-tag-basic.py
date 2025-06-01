#!/usr/bin/env python3

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
import sys
import requests
import json
import argparse
import automationassets
from automationassets import AutomationAssetNotFound

# Sender email, which should be a verified sender in SendGrid
sender_email = "sender@address.com"  # Replace with your sender email

# Retrieve SendGrid API key from Azure Automation Credential
try:
    creds = automationassets.get_automation_credential("sendgrid_key")
    SENDGRID_API_KEY = creds["password"]  # the API key secret
except AutomationAssetNotFound:
    print("Credential not found")
    sys.exit(1)

# Function to send email using SendGrid API
def send_email_via_api(recipient_emails, subject, body):
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
                "subject": subject
            }
        ],
        "from": {"email": sender_email},
        "content": [{"type": "text/plain", "value": body}]
    }

    # Send the POST request to SendGrid API
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check if the email was sent successfully
    if response.status_code == 202:
        print("Email sent successfully!")
    else:
        print(f"Failed to send email: {response.status_code}, {response.text}")

# Function to create argument parser. REMEMBER to define parameters in schedule LIKE 
# --tag_name=availability
# --tag_value=mytesttag
# --shutdown=False
# --email_list=emai2@addres.com; email1@addres.com

def createParser():
    parser = argparse.ArgumentParser(description='Azure VM start/stop actions')
    parser.add_argument('--tag_name', type=str, help='Tag name', required=True)
    parser.add_argument('--tag_value', type=str, help='Tag value', required=True)
    parser.add_argument('--shutdown', type=str, help='Shutdown: True or False', required=True)
    parser.add_argument('--email_list', type=str, help='Recipient mailboxes separated by semicolons', required=False)
    return parser

# Parse input parameters
parser = createParser()
args = parser.parse_args(sys.argv[1:])

# Azure credentials and VM client
credentials = DefaultAzureCredential()
subscription_id = ""  # Provide your subscription ID
compute_client = ComputeManagementClient(credentials, subscription_id)
vm_list = compute_client.virtual_machines.list_all()

for vm in vm_list:
    resource_group = vm.id.split("/")[4]
    vm_name = vm.id.split("/")[-1]

    try:
        if vm.tags:
            tags = vm.tags
            for (tag, value) in tags.items():
                if tag == args.tag_name and value == args.tag_value:
                    if args.shutdown == 'True':
                        vm_stop = compute_client.virtual_machines.begin_deallocate(resource_group, vm_name)
                        vm_stop.wait()
                        message = f"VM {resource_group.lower()}/{vm_name} has been stopped"
                        print(message)
                        # Send email notification after VM stop action
                        if args.email_list:
                            send_email_via_api(args.email_list, "Automation Account job completed: VM Stopped", message)
                    elif args.shutdown == 'False':
                        vm_start = compute_client.virtual_machines.begin_start(resource_group, vm_name)
                        vm_start.wait()
                        message = f"VM {resource_group.lower()}/{vm_name} has been started"
                        print(message)
                        # Send email notification after VM start action
                        if args.email_list:
                            send_email_via_api(args.email_list, "Automation Account job completed: VM Started", message)
                    else:
                        print('Incorrect value for shutdown flag')
    except Exception as e:
        message = f"Script failed with error:\n{e}"
        print(message)
        # Send failure email notification
        if args.email_list:
            send_email_via_api(args.email_list, "VM Script Failure", message)
        sys.exit(1)
