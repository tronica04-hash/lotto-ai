#!/usr/bin/env python3
"""
LottoAI — Universal Scraper v2 สำหรับ myhora.com
Parse ข้อมูลจาก HTML structure จริง
รองรับทุกช่วงปี 1990-2026
"""
import re, json, time, urllib.request, os
from datetime import date

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'th-TH,th;q=0.9,en;q=0.8',
}

DATA_DIR = r"D:\lotto-ai\ml-models\data"

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode('utf-8', errors='replace')
    except:
        return None

def parse_draw(html, date_str):
    """Parse ข้อมูลหวยจาก HTML"""
    if not html:
        return None
    
    result = {'draw_date': date_str}
    
    # Find main_lotto section
    main = re.search(r'id="main_lotto">(.*?)(?=<div class="cls"></div>\s*<div id="p_result2"|<div id="p_share_image2"|$)', html, re.DOTALL)
    if not main:
        return None
    
    section = main.group(1)
    
    # Get all lot-dc values
    dcs = re.findall(r"<div class='lot-dc[^']*'[^>]*>(.*?)</div>", section, re.DOTALL)
    # Clean values
    dcs = [re.sub(r'<[^>]+>', '', d).strip() for d in dcs]
    dcs = [d for d in dcs if d]  # Remove empty
    
    if not dcs:
        return None
    
    # ── Parse based on number of values ─────────────────────
    # Pattern: [first_prize, three_digit_first (optional), three_digit_last, two_digit, nearby1, nearby2, prize2..., prize3..., prize4..., prize5...]
    
    idx = 0
    
    # 1. first_prize (6 or 7 digits)
    if idx < len(dcs):
        fp = dcs[idx]
        fp_clean = re.sub(r'&nbsp;', '', fp).strip()
        if re.match(r'^\d{6,7}$', fp_clean):
            result['first_prize'] = fp_clean[-6:]  # Take last 6 digits
            idx += 1
        else:
            result['first_prize'] = ''
    
    # 2. Check if next is three_digit_first or three_digit_last
    # three_digit_first: 2-3 digits separated by space/nbsp
    # three_digit_last: 3-4 digits separated by space/nbsp
    three_digit_first = []
    three_digit_last = []
    two_digit = ''
    
    if idx < len(dcs):
        val = dcs[idx]
        # Check if this looks like three_digit_first (2-3 numbers of 3 digits each)
        nums = re.findall(r'\d{3}', val)
        # Check the header to see if this is เลขหน้า or เลขท้าย
        # Look at the section header
        header_match = re.search(r"<u>เลขหน้า 3 ตัว</u>.*?<div class='lot-dc[^']*'[^>]*>(.*?)</div>", section, re.DOTALL)
        if header_match:
            header_val = re.sub(r'<[^>]+>', '', header_match.group(1)).strip()
            three_digit_first = re.findall(r'\d{3}', header_val)
            idx += 1
        
        # three_digit_last
        if idx < len(dcs):
            val = dcs[idx]
            nums = re.findall(r'\d{3}', val)
            if len(nums) >= 2:
                three_digit_last = nums
                idx += 1
        
        # two_digit
        if idx < len(dcs):
            val = re.sub(r'&nbsp;', '', dcs[idx]).strip()
            if re.match(r'^\d{2}$', val):
                two_digit = val
                idx += 1
    
    result['three_digit_first'] = three_digit_first
    result['three_digit_last'] = three_digit_last
    result['two_digit'] = two_digit
    
    # 3. nearby_1st (2 values of 6 digits each)
    nearby = []
    while idx < len(dcs) and len(nearby) < 2:
        val = re.sub(r'&nbsp;', '', dcs[idx]).strip()
        if re.match(r'^\d{6}$', val):
            nearby.append(val)
        idx += 1
    result['nearby_1st'] = nearby
    
    # 4. Prize 2-5 (remaining 6-digit numbers)
    # Prize 2: 5 numbers, Prize 3: 10 numbers, Prize 4: 50 numbers, Prize 5: 100 numbers
    remaining = []
    while idx < len(dcs):
        val = re.sub(r'&nbsp;', '', dcs[idx]).strip()
        if re.match(r'^\d{6}$', val):
            remaining.append(val)
        idx += 1
    
    # Split remaining into prizes
    result['second_prize'] = remaining[:5]
    result['third_prize'] = remaining[5:15]
    result['prize_4'] = remaining[15:65]
    result['prize_5'] = remaining[65:165]
    
    return result

def date_to_url(draw_date):
    y, m, d = draw_date.split('-')
    by = int(y) + 543
    return f"https://myhora.com/lottery/result-{int(d):02d}-{int(m):02d}-{by}.aspx"

def generate_dates(start_year, end_year):
    dates = []
    for y in range(start_year, end_year + 1):
        for m in range(1, 13):
            for d in [1, 16]:
                try:
                    dt = date(y, m, d)
                    if dt <= date.today():
                        dates.append(dt.strftime('%Y-%m-%d'))
                except:
                    pass
    return dates

