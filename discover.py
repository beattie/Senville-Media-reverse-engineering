#!/usr/bin/env python3
"""
Senville/Midea Device Discovery Script

This script discovers Midea-based devices on your network and retrieves
their credentials (token and key) for local control.

Usage:
    python3 discover.py --account YOUR_EMAIL --password YOUR_PASSWORD

Or set environment variables and run:
    python3 discover.py
"""

import os
import sys
import argparse
from midea_beautiful import find_appliances

def discover_devices(account=None, password=None):
    """
    Discover all Midea devices on the network

    Args:
        account: Midea account email
        password: Midea account password

    Returns:
        List of discovered appliances
    """
    # Try environment variables if not provided
    if not account:
        account = os.getenv('MIDEA_ACCOUNT')
    if not password:
        password = os.getenv('MIDEA_PASSWORD')

    if not account or not password:
        print("Error: Midea account credentials required!")
        print("Provide via --account/--password or set MIDEA_ACCOUNT/MIDEA_PASSWORD env vars")
        sys.exit(1)

    print("Discovering devices on network...")
    print(f"Using account: {account}")
    print()

    try:
        appliances = find_appliances(
            account=account,
            password=password
        )

        if not appliances:
            print("No devices found on network.")
            print("\nTroubleshooting:")
            print("  1. Ensure device is powered on and connected to WiFi")
            print("  2. Verify you're on the same network")
            print("  3. Check Midea account credentials are correct")
            return []

        print(f"Found {len(appliances)} device(s):\n")

        for i, appliance in enumerate(appliances, 1):
            print(f"--- Device {i} ---")
            print(f"Type:       {appliance.type}")
            print(f"Name:       {appliance.name}")
            print(f"ID:         {appliance.id}")
            print(f"IP Address: {appliance.address}")
            print(f"Online:     {appliance.online}")

            # Show credentials if available
            if hasattr(appliance, 'token') and appliance.token:
                print(f"Token:      {appliance.token[:20]}... ({len(appliance.token)} chars)")
            if hasattr(appliance, 'key') and appliance.key:
                print(f"Key:        {appliance.key[:20]}... ({len(appliance.key)} chars)")

            print()

            # Generate .env format output
            print("Add to your .env file:")
            print(f"SENVILLE_IP={appliance.address}")
            print(f"SENVILLE_DEVICE_ID={appliance.id}")
            if hasattr(appliance, 'token') and appliance.token:
                print(f"SENVILLE_TOKEN={appliance.token}")
            if hasattr(appliance, 'key') and appliance.key:
                print(f"SENVILLE_KEY={appliance.key}")
            print()

        return appliances

    except Exception as e:
        print(f"Error during discovery: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    parser = argparse.ArgumentParser(
        description='Discover Midea/Senville devices on network'
    )
    parser.add_argument(
        '-a', '--account',
        help='Midea account email (or set MIDEA_ACCOUNT env var)'
    )
    parser.add_argument(
        '-p', '--password',
        help='Midea account password (or set MIDEA_PASSWORD env var)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    appliances = discover_devices(args.account, args.password)

    if appliances:
        print(f"\nSuccess! Discovered {len(appliances)} device(s)")
        print("\nNext steps:")
        print("  1. Copy .env.example to .env")
        print("  2. Add the credentials shown above to .env")
        print("  3. Run: python3 status.py")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
