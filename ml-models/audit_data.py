#!/usr/bin/env python3
"""
LottoAI Data Hunter — ไล่เก็บข้อมูลหวยที่ขาดหาย
1. เติมข้อมูล 1990-1994 (ก่อนที่ scraped_all.json จะเริ่ม)
2. เติม three_digit_first ที่ขาด (มีแค่ 32.9%)
3. ตรวจสอบงวดที่หายไป
4. ดึงข้อมูลจากแหล่งใหม่
"""
import json, os, sys, time, re
from datetime import datetime, timedelta
from collections import defaultdict

DATA_DIR = r"D:\lotto-ai\ml-models\data"
OUTPUT_DIR = r"D:\lotto-ai\ml-models\data"
SCRAPED_FILE = os.path.join(DATA_DIR, "scraped_all.json")

# ── Load existing data ─────────────────────────────────────
with open(SCRAPED_FILE, "r", encoding="utf-8") as f:
    existing = json.load(f)

existing_dates = {d["draw_date"] for d in existing}
print(f"📊 ข้อมูลที่มี: {len(existing)} งวด ({existing[0]['draw_date']} → {existing[-1]['draw_date']})")
print(f"   วันที่ซ้ำ: {len(existing) - len(existing_dates)}")

# ── 1. ตรวจสอบงวดที่หาย ──────────────────────────────────
print("\n🔍 ตรวจสอบงวดที่หายไป...")
parsed_dates = sorted([datetime.strptime(d, "%Y-%m-%d") for d in existing_dates])
missing = []
for i in range(1, len(parsed_dates)):
    gap = (parsed_dates[i] - parsed_dates[i-1]).days
    if gap > 20:  # ปกติห่าง 14-16 วัน
        # คาดว่าควรมีงวดกลาง
        mid = parsed_dates[i-1] + timedelta(days=15)
        # หาวันที่ 1 หรือ 16 ที่ใกล้ที่สุด
        if mid.day <= 8:
            expected = mid.replace(day=1)
        elif mid.day <= 23:
            expected = mid.replace(day=16)
        else:
            # ขึ้นเดือนถัดไป
            if mid.month == 12:
                expected = datetime(mid.year + 1, 1, 1)
            else:
                expected = datetime(mid.year, mid.month + 1, 1)
        missing.append({
            "after": parsed_dates[i-1].strftime("%Y-%m-%d"),
            "before": parsed_dates[i].strftime("%Y-%m-%d"),
            "gap_days": gap,
            "expected_date": expected.strftime("%Y-%m-%d")
        })

print(f"   พบช่องว่าง {len(missing)} จุด")
for m in missing[:10]:
    print(f"   ⚠ {m['after']} → {m['before']} (ห่าง {m['gap_days']} วัน, คาดว่า {m['expected_date']})")
if len(missing) > 10:
    print(f"   ... อีก {len(missing)-10} จุด")

# ── 2. วิเคราะห์ข้อมูลที่ขาดในแต่ละ field ───────────────
print("\n📋 วิเคราะห์ field ที่ขาด:")

def check_field(draws, field, check_fn=None):
    total = len(draws)
    has = sum(1 for d in draws if check_fn(d) if check_fn else d.get(field))
    missing = total - has
    return total, has, missing

checks = [
    ("first_prize", lambda d: d.get("first_prize") and len(str(d["first_prize"])) == 6),
    ("two_digit", lambda d: d.get("two_digit") and len(str(d["two_digit"])) == 2),
    ("three_digit_last", lambda d: d.get("three_digit_last") and len(d["three_digit_last"]) > 0),
    ("three_digit_first", lambda d: d.get("three_digit_first") and len(d["three_digit_first"]) > 0),
    ("nearby_1st", lambda d: d.get("nearby_1st") and len(d["nearby_1st"]) > 0),
    ("second_prize", lambda d: d.get("second_prize") and len(d["second_prize"]) > 0),
    ("third_prize", lambda d: d.get("third_prize") and len(d["third_prize"]) > 0),
    ("prize_4", lambda d: d.get("prize_4") and len(d["prize_4"]) > 0),
    ("prize_5", lambda d: d.get("prize_5") and len(d["prize_5"]) > 0),
]

for field, check_fn in checks:
    total, has, miss = check_field(existing, field, check_fn)
    pct = has/total*100
    status = "✅" if pct == 100 else "⚠️" if pct > 80 else "❌"
    print(f"   {status} {field}: {has}/{total} ({pct:.1f}%) — ขาด {miss}")

# ── 3. หาวันที่ three_digit_first ขาด ─────────────────────
print("\n🔎 งวดที่ three_digit_first ขาด:")
missing_3f = [d for d in existing if not d.get("three_digit_first") or len(d["three_digit_first"]) == 0]
print(f"   ขาดทั้งหมด: {len(missing_3f)} งวด")
print(f"   10 งวดแรกที่ขาด:")
for d in missing_3f[:10]:
    print(f"     {d['draw_date']}: 1st={d.get('first_prize')}, 3last={d.get('three_digit_last')}, 3first={d.get('three_digit_first')}")

# ── 4. สรุปข้อมูลที่ต้องไล่เก็บ ────────────────────────────
print("\n" + "="*60)
print("📝 สรุป: สิ่งที่ต้องไล่เก็บเพิ่ม")
print("="*60)
print(f"1. ข้อมูล 1990-1994: ยังไม่มีเลย (myhora เริ่มที่ 1995)")
print(f"2. three_digit_first: ขาด {len(missing_3f)} งวด (ต้อง scrape ใหม่)")
print(f"3. งวดที่หาย: {len(missing} จุด (อาจมีงวดที่ myhora ไม่ได้แสดง)")
print(f"4. prize_4/prize_5: ต้องตรวจสอบว่า scrape มาครบไหม")

# Save analysis
analysis = {
    "timestamp": datetime.now().isoformat(),
    "total_draws": len(existing),
    "date_range": f"{existing[0]['draw_date']} → {existing[-1]['draw_date']}",
    "field_completeness": {},
    "missing_3f_count": len(missing_3f),
    "missing_3f_dates": [d["draw_date"] for d in missing_3f],
    "date_gaps": missing,
}

for field, check_fn in checks:
    total, has, miss = check_field(existing, field, check_fn)
    analysis["field_completeness"][field] = {"has": has, "missing": miss, "pct": round(has/total*100, 1)}

with open(os.path.join(OUTPUT_DIR, "data_audit.json"), "w", encoding="utf-8") as f:
    json.dump(analysis, f, ensure_ascii=False, indent=2)

print(f"\n💾 บันทึกผลวิเคราะห์: {os.path.join(OUTPUT_DIR, 'data_audit.json')}")
