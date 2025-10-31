#!/usr/bin/env python3
"""
Extract Token and Key from Midea Protocol Packet Capture

Analyzes captured traffic to find authentication credentials.
"""

import sys
import argparse
import binascii

try:
    from scapy.all import rdpcap, TCP, Raw
except ImportError:
    print("Error: scapy not installed")
    print("Install with: source venv/bin/activate && pip install scapy")
    sys.exit(1)

def extract_credentials(filename):
    """Extract token and key from packet capture"""
    print(f"Reading capture file: {filename}\n")

    try:
        packets = rdpcap(filename)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)

    print(f"Loaded {len(packets)} packets")
    print("="*60)

    token_candidates = []
    key_candidates = []

    for i, pkt in enumerate(packets):
        if TCP in pkt and Raw in pkt:
            payload = bytes(pkt[Raw].load)
            hex_payload = payload.hex()

            # Look for token (128 hex chars = 64 bytes)
            if len(payload) >= 64:
                # Check for hex-like strings
                try:
                    hex_str = payload.decode('ascii', errors='ignore')
                    # Look for 128-char hex strings
                    if len(hex_str) >= 128 and all(c in '0123456789ABCDEFabcdef' for c in hex_str[:128]):
                        if hex_str[:128] not in token_candidates:
                            token_candidates.append(hex_str[:128])
                            print(f"\n[Packet {i}] Possible TOKEN found:")
                            print(f"  {hex_str[:128]}")
                except:
                    pass

            # Look for key (64 hex chars = 32 bytes)
            if len(payload) >= 32:
                try:
                    hex_str = payload.decode('ascii', errors='ignore')
                    # Look for 64-char hex strings
                    if len(hex_str) >= 64 and all(c in '0123456789ABCDEFabcdef' for c in hex_str[:64]):
                        if hex_str[:64] not in key_candidates and hex_str[:64] not in [t[:64] for t in token_candidates]:
                            key_candidates.append(hex_str[:64])
                            print(f"\n[Packet {i}] Possible KEY found:")
                            print(f"  {hex_str[:64]}")
                except:
                    pass

            # Print all payloads for manual inspection
            if len(payload) > 10:
                print(f"\n--- Packet {i} ---")
                print(f"Length: {len(payload)} bytes")
                print(f"Hex: {hex_payload[:200]}{'...' if len(hex_payload) > 200 else ''}")

                # Try to find readable strings
                try:
                    ascii_data = payload.decode('ascii', errors='ignore')
                    readable = ''.join(c if c.isprintable() else '.' for c in ascii_data)
                    if any(c.isalnum() for c in readable):
                        print(f"ASCII: {readable[:100]}")
                except:
                    pass

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if token_candidates:
        print(f"\nFound {len(token_candidates)} possible TOKEN(s):")
        for t in token_candidates:
            print(f"  {t}")
    else:
        print("\nNo 128-character hex strings found (tokens)")

    if key_candidates:
        print(f"\nFound {len(key_candidates)} possible KEY(s):")
        for k in key_candidates:
            print(f"  {k}")
    else:
        print("\nNo 64-character hex strings found (keys)")

    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Look for token (128 hex chars) and key (64 hex chars) in output above")
    print("2. Add them to your .env file:")
    print("   SENVILLE_TOKEN=<128-char-token>")
    print("   SENVILLE_KEY=<64-char-key>")
    print("3. Test with: python3 status.py")
    print("\nNote: Token/key might be encrypted in transit.")
    print("If not found, we may need to try MITM decryption or UART sniffing.")

def main():
    parser = argparse.ArgumentParser(
        description='Extract credentials from Midea protocol capture'
    )
    parser.add_argument(
        'capture_file',
        help='Packet capture file (.pcap)'
    )

    args = parser.parse_args()
    extract_credentials(args.capture_file)

if __name__ == '__main__':
    main()
