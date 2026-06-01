#!/usr/bin/env python3
"""
Export ข้อมูลจาก all_prizes.json -> import เข้า Supabase ผ่าน RPC function
ก่อนรัน: รัน import-script.sql ใน Supabase SQL Editor ก่อน
"""
import json, time, urllib.request, urllib.error

SUPABASE_URL = "https://jiulxmylgwaaygdytdfj.supabase.co"
ANON_KEY = "eyJhbG...uvns"  # เปลี่ยนเป็น anon key ที่ถูกต้อง

def post_batch(batch):
    url = f"{SUPABASE_URL}/rest/v1/rpc/import_lotto_data"
    payload = json.dumps({"data_json": batch}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={
        "apikey": ANON_KEY, "Authorization": f"Bearer {ANON_KEY}",
        "Content-Type": "application/json",
    }, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return True, r.read().decode()
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.read().decode()[:300]}"
    except Exception as e:
        return False, str(e)

def build_row(d):
    draw_date = d.get('draw_date', '')
    if not draw_date:
        return None
    y, m, date = draw_date.split('-')
    return {
        "draw_date": draw_date,
        "draw_number": f"{int(y[2:])}{m}{date}",
        "first_prize": d.get('first_prize', '') or '',
        "two_digit": d.get('last_2', '') or '',
        "nearby_1st": d.get('nearby_1st', []) or [],
        "three_digit_first": (d.get('front_3', []) or d.get('three_digit_first', [])) or [],
        "three_digit_last": (d.get('last_3', []) or d.get('three_digit_last', [])) or [],
        "second_prize": d.get('prize_2', []) or [],
        "third_prize": d.get('prize_3', []) or [],
        "prize_4": d.get('prize_4', []) or [],
        "prize_5": d.get('prize_5', []) or [],
    }

def main():
    print("LottoAI Import: all_prizes.json -> Supabase")
    print("=" * 50)

    with open('/tmp/myhora-lotto/all_prizes.json') as f:
        data = json.load(f)
    print(f"โหลด {len(data)} งวด")

    rows = [r for r in (build_row(d) for d in data) if r and r.get('first_prize')]
    print(f"พร้อม import: {len(rows)} งวด")

    batch_size = 25
    batches = [rows[i:i+batch_size] for i in range(0, len(rows), batch_size)]
    ok_total = fail_total = 0
    errors = []

    for i, batch in enumerate(batches):
        ok, resp = post_batch(batch)
        if ok:
            ok_total += len(batch)
        else:
            fail_total += len(batch)
            errors.append(f"Batch {i+1}: {resp[:120]}")
        print(f"  Batch {i+1}/{len(batches)} | ok={ok_total} fail={fail_total}")
        time.sleep(0.1)

    print(f"\nสรุป: ok={ok_total}, fail={fail_total}")
    if errors:
        print("Errors:", errors[:3])

    # ตรวจสอบผล
    try:
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/lotto_results?select=draw_date&order=draw_date.desc&limit=3",
            headers={"apikey": ANON_KEY}
        )
        with urllib.request.urlopen(req) as r:
            d = json.loads(r.read())
            print(f"ตรวจสอบ: งวดล่าสุด = {d[0]['draw_date'] if d else 'N/A'}")        
    except Exception as e:
        print(f"ตรวจสอบไม่ได้: {e}")

if __name__ == '__main__':
    main()
