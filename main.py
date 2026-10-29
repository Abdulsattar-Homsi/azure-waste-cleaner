import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

def scan_unattached_disks(subscription_id: str):
    """
    Scans the Azure subscription and identifies all managed disks
    that are currently unattached to any Virtual Machine (VM).
    """
    print(f"[*] Scanning subscription: {subscription_id} ...\n")
    
    # Authenticate using the active Azure CLI session (via DefaultAzureCredential)
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)
    
    unattached_disks = []
    
    # Iterate through all disks across the subscription
    for disk in compute_client.disks.list():
        # An unattached disk will have its 'managed_by' property set to None
        if not disk.managed_by:
            disk_info = {
                "name": disk.name,
                "resource_group": disk.id.split("/")[4],
                "size_gb": disk.disk_size_gb,
                "sku": disk.sku.name if disk.sku else "Unknown",
                "location": disk.location
            }
            unattached_disks.append(disk_info)
            
    return unattached_disks

def display_report(disks: list):
    """
    Prints a formatted summary table of unattached disks to the terminal.
    """
    if not disks:
        print("[✓] No unattached disks found. Your environment is clean and optimized!")
        return

    print(f"[!] Found ({len(disks)}) unattached disk(s):\n")
    print(f"{'Disk Name':<30} | {'Resource Group':<20} | {'Size (GB)':<10} | {'SKU':<15} | {'Location'}")
    print("-" * 95)
    
    total_wasted_gb = 0
    for d in disks:
        total_wasted_gb += d["size_gb"]
        print(f"{d['name']:<30} | {d['resource_group']:<20} | {d['size_gb']:<10} | {d['sku']:<15} | {d['location']}")
        
    print("-" * 95)
    print(f"Total unattached storage capacity: {total_wasted_gb} GB\n")

if __name__ == "__main__":
    # Fetch subscription ID from environment variable
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    
    if not subscription_id:
        print("[X] Error: AZURE_SUBSCRIPTION_ID environment variable is not set.")
        print("Please export or set AZURE_SUBSCRIPTION_ID before running.")
        exit(1)
        
    try:
        results = scan_unattached_disks(subscription_id)
        display_report(results)
    except Exception as e:
        print(f"[X] An error occurred while connecting to Azure:\n{e}")