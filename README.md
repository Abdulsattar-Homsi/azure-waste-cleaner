# Azure Waste Cleaner & FinOps Optimizer

A lightweight, read-only FinOps CLI scanner written in Python that inspects Microsoft Azure subscriptions for unattached Managed Disks and orphaned Public IP addresses, reporting idle cloud assets in the terminal to reduce unnecessary costs.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Azure SDK](https://img.shields.io/badge/azure--sdk-python-0078D4.svg)
![Security](https://img.shields.io/badge/auth-DefaultAzureCredential-green.svg)
![RBAC Scope](https://img.shields.io/badge/rbac-Reader-success.svg)
![Mode](https://img.shields.io/badge/mode-read--only-informational.svg)

---

## Overview

Infrastructure provisioning cycles often leave behind orphaned resources—such as unattached Managed Disks after virtual machine teardowns, and unassociated Public IP addresses that accrue idle reservation fees.

This utility automates the discovery of these idle assets using the official Azure SDK for Python. It audits compute and network resource states across all resource groups, generating a clear summary without executing state changes or automated deletions.

---

## Key Features

- **Unattached Disk Detection:** Queries Azure Compute APIs to find managed disks where `managed_by` is null across the target subscription.
- **Orphaned Public IP Auditing:** Queries Azure Network APIs to discover reserved Public IP addresses where `ip_configuration` is null.
- **Passwordless Authentication:** Uses `DefaultAzureCredential` to acquire tokens dynamically from an active Azure CLI session.
- **Zero Embedded Secrets:** Consumes target subscription details solely from the `AZURE_SUBSCRIPTION_ID` environment variable.
- **Read-Only Operation:** Restricts execution strictly to querying and reporting, preventing accidental downtime or data loss.
- **Aligned CLI Output:** Formats findings into separated terminal tables displaying resource names, resource groups, SKUs, locations, and capacities.

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

Set the target subscription ID and execute:

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

The detection logic for both storage and network resources was verified against intentionally provisioned ephemeral resources in an isolated lab:

### 1. Storage Detection Validation
```bash
# Provision test disk
az disk create \
  --name "temp-unattached-disk-test" \
  --resource-group "NetworkWatcherRG" \
  --size-gb 4 \
  --sku "Standard_LRS"

# Run scanner to verify detection
python main.py

# Clean up resource immediately
az disk delete \
  --name "temp-unattached-disk-test" \
  --resource-group "NetworkWatcherRG" \
  --yes
```

### 2. Network Public IP Validation
```bash
# Provision test public IP
az network public-ip create \
  --name "temp-unassociated-pip-test" \
  --resource-group "NetworkWatcherRG" \
  --sku "Standard" \
  --allocation-method "Static"

# Run scanner to verify detection
python main.py

# Clean up resource immediately
az network public-ip delete \
  --name "temp-unassociated-pip-test" \
  --resource-group "NetworkWatcherRG"
```

### Observed Terminal Output

```text
[*] Scanning subscription: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx ...

===============================================================================================
                      AZURE FINOPS & COST OPTIMIZATION REPORT                      
===============================================================================================

[✓] Disks: No unattached disks found. Storage is clean.

-----------------------------------------------------------------------------------------------

[!] Public IPs: Found (1) unassociated public IP(s):

IP Name                        | Resource Group       | IP Address           | SKU                             | Location
-----------------------------------------------------------------------------------------------
temp-unassociated-pip-test     | NetworkWatcherRG     | 20.218.102.66        | PublicIPAddressSkuName.STANDARD | germanywestcentral
-----------------------------------------------------------------------------------------------

===============================================================================================
```

---

## Security & Permissions

- **Identity Flow:** Built on `DefaultAzureCredential`, chaining authentication from local developer tools to Managed Identities without code changes.
- **Least Privilege:** Operates entirely under the built-in Azure RBAC `Reader` role (`Microsoft.Compute/disks/read`, `Microsoft.Network/publicIPAddresses/read`).
- **Secret Isolation:** No account keys, connection strings, or service principal secrets are stored in files or Git history.

---

## Limitations

- **Read-Only Scope:** The scanner flags idle assets for review; it does not automatically modify or delete resources. Detached assets may be temporarily reserved for failover or maintenance.
- **Resource Boundary:** Covers Azure Managed Disks and Public IP addresses. Does not currently inspect app service tiers, container registries, or database reservations.
- **Cost Metrics:** Measures unattached storage in gigabytes and lists reserved IP allocations without generating dynamic billing calculations.

---

## Technical Decisions

| Decision | Implementation | Rationale |
| :--- | :--- | :--- |
| **Authentication** | `DefaultAzureCredential` | Native Microsoft identity standard; avoids hardcoding service principal secrets. |
| **API Interface** | Azure Python SDK (`compute`, `network`) | Ensures type safety, pagination management, and native ARM API integration. |
| **Operational Stance** | Audit and Report Only | Preserves infrastructure stability and prevents catastrophic accidental data deletion. |

---

## Repository Structure

```text
azure-waste-cleaner/
├── .gitignore               # Excludes virtual environments, cache files, and local settings
├── main.py                  # Core auditing logic and CLI reporting engine
├── requirements.txt         # Pinned Python dependencies (compute, network, identity)
└── README.md                # Standardized technical documentation
```

---

## Roadmap

- [x] **Unattached Managed Disks:** Query and report idle persistent disks.
- [x] **Unassociated Public IPs:** Audit detached public IP addresses incurring reservation fees.
- [ ] **Empty App Service Plans:** Audit App Service Plans hosting zero active web applications.
- [ ] **Automated Alerts:** Deliver scheduled summaries via Webhook to Microsoft Teams or Slack.
- [ ] **Serverless Execution:** Containerize scanner execution via Azure Functions timer triggers.