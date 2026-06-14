#!/usr/bin/env python3
"""
Import 776 draws (1990-2026) into Supabase
Uses upsert on draw_date to avoid duplicates
"""
import json
import urllib.request
import time
import os

# Load credentials from .env.local
url = ""
key = ""
env_path = r"D:\lotto-ai\.env.local"
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("NEXT_PUBLIC_SUPABASE_URL="):
            url = line.split("=", 1)[1]
        elif line.startswith("NEXT_PUBLIC_SUPABASE_ANON_KEY="):
            key = line.split("=", 1)[1]

print(f"Supabase URL: {url[:40]}...")

# Load the merged 776 draws data
data_path = r"D:\lotto-ai\ml-models\data\scraped_all.json"
with open(data_path, "r", encoding="utf-8") as f:
    draws = json.load(f)

print(f"Loaded {len(draws)} draws")

# Check if we need to load the 1990-1994 data and merge
extra_path = r"D:\lotto-ai\ml-models\data\scraped_1990_1994.json"
if os.path.exists(extra_path):
    with open(extra_path, "r", encoding="utf-8") as f:
        extra = json.load(f)
    print(f"Loaded {len(extra)} extra draws (1990-1994)")
    
    # Merge: extra draws that don't exist in main data
    existing_dates = {d["draw_date"] for d in draws}
    new_draws = [d for d in extra if d["draw_date"] not in existing_dates]
    draws = draws + new_draws
    print(f"After merge: {len(draws)} total draws ({len(new_draws)} new from 1990-1994)")

# Sort by date
draws.sort(key=lambda x: x["draw_date"])
print(f"Date range: {draws[0]['draw_date']} -> {draws[-1]['draw_date']}")

# Map to Supabase column format
def map_draw(d):
    def safe_list(v):
        if not v:
            return []
        if isinstance(v, list):
            return v
        try:
            return json.loads(v)
        except:
            return []
    
    def safe_str(v):
        if not v:
            return None
        return str(v)
    
    return {
        "draw_date": d["draw_date"],
        "first_prize": d.get("first_prize", "") or None,
        "two_digit": safe_str(d.get("two_digit")),
        "three_digit_last": safe_list(d.get("three_digit_last")),
        "three_digit_first": safe_list(d.get("three_digit_first")),
        "nearby_1st": safe_list(d.get("nearby_1st")),
        "second_prize": safe_list(d.get("second_prize")),
        "third_prize": safe_list(d.get("third_prize")),
        "prize_4": safe_list(d.get("prize_4")),
        "prize_5": safe_list(d.get("prize_5")),
    }

# Upsert in batches of 50
batch_size = 50
total_upserted = 0

for i in range(0, len(draws), batch_size):
    batch = draws[i:i+batch_size]
    rows = [map_draw(d) for d in batch]
    
    insert_url = url + "/rest/v1/lotto_results"
    payload = json.dumps(rows).encode("utf-8")
    
    req = urllib.request.Request(insert_url, data=payload, method="POST", headers={
        "apikey": key,
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    })
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            total_upserted += len(batch)
            print(f"  Upserted batch {i//batch_size + 1}: {total_upserted}/{len(draws)}")
    except Exception as e:
        print(f"  Error at batch {i//batch_size + 1}: {e}")
        # Try smaller batch
        for j, row in enumerate(rows):
            try:
                single_payload = json.dumps(row).encode("utf-8")
                single_req = urllib.request.Request(insert_url, data=single_payload, method="POST", headers={
                    "apikey": key,
                    "Authorization": "Bearer " + key,
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates,return=minimal",
                })
                with urllib.request.urlopen(single_req, timeout=15) as resp:
                    total_upserted += 1
            except Exception as e2:
                print(f"    Error on row {i+j}: {e2}")
    
    time.sleep(0.1)  # Rate limit

print(f"\n✅ Done! Upserted {total_upserted}/{len(draws)} draws")
