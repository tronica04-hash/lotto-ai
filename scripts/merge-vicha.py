#!/usr/bin/env python3
"""
Merge myhora scrape + vicha-w/thai-lotto-archive (concurrent download)
"""
import json, os, re, urllib.request, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

GITHUB_BASE = "https://raw.githubusercontent.com/vicha-w/thai-lotto-archive/master/lottonumbers"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode('utf-8', errors='replace')
    except:
        return None

def parse_vicha_file(text):
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    if not lines:
        return None
    result = {}
    for line in lines:
        if line.startswith('http'):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        key = parts[0].upper()
        vals = parts[1:]
        if key == 'FIRST':
            result['first_prize'] = vals[0] if vals else ''
        elif key == 'THREE_FIRST':
            result['front_3'] = vals[:2]
        elif key == 'THREE_LAST':
            result['last_3'] = vals[:2]
        elif key == 'THREE':
            nums = [v for v in vals if len(v) == 3]
            result['last_3'] = nums[:2]
            if 'front_3' not in result:
                result['front_3'] = []
        elif key == 'TWO':
            result['last_2'] = vals[0] if vals else ''
        elif key == 'NEAR_FIRST':
            result['nearby_1st'] = vals[:2]
        elif key == 'SECOND':
            result['prize_2'] = [v for v in vals if len(v) == 6][:5]
        elif key == 'THIRD':
            result['prize_3'] = [v for v in vals if len(v) == 6][:10]
        elif key == 'FOURTH':
            result['prize_4'] = [v for v in vals if len(v) == 6][:50]
        elif key == 'FIFTH':
            result['prize_5'] = [v for v in vals if len(v) == 6][:100]
    return result if result.get('first_prize') else None

def download_one(date_str):
    url = f"{GITHUB_BASE}/{date_str}.txt"
    text = fetch_url(url)
    if text:
        parsed = parse_vicha_file(text)
        if parsed:
            return date_str, parsed
    return None, None

def main():
    myhora_file = '/tmp/myhora-lotto/all_phores.json'
    # ใช้ชื่อไฟล์ที่ถูกต้อง
    myhora_file = '/tmp/myhora-lotto/all_prizes.json'
    with open(myhora_file) as f:
        myhora_data = json.load(f)

    print(f"myhora scrape: {len(myhora_data)} งวด")

    # สร้าง list วันที่
    dates = []
    for y in range(2006, 2027):
        for m in range(1, 13):
            for d in [1, 16]:
                try:
                    dt = date(y, m, d)
                    if dt <= date.today():
                        dates.append(dt.strftime('%Y-%m-%d'))
                except:
                    pass

    print(f"กำลัง download {len(dates)} ไฟล์จาก GitHub (concurrent)...")
    vicha = {}
    with ThreadPoolExecutor(max_workers=20) as ex:
        futures = {ex.submit(download_one, d): d for d in dates}
        done = 0
        for fut in as_completed(futures):
            date_str, parsed = fut.result()
            if parsed:
                vicha[date_str] = parsed
            done += 1
            if done % 100 == 0:
                print(f"  {done}/{len(dates)} — ได้ {len(vicha)} ไฟล์")

    print(f"download สำเร็จ: {len(vicha)} ไฟล์")

    # Merge
    merged = {}
    for d in myhora_data:
        merged[d['draw_date']] = d.copy()

    vicha_updated = 0
    vicha_new = 0

    for date_str, parsed in vicha.items():
        if date_str in merged:
            existing = merged[date_str]
            updated = False
            if not existing.get('front_3') and parsed.get('front_3'):
                existing['front_3'] = parsed['front_3']
                updated = True
            if not existing.get('last_3') and parsed.get('last_3'):
                existing['last_3'] = parsed['last_3']
                updated = True
            if not existing.get('last_2') and parsed.get('last_2'):
                existing['last_2'] = parsed['last_2']
                updated = True
            if not existing.get('nearby_1st') and parsed.get('nearby_1st'):
                existing['nearby_1st'] = parsed['nearby_1st']
                updated = True
            if len(existing.get('prize_2', [])) < 5 and len(parsed.get('prize_2', [])) >= 5:
                existing['prize_2'] = parsed['prize_2']
                updated = True
            if len(existing.get('prize_3', [])) < 10 and len(parsed.get('prize_3', [])) >= 10:
                existing['prize_3'] = parsed['prize_3']
                updated = True
            if len(existing.get('prize_4', [])) < 50 and len(parsed.get('prize_4', [])) >= 50:
                existing['prize_4'] = parsed['prize_4']
                updated = True
            if len(existing.get('prize_5', [])) < 100 and len(parsed.get('prize_5', [])) >= 100:
                existing['prize_5'] = parsed['prize_5']
                updated = True
            if updated:
                vicha_updated += 1
        else:
            parsed['draw_date'] = date_str
            merged[date_str] = parsed
            vicha_new += 1

    result = sorted(merged.values(), key=lambda x: x['draw_date'])

    with open(myhora_file, 'w') as f:
        json.dump(result, f, ensure_ascii=False)

    # สรุป
    n = len(result)
    p1 = sum(1 for d in result if d.get('first_prize'))
    t3f = sum(1 for d in result if d.get('front_3'))
    l3f = sum(1 for d in result if d.get('last_3'))
    l2f = sum(1 for d in result if d.get('last_2'))
    p2f = sum(1 for d in result if len(d.get('prize_2', [])) == 5)
    p3f = sum(1 for d in result if len(d.get('prize_3', [])) == 10)
    p4f = sum(1 for d in result if len(d.get('prize_4', [])) == 50)
    p5f = sum(1 for d in result if len(d.get('prize_5', [])) == 100)

    print(f"\n=== เสร็จสิ้น ===")
    print(f"เพิ่มจาก vicha-w:  update={vicha_updated}, new={vicha_new}")
    print(f"รวมทั้งหมด: {n} งวด ({result[0]['draw_date']} → {result[-1]['draw_date']})")
    print(f"\nความครบ:")
    print(f"  รางวัลที่1:  {p1}/{n}")
    print(f"  เลขหน้า3:    {t3f}/{n}")
    print(f"  เลขท้าย3:    {l3f}/{n}")
    print(f"  เลขท้าย2:    {l2f}/{n}")
    print(f"  รางวัลที่2:  {p2f}/{n}")
    print(f"  รางวัลที่3:  {p3f}/{n}")
    print(f"  รางวัลที่4:  {p4f}/{n}")
    print(f"  รางวัลที่5:  {p5f}/{n}")

if __name__ == '__main__':
    main()
