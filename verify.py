"""
SOL Menu — Verify Script
─────────────────────────
Checks that your .env credentials work and lists the tables in your base.
Run this before seed.py to confirm everything is wired up correctly.

Usage:
    python verify.py
"""

import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN   = os.environ.get("AIRTABLE_TOKEN", "")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID", "")

if not TOKEN or not BASE_ID:
    print("ERROR: AIRTABLE_TOKEN and AIRTABLE_BASE_ID must be set in .env")
    sys.exit(1)

HEADERS = {"Authorization": "Bearer " + TOKEN}

print("SOL Menu — Airtable Verify")
print("=" * 44)
print("Token:   " + TOKEN[:12] + "..." + TOKEN[-4:])
print("Base ID: " + BASE_ID)
print()

# Check token is valid
resp = requests.get(
    "https://api.airtable.com/v0/meta/bases/" + BASE_ID + "/tables",
    headers=HEADERS,
)

if resp.status_code == 401:
    print("FAIL — Token is invalid or expired.")
    print("  Go to airtable.com/create/tokens and create a new token.")
    print("  Scope needed: data.records:read  +  data.records:write  +  schema.bases:read")
    sys.exit(1)

if resp.status_code == 403:
    print("FAIL — Token doesn't have access to this base.")
    print("  When creating the token, add your base under 'Access'.")
    sys.exit(1)

if resp.status_code == 404:
    print("FAIL — Base ID not found: " + BASE_ID)
    print("  Open your base in Airtable. The URL looks like:")
    print("  https://airtable.com/appXXXXXXXXXXXXXX/...")
    print("  Copy the appXXX... segment.")
    sys.exit(1)

if resp.status_code != 200:
    print("FAIL — Unexpected response " + str(resp.status_code) + ": " + resp.text)
    sys.exit(1)

tables = resp.json().get("tables", [])
table_names = [t["name"] for t in tables]

print("Token and Base ID are valid.")
print()
print("Tables found in base (" + str(len(tables)) + "):")
for name in table_names:
    print("  " + name)

print()

REQUIRED = ["Meta", "Menu Items", "BBQ Cuts", "BBQ Assortments", "Tasting", "Photos"]
missing  = [t for t in REQUIRED if t not in table_names]

if missing:
    print("Missing tables — create these in Airtable before running seed.py:")
    for t in missing:
        print("  [MISSING] " + t)
    print()
    print("See airtable_schema.md for exact field definitions.")
    sys.exit(1)

print("All 6 required tables present:")
for t in REQUIRED:
    print("  [OK] " + t)

print()
print("Ready. Run:  py seed.py")
