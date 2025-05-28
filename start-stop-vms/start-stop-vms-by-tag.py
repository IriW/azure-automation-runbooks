#!/usr/bin/env python3
# === Static metadata ===
owner_name = automationassets.get_automation_variable("runbook_owner_name")
owner_email = automationassets.get_automation_variable("runbook_owner_email")
runbook_name = automationassets.get_automation_variable("runbook_display_name")
subscription_name = automationassets.get_automation_variable("runbook_subscription_name")
environment = automationassets.get_automation_variable("environment")

# REMEMBER to define parameters in schedule LIKE 
# --tag_name=availability
# --tag_value=bizhours
# --shutdown=False
# --email_list=emai2@addres.com;email1@addres.com

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
import sys
import requests
import json
import argparse
# import smtplib, ssl
import automationassets
from automationassets import AutomationAssetNotFound
from datetime import datetime
import pytz

cet = pytz.timezone("Europe/Warsaw")
timestamp = datetime.now(cet).strftime("%Y-%m-%d %H:%M:%S %Z") # Switches to summertime automatically (cet to cest), no need to manual adjustment.

sender_email = automationassets.get_automation_variable("sender_email")

# Retrieve SendGrid API key from Azure Automation Credential
try:
    creds = automationassets.get_automation_credential("sendgrid_key")
    SENDGRID_API_KEY = creds["password"]  # the API key secret
except AutomationAssetNotFound:
    print("Credential not found")
    sys.exit(1)

