#!/usr/bin/env python3
"""
Thai Lottery Analysis - Latest 100 Draws
Frequency analysis, hot/cold numbers, gap analysis
"""
import urllib.request
import json
import os
from collections import Counter, defaultdict
from datetime import datetime

# ── Load env ──────────────────────────────────────────────
env_path = r"D:\lotto-ai\.env.local"
SUPABASE_URL = ""
SUPABASE_KEY = ""
with open(env_path, "r") as f:
    for line in f:
        line = line.strip()
        if line.startswith("NEXT_PUBLIC_SUPABASE_URL="):
            SUPABASE_URL = line.split("=", 1)[1]
        elif line.startswith("NEXT_PUBLIC_SUPABASE_ANON_KEY="):
            SUPABASE_KEY = line.split("=", 1)[1]

# ── Fetch data ────────────────────────────────────────────
url = f"{SUPABASE_URL}/rest/v1/lotto_results?select=*&order=draw_date.desc&limit=100"
req = urllib.request.Request(url, headers={
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())

print(f"=" * 70)
print(f"  THAI LOTTERY ANALYSIS - LATEST 100 DRAWS")
print(f"  Data loaded: {len(data)} draws")
print(f"  Date range: {data[-1].get('draw_date','?')} → {data[0].get('draw_date','?')}")
print(f"=" * 70)

# ── Inspect columns ───────────────────────────────────────
print(f"\n📋 Columns: {list(data[0].keys())}")

# ── 1. Two-digit (เลขท้าย 2 ตัว) frequency ───────────────
print(f"\n{'='*70}")
print("📊 1. ความถี่เลขท้าย 2 ตัว (Two-Digit Frequency)")
print(f"{'='*70}")

two_digit_counter = Counter()
two_digit_last_seen = {}
for i, row in enumerate(data):
    val = row.get("two_digit")
    if val is not None:
        s = str(val).zfill(2)
        two_digit_counter[s] += 1
        if s not in two_digit_last_seen:
            two_digit_last_seen[s] = i

print(f"\n  🔥 เลขร้อน (Hot) - Top 10 ที่ออกบ่อยที่สุด:")
for num, cnt in two_digit_counter.most_common(10):
    bar = "█" * cnt
    print(f"    {num}: {cnt:2d} ครั้ง  {bar}")

print(f"\n  ❄️  เลขเย็น (Cold) - 10 ตัวที่ออกน้อยที่สุด:")
for num, cnt in two_digit_counter.most_common()[-10:]:
    bar = "█" * cnt
    print(f"    {num}: {cnt:2d} ครั้ง  {bar}")

# ── 2. First prize analysis ───────────────────────────────
print(f"\n{'='*70}")
print("📊 2. วิเคราะห์เลขรางวัลที่ 1 (First Prize)")
print(f"{'='*70}")

first_prize_counter = Counter()
first_prize_last_seen = {}  # number -> draw index (0 = latest)
first_prize_gaps = defaultdict(list)  # number -> list of gaps
prev_seen = {}  # number -> last draw index

for i, row in enumerate(data):
    val = row.get("first_prize")
    if val is not None:
        s = str(val)
        first_prize_counter[s] += 1
        if s not in first_prize_last_seen:
            first_prize_last_seen[s] = i
        if s in prev_seen:
            gap = i - prev_seen[s]
            first_prize_gaps[s].append(gap)
        prev_seen[s] = i

# Last 2 digits of first prize
fp_2digit_counter = Counter()
for row in data:
    val = row.get("first_prize")
    if val is not None:
        s = str(val)[-2:].zfill(2)
        fp_2digit_counter[s] += 1

print(f"\n  🔥 เลขท้าย 2 ตัวจากรางวัลที่ 1 - Top 10 ร้อน:")
for num, cnt in fp_2digit_counter.most_common(10):
    bar = "█" * cnt
    print(f"    {num}: {cnt:2d} ครั้ง  {bar}")

print(f"\n  ❄️  เลขท้าย 2 ตัวจากรางวัลที่ 1 - 10 ตัวเย็น:")
for num, cnt in fp_2digit_counter.most_common()[-10:]:
    bar = "█" * cnt
    print(f"    {num}: {cnt:2d} ครั้ง  {bar}")

# ── 3. Gap Analysis ───────────────────────────────────────
print(f"\n{'='*70}")
print("📊 3. GAP ANALYSIS - ระยะห่างระหว่างครั้งที่ออก")
print(f"{'='*70}")

# Gap for two_digit numbers
two_digit_gaps = defaultdict(list)
two_digit_prev = {}
for i, row in enumerate(data):
    val = row.get("two_digit")
    if val is not None:
        s = str(val).zfill(2)
        if s in two_digit_gaps or s in two_digit_prev:
            if s in two_digit_prev:
                gap = i - two_digit_prev[s]
                two_digit_gaps[s].append(gap)
            two_digit_prev[s] = i
        else:
            two_digit_prev[s] = i

print(f"\n  📈 เลขที่ขาดตัวนานที่สุด (Due Numbers) - Gap เฉลี่ยสูง):")
avg_gaps = {}
for num, gaps in two_digit_gaps.items():
    avg_gap = sum(gaps) / len(gaps)
    avg_gaps[num] = avg_gap

# Also include numbers not seen recently
all_nums = {str(i).zfill(2) for i in range(100)}
seen_nums = set(two_digit_counter.keys())
never_seen = all_nums - seen_nums
print(f"    ⚠️  เลขที่ไม่เคยออกใน 100 งวด: {len(never_seen)} ตัว")
if never_seen:
    sorted_never = sorted(never_seen)
    print(f"    {', '.join(sorted_never[:20])}{'...' if len(sorted_never) > 20 else ''}")

print(f"\n  🔴 เลขที่ขาดยาวนานที่สุด (Highest Avg Gap):")
sorted_by_gap = sorted(avg_gaps.items(), key=lambda x: -x[1])
for num, avg in sorted_by_gap[:15]:
    last = two_digit_last_seen.get(num, '?')
    print(f"    {num}: เฉลี่ย {avg:.1f} งวด/ครั้ง, ออกล่าสุดงวดที่ {last}")

print(f"\n  🟢 เลขที่ออกถี่ที่สุด (Lowest Avg Gap):")
for num, avg in sorted_by_gap[-10:]:
    last = two_digit_last_seen.get(num, '?')
    print(f"    {num}: เฉลี่ย {avg:.1f} งวด/ครั้ง, ออกล่าสุดงวดที่ {last}")

# ── 4. Hot/Cold Summary ───────────────────────────────────
print(f"\n{'='*70}")
print("📊 4. สรุป เลขร้อน-เย็น (Hot/Cold Summary)")
print(f"{'='*70}")

hot_10 = [num for num, _ in two_digit_counter.most_common(10)]
cold_10 = [num for num, _ in two_digit_counter.most_common()[-10:]]

print(f"\n  🔥🔥🔥 TOP 10 เลขร้อน (HOT):")
print(f"    {', '.join(hot_10)}")

print(f"\n  ❄️❄️❄️ TOP 10 เลขเย็น (COLD):")
print(f"    {', '.join(cold_10)}")

# ── 5. Distribution check ─────────────────────────────────
print(f"\n{'='*70}")
print("📊 5. การกระจายตัว (Distribution)")
print(f"{'='*70}")

freqs = list(two_digit_counter.values())
avg_freq = sum(freqs) / len(freqs) if freqs else 0
max_freq = max(freqs) if freqs else 0
min_freq = min(freqs) if freqs else 0
unique_nums = len(two_digit_counter)

print(f"  จำนวนเลข 2 ตัวที่ออกทั้งหมด: {unique_nums}/100")
print(f"  ความถี่เฉลี่ย: {avg_freq:.2f} ครั้ง")
print(f"  ความถี่สูงสุด: {max_freq} ครั้ง")
print(f"  ความถี่ต่ำสุด: {min_freq} ครั้ง")
print(f"  สัดส่วน: {unique_nums}% ของเลขทั้งหมด 00-99")

# Expected vs observed
expected_per_num = len([r for r in data if r.get("two_digit") is not None]) / 100
print(f"  คาดหวังทางสถิติ: {expected_per_num:.2f} ครั้ง/ตัว (ถ้ากระจายเท่ากัน)")

print(f"\n{'='*70}")
print("✅ วิเคราะห์เสร็จสิ้น")
print(f"{'='*70}")
