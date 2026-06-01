#!/usr/bin/env python3
"""
Scrape ข้อมูลหวย myhora.com ย้อนหลัง — parse ทุกรางวัลที่มี
- ปี 2002+: มีรางวัลครบ (p1, p2, p3, p4, p5, nearby, front3, last3, last2)
- ปี ก่อน 2002: มีบางส่วน (p1, last3, last2)
"""
import re, json, time, random, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'th-TH,th;q=0.9',
}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.read().decode('utf-8', errors='replace')
    except:
        return None

def parse_full(html, date_str):
    """Parse ทุกรางวัลที่หน้าเว็บมี"""
    if not html:
        return None
    
    result = {'draw_date': date_str}
    lotdc = re.findall(r"class='lot-dc lotto-fxl py-20'[^>]*>([^<]*)</div>", html)

    # --- รางวัลที่ 1 ---
    m1 = re.search(r'รางวัลที่ 1 \((\d{6})\)', html)
    m2 = re.search(r'รางวัลที่หนึ่ง[^0-9]*?(\d{6})', html, re.DOTALL)
    if m1:
        result['first_prize'] = m1.group(1)
    elif m2:
        result['first_prize'] = m2.group(1)
    elif lotdc and lotdc[0].strip():
        result['first_prize'] = lotdc[0].strip()
    else:
        result['first_prize'] = ''

    # --- เลขท้าย 2 ---
    m = re.search(r'เลขท้าย 2 ตัว\((\d+)\)', html)
    result['last_2'] = m.group(1) if m else (lotdc[3].strip() if len(lotdc) > 3 else '')

    # --- เลขท้าย 3 ---
    m = re.search(r'เลขท้าย 3 ตัว\((\d+)\s*&nbsp;\s*(\d+)\s*&nbsp;\s*(\d+)\s*&nbsp;\s*(\d+)', html)
    if m:
        result['last_3'] = [m.group(1), m.group(2), m.group(3), m.group(4)]
    else:
        m2 = re.search(r'เลขท้าย 3 ตัว\((\d+)\s*&nbsp;\s*(\d+)', html)
        if m2:
            result['last_3'] = [m2.group(1), m2.group(2)]
        elif len(lotdc) > 2:
            result['last_3'] = re.findall(r'\d{3}', lotdc[2])[:4]
        else:
            result['last_3'] = []

    # --- รางวัลข้างเคียง ---
    nearby = re.search(r'รางวัลข้างเคียง(.*?)(?=รางวัลที่ 2|เลขหน้า|$)', html, re.DOTALL)
    if nearby:
        result['nearby_1st'] = re.findall(r'\b(\d{6})\b', nearby.group(1))[:2]
    elif len(lotdc) > 5:
        result['nearby_1st'] = [x.strip() for x in lotdc[4:6] if x.strip()]
    else:
        result['nearby_1st'] = []

    # --- รางวัลที่ 2 ---
    p2 = re.search(r'รางวัลที่ 2(.*?)(?=รางวัลที่ 3)', html, re.DOTALL)
    result['prize_2'] = re.findall(r'\b(\d{6})\b', p2.group(1))[:5] if p2 else []

    # --- รางวัลที่ 3 ---
    p3 = re.search(r'รางวัลที่ 3(.*?)(?=รางวัลที่ 4)', html, re.DOTALL)
    result['prize_3'] = re.findall(r'\b(\d{6})\b', p3.group(1))[:10] if p3 else []

    # --- รางวัลที่ 4 ---
    p4 = re.search(r'รางวัลที่ 4(.*?)(?=รางวัลที่ 5)', html, re.DOTALL)
    result['prize_4'] = re.findall(r'\b(\d{6})\b', p4.group(1))[:50] if p4 else []

    # --- รางวัลที่ 5 ---
    p5 = re.search(r'รางวัลที่ 5(.*?)(?=สามตรง|เลขหน้า|$)', html, re.DOTALL)
    result['prize_5'] = re.findall(r'\b(\d{6})\b', p5.group(1))[:100] if p5 else []

    # --- เลขหน้า 3 (meta) ---
    m = re.search(r'3 ตัวหน้า\((\d+)\s*&nbsp;\s*(\d+)', html)
    if m:
        result['front_3'] = [m.group(1), m.group(2)]
    else:
        result['front_3'] = []

    return result

