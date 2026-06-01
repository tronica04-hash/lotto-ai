#!/usr/bin/env python3
"""
Import ข้อมูลหวยรวม (myhora + vicha-w) เข้า Supabase
"""
import json, csv, time, urllib.request, urllib.error
from datetime import datetime

SUPABASE_URL = "https://jiulxmylgwaaygdytdfj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppdWx4bXlsZ3dhYXlnZHl0ZGZqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAzMDEzNjMsImV4cCI6MjA5NTg3NzM2M30.UZ7mndrVgOTiKDJRsOqRl57EsEG9q5B98c3j0JLuvns"

def upsert_row(row_dict):
    url = f"{SUPABASE_URL}/rest/v1/lotto_results"
    payload = json.dumps(row_dict).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal,resolution=merge-duplicates",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return True, resp.status
    except urllib.error.HTTPError as e:
        return False, f"{e.code}: {e.read().decode()[:200]}"
    except Exception as e:
        return False, str(e)

# โหลดข้อมูลรวม
with open('/tmp/lotto-merged.json') as f:
    merged = json.load(f)

myhora = merged['myhora']
vicha = merged['vicha']
all_dates = merged['all_dates']

# สร้าง import rows
def build_row(date_str):
    """สร้าง row จากข้อมูล myhora (หลัก) + vicha (เสริม)"""
    m = myhora.get(date_str, {})
    v = vicha.get(date_str, {})
    
    draw_number = date_str.replace("-", "")
    
    # ใช้ myhora เป็นหลัก
    first_prize = m.get('first_prize') or v.get('first_prize', '')
    two_digit = m.get('last_2') or v.get('two_digit', '')
    
    # nearby_1st
    nearby = m.get('nearby_1st', [])
    nearby_json = json.dumps(nearby) if nearby else '[]'
    
    # three_digit_first
    front3 = m.get('front_3', [])
    if not front3 and v.get('pre_3digit'):
        front3 = json.loads(v['pre_3digit']) if isinstance(v['pre_3digit'], str) else v['pre_3digit']
    three_digit_first = json.dumps(front3) if front3 else '[]'
    
    # three_digit_last
    last3 = m.get('last_3', [])
    if not last3 and v.get('sub_3digits'):
        last3 = json.loads(v['sub_3digits']) if isinstance(v['sub_3digits'], str) else v['sub_3digits']
    three_digit_last = json.dumps(last3) if last3 else '[]'
    
    # prize_2: myhora ก่อน แล้ว vicha เสริม
    prize_2 = m.get('prize_2', [])
    if not prize_2 and v.get('second_prize'):
        prize_2 = json.loads(v['second_prize']) if isinstance(v['second_prize'], str) else []
    second_prize = json.dumps(prize_2) if prize_2 else '[]'
    
    # prize_3
    prize_3 = m.get('prize_3', [])
    if not prize_3 and v.get('third_prize'):
        prize_3 = json.loads(v['third_prize']) if isinstance(v['third_prize'], str) else []
    third_prize = json.dumps(prize_3) if prize_3 else '[]'
    
    # prize_4, prize_5 (myhora เท่านั้น)
    prize_4 = m.get('prize_4', [])
    prize_5 = m.get('prize_5', [])
    
    return {
        "draw_date": date_str,
        "draw_number": draw_number,
        "first_prize": first_prize,
        "two_digit": two_digit,
        "nearby_1st": nearby_json,
        "three_digit_first": three_digit_first,
        "three_digit_last": three_digit_last,
        "second_prize": second_prize,
        "third_prize": third_prize,
        "prize_4": json.dumps(prize_4),
        "prize_5": json.dumps(prize_5),
    }

# ตรวจสอบ schema ปัจจุบัน
print("ตรวจสอบ schema ปัจจุบัน...")
test_row = build_row(all_dates[0])
print(f"Fields: {list(test_row.keys())}")

# เตรียม import
print(f"\nเตรียม import {len(all_dates)} งวด")

# ส่ง Supabase (แบบ batch)
success = 0
failed = 0
failures = []

for i, date_str in enumerate(all_dates):
    row = build_row(date_str)
    ok, status = upsert_row(row)
    if ok:
        success += 1
    else:
        failed += 1
        failures.append(f"  {date_str}: {status}")
    
    if (i + 1) % 50 == 0:
        print(f"  Progress: {i+1}/{len(all_dates)} (ok={success}, fail={failed})")
    time.sleep(0.03)

print(f"\n=== Import เสร็จ ===")
print(f"สำเร็จ: {success}/{len(all_dates)}")
print(f"ล้มเหลว: {failed}")

if failures:
    print(f"\nตัวอย่าง error:")
    for f in failures[:5]:
        print(f)

# ตรวจสอบผล
print(f"\nตรวจสอบข้อมูลใน Supabase...")
import urllib.request
req = urllib.request.Request(
    f"{SUPABASE_URL}/rest/v1/lotto_results?select=draw_date&order=draw_date.asc&limit=3",
    headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())
    print(f"3 แถวแรก: {[d['draw_date'] for d in data]}")

req2 = urllib.request.Request(
    f"{SUPABASE_URL}/rest/v1/lotto_results?select=draw_date&order=draw_date.desc&limit=3",
    headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
)
with urllib.request.urlopen(req2) as resp:
    data = json.loads(resp.read())
    print(f"3 แถวสุดท้าย: {[d['draw_date'] for d in data]}")
