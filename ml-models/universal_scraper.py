#!/usr/bin/env python3
"""
LottoAI — Universal Scraper สำหรับ myhora.com
Parse ข้อมูลจาก HTML structure จริง (lot-dc lotto-fxl)
รองรับทั้ง 1990-1994 (7 หลัก) และ 1995+ (6 หลัก)
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

def parse_meta_description(html):
    """Extract lottery data from meta description tag"""
    meta = re.search(r'<meta name="description" content="([^"]+)"', html)
    if not meta:
        return {}
    
    desc = meta.group(1)
    result = {}
    
    # รางวัลที่ 1
    m = re.search(r'รางวัลที่ 1 \((\d{6,7})\)', desc)
    if not m:
        m = re.search(r'รางวัลที่หนึ่ง \((\d{6,7})\)', desc)
    if m:
        fp = m.group(1)
        result['first_prize'] = fp[-6:] if len(fp) == 7 else fp
    
    # เลขท้าย 2 ตัว
    m = re.search(r'เลขท้าย 2 ตัว\((\d{2})\)', desc)
    if m:
        result['two_digit'] = m.group(1)
    
    # เลขท้าย 3 ตัว
    m = re.search(r'เลขท้าย 3 ตัว\(([^)]+)\)', desc)
    if m:
        result['three_digit_last'] = re.findall(r'\d{3}', m.group(1))
    
    return result

def parse_html_structure(html):
    """Parse lottery data from HTML div structure"""
    result = {}
    
    # Find the main lottery result section
    main = re.search(r'id="main_lotto">(.*?)(?=<div class="cls"></div>\s*<div id="p_result2"|$)', html, re.DOTALL)
    if not main:
        return result
    
    section = main.group(1)
    
    # รางวัลที่ 1 — first lot-dc div
    m = re.search(r"class='lot-dc lotto-fxl[^']*'[^>]*>(\d{6,7})</div>", section)
    if m:
        fp = m.group(1)
        result['first_prize'] = fp[-6:] if len(fp) == 7 else fp
    
    # เลขท้าย 3 ตัว
    m = re.search(r"width:54%;[^>]*>(\d{3}&nbsp;[^<]*)</div>", section)
    if m:
        result['three_digit_last'] = re.findall(r'\d{3}', m.group(1))
    
    # เลขท้าย 2 ตัว
    m = re.search(r"width:18%;[^>]*>(\d{2})</div>", section)
    if m:
        result['two_digit'] = m.group(1)
    
    # เลขหน้า 3 ตัว — check if exists
    if 'เลขหน้า 3 ตัว' in html or '3 ตัวหน้า' in html:
        # Find the front 3 section
        front_section = re.search(r'เลขหน้า 3 ตัว.*?<div class=\'lot-dc[^>]*>([^<]*)</div>', html, re.DOTALL)
        if front_section:
            val = front_section.group(1).strip()
            if val:
                result['three_digit_first'] = re.findall(r'\d{3}', val)
    
    return result

def parse_prizes(html):
    """Parse prize 2-5 from HTML"""
    result = {}
    
    # รางวัลข้างเคียง
    nearby = re.search(r'รางวัลข้างเคียง.*?(?=รางวัลที่ 2|$)', html, re.DOTALL)
    if nearby:
        result['nearby_1st'] = re.findall(r'\b(\d{6})\b', nearby.group(0))[:2]
    else:
        result['nearby_1st'] = []
    
    # รางวัลที่ 2-5
    for prize_num, field in [(2, 'second_prize'), (3, 'third_prize'), (4, 'prize_4'), (5, 'prize_5')]:
        # Try multiple patterns
        patterns = [
            rf'รางวัลที่ {prize_num}(.*?)(?=รางวัลที่ {prize_num+1}|$)',
            rf'รางวัลที่ {prize_num}[^(]*\(([^)]+)\)',
        ]
        found = []
        for pat in patterns:
            m = re.search(pat, html, re.DOTALL)
            if m:
                found = re.findall(r'\b(\d{6})\b', m.group(1))
                if found:
                    break
        result[field] = found
    
    return result

def parse_draw(html, date_str):
    """Parse ข้อมูลหวยจาก HTML — รวมทุกวิธี"""
    if not html:
        return None
    
    result = {'draw_date': date_str}
    
    # Method 1: Meta description (most reliable)
    meta = parse_meta_description(html)
    result.update(meta)
    
    # Method 2: HTML structure
    html_data = parse_html_structure(html)
    # Only update if not already found
    for k, v in html_data.items():
        if k not in result or not result[k]:
            result[k] = v
    
    # Method 3: Prizes
    prizes = parse_prizes(html)
    result.update(prizes)
    
    # Ensure all fields exist
    for field in ['first_prize', 'two_digit', 'three_digit_last', 'three_digit_first',
                  'nearby_1st', 'second_prize', 'third_prize', 'prize_4', 'prize_5']:
        if field not in result:
            result[field] = [] if field != 'first_prize' and field != 'two_digit' else ''
    
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
    print("  LottoAI Universal Scraper — myhora.com")
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
            if data and data.get('first_prize') and len(data['first_prize']) == 6:
                results_1990.append(data)
        
        if (i + 1) % 10 == 0 or i == len(dates_1990) - 1:
            print(f"  [{i+1}/{len(dates_1990)}] ok={len(results_1990)}")
        
        if (i + 1) % 10 == 0:
            time.sleep(1.5)
    
    print(f"  1990-1994: {len(results_1990)} งวด")
    
    # ── 2. Fill gaps in 1995-2026 ─────────────────────────────
    print("\n[Phase 2] เติมข้อมูลที่ขาดใน 1995-2026...")
    
    # Load existing
    scraped_file = os.path.join(DATA_DIR, "scraped_all.json")
    with open(scraped_file, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    existing_dates = {d['draw_date']: i for i, d in enumerate(existing)}
    
    # Find draws missing three_digit_first
    missing_3f = [d for d in existing if not d.get('three_digit_first') or len(d['three_digit_first']) == 0]
    print(f"  three_digit_first ขาด: {len(missing_3f)} งวด")
    
    updated = 0
    for i, draw in enumerate(missing_3f):
        draw_date = draw['draw_date']
        url = date_to_url(draw_date)
        html = fetch_url(url)
        if html:
            data = parse_draw(html, draw_date)
            if data:
                # Update missing fields
                idx = existing_dates[draw_date]
                for field in ['three_digit_first', 'nearby_1st', 'second_prize', 'third_prize', 'prize_4', 'prize_5']:
                    if (not existing[idx].get(field) or len(existing[idx][field]) == 0) and \
                       (data.get(field) and len(data[field]) > 0):
                        existing[idx][field] = data[field]
                        updated += 1
        
        if (i + 1) % 20 == 0 or i == len(missing_3f) - 1:
            print(f"  [{i+1}/{len(missing_3f)}] updated={updated}")
        
        if (i + 1) % 10 == 0:
            time.sleep(1.5)
    
    # ── 3. Merge & Save ──────────────────────────────────────
    print("\n[Phase 3] รวมข้อมูล & บันทึก...")
    
    # Merge 1990-1994 into existing
    all_data = results_1990 + existing
    all_data.sort(key=lambda d: d['draw_date'])
    
    # Backup
    backup_file = scraped_file.replace('.json', '_backup2.json')
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    # Save
    with open(scraped_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    # ── Summary ──────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  ผลการ Scrape")
    print(f"{'='*60}")
    print(f"  ข้อมูล 1990-1994 ที่เพิ่ม: {len(results_1990)} งวด")
    print(f"  อัปเดต field ที่ขาด: {updated} fields")
    print(f"  ข้อมูลรวมทั้งหมด: {len(all_data)} งวด")
    print(f"  Backup: {backup_file}")
    
    # Completeness check
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

if __name__ == '__main__':
    main()