def date_to_url(date_str):
    y, m, d = date_str.split('-')
    by = int(y) + 543
    return f"https://myhora.com/lottery/result-{int(d):02d}-{int(m):02d}-{by}.aspx"

def main():
    print("=" * 60)
    print("  Thai Lottery Scraper — myhora.com (ย้อนหลังถึง 1990)")
    print("=" * 60)

    # โหลดข้อมูลเก่า
    out_file = '/tmp/myhora-lotto/all_prizes.json'
    with open(out_file) as f:
        existing = json.load(f)

    # index by date
    existing_map = {d['draw_date']: d for d in existing}
    print(f"มีข้อมูลเก่า: {len(existing_map)} งวด")

    # สร้างรายการวันที่ (1990-2005, เฉพาะที่ยัง scrape ไม่ครบ)
    dates = []
    for y in range(1990, 2006):
        for m in range(1, 13):
            for d in [1, 16]:
                try:
                    dates.append(date(y, m, d).strftime('%Y-%m-%d'))
                except:
                    pass

    # ข้างที่ scrape ได้ first_prize แล้ว แต่ขาดรางวัลอื่น
    need_update = []
    for d in dates:
        if d in existing_map:
            old = existing_map[d]
            # ถ้ามี first_prize แต่ยังไม่มี prize_2 หรือ prize_5
            if old.get('first_prize') and (not old.get('prize_2') and not old.get('prize_5')):
                need_update.append(d)

    print(f"ต้อง re-scrape (มี p1 แต่ขาด p2-p5): {len(need_update)} งวด")

    if not need_update:
        print("ไม่มีข้อมูลต้อง re-scrape")
        # ตรวจสอบว่ามีข้อมูลก่อน 1998 ไหม
        before_1998 = [d for d in dates if d < '1998-01-01' and d not in existing_map]
        if before_1998:
            print(f"ยังขาดข้อมูลก่อน 1998: {len(before_1998)} งวด")
            need_update = before_1998
        else:
            print("ข้อมูลครบถ้วนแล้ว!")
            return

    # Re-scrape
    ok = fail = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {}
        for date_str in need_update:
            url = date_to_url(date_str)
            futures[ex.submit(fetch, url)] = date_str

        done = 0
        for fut in as_completed(futures):
            done += 1
            date_str = futures[fut]
            html = fut.result()
            data = parse_full(html, date_str) if html else None

            if data and data.get('first_prize'):
                existing_map[date_str] = data
                ok += 1
            else:
                fail += 1

            if done % 50 == 0:
                print(f"  {done}/{len(need_update)} — ok={ok}, fail={fail}")

    # Save
    all_data = sorted(existing_map.values(), key=lambda x: x['draw_date'])
    with open(out_file, 'w') as f:
        json.dump(all_data, f, ensure_ascii=False)

    print(f"\n=== เสร็จ ===")
    print(f"Re-scrape สำเร็จ: {ok}")
    print(f"ล้มเหลว: {fail}")
    print(f"รวมทั้งหมด: {len(all_data)} งวด")
    print(f"  ตั้งแต่: {all_data[0]['draw_date']}")
    print(f"  ถึง: {all_data[-1]['draw_date']}")

    # สรุปความครบ
    has_p5 = sum(1 for d in all_data if d.get('prize_5'))
    has_p2 = sum(1 for d in all_data if d.get('prize_2'))
    has_nearby = sum(1 for d in all_data if d.get('nearby_1st'))
    print(f"\nความครบ:")
    print(f"  prize_2: {has_p2}/{len(all_data)}")
    print(f"  prize_5: {has_p5}/{len(all_data)}")
    print(f"  nearby: {has_nearby}/{len(all_data)}")

if __name__ == '__main__':
    main()
