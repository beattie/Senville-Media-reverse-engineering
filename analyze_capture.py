#!/usr/bin/env python3
"""
WiFi Packet Capture Analyzer for Senville/Midea Protocol

Analyzes captured WiFi packets to understand the protocol structure.

Usage:
    python3 analyze_capture.py senville_capture-01.cap

Requires:
    pip install scapy
"""

import sys
import argparse
from collections import defaultdict

try:
    from scapy.all import rdpcap, IP, TCP, UDP, Raw
    from scapy.layers.dot11 import Dot11
except ImportError:
    print("Error: scapy not installed")
    print("Install with: ./venv/bin/pip install scapy")
    sys.exit(1)

def analyze_capture(filename, verbose=False):
    """Analyze a packet capture file"""
    print(f"Reading capture file: {filename}")

    try:
        packets = rdpcap(filename)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading capture: {e}")
        sys.exit(1)

    print(f"Loaded {len(packets)} packets\n")

    # Statistics
    stats = {
        'total': len(packets),
        'tcp': 0,
        'udp': 0,
        'port_6444': 0,
        'port_6445': 0,
        'with_payload': 0
    }

    # Track connections
    connections = defaultdict(int)
    payloads = []

    # Analyze each packet
    for i, pkt in enumerate(packets):
        if verbose:
            print(f"\n--- Packet {i} ---")
            print(pkt.summary())

        # TCP packets
        if TCP in pkt:
            stats['tcp'] += 1
            sport = pkt[TCP].sport
            dport = pkt[TCP].dport

            # Look for Midea protocol port
            if sport == 6444 or dport == 6444:
                stats['port_6444'] += 1
                connections[f"TCP:{sport}->{dport}"] += 1

                if Raw in pkt:
                    payload = bytes(pkt[Raw].load)
                    payloads.append({
                        'packet': i,
                        'protocol': 'TCP',
                        'sport': sport,
                        'dport': dport,
                        'data': payload
                    })
                    stats['with_payload'] += 1

                    if verbose:
                        print(f"  TCP Port 6444 - Payload: {len(payload)} bytes")
                        print(f"  Hex: {payload.hex()}")

        # UDP packets
        elif UDP in pkt:
            stats['udp'] += 1
            sport = pkt[UDP].sport
            dport = pkt[UDP].dport

            # Look for discovery port
            if sport == 6445 or dport == 6445:
                stats['port_6445'] += 1
                connections[f"UDP:{sport}->{dport}"] += 1

                if Raw in pkt:
                    payload = bytes(pkt[Raw].load)
                    payloads.append({
                        'packet': i,
                        'protocol': 'UDP',
                        'sport': sport,
                        'dport': dport,
                        'data': payload
                    })
                    stats['with_payload'] += 1

                    if verbose:
                        print(f"  UDP Port 6445 - Payload: {len(payload)} bytes")
                        print(f"  Hex: {payload.hex()}")

    # Print summary
    print("\n" + "="*60)
    print("CAPTURE ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total Packets:        {stats['total']}")
    print(f"TCP Packets:          {stats['tcp']}")
    print(f"UDP Packets:          {stats['udp']}")
    print(f"Port 6444 (command):  {stats['port_6444']}")
    print(f"Port 6445 (discovery):{stats['port_6445']}")
    print(f"With Payload:         {stats['with_payload']}")

    if connections:
        print(f"\nConnections:")
        for conn, count in sorted(connections.items(), key=lambda x: x[1], reverse=True):
            print(f"  {conn:30} : {count} packets")

    # Analyze payloads
    if payloads:
        print(f"\n" + "="*60)
        print(f"PAYLOAD ANALYSIS ({len(payloads)} payloads)")
        print("="*60)

        for i, p in enumerate(payloads[:20]):  # Show first 20
            print(f"\n--- Payload {i+1} (Packet #{p['packet']}) ---")
            print(f"Protocol: {p['protocol']}")
            print(f"Ports:    {p['sport']} -> {p['dport']}")
            print(f"Length:   {len(p['data'])} bytes")
            print(f"Hex:      {p['data'].hex()}")

            # Try to identify patterns
            data = p['data']
            if len(data) > 0:
                # Check for common start bytes
                if data[0] == 0xAA:
                    print("  -> Starts with 0xAA (likely Midea protocol)")

                # Look for patterns
                if len(data) > 2:
                    print(f"  -> First 3 bytes: {data[:3].hex()}")

                # Try ASCII
                try:
                    ascii_str = data.decode('ascii', errors='ignore')
                    if ascii_str.isprintable() and len(ascii_str) > 3:
                        print(f"  -> ASCII: {ascii_str[:50]}")
                except:
                    pass

        if len(payloads) > 20:
            print(f"\n... and {len(payloads) - 20} more payloads")

    print("\n" + "="*60)
    print("\nNext steps:")
    print("  1. Look for patterns in payloads")
    print("  2. Correlate with app actions (on/off, temp changes)")
    print("  3. Compare encrypted vs unencrypted sections")
    print("  4. Use existing libraries to decrypt if possible")
    print("  5. Run with --verbose for detailed packet info")

def main():
    parser = argparse.ArgumentParser(
        description='Analyze WiFi packet captures for Senville/Midea protocol'
    )
    parser.add_argument(
        'capture_file',
        help='Packet capture file (.cap or .pcap)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed packet information'
    )

    args = parser.parse_args()

    analyze_capture(args.capture_file, args.verbose)

if __name__ == '__main__':
    main()
