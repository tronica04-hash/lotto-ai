#!/usr/bin/env python3
"""
Import scraped lottery data into Supabase
Replaces all existing data with fresh scraped data
"""
import json
import urllib.request
import time

# Load credentials
url = ""
key = ""
with open(r"D:\lotto-ai\.env.local") as f:
    for line in f:
        line = line.strip()
        if line.startswith("NEXT_PUBLIC_SUPABASE_URL="):
            url = line.split("=", 1)[1]
        elif line.startswith("NEXT_PUBLIC_SUPABASE_ANON_KEY="):
            key = line.split("=", 1)[1]

# Load scraped data
data_path = r"D:\lotto-ai\ml-models\data\scraped_all.json"
with open(data_path, "r", encoding="utf-8") as f:
    draws = json.load(f)

print(f"Loaded {len(draws)} draws from scraped data")

# Map to Supabase column format
def map_draw(d):
    return {
        "draw_date": d["draw_date"],
        "first_prize": d.get("first_prize", ""),
        "two_digit": d.get("two_digit", None) or None,
        "three_digit_last": d.get("three_digit_last", []),
        "three_digit_first": d.get("three_digit_first", []),
        "nearby_1st": d.get("nearby_1st", []),
        "second_prize": d.get("second_prize", []),
        "third_prize": d.get("third_prize", []),
        "prize_4": d.get("prize_4", []),
        "prize_5": d.get("prize_5", []),
    }

# First, clear existing data
print("Clearing existing data...")
clear_url = url + "/rest/v1/lotto_results?id=gt.0"
req = urllib.request.Request(clear_url, method="DELETE", headers={
    "apikey": key,
    "Authorization": "Bearer " + key,
    "Prefer": "return=minimal"
})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f"Clear status: {resp.status}")
except Exception as e:
    print(f"Clear error (may be OK): {e}")

# Insert in batches of 100
batch_size = 100
total_inserted = 0

for i in range(0, len(draws), batch_size):
    batch = draws[i:i+batch_size]
    rows = [map_draw(d) for d in batch]
    
    insert_url = url + "/rest/v1/lotto_results"
    payload = json.dumps(rows).encode("utf-8")
    
    req = urllib.request.Request(insert_url, data=payload, method="POST", headers={
        "apikey": key,
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    })
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            total_inserted += len(batch)
            print(f"  Inserted batch {i//batch_size + 1}: {total_inserted}/{len(draws)}")
    except Exception as e:
        print(f"  Error at batch {i//batch_size + 1}: {e}")
    
    time.sleep(0.5)  # Rate limit

print(f"\nDone! Inserted {total_inserted} rows")