# Function wor wrapping the message into html format report
def generate_html_report(entries, action, owner_name, owner_email, runbook_name, subscription_name, timestamp):
    timestamp = datetime.now(cet).strftime("%Y-%m-%d %H:%M:%S %Z") # Switches to summertime automatically (cet to cest), no need to manual adjustment.
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h2>Automation Report: {automationassets.get_automation_variable("environment")} VMs {action}</h2>
        <p><strong>Timestamp:</strong> {timestamp}</p>
        <table>
            <tr>
                <th>#</th>
                <th>Resource Group</th>
                <th>VM Name</th>
                <th>Action</th>
                <th>Public IP</th>
            </tr>
    """
    
    for idx, entry in enumerate(entries, start=1):
        rg = entry.get("resource_group", "N/A")
        vm = entry.get("vm_name", "N/A")
        act = entry.get("action", "N/A")
        ip = entry.get("public_ip", "N/A")
        html += f"""
            <tr>
                <td>{idx}</td>
                <td>{rg}</td>
                <td>{vm}</td>
                <td>{act}</td>
                <td>{ip}</td>
            </tr>
        """
    html += f"""
        </table>
        <br/>
        <hr/>
    </body>
    <footer>
        <p>
            <strong>Runbook:</strong> {runbook_name}<br/>
            <strong>Subscription:</strong> {subscription_name}
        </p>
        <br/>
        <p style="font-size: 11px;">
            If you have any questions regarding this automation,<br/>
            please contact {owner_name} at <a href="mailto:{owner_email}">{owner_email}</a>.
        </p>
    </footer>
    </html>
    """
    return html

# Function to send email using SendGrid API
def send_email_via_api(recipient_emails, subject, plain_body, html_body):
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
        "content": [
            {"type": "text/plain", "value": plain_body},
            {"type": "text/html", "value": html_body}
        ]
    }

    # Send the POST request to SendGrid API
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check if the email was sent successfully
    if response.status_code == 202:
        print("Email sent successfully!")
    else:
        print(f"Failed to send email: {response.status_code}, {response.text}")

def str2bool(value):
    return value.lower() in ("true", "1", "yes")

def createParser():
    parser = argparse.ArgumentParser(description='Azure VM start/stop actions')
    parser.add_argument('--tag_name', type=str, help='Tag name', required=True)
    parser.add_argument('--tag_value', type=str, help='Tag value', required=True)
    parser.add_argument('--shutdown', type=str2bool, help='Shutdown: True or False', required=True)
    parser.add_argument('--email_list', type=str, help='Recipient mailboxes separated by semicolons', required=False)
    return parser

def get_vm_public_ip(resource_group, vm_name):
    try:
        nic_list = compute_client.virtual_machines.get(resource_group, vm_name).network_profile.network_interfaces
        for nic_ref in nic_list:
            nic_name = nic_ref.id.split('/')[-1]
            nic_rg = nic_ref.id.split('/')[4]
            nic = network_client.network_interfaces.get(nic_rg, nic_name)
            for ip_config in nic.ip_configurations:
                if ip_config.public_ip_address:
                    public_ip_id = ip_config.public_ip_address.id
                    ip_rg = public_ip_id.split('/')[4]
                    public_ip_name = public_ip_id.split('/')[-1]
                    print(f"Looking for public IP: {public_ip_name} in RG: {ip_rg}")
                    public_ip = network_client.public_ip_addresses.get(ip_rg, public_ip_name)
                    return public_ip.ip_address
        return "No Public IP"
    except Exception as e:
        return f"Error: {str(e)}"

# Parse input parameters
parser = createParser()
args = parser.parse_args(sys.argv[1:])

# Azure credentials and VM client
credentials = DefaultAzureCredential()
subscription_id = automationassets.get_automation_variable("subscription_id")
compute_client = ComputeManagementClient(credentials, subscription_id)
vm_list = compute_client.virtual_machines.list_all()
network_client = NetworkManagementClient(credentials, subscription_id)

# Bulk messages (VMs as strings list)
summary_messages = []
subject_action = "Stopped" if args.shutdown else "Started"

for vm in vm_list:
    resource_group = vm.id.split("/")[4]
    vm_name = vm.id.split("/")[-1]

    try:
        if vm.tags:
            tags = vm.tags
            for (tag, value) in tags.items():
                if tag == args.tag_name and value == args.tag_value:
                    if args.shutdown:
                        vm_stop = compute_client.virtual_machines.begin_deallocate(resource_group, vm_name)
                        vm_stop.wait()
                        message = f"VM {resource_group.lower()}/{vm_name} has been stopped"
                        print(message)
                        summary_messages.append({
                            "resource_group": resource_group,
                            "vm_name": vm_name,
                            "action": subject_action,
                            "public_ip": get_vm_public_ip(resource_group, vm_name)
                        })

                    elif not args.shutdown:
                        vm_start = compute_client.virtual_machines.begin_start(resource_group, vm_name)
                        vm_start.wait()
                        message = f"VM {resource_group.lower()}/{vm_name} has been started"
                        print(message)
                        summary_messages.append({
                            "resource_group": resource_group,
                            "vm_name": vm_name,
                            "action": subject_action,
                            "public_ip": get_vm_public_ip(resource_group, vm_name)
                        })
                    else:
                        print('Incorrect value for shutdown flag')
    except Exception as e:
        print(f"Failed to process VM {vm_name} in RG {resource_group}: {e}")
        summary_messages.append({
            "resource_group": resource_group,
            "vm_name": vm_name,
            "action": "Error",
            "public_ip": f"Error: {e}"
        })

# Send email with summary (if there are any messages)
if args.email_list and summary_messages:
    email_subject = f"Automation Account job completed: VMs {subject_action} - ({timestamp})"
    plain_body = "\n".join(
        f"{entry.get('resource_group', 'N/A')}/{entry.get('vm_name', 'N/A')} - {entry.get('action', 'N/A')} - {entry.get('public_ip', 'N/A')}"
        for entry in summary_messages
    )

    html_body = generate_html_report(
        summary_messages,
        subject_action,
        owner_name,
        owner_email,
        runbook_name,
        subscription_name,
        timestamp
    )

    send_email_via_api(args.email_list, email_subject, plain_body, html_body)
