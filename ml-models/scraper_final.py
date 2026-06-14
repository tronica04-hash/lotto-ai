#!/usr/bin/env python3
"""
LottoAI — Universal Scraper v4 (FINAL)
Parse ข้อมูลหวยจาก myhora.com — รองรับทุกช่วงปี 1990-2026
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
    """Parse ข้อมูลหวยจาก HTML — universal parser v4"""
    if not html:
        return None
    
    result = {'draw_date': date_str}
    
    # Find main_lotto section
    main = re.search(r'id="main_lotto">(.*?)(?=<div class="cls"></div>\s*<div id="p_result2"|<div id="p_share_image2"|$)', html, re.DOTALL)
    if not main:
        return None
    section = main.group(1)
    
    # Get column headers
    tc_blocks = re.findall(r"<div class='lot-tc lot-pd' style='([^']*)'>(.*?)</div>", section, re.DOTALL)
    headers = []
    for style, content in tc_blocks:
        # Try <u> tag first, then <div> text
        m = re.search(r'<u>([^<]+)</u>', content)
        if not m:
            m = re.search(r'<div[^>]*>([^<]+)</div>', content)
        if m:
            headers.append((style, m.group(1).strip()))
    
    # Get ALL lot-dc values in the first lot-dr row
    dr = re.search(r"<div class='lot-dr[^']*'[^>]*>(.*?)</div>\s*<div class='cls'>", section, re.DOTALL)
    if not dr:
        return None
    
    dcs = re.findall(r"<div class='lot-dc[^']*'[^>]*>(.*?)</div>", dr.group(1), re.DOTALL)
    dcs = [re.sub(r'<[^>]+>', '', v).strip().replace('&nbsp;', ' ').strip() for v in dcs]
    
    if len(dcs) < 3:
        return None
    
    # ── Parse main values ────────────────────────────────────
    # Position 0: first_prize (6 or 7 digits)
    fp = re.sub(r'\s+', '', dcs[0])
    if re.match(r'^\d{6,7}$', fp):
        result['first_prize'] = fp[-6:]
    else:
        result['first_prize'] = ''
    
    # Position 1: three_digit_first (may be empty)
    three_digit_first = []
    val1 = dcs[1]
    if val1 and not re.match(r'^\d{6,7}$', re.sub(r'\s+', '', val1)):
        # This is three_digit_first (3-digit numbers)
        nums = re.findall(r'\d{3}', val1)
        if nums and len(nums) <= 3:
            three_digit_first = nums
    
    # Position 2: three_digit_last (3-digit numbers, 2-4 values)
    three_digit_last = []
    val2 = dcs[2]
    nums2 = re.findall(r'\d{3}', val2)
    if len(nums2) >= 2:
        three_digit_last = nums2
    
    # Position 3: two_digit (2 digits)
    two_digit = ''
    if len(dcs) >= 4:
        val3 = re.sub(r'\s+', '', dcs[3])
        if re.match(r'^\d{2}$', val3):
            two_digit = val3
    
    # If position 1 was actually three_digit_last (no three_digit_first column)
    if not three_digit_first and not three_digit_last:
        # Position 1 might be three_digit_last
        nums = re.findall(r'\d{3}', dcs[1])
        if len(nums) >= 2:
            three_digit_last = nums
    
    result['three_digit_first'] = three_digit_first
    result['three_digit_last'] = three_digit_last
    result['two_digit'] = two_digit
    
    # ── Parse prizes from p_result2 section ──────────────────
    p2_section = re.search(r'<div id="p_result2">(.*?)(?=<div id="p_share_image2"|$)', html, re.DOTALL)
    
    if p2_section:
        p2_html = p2_section.group(1)
        p2_dcs = re.findall(r"<div class='lot-dc[^']*'[^>]*>(.*?)</div>", p2_html, re.DOTALL)
        p2_dcs = [re.sub(r'<[^>]+>', '', v).strip().replace('&nbsp;', '').strip() for v in p2_dcs]
        six_digit = [v for v in p2_dcs if re.match(r'^\d{6}$', v)]
        
        result['nearby_1st'] = six_digit[:2]
        result['second_prize'] = six_digit[2:7]
        result['third_prize'] = six_digit[7:17]
        result['prize_4'] = six_digit[17:67]
        result['prize_5'] = six_digit[67:167]
    else:
        result['nearby_1st'] = []
        result['second_prize'] = []
        result['third_prize'] = []
        result['prize_4'] = []
        result['prize_5'] = []
    
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
    print("  LottoAI Universal Scraper v4 (FINAL)")
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
    
    updated_fields = 0
    for i, draw_date in enumerate(missing):
        url = date_to_url(draw_date)
        html = fetch_url(url)
        if html:
            data = parse_draw(html, draw_date)
            if data:
                idx = existing_dates[draw_date]
                for field in ['three_digit_first', 'nearby_1st', 'second_prize',
                              'third_prize', 'prize_4', 'prize_5', 'two_digit', 'first_prize']:
                    if data.get(field):
                        old = existing[idx].get(field)
                        new = data[field]
                        should_update = False
                        if not old:
                            should_update = True
                        elif isinstance(old, list) and isinstance(new, list):
                            if len(new) > len(old):
                                should_update = True
                        elif isinstance(old, str) and isinstance(new, str):
                            if new and not old:
                                should_update = True
                        if should_update:
                            existing[idx][field] = new
                            updated_fields += 1
        
        if (i + 1) % 20 == 0 or i == len(missing) - 1:
            print(f"  [{i+1}/{len(missing)}] updated_fields={updated_fields}", flush=True)
        
        if (i + 1) % 10 == 0:
            time.sleep(1.5)
    
    # ── 3. Merge & Save ──────────────────────────────────────
    print("\n[Phase 3] รวมข้อมูล & บันทึก...")
    
    all_data = results_1990 + existing
    all_data.sort(key=lambda d: d['draw_date'])
    
    # Remove duplicates (keep the one with more data)
    seen = {}
    for d in all_data:
        dd = d['draw_date']
        if dd not in seen:
            seen[dd] = d
        else:
            old = seen[dd]
            old_score = sum(1 for f in ['three_digit_first', 'nearby_1st', 'second_prize', 'third_prize', 'prize_4', 'prize_5'] if old.get(f))
            new_score = sum(1 for f in ['three_digit_first', 'nearby_1st', 'second_prize', 'third_prize', 'prize_4', 'prize_5'] if d.get(f))
            if new_score > old_score:
                seen[dd] = d
    
    all_data = sorted(seen.values(), key=lambda d: d['draw_date'])
    
    # Backup
    backup_file = scraped_file.replace('.json', '_backup5.json')
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    with open(scraped_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    # ── Summary ──────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  ผลการ Scrape")
    print(f"{'='*60}")
    print(f"  ข้อมูล 1990-1994 ที่เพิ่ม: {len(results_1990)} งวด")
    print(f"  field ที่อัปเดต: {updated_fields}")
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
        print(f"\n  ตัวอย่าง 1990-1994 (5 งวดแรก):")
        for d in results_1990[:5]:
            print(f"    {d['draw_date']}: 1st={d['first_prize']}, 2d={d['two_digit']}, 3last={d['three_digit_last']}, nearby={d['nearby_1st']}, p2={len(d['second_prize'])}")

if __name__ == '__main__':
    main()