def main():
    print("=" * 60)
    print("  LottoAI Universal Scraper v2")
    print("=" * 60)
    
    # ── 1. Scrape 1990-1994 ──────────────────────────────────
    print("\n[Phase 1] Scrape ข้อมูล 1990-1994...")
    dates_1990 = generate_dates(1990, 1994)
    results_1990 = []
    
    for i, draw_date in enumerate(dates_1990):
        url = date_to_url(draw_date)
        html = fetch_url(url)
        if html:
            data = parse_draw(html, draw_date)
            if data and data.get('first_prize'):
                results_1990.append(data)
        
        if (i + 1) % 10 == 0 or i == len(dates_1990) - 1:
            print(f"  [{i+1}/{len(dates_1990)}] ok={len(results_1990)}", flush=True)
        
        if (i + 1) % 10 == 0:
            time.sleep(1.5)
    
    print(f"  1990-1994: {len(results_1990)} งวด")
    
    # ── 2. Fill gaps in existing data ─────────────────────────
    print("\n[Phase 2] เติมข้อมูลที่ขาดใน 1995-2026...")
    
    scraped_file = os.path.join(DATA_DIR, "scraped_all.json")
    with open(scraped_file, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    existing_dates = {d['draw_date']: i for i, d in enumerate(existing)}
    
    # Find draws missing key fields
    missing = []
    for d in existing:
        needs_update = (
            not d.get('three_digit_first') or len(d['three_digit_first']) == 0 or
            not d.get('nearby_1st') or len(d['nearby_1st']) == 0 or
            not d.get('prize_4') or len(d['prize_4']) == 0 or
            not d.get('prize_5') or len(d['prize_5']) == 0
        )
        if needs_update:
            missing.append(d['draw_date'])
    
    print(f"  งวดที่ต้องอัปเดต: {len(missing)}")
    
    updated = 0
    for i, draw_date in enumerate(missing):
        url = date_to_url(draw_date)
        html = fetch_url(url)
        if html:
            data = parse_draw(html, draw_date)
            if data:
                idx = existing_dates[draw_date]
                for field in ['three_digit_first', 'nearby_1st', 'second_prize', 
                              'third_prize', 'prize_4', 'prize_5', 'two_digit']:
                    if data.get(field):
                        old = existing[idx].get(field)
                        if not old or (isinstance(old, list) and len(old) == 0) or (isinstance(old, str) and not old):
                            existing[idx][field] = data[field]
                            updated += 1
                        elif isinstance(old, list) and isinstance(data[field], list):
                            if len(data[field]) > len(old):
                                existing[idx][field] = data[field]
                                updated += 1
        
        if (i + 1) % 20 == 0 or i == len(missing) - 1:
            print(f"  [{i+1}/{len(missing)}] updated={updated}", flush=True)
        
        if (i + 1) % 10 == 0:
            time.sleep(1.5)
    
    # ── 3. Merge & Save ──────────────────────────────────────
    print("\n[Phase 3] รวมข้อมูล & บันทึก...")
    
    all_data = results_1990 + existing
    all_data.sort(key=lambda d: d['draw_date'])
    
    # Backup
    backup_file = scraped_file.replace('.json', '_backup3.json')
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    with open(scraped_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    # ── Summary ──────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  ผลการ Scrape")
    print(f"{'='*60}")
    print(f"  ข้อมูล 1990-1994 ที่เพิ่ม: {len(results_1990)} งวด")
    print(f"  field ที่อัปเดต: {updated}")
    print(f"  ข้อมูลรวมทั้งหมด: {len(all_data)} งวด")
    
    # Completeness
    print(f"\n  ความครบของข้อมูล:")
    checks = [
        ('first_prize', lambda d: d.get('first_prize') and len(d['first_prize']) == 6),
        ('two_digit', lambda d: d.get('two_digit') and len(d['two_digit']) == 2),
        ('three_digit_last', lambda d: d.get('three_digit_last') and len(d['three_digit_last']) > 0),
        ('three_digit_first', lambda d: d.get('three_digit_first') and len(d['three_digit_first']) > 0),
        ('nearby_1st', lambda d: d.get('nearby_1st') and len(d['nearby_1st']) > 0),
        ('second_prize', lambda d: d.get('second_prize') and len(d['second_prize']) > 0),
        ('third_prize', lambda d: d.get('third_prize') and len(d['third_prize']) > 0),
        ('prize_4', lambda d: d.get('prize_4') and len(d['prize_4']) > 0),
        ('prize_5', lambda d: d.get('prize_5') and len(d['prize_5']) > 0),
    ]
    for field, check_fn in checks:
        has = sum(1 for d in all_data if check_fn(d))
        pct = has/len(all_data)*100
        status = "✅" if pct >= 95 else "⚠️" if pct > 70 else "❌"
        print(f"    {status} {field}: {has}/{len(all_data)} ({pct:.1f}%)")
    
    # Sample
    if results_1990:
        print(f"\n  ตัวอย่าง 1990-1994:")
        for d in results_1990[:3]:
            print(f"    {d['draw_date']}: 1st={d['first_prize']}, 2d={d['two_digit']}, 3last={d['three_digit_last']}")

if __name__ == '__main__':
    main()
