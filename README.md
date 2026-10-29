# Azure Waste Cleaner & FinOps Optimizer

A lightweight, automated FinOps CLI utility written in Python to detect orphaned and idle Azure resources, reducing cloud waste and enforcing cost governance.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Azure SDK](https://img.shields.io/badge/azure--sdk-python-0078D4.svg)
![Security](https://img.shields.io/badge/auth-DefaultAzureCredential-green.svg)
![RBAC Scope](https://img.shields.io/badge/rbac-Reader-success.svg)
![License](https://img.shields.io/badge/license-MIT-informational.svg)

---

## Overview

Infrastructure churn often leaves orphaned resources—such as unattached Managed Disks after VM deletion—that continue to accrue storage costs. 

This project provides an automated Python scanner that inspects an Azure subscription, identifies unattached disks (`managed_by is null`), and generates a clear CLI cost-audit report without embedding credentials.

---

## Key Features

- **Automated Detection:** Scans Azure subscriptions via `azure-mgmt-compute` to locate unattached managed disks.
- **Passwordless Security:** Leverages `DefaultAzureCredential` to authenticate dynamically via an active Azure CLI session.
- **Zero Hardcoded Secrets:** Subscription ID is consumed strictly via runtime environment variables (`AZURE_SUBSCRIPTION_ID`).
- **Clean CLI Reporting:** Generates an aligned terminal summary detailing resource name, group, SKU, location, and provisioned size.

---

## Quick Start

### 1. Prerequisites
- Python 3.10+
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) authenticated (`az login`)
- Azure **Reader** role on the target subscription

### 2. Setup
```bash
# Clone repository
git clone [https://github.com/Abdulsattar-Homsi/azure-waste-cleaner.git](https://github.com/Abdulsattar-Homsi/azure-waste-cleaner.git)
cd azure-waste-cleaner

# Create and activate virtual environment
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Execution
```bash
# Set subscription ID
# Linux/macOS:
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
# Windows PowerShell:
$env:AZURE_SUBSCRIPTION_ID="your-subscription-id"

# Run scanner
python main.py
```

---

## Verification & Lab Testing

The detection logic was verified against an ephemeral test disk staged via Azure CLI:

```bash
# 1. Create a 4GB test disk
az disk create --name "temp-unattached-disk-test" --resource-group "NetworkWatcherRG" --size-gb 4 --sku "Standard_LRS"

# 2. Run scanner to confirm detection
python main.py

# 3. Clean up immediately (Zero lingering cost)
az disk delete --name "temp-unattached-disk-test" --resource-group "NetworkWatcherRG" --yes
```

**Observed Output:**
```text
[*] Scanning subscription: c71e597a-7158-4f70-b8ad-3cd2b1f68bf1 ...

[!] Found (1) unattached disk(s):

Disk Name                      | Resource Group       | Size (GB)  | SKU                                  | Location
-----------------------------------------------------------------------------------------------
temp-unattached-disk-test      | NETWORKWATCHERRG     | 4          | DiskStorageAccountTypes.STANDARD_LRS | germanywestcentral
-----------------------------------------------------------------------------------------------
Total unattached storage capacity: 4 GB
```

---

## Technical Decisions

| Decision | Implementation | Rationale |
| :--- | :--- | :--- |
| **Authentication** | `DefaultAzureCredential` | Eliminates hardcoded secrets; seamlessly transitions from local CLI to Managed Identity. |
| **Interface** | Azure Python SDK | Provides strict typing, built-in retry logic, and native pagination. |
| **Remediation** | Report-Only | Follows safe FinOps practices; prevents accidental deletion of maintenance disks. |

---

## Repository Structure

```text
azure-waste-cleaner/
├── .gitignore               # Excludes venv, environment files, and pycache
├── main.py                  # Core scanner logic and reporting engine
├── requirements.txt         # Pinned project dependencies
└── README.md                # Project documentation
```

---

## Roadmap

- [ ] **Unassociated Public IPs:** Identify idle reserved Public IPs generating billing waste.
- [ ] **Empty App Service Plans:** Audit App Service Plans running zero web applications.
- [ ] **ChatOps Integration:** Automated scheduled summaries sent via Webhook to Microsoft Teams / Slack.
- [ ] **Serverless Execution:** Containerize as a periodic Azure Timer-Triggered Function.