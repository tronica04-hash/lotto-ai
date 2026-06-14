#!/usr/bin/env python3
"""
LottoAI Data Gap Filler — เติมข้อมูลหวยที่ขาดหาย
1. เติม three_digit_first สำหรับงวด 1995-2015 (ขาด 447 งวด)
2. เก็บข้อมูล 1990-1994 ที่ยังไม่มี
3. เติม nearby_1st, prize_4, prize_5 ที่ขาด
"""
import re, json, time, urllib.request, os
from datetime import date, datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'th-TH,th;q=0.9,en;q=0.8',
}

DATA_DIR = r"D:\lotto-ai\ml-models\data"
SCRAPED_FILE = os.path.join(DATA_DIR, "scraped_all.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "gap_filled.json")

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None

def parse_draw_full(html, date_str):
    """Parse ข้อมูลหวยจาก HTML — ครบทุก field"""
    if not html:
        return None
    
    result = {'draw_date': date_str}
    
    # รางวัลที่ 1 (6 หลัก)
    m = re.search(r'รางวัลที่ 1[^(]*\\((\\d{6})\\)', html)
    if not m:
        m = re.search(r'รางวัลที่หนึ่ง[^0-9]*(\\d{6})', html, re.DOTALL)
    result['first_prize'] = m.group(1) if m else ''
    
    # เลขท้าย 2 ตัว
    m = re.search(r'เลขท้าย 2 ตัว[^(]*\\((\\d{2})\\)', html)
    result['two_digit'] = m.group(1) if m else ''
    
    # เลขท้าย 3 ตัว
    last3 = re.search(r'เลขท้าย 3 ตัว\\(([^)]+)\\)', html)
    if last3:
        nums = re.findall(r'\\d{3}', last3.group(1))
        result['three_digit_last'] = nums
    else:
        result['three_digit_last'] = []
    
    # เลขหน้า 3 ตัว — ลองหาหลาย pattern
    front3 = re.search(r'3 ตัวหน้า\\(([^)]+)\\)', html)
    if not front3:
        front3 = re.search(r'เลขหน้า 3 ตัว\\(([^)]+)\\)', html)
    if not front3:
        front3 = re.search(r'หน้า 3 ตัว\\(([^)]+)\\)', html)
    if front3:
        nums = re.findall(r'\\d{3}', front3.group(1))
        result['three_digit_first'] = nums
    else:
        result['three_digit_first'] = []
    
    # รางวัลข้างเคียงรางวัลที่ 1
    nearby = re.search(r'รางวัลข้างเคียง.*?(?=รางวัลที่ 2|เลขหน้า|เลขท้าย|$)', html, re.DOTALL)
    if nearby:
        result['nearby_1st'] = re.findall(r'\\b(\\d{6})\\b', nearby.group(0))[:2]
    else:
        result['nearby_1st'] = []
    
    # รางวัลที่ 2
    p2 = re.search(r'รางวัลที่ 2(.*?)(?=รางวัลที่ 3)', html, re.DOTALL)
    result['second_prize'] = re.findall(r'\\b(\\d{6})\\b', p2.group(1))[:5] if p2 else []
    
    # รางวัลที่ 3
    p3 = re.search(r'รางวัลที่ 3(.*?)(?=รางวัลที่ 4)', html, re.DOTALL)
    result['third_prize'] = re.findall(r'\\b(\\d{6})\\b', p3.group(1))[:10] if p3 else []
    
    # รางวัลที่ 4
    p4 = re.search(r'รางวัลที่ 4(.*?)(?=รางวัลที่ 5)', html, re.DOTALL)
    result['prize_4'] = re.findall(r'\\b(\\d{6})\\b', p4.group(1))[:50] if p4 else []
    
    # รางวัลที่ 5
    p5 = re.search(r'รางวัลที่ 5(.*?)(?=สามตรง|เลขหน้า|เลขท้าย|$)', html, re.DOTALL)
    result['prize_5'] = re.findall(r'\\b(\\d{6})\\b', p5.group(1))[:100] if p5 else []
    
    return result

def date_to_url(draw_date):
    y, m, d = draw_date.split('-')
    by = int(y) + 543
    return f"https://myhora.com/lottery/result-{int(d):02d}-{int(m):02d}-{by}.aspx"

def main():
    # Load existing data
    with open(SCRAPED_FILE, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    existing_dates = {d['draw_date']: d for d in existing}
    
    # ── 1. หางวดที่ three_digit_first ขาด ──────────────────
    missing_3f = [d['draw_date'] for d in existing 
                  if not d.get('three_digit_first') or len(d['three_digit_first']) == 0]
    
    # ── 2. หางวด 1990-1994 ที่ยังไม่มี ─────────────────────
    all_dates_1990_1994 = []
    for y in range(1990, 1995):
        for m in range(1, 13):
            for d in [1, 16]:
                try:
                    dt = date(y, m, d)
                    if dt <= date.today():
                        all_dates_1990_1994.append(dt.strftime('%Y-%m-%d'))
                except:
                    pass
    
    new_dates_1990 = [d for d in all_dates_1990_1994 if d not in existing_dates]
    
    # ── 3. หางวดที่ nearby_1st, prize_4, prize_5 ขาด ───────
    missing_other = [d['draw_date'] for d in existing
                     if not (d.get('nearby_1st') and len(d['nearby_1st']) > 0)
                     or not (d.get('prize_4') and len(d['prize_4']) > 0)
                     or not (d.get('prize_5') and len(d['prize_5']) > 0)]
    
    # รวมวันที่ที่ต้อง scrape (ไม่ซ้ำ)
    to_scrape = list(set(missing_3f + new_dates_1990 + missing_other))
    to_scrape.sort()
    
    print("=" * 60)
    print("  LottoAI Data Gap Filler")
    print("=" * 60)
    print(f"  three_digit_first ขาด: {len(missing_3f)} งวด")
    print(f"  ข้อมูล 1990-1994 ที่ไม่มี: {len(new_dates_1990)} งวด")
    print(f"  งวดที่ prize ขาด: {len(missing_other)} งวด")
    print(f"  รวมต้อง scrape: {len(to_scrape)} งวด (ไม่ซ้ำ)")
    print()
    
    # ── Scrape ──────────────────────────────────────────────
    new_results = []
    updated_count = 0
    ok = fail = skip = 0
    
    for i, draw_date in enumerate(to_scrape):
        url = date_to_url(draw_date)
        html = fetch_url(url)
        
        if html:
            data = parse_draw_full(html, draw_date)
            if data and data.get('first_prize'):
                if draw_date in existing_dates:
                    # Update existing record
                    idx = next(j for j, d in enumerate(existing) if d['draw_date'] == draw_date)
                    # Merge: เซฟ field ที่ขาด
                    old = existing[idx]
                    updated = False
                    for field in ['three_digit_first', 'nearby_1st', 'second_prize', 
                                  'third_prize', 'prize_4', 'prize_5']:
                        if (not old.get(field) or len(old[field]) == 0) and \
                           (data.get(field) and len(data[field]) > 0):
                            existing[idx][field] = data[field]
                            updated = True
                    if updated:
                        updated_count += 1
                else:
                    # New record (1990-1994)
                    new_results.append(data)
                ok += 1
            else:
                skip += 1
        else:
            fail += 1
        
        if (i + 1) % 20 == 0 or i == len(to_scrape) - 1:
            print(f"  [{i+1}/{len(to_scrape)}] ok={ok} updated={updated_count} new={len(new_results)} skip={skip} fail={fail}")
        
        if (i + 1) % 10 == 0:
            time.sleep(1.5)
    
    # ── Merge & Save ────────────────────────────────────────
    # เพิ่มข้อมูลใหม่ 1990-1994 เข้าไปใน existing
    all_data = new_results + existing
    all_data.sort(key=lambda d: d['draw_date'])
    
    # Backup ข้อมูลเดิม
    backup_file = SCRAPED_FILE.replace('.json', '_backup.json')
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    # Save ข้อมูลใหม่
    with open(SCRAPED_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    # ── Summary ─────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  ผลการเติมข้อมูล")
    print(f"{'='*60}")
    print(f"  อัปเดตงวดเดิม: {updated_count} งวด")
    print(f"  เพิ่มงวดใหม่ (1990-1994): {len(new_results)} งวด")
    print(f"  ข้อมูลรวมทั้งหมด: {len(all_data)} งวด")
    print(f"  Backup ข้อมูลเดิม: {backup_file}")
    print(f"  บันทึกที่: {SCRAPED_FILE}")
    
    # สรุปความครบหลังอัปเดต
    print(f"\n  ความครบของข้อมูล (หลังอัปเดต):")
    checks = [
        ('first_prize', lambda d: d.get('first_prize') and len(str(d['first_prize'])) == 6),
        ('two_digit', lambda d: d.get('two_digit') and len(str(d['two_digit'])) == 2),
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
        status = "✅" if pct == 100 else "⚠️" if pct > 80 else "❌"
        print(f"    {status} {field}: {has}/{len(all_data)} ({pct:.1f}%)")

if __name__ == '__main__':
    main()
