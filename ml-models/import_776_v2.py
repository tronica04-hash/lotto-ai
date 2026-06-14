#!/usr/bin/env python3
"""
Import 776 draws (1990-2026) into Supabase
Strategy: DELETE all existing, then INSERT fresh
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

print(f"Supabase URL: {url[:40]}...")

# Load the merged 776 draws
with open(r"D:\lotto-ai\ml-models\data\scraped_all.json", "r", encoding="utf-8") as f:
    draws = json.load(f)

draws.sort(key=lambda x: x["draw_date"])
print(f"Loaded {len(draws)} draws | {draws[0]['draw_date']} -> {draws[-1]['draw_date']}")

# Map to Supabase format
def map_draw(d):
    def safe_list(v):
        if not v: return []
        if isinstance(v, list): return v
        try: return json.loads(v)
        except: return []
    def safe_str(v):
        if not v: return None
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

# Step 1: DELETE all existing data
print("\n[Step 1] Deleting existing data...")
delete_url = url + "/rest/v1/lotto_results?id=gt.0"
req = urllib.request.Request(delete_url, method="DELETE", headers={
    "apikey": key,
    "Authorization": "Bearer " + key,
    "Prefer": "return=minimal",
})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f"  Delete status: {resp.status}")
except Exception as e:
    print(f"  Delete error: {e}")

time.sleep(1)

# Step 2: INSERT all 776 draws in batches of 50
print("\n[Step 2] Inserting 776 draws...")
batch_size = 50
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
            print(f"  Batch {i//batch_size + 1}: {total_inserted}/{len(draws)} inserted")
    except Exception as e:
        print(f"  Error at batch {i//batch_size + 1}: {e}")
        # Retry one by one
        for j, row in enumerate(rows):
            try:
                single_payload = json.dumps(row).encode("utf-8")
                single_req = urllib.request.Request(insert_url, data=single_payload, method="POST", headers={
                    "apikey": key,
                    "Authorization": "Bearer " + key,
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal",
                })
                with urllib.request.urlopen(single_req, timeout=15) as resp:
                    total_inserted += 1
            except Exception as e2:
                print(f"    Row {i+j} failed: {e2}")
    
    time.sleep(0.1)

print(f"\n✅ Done! Inserted {total_inserted}/{len(draws)} draws into Supabase")
