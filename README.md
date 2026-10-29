# Azure Waste Cleaner & FinOps Optimizer

A lightweight, read-only FinOps CLI scanner written in Python that inspects Microsoft Azure subscriptions for unattached Managed Disks, reporting unused storage capacity directly in the terminal to reduce cloud waste.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Azure SDK](https://img.shields.io/badge/azure--sdk-python-0078D4.svg)
![Security](https://img.shields.io/badge/auth-DefaultAzureCredential-green.svg)
![RBAC Scope](https://img.shields.io/badge/rbac-Reader-success.svg)
![Mode](https://img.shields.io/badge/mode-read--only-informational.svg)

---

## Overview

When Virtual Machines are deleted or deprovisioned in Microsoft Azure, associated Managed Disks frequently remain behind in an unattached state. Because Azure bills for provisioned disk capacity regardless of VM association, these orphaned disks generate continuous passive costs.

This utility automates the discovery of unattached managed disks using the official Azure SDK for Python. It strictly audits resources and summarizes provisioned storage capacity across resource groups without making state modifications or initiating deletions.

---

## Key Features

- **Automated Disk Discovery:** Identifies all managed disks where the `managed_by` property is null across the target subscription scope.
- **Passwordless Authentication:** Utilizes `DefaultAzureCredential` to authenticate dynamically via an active Azure CLI session (`az login`).
- **No Embedded Credentials:** Reads the target subscription ID strictly from the `AZURE_SUBSCRIPTION_ID` environment variable.
- **Read-Only Operation:** Evaluates resource states without executing modifications, deletions, or disruptive actions.
- **Clean CLI Reporting:** Outputs findings in an aligned terminal table detailing resource names, resource groups, storage SKU types, Azure locations, and provisioned sizes in GB.

---

## Quick Start

### 1. Prerequisites
- Python 3.10 or higher.
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed and authenticated.
- Azure built-in **Reader** role assigned on the target subscription or resource group.

### 2. Clone and Setup

```bash
git clone [https://github.com/Abdulsattar-Homsi/azure-waste-cleaner.git](https://github.com/Abdulsattar-Homsi/azure-waste-cleaner.git)
cd azure-waste-cleaner
```

#### On Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Authentication & Execution

Ensure you are logged into Azure via Azure CLI:
```bash
az login
```

Set your target subscription ID and run the scanner:

#### On Linux / macOS:
```bash
export AZURE_SUBSCRIPTION_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
python main.py
```

#### On Windows (PowerShell):
```powershell
$env:AZURE_SUBSCRIPTION_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
python main.py
```

---

## Verification & Ephemeral Lab Testing

The detection logic was verified against an intentionally staged, unattached test disk in an Azure sandbox environment:

```bash
# 1. Provision a 4GB test disk
az disk create \
  --name "temp-unattached-disk-test" \
  --resource-group "NetworkWatcherRG" \
  --size-gb 4 \
  --sku "Standard_LRS"

# 2. Execute scanner to confirm detection
python main.py

# 3. Clean up the test resource immediately to prevent costs
az disk delete \
  --name "temp-unattached-disk-test" \
  --resource-group "NetworkWatcherRG" \
  --yes
```

### Observed Terminal Output

```text
[*] Scanning subscription: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx ...

[!] Found (1) unattached disk(s):

Disk Name                      | Resource Group       | Size (GB)  | SKU                                  | Location
-----------------------------------------------------------------------------------------------
temp-unattached-disk-test      | NETWORKWATCHERRG     | 4          | DiskStorageAccountTypes.STANDARD_LRS | germanywestcentral
-----------------------------------------------------------------------------------------------
Total unattached storage capacity: 4 GB
```

---

## Security & Permissions

- **Authentication Flow:** Leverages `azure-identity`'s `DefaultAzureCredential`, which sequentially checks environment variables, Managed Identity, and local developer CLI tokens.
- **Least Privilege:** The application functions entirely with read-only access. Assigning the built-in `Reader` role (`Microsoft.Compute/disks/read`) is sufficient.
- **Zero Secrets at Rest:** The tool stores no API keys, client secrets, or persistent connection tokens.

---

## Limitations

- **Storage Capacity vs. Monetary Cost:** The tool calculates and sums wasted provisioned capacity in gigabytes (GB); it does not pull dynamic pricing models or calculate currency totals.
- **No Automated Remediation:** Disks are not deleted automatically. An unattached disk is not necessarily abandoned; it may serve as an offline backup, a volume awaiting VM maintenance, or disaster recovery data. Human verification is required prior to deletion.
- **Scope:** Detection is currently scoped exclusively to Azure Managed Disks and does not yet inspect unassociated network or app resources.

---

## Technical Decisions

| Decision | Implementation | Rationale |
| :--- | :--- | :--- |
| **Authentication** | `DefaultAzureCredential` | Native Microsoft standard; allows seamless local CLI authentication without embedding Service Principal keys. |
| **API Interface** | Azure SDK for Python (`azure-mgmt-compute`) | Provides built-in pagination, strict data typing, and reliable ARM API compatibility over raw HTTP calls. |
| **Safety Posture** | Audit & Report Only | Avoids catastrophic data loss; leaves resource destruction decisions to cloud administrators. |

---

## Repository Structure

```text
azure-waste-cleaner/
├── .gitignore               # Excludes virtual environment, bytecode caches, and local configurations
├── main.py                  # Scanner implementation, Azure SDK client calls, and CLI table output
├── requirements.txt         # Pinned Python package dependencies
└── README.md                # Technical project documentation and usage guide
```

---

## Roadmap

- [ ] **Unassociated Public IPs:** Identify idle reserved Public IPs incurring hourly reservation fees.
- [ ] **Empty App Service Plans:** Audit App Service Plans running zero web applications.
- [ ] **Automated Alerts:** Deliver scheduled audit reports via Webhook to Microsoft Teams or Slack.
- [ ] **Serverless Execution:** Package scanner as an Azure Timer-Triggered Function.