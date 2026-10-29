# Azure Waste Cleaner & FinOps Optimizer

A lightweight, read-only FinOps CLI scanner written in Python that audits Microsoft Azure subscriptions for unattached Managed Disks, orphaned Public IP addresses, and empty App Service Plans, reporting idle cloud assets in the terminal to reduce unnecessary operational spend.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Azure SDK](https://img.shields.io/badge/azure--sdk-python-0078D4.svg)
![Security](https://img.shields.io/badge/auth-DefaultAzureCredential-green.svg)
![RBAC Scope](https://img.shields.io/badge/rbac-Reader-success.svg)
![Mode](https://img.shields.io/badge/mode-read--only-informational.svg)

---

## Overview

Infrastructure provisioning lifecycles frequently result in orphaned cloud assets that remain unmonitored. Common waste drivers include unattached Managed Disks remaining after virtual machine teardowns, idle Public IP addresses incurring hourly reservation fees, and empty App Service Plans generating ongoing compute capacity charges despite running zero hosted applications.

This utility automates multi-resource auditing using the official Azure SDK for Python. It inspects compute, networking, and application hosting layers across all resource groups, delivering a clear operational status report without executing destructive actions or state mutations.

---

## Key Features

- **Unattached Disk Detection:** Queries Azure Compute APIs to discover managed disks where `managed_by` evaluates to null across the subscription scope.
- **Orphaned Public IP Auditing:** Evaluates Azure Network APIs to detect allocated Public IP addresses where `ip_configuration` is unassigned.
- **Empty App Service Plan Discovery:** Identifies hosting plans where `number_of_sites` equals zero, highlighting idle provisioned compute capacity.
- **Passwordless Identity Integration:** Authenticates dynamically through `DefaultAzureCredential` using an active Azure CLI session or Managed Identities.
- **Zero Embedded Credentials:** Consumes the target subscription ID strictly from runtime environment variables (`AZURE_SUBSCRIPTION_ID`).
- **Read-Only Posture:** Restricts operations to telemetry gathering and reporting, mitigating any risk of production downtime or accidental data loss.
- **Clean CLI Reporting:** Outputs structured, aligned terminal summaries categorizing detected assets, tiers, resource groups, and geographical regions.

---

## Quick Start

### Prerequisites
- Python 3.10 or higher.
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed and authenticated.
- Azure built-in **Reader** role on the target subscription scope.

### Clone and Setup

```bash
git clone [https://github.com/Abdulsattar-Homsi/azure-waste-cleaner.git](https://github.com/Abdulsattar-Homsi/azure-waste-cleaner.git)
cd azure-waste-cleaner
```

#### On Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### On Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Authentication & Execution

Authenticate via Azure CLI:
```bash
az login
```

Set your target subscription ID and execute:

#### On Linux / macOS
```bash
export AZURE_SUBSCRIPTION_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
python main.py
```

#### On Windows (PowerShell)
```powershell
$env:AZURE_SUBSCRIPTION_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
python main.py
```

---

## Verification & Ephemeral Lab Testing

The scanner's detection logic across compute, network, and hosting tiers was verified against staged ephemeral resources in an isolated subscription:

### 1. Storage Detection Validation
```bash
# Provision test managed disk
az disk create \
  --name "temp-unattached-disk-test" \
  --resource-group "NetworkWatcherRG" \
  --size-gb 4 \
  --sku "Standard_LRS"

# Run scanner to verify detection
python main.py

# Clean up immediately
az disk delete \
  --name "temp-unattached-disk-test" \
  --resource-group "NetworkWatcherRG" \
  --yes
```

### 2. Network Detection Validation
```bash
# Provision test public IP
az network public-ip create \
  --name "temp-unassociated-pip-test" \
  --resource-group "NetworkWatcherRG" \
  --sku "Standard" \
  --allocation-method "Static"

# Run scanner to verify detection
python main.py

# Clean up immediately
az network public-ip delete \
  --name "temp-unassociated-pip-test" \
  --resource-group "NetworkWatcherRG"
```

### 3. App Service Plan Validation
```bash
# Provision test empty App Service Plan
az appservice plan create \
  --name "temp-empty-asp-test" \
  --resource-group "NetworkWatcherRG" \
  --sku "F1"

# Run scanner to verify detection
python main.py

# Clean up immediately
az appservice plan delete \
  --name "temp-empty-asp-test" \
  --resource-group "NetworkWatcherRG" \
  --yes
```

### Observed Terminal Output (Sanitized)

```text
[*] Scanning subscription: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx ...

===============================================================================================
                      AZURE FINOPS & COST OPTIMIZATION REPORT                      
===============================================================================================

[✓] Disks: No unattached disks found. Storage is clean.

-----------------------------------------------------------------------------------------------

[✓] Public IPs: No orphaned public IP addresses found. Network is clean.

-----------------------------------------------------------------------------------------------

[!] App Service Plans: Found (1) empty hosting plan(s):

Plan Name                      | Resource Group       | Tier            | SKU        | Location
-----------------------------------------------------------------------------------------------
temp-empty-asp-test            | NetworkWatcherRG     | Free            | F1         | Germany West Central
-----------------------------------------------------------------------------------------------

===============================================================================================
```

---

## Security & Permissions

- **Identity Flow:** Built on `DefaultAzureCredential`, chaining authentication seamlessly from local developer tools to Managed Identities without hardcoding secrets.
- **Least Privilege Access:** Operates strictly under the built-in Azure RBAC `Reader` role (`Microsoft.Compute/disks/read`, `Microsoft.Network/publicIPAddresses/read`, `Microsoft.Web/serverfarms/read`).
- **Zero Secrets at Rest:** The tool stores no API keys, client secrets, or persistent connection tokens.

---

## Limitations

- **Read-Only Scope:** The utility functions strictly as an auditing scanner. Identified resources are not modified or deleted automatically. Empty plans or detached disks may be intentionally reserved for DR failover, testing, or planned maintenance.
- **Pricing Model Variations:** The tool surfaces resource allocations and SKUs; it does not compute dynamic currency billing totals. Financial impacts vary based on tier agreements, reserved instances, or free-tier quotas.
- **Coverage Scope:** Scans managed disks, public IPs, and app service hosting plans. Does not currently inspect orphaned NICs, NSGs, or SQL databases.

---

## Technical Decisions

| Decision | Implementation | Rationale |
| :--- | :--- | :--- |
| **Authentication** | `DefaultAzureCredential` | Native Microsoft identity standard; avoids embedding long-lived service principal secrets. |
| **SDK Interfaces** | Official Azure SDK for Python | Provides strong typing, automatic pagination, and reliable ARM API compatibility over raw REST calls. |
| **Safety Posture** | Audit and Report Only | Preserves infrastructure stability and prevents catastrophic accidental data deletion. |

---

## Repository Structure

```text
azure-waste-cleaner/
├── .gitignore               # Excludes virtual environments, cache files, and local settings
├── main.py                  # Core auditing logic and CLI reporting engine
├── requirements.txt         # Pinned Python dependencies (compute, network, web, identity)
└── README.md                # Standardized technical documentation
```

---

## Roadmap

- [x] **Unattached Managed Disks:** Query and report idle persistent disks.
- [x] **Unassociated Public IPs:** Audit detached public IP addresses incurring reservation fees.
- [x] **Empty App Service Plans:** Audit App Service Plans hosting zero active web applications.
- [ ] **Automated Alerts:** Deliver scheduled summaries via Webhook to Microsoft Teams or Slack.
- [ ] **Serverless Execution:** Containerize scanner execution via Azure Functions timer triggers.