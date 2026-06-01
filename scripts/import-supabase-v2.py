#!/usr/bin/env python3
"""
Export ข้อมูลจาก all_prizes.json -> import เข้า Supabase ผ่าน REST API
ไม่ต้อง service role key ใช้ anon key ได้ (ถ้า RLS policy อนุญาต)
"""
import json, time, urllib.request, urllib.error

SUPABASE_URL = "https://jiulxmylgwaaygdytdfj.supabase.co"
# ใช้ anon key — ถ้า insert ไม่ได้เปลี่ยนเป็น service role key
ANON_KEY = "eyJhbG...uvns"

def post_batch(batch, batch_num, total_batches):
    """POST batch ข้อมูลไป Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/rpc/import_lotto_data"
    payload = json.dumps({"data_json": batch}).encode("utf-8")

    req = urllib.request.Request(
        url, data=payload,
        headers={
            "apikey": ANON_KEY,
            "Authorization": f"Bearer {ANON_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = r.read().decode()
            return True, resp
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        return False, f"HTTP {e.code}: {body}"
    except Exception as e:
        return False, str(e)

def build_row(d):
    """แปลงข้อมูลจาก all_prizes.json เป็น format ที่ Supabase ต้องการ"""
    draw_date = d.get('draw_date', '')
    if not draw_date:
        return None

    year, month, day = draw_date.split('-')
    draw_number = f"{int(year[2:])}{month}{day}"

    # first_prize
    first = d.get('first_prize', '') or ''

    # two_digit
    two = d.get('last_2', '') or ''

    # nearby_1st
    nearby = d.get('nearby_1st', []) or []

    # three_digit_first
    front3 = d.get('front_3', []) or []
    if not front3:
        front3 = d.get('three_digit_first', []) or []

    # three_digit_last
    last3 = d.get('last_3', []) or []
    if not last3:
        last3 = d.get('three_digit_last', []) or []

    # second_prize (myhora format = list of 5 numbers)
    p2 = d.get('prize_2', []) or []

    # third_prize
    p3 = d.get('prize_3', []) or []

    # prize_4, prize_5
    p4 = d.get('prize_4', []) or []
    p5 = d.get('prize_5', []) or []

    return {
        "draw_date": draw_date,
        "draw_number": draw_number,
        "first_prize": first,
        "two_digit": two,
        "nearby_1st": nearby,
        "three_digit_first": front3,
        "three_digit_last": last3,
        "second_prize": p2,
        "third_prize": p3,
        "prize_4": p4,
        "prize_5": p5,
    }

def main():
    print("=" * 60)
    print("  LottoAI Import: all_prizes.json -> Supabase")
    print("=" * 60)

    # โหลดข้อมูล
    print("\n1. โหลดข้อมูล...")
    with open('/tmp/myhora-lotto/all_prizes.json') as f:
        data = json.load(f)
    print(f"   มีข้อมูล {len(data)} งวด")

    # แปลงเป็น rows
    print("\n2. เตรียมข้อมูล...")
    rows = []
    skip_count = 0
    for d in data:
        row = build_row(d)
        if row and row.get('first_prize'):
            rows.append(row)
        else:
            skip_count += 1

    print(f"   พร้อม import: {len(rows)} งวด")
    print(f"   ข้าม (ไม่มี first_prize): {skip_count} งวด")

    if not rows:
        print("   ❌ ไม่มีข้อมูลสำหรับ import")
        return

    # Import เป็น batch ละ 25
    batch_size = 25
    batches = [rows[i:i+batch_size] for i in range(0, len(rows), batch_size)]
    total_batches = len(batches)
    success_total = 0
    fail_total = 0
    errors = []

    print(f"\n3. Import เป็น {total_batches} batches (ละ {batch_size} งวด)...")
    print(f"   URL: {SUPABASE_URL}/rest/v1/rpc/import_lotto_data")
    print()

    for i, batch in enumerate(batches):
        ok, resp = post_batch(batch, i + 1, total_batches)
        if ok:
            success_total += len(batch)
            status = "✅"
        else:
            fail_total += len(batch)
            errors.append(f"Batch {i+1}: {resp[:100]}")
            status = "❌"

        progress = (i + 1) / total_batches * 100
        print(f"   {status} Batch {i+1:3d}/{total_batches} ({progress:5.1f}%) | ok={success_total}, fail={fail_total}")

        time.sleep(0.15)

    # สรุป
    print(f"\n{'='*60}")
    print(f"  ผล Import")
    print(f"{'='*60}")
    print(f"  สำเร็จ: {success_total}/{len(rows)}")
    print(f"  ล้มเหลว: {fail_total}")

    if errors:
        print(f"\n  ตัวอย่าง Error:")
        for e in errors[:5]:
            print(f"    {e}")

    # ตรวจสอบผล
    print(f"\n4. ตรวจสอบข้อมูลใน Supabase...")
    try:
        url = f"{SUPABASE_URL}/rest/v1/lotto_results?select=draw_date&order=draw_date.desc&limit=3"
        req = urllib.request.Request(url, headers={"apikey": ANON_KEY, "Authorization": f"Bearer {ANON_KEY}"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            if d:
                print(f"   งวดล่าสุด: {d[0]['draw_date']}")
                print(f"   ทั้งหมด 3 งวดล่าสุด: {[x['draw_date'] for x in d]}")
    except Exception as e:
        print(f"   ตรวจสอบไม่สำเร็จ: {e}")

    print(f"\n✅ เสร็จสิ้น!")

if __name__ == '__main__':
    main()
