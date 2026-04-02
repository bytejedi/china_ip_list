#!/usr/bin/env python3
"""
Compute AllowedIPs = 0.0.0.0/0 - china_ip_list.txt - extra skips
Output: comma-separated CIDR ranges for WireGuard AllowedIPs

Uses integer interval complement algorithm for efficiency.
"""

import argparse
import ipaddress
from pathlib import Path


def ip_net_to_range(net):
    """Convert an IPv4Network to (start, end) inclusive integer range."""
    start = int(net.network_address)
    end = start + net.num_addresses - 1
    return start, end


def range_to_cidrs(start, end):
    """Convert an integer range [start, end] to a list of CIDR networks."""
    cidrs = []
    while start <= end:
        if start == 0:
            max_bits = 32
        else:
            max_bits = (start & -start).bit_length() - 1
        range_bits = (end - start + 1).bit_length() - 1
        bits = min(max_bits, range_bits)
        cidrs.append(ipaddress.IPv4Network((start, 32 - bits)))
        start += 1 << bits
    return cidrs


def main():
    parser = argparse.ArgumentParser(
        description="Generate WireGuard AllowedIPs by subtracting China IPs from 0.0.0.0/0",
        epilog="""\
Common private/reserved CIDRs you may want to skip:
  10.0.0.0/8        Private (Class A) - NOTE: do NOT skip if WireGuard uses 10.x subnet
  172.16.0.0/12     Private (Class B)
  192.168.0.0/16    Private (Class C)
  100.64.0.0/10     Carrier-grade NAT (CGNAT)
  127.0.0.0/8       Loopback
  169.254.0.0/16    Link-local
  224.0.0.0/4       Multicast
  240.0.0.0/4       Reserved

Examples:
  %(prog)s
  %(prog)s --skip 192.168.0.0/16
  %(prog)s --skip 192.168.0.0/16 172.16.0.0/12 169.254.0.0/16
  %(prog)s --skip 192.168.0.0/16 -o my_allowed.txt""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--skip", nargs="+", default=[], metavar="CIDR",
        help="additional CIDRs to skip (not routed through WireGuard)",
    )
    parser.add_argument(
        "-o", "--output", default=None, metavar="FILE",
        help="output file path (default: allowed_ips.txt in script directory)",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    china_ip_file = script_dir / "china_ip_list.txt"
    output_file = Path(args.output) if args.output else script_dir / "allowed_ips.txt"

    # Read and parse China IP ranges
    exclude_nets = []
    with open(china_ip_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                exclude_nets.append(ipaddress.ip_network(line, strict=False))

    # Add extra skips from command line
    for cidr in args.skip:
        exclude_nets.append(ipaddress.ip_network(cidr, strict=False))

    # Collapse overlapping/adjacent ranges
    exclude_nets = list(ipaddress.collapse_addresses(exclude_nets))
    print(f"Loaded {len(exclude_nets)} collapsed exclude ranges")

    # Convert to sorted integer intervals and merge
    intervals = sorted(ip_net_to_range(net) for net in exclude_nets)
    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    # Compute complement within [0, 2^32 - 1]
    full_end = (1 << 32) - 1
    gaps = []
    cursor = 0
    for start, end in merged:
        if cursor < start:
            gaps.append((cursor, start - 1))
        cursor = end + 1
    if cursor <= full_end:
        gaps.append((cursor, full_end))

    # Convert gaps to CIDR notation
    result = []
    for start, end in gaps:
        result.extend(range_to_cidrs(start, end))

    print(f"Result: {len(result)} allowed IP ranges")

    # Write comma-separated output
    output = ",".join(str(net) for net in result)
    with open(output_file, "w") as f:
        f.write(output)
        f.write("\n")

    print(f"Written to {output_file}")


if __name__ == "__main__":
    main()
