import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient


def scan_unattached_disks(compute_client: ComputeManagementClient) -> list:
    """
    Scans for managed disks across the subscription that are not attached to any VM.
    """
    unattached_disks = []
    for disk in compute_client.disks.list():
        if not disk.managed_by:
            unattached_disks.append({
                "name": disk.name,
                "resource_group": disk.id.split("/")[4],
                "size_gb": disk.disk_size_gb,
                "sku": disk.sku.name if disk.sku else "Unknown",
                "location": disk.location
            })
    return unattached_disks


def scan_unassociated_public_ips(network_client: NetworkManagementClient) -> list:
    """
    Scans for Public IP addresses that are not attached to any network interface or resource.
    """
    unassociated_ips = []
    for pip in network_client.public_ip_addresses.list_all():
        # If ip_configuration is None, the Public IP is detached and idling
        if not pip.ip_configuration:
            unassociated_ips.append({
                "name": pip.name,
                "resource_group": pip.id.split("/")[4],
                "ip_address": pip.ip_address if pip.ip_address else "Dynamic (Unallocated)",
                "sku": pip.sku.name if pip.sku else "Basic",
                "location": pip.location
            })
    return unassociated_ips


def display_report(disks: list, public_ips: list):
    """
    Prints a formatted operational audit summary to the terminal.
    """
    print("\n" + "=" * 95)
    print("                      AZURE FINOPS & COST OPTIMIZATION REPORT                      ")
    print("=" * 95 + "\n")

    # 1. Managed Disks Section
    if not disks:
        print("[✓] Disks: No unattached disks found. Storage is clean.")
    else:
        print(f"[!] Disks: Found ({len(disks)}) unattached disk(s):\n")
        print(f"{'Disk Name':<30} | {'Resource Group':<20} | {'Size (GB)':<10} | {'SKU':<15} | {'Location'}")
        print("-" * 95)
        total_gb = 0
        for d in disks:
            total_gb += d["size_gb"]
            print(f"{d['name']:<30} | {d['resource_group']:<20} | {d['size_gb']:<10} | {d['sku']:<15} | {d['location']}")
        print("-" * 95)
        print(f"Total unattached storage capacity: {total_gb} GB\n")

    print("\n" + "-" * 95 + "\n")

    # 2. Public IP Addresses Section
    if not public_ips:
        print("[✓] Public IPs: No orphaned public IP addresses found. Network is clean.")
    else:
        print(f"[!] Public IPs: Found ({len(public_ips)}) unassociated public IP(s):\n")
        print(f"{'IP Name':<30} | {'Resource Group':<20} | {'IP Address':<20} | {'SKU':<10} | {'Location'}")
        print("-" * 95)
        for ip in public_ips:
            print(f"{ip['name']:<30} | {ip['resource_group']:<20} | {ip['ip_address']:<20} | {ip['sku']:<10} | {ip['location']}")
        print("-" * 95)

    print("\n" + "=" * 95 + "\n")


def main():
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        print("[X] Error: AZURE_SUBSCRIPTION_ID environment variable is not set.")
        print("Please export or set AZURE_SUBSCRIPTION_ID before running.")
        exit(1)

    print(f"[*] Scanning subscription: {subscription_id} ...")
    credential = DefaultAzureCredential()

    compute_client = ComputeManagementClient(credential, subscription_id)
    network_client = NetworkManagementClient(credential, subscription_id)

    disks = scan_unattached_disks(compute_client)
    public_ips = scan_unassociated_public_ips(network_client)

    display_report(disks, public_ips)


if __name__ == "__main__":
    main()