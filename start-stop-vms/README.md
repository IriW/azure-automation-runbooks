# Azure VM Start/Stop Automation with Email Notification

This Azure Automation Runbook automates the **start and stop actions** of Azure Virtual Machines (VMs) based on tags.  
It integrates with the **SendGrid API** to send consolidated email notifications to specified recipients after all applicable actions (start/stop) are completed.

The **SendGrid API key** is securely retrieved from Azure Automation's **Credential Store**, and configuration values like runbook owner or sender email are fetched from **Automation Variables**.

---

## Features

- Start or stop Azure VMs by **tag name/value**
- Automatically send a **formatted HTML report** (plus plain text) via SendGrid
- Pull metadata like **public IP, resource group, action**
- Use variables defined in **Azure Automation Account → Variables**
- Optional fallback to hardcoded parameters (for testing/local use)

---

## Prerequisites

Before running this automation, ensure:

1. **Azure Automation Account** exists.
2. **SendGrid Account** is set up and verified.
3. **SendGrid API key** is stored as an Automation **Credential** named `sendgrid_key`.
4. **VMs use consistent tags**, such as `availability = devops-auto`.
5. The following variables are declared in **Azure Automation → Variables**, or overridden in the script for local testing:

| Variable Name             | Purpose                                 |
|--------------------------|------------------------------------------|
| `runbook_owner_name`     | Display name of the automation owner     |
| `runbook_owner_email`    | Contact email shown in footer of report  |
| `runbook_display_name`   | Name of this runbook                     |
| `runbook_subscription_name` | Logical name of the subscription      |
| `subscription_id`        | Azure Subscription ID (used in SDK auth) |
| `sender_email`           | Verified sender in SendGrid              |
| `default_tag_name`       | Tag key to filter VMs                    |
| `default_tag_value`      | Tag value to filter VMs                  |
| `default_shutdown`       | `True` or `False` (start/stop flag)      |
| `default_email_list`     | Recipients (semicolon-separated)         |

You can define these manually in the portal or import them using CLI with `runbook_variables.json`.

---

## How to Import Variables from JSON

Use the provided `runbook_variables.json` template with PowerShell:

```powershell
Connect-AzAccount

$automationAccountName = "<your-automation-account>"
$resourceGroup = "<your-resource-group>"
$variables = Get-Content "./runbook_variables.json" | ConvertFrom-Json

foreach ($var in $variables) {
    $existing = Get-AzAutomationVariable -AutomationAccountName $automationAccountName -ResourceGroupName $resourceGroup -Name $var.name -ErrorAction SilentlyContinue
    if ($existing) {
        Set-AzAutomationVariable -AutomationAccountName $automationAccountName -ResourceGroupName $resourceGroup -Name $var.name -Value $var.value -Encrypted $var.isEncrypted
    } else {
        New-AzAutomationVariable -AutomationAccountName $automationAccountName -ResourceGroupName $resourceGroup -Name $var.name -Value $var.value -Encrypted $var.isEncrypted
    }
}
```

---

## Scheduling & Parameters

The runbook supports parameters:

- `--tag_name`
- `--tag_value`
- `--shutdown` (`True` or `False`)
- `--email_list` (semicolon-separated list)

If these are omitted during scheduling, the script will fall back to values from Automation Variables (if coded accordingly).

---

## Setup Summary

### 1. **Store SendGrid Credential**

- Go to: `Shared Resources` → `Credentials`
- Add credential:
  - **Name**: `sendgrid_key`
  - **Username**: `api`
  - **Password**: *your SendGrid API key*

### 2. **Configure Variables (optional)**

Use the `runbook_variables.json` to populate commonly reused values such as contact info, tag filters, etc.

### 3. **Deploy and Test the Runbook**

- Paste the Python script into the Runbook
- Test manually with parameters or use the default variable fallback
- Add a Schedule and link parameters if needed

---

## Email Output

The runbook generates:
- A plain-text email body
- A well-formatted HTML table including:
  - Timestamp (Europe/Warsaw timezone)
  - VM name, resource group, action taken, public IP
- Footer with contact info and runbook metadata

---

## Optional Improvements

- Add region/location/VM size to the report
- Push logs to Log Analytics or storage account
- Visualize metrics in Workbook
- Add error highlighting in the HTML table

---

Made with ☕ by Platform & DevOps Mermaid  
