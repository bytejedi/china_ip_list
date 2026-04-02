#!/usr/bin/env python3
"""
Compute AllowedIPs = 0.0.0.0/0 - china_ip_list.txt
Output: comma-separated CIDR ranges (non-China IPs)

Uses integer interval complement algorithm for efficiency.
"""

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
        # Largest prefix that starts at 'start' and fits within [start, end]
        # 1. max bits from trailing zeros of start
        if start == 0:
            max_bits = 32
        else:
            max_bits = (start & -start).bit_length() - 1
        # 2. max bits that fit within remaining range
        range_bits = (end - start + 1).bit_length() - 1
        bits = min(max_bits, range_bits)
        cidrs.append(ipaddress.IPv4Network((start, 32 - bits)))
        start += 1 << bits
    return cidrs


def main():
    script_dir = Path(__file__).parent
    china_ip_file = script_dir / "china_ip_list.txt"
    output_file = script_dir / "allowed_ips.txt"

    # Read and parse China IP ranges
    china_nets = []
    with open(china_ip_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                china_nets.append(ipaddress.ip_network(line, strict=False))

    # Collapse overlapping/adjacent ranges
    china_nets = list(ipaddress.collapse_addresses(china_nets))
    print(f"Loaded {len(china_nets)} collapsed China IP ranges")

    # Convert to sorted integer intervals and merge
    intervals = sorted(ip_net_to_range(net) for net in china_nets)
    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    # Compute complement within [0, 2^32 - 1]
    full_start, full_end = 0, (1 << 32) - 1
    gaps = []
    cursor = full_start
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

    print(f"Result: {len(result)} non-China IP ranges")

    # Write comma-separated output
    output = ",".join(str(net) for net in result)
    with open(output_file, "w") as f:
        f.write(output)
        f.write("\n")

    print(f"Written to {output_file}")


if __name__ == "__main__":
    main()
