#!/usr/bin/env python3
"""
Scrape ข้อมูลหวยจาก myhora.com ย้อนหลัง — ไล่ปีจาก 2005 ลงไปเรื่อยๆ
เพื่อเติมข้อมูลก่อน 2006 ที่ยังขาดหาย
"""
import re, json, os, time, random, sys
import urllib.request, urllib.error

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'th-TH,th;q=0.9',
}

def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.read().decode('utf-8', errors='replace')
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
        except Exception:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
    return None

def date_to_url(date_str):
    from datetime import datetime
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    by = dt.year + 543
    return f"https://myhora.com/lottery/result-{dt.day:02d}-{dt.month:02d}-{by}.aspx"

def parse_page(html, date_str):
    if not html:
        return None
    result = {'draw_date': date_str}

    # รางวัลที่ 1: ลองหลาย pattern
    m1 = re.search(r'รางวัลที่ 1 \((\d{6})\)', html)
    m2 = re.search(r'รางวัลที่หนึ่ง[^0-9]*?(\d{6})', html, re.DOTALL)
    lotdc = re.findall(r"class='lot-dc lotto-fxl py-20'[^>]*>([^<]*)</div>", html)

    if m1:
        result['first_prize'] = m1.group(1)
    elif m2:
        result['first_prize'] = m2.group(1)
    elif lotdc and lotdc[0].strip():
        result['first_prize'] = lotdc[0].strip()
    else:
        result['first_prize'] = ''

    # เลขท้าย 2
    m2d = re.search(r'เลขท้าย 2 ตัว\((\d+)\)', html)
    result['last_2'] = m2d.group(1) if m2d else (lotdc[3].strip() if len(lotdc) > 3 else '')

    # เลขท้าย 3
    m3d = re.search(r'เลขท้าย 3 ตัว\((\d+)\s*&nbsp;\s*(\d+)', html)
    if m3d:
        result['last_3'] = [m3d.group(1), m3d.group(2)]
    elif len(lotdc) > 2:
        nums = re.findall(r'\d{3}', lotdc[2])
        result['last_3'] = nums[:2]
    else:
        result['last_3'] = []

    # ข้างเคียง
    nearby = re.search(r'รางวัลข้างเคียง(.*?)(?=รางวัลที่ 2|เลขหน้า)', html, re.DOTALL)
    if nearby:
        result['nearby_1st'] = re.findall(r'\b(\d{6})\b', nearby.group(1))[:2]
    elif len(lotdc) > 5:
        result['nearby_1st'] = [x.strip() for x in lotdc[4:6] if x.strip()]
    else:
        result['nearby_1st'] = []

    # รางวัลที่ 2-5
    for i, key in [(2, 'prize_2'), (3, 'prize_3'), (4, 'prize_4'), (5, 'prize_5')]:
        p = re.search(rf'รางวัลที่ {i}(.*?)(?=รางวัลที่ {i+1}|$)', html, re.DOTALL)
        lim = {2: 5, 3: 10, 4: 50, 5: 100}[i]
        result[key] = re.findall(r'\b(\d{6})\b', p.group(1))[:lim] if p else []

    return result

def generate_dates(start_year, end_year=2006):
    from datetime import date
    dates = []
    for y in range(start_year, end_year + 1):
        for m in range(1, 13):
            for d in [1, 16]:
                try:
                    dt = date(y, m, d)
                    dates.append(dt.strftime('%Y-%m-%d'))
                except:
                    pass
    return sorted(set(dates))

def main():
    print("=" * 60)
    print("  Thai Lottery Scraper — myhora.com (ย้อนหลัง)")
    print("=" * 60)

    # โหลดข้อมูลเก่า
    out_file = '/tmp/myhora-lotto/all_prizes.json'
    with open(out_file) as f:
        existing = json.load(f)

    existing_dates = {d['draw_date'] for d in existing}
    print(f"มีข้อมูลเก่า: {len(existing_dates)} งวด")
    print(f"  ตั้งแต่: {min(existing_dates)}")
    print(f"  ถึง: {max(existing_dates)}")

    # สร้างรายการวันที่ที่ต้อง scrape (ก่อน 2006)
    dates = generate_dates(1990, 2005)  # ลองลงไปถึง 1990
    pending = [d for d in dates if d not in existing_dates]
    print(f"\nต้อง scrape เพิ่ม: {len(pending)} งวด (1990-2005)")
    print(f"  ตั้งแต่: {pending[0] if pending else '?'}")

    if not pending:
        print("ไม่มีข้อมูลใหม่ต้อง scrape")
        return

    ok = fail = 0
    all_data = list(existing)
    checkpoint_interval = 50

    for i, date_str in enumerate(pending):
        url = date_to_url(date_str)
        html = fetch(url)
        data = parse_page(html, date_str) if html else None

        if data and data.get('first_prize'):
            all_data.append(data)
            ok += 1
        else:
            fail += 1

        # Save checkpoint
        if (i + 1) % checkpoint_interval == 0:
            all_data_sorted = sorted(all_data, key=lambda x: x['draw_date'])
            with open(out_file, 'w') as f:
                json.dump(all_data_sorted, f, ensure_ascii=False)
            print(f"  {i+1}/{len(pending)} — ok={ok}, fail={fail} [checkpoint saved]")

        time.sleep(random.uniform(0.3, 0.7))

    # Final save
    all_data_sorted = sorted(all_data, key=lambda x: x['draw_date'])
    with open(out_file, 'w') as f:
        json.dump(all_data_sorted, f, ensure_ascii=False)

    new_count = len(all_data_sorted) - len(existing_dates)
    print(f"\n=== เสร็จ ===")
    print(f"ใหม่: {ok} งวด")
    print(f"ล้มเหลว: {fail}")
    print(f"รวมทั้งหมด: {len(all_data_sorted)} งวด")
    print(f"  ตั้งแต่: {all_data_sorted[0]['draw_date']}")
    print(f"  ถึง: {all_data_sorted[-1]['draw_date']}")

if __name__ == '__main__':
    main()
