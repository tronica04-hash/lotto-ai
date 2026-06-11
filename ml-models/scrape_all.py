#!/usr/bin/env python3
"""
Thai Lottery Full Scraper — myhora.com
Scrape ข้อมูลหวยย้อนหลัง 1990-2026 ทุกรางวัลที่หน้าเว็บมี
ใช้ urllib เพราะ requests มีปัญหา DNS บน Windows
"""
import re, json, time, urllib.request
from datetime import date

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'th-TH,th;q=0.9,en;q=0.8',
}

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None

def parse_draw(html, date_str):
    if not html:
        return None
    
    result = {'draw_date': date_str}
    
    # รางวัลที่ 1 (6 หลัก)
    m = re.search(r'รางวัลที่ 1[^(]*\((\d{6})\)', html)
    if not m:
        m = re.search(r'รางวัลที่หนึ่ง[^0-9]*(\d{6})', html, re.DOTALL)
    result['first_prize'] = m.group(1) if m else ''
    
    # เลขท้าย 2 ตัว
    m = re.search(r'เลขท้าย 2 ตัว[^(]*\((\d{2})\)', html)
    result['two_digit'] = m.group(1) if m else ''
    
    # เลขท้าย 3 ตัว (อาจมี 2-4 ตัว)
    last3 = re.search(r'เลขท้าย 3 ตัว\(([^)]+)\)', html)
    if last3:
        nums = re.findall(r'\d{3}', last3.group(1))
        result['three_digit_last'] = nums
    else:
        result['three_digit_last'] = []
    
    # เลขหน้า 3 ตัว
    front3 = re.search(r'3 ตัวหน้า\(([^)]+)\)', html)
    if front3:
        nums = re.findall(r'\d{3}', front3.group(1))
        result['three_digit_first'] = nums
    else:
        result['three_digit_first'] = []
    
    # รางวัลข้างเคียงรางวัลที่ 1
    nearby = re.search(r'รางวัลข้างเคียง.*?(?=รางวัลที่ 2|เลขหน้า|เลขท้าย|$)', html, re.DOTALL)
    if nearby:
        result['nearby_1st'] = re.findall(r'\b(\d{6})\b', nearby.group(0))[:2]
    else:
        result['nearby_1st'] = []
    
    # รางวัลที่ 2 (5 ตัว)
    p2 = re.search(r'รางวัลที่ 2(.*?)(?=รางวัลที่ 3)', html, re.DOTALL)
    result['second_prize'] = re.findall(r'\b(\d{6})\b', p2.group(1))[:5] if p2 else []
    
    # รางวัลที่ 3 (10 ตัว)
    p3 = re.search(r'รางวัลที่ 3(.*?)(?=รางวัลที่ 4)', html, re.DOTALL)
    result['third_prize'] = re.findall(r'\b(\d{6})\b', p3.group(1))[:10] if p3 else []
    
    # รางวัลที่ 4 (50 ตัว)
    p4 = re.search(r'รางวัลที่ 4(.*?)(?=รางวัลที่ 5)', html, re.DOTALL)
    result['prize_4'] = re.findall(r'\b(\d{6})\b', p4.group(1))[:50] if p4 else []
    
    # รางวัลที่ 5 (100 ตัว)
    p5 = re.search(r'รางวัลที่ 5(.*?)(?=สามตรง|เลขหน้า|เลขท้าย|$)', html, re.DOTALL)
    result['prize_5'] = re.findall(r'\b(\d{6})\b', p5.group(1))[:100] if p5 else []
    
    return result

def date_to_url(draw_date):
    y, m, d = draw_date.split('-')
    by = int(y) + 543
    return f"https://myhora.com/lottery/result-{int(d):02d}-{int(m):02d}-{by}.aspx"

def generate_dates():
    """สร้างรายการวันที่หวย 1990-2026 (วันที่ 1 และ 16 ของทุกเดือน)"""
    dates = []
    for y in range(1990, 2027):
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
    print("  Thai Lottery Full Scraper — myhora.com")
    print("  ข้อมูลหวยย้อนหลัง 1990-2026 ทุกรางวัล")
    print("=" * 60)
    
    dates = generate_dates()
    print(f"จำนวนงวดทั้งหมด: {len(dates)}")
    print(f"ช่วงวันที่: {dates[0]} -> {dates[-1]}")
    print()
    
    results = []
    ok = fail = skip = 0
    
    for i, draw_date in enumerate(dates):
        url = date_to_url(draw_date)
        html = fetch_url(url)
        
        if html:
            data = parse_draw(html, draw_date)
            if data and data.get('first_prize'):
                results.append(data)
                ok += 1
            else:
                # หน้าเว็บโหลดได้แต่ไม่มีข้อมูล (อาจไม่ใช่วันหวยจริง)
                skip += 1
        else:
            fail += 1
        
        # Progress report
        if (i + 1) % 50 == 0 or i == len(dates) - 1:
            print(f"  [{i+1}/{len(dates)}] ok={ok} skip={skip} fail={fail}")
        
        # Rate limit — ไม่ให้ส่ง request เร็วเกินไป
        if (i + 1) % 10 == 0:
            time.sleep(1)
    
    # Save results
    out_path = r"D:\lotto-ai\ml-models\data\scraped_all.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"  ผลการ Scrape")
    print(f"{'='*60}")
    print(f"  สำเร็จ: {ok} งวด")
    print(f"  ไม่มีข้อมูล: {skip} งวด")
    print(f"  ล้มเหลว: {fail} งวด")
    print(f"  บันทึกที่: {out_path}")
    
    if results:
        print(f"\n  ข้อมูลตั้งแต่: {results[0]['draw_date']}")
        print(f"  ถึง: {results[-1]['draw_date']}")
        
        # สรุปความครบของข้อมูล
        has_p1 = sum(1 for d in results if d.get('first_prize'))
        has_2d = sum(1 for d in results if d.get('two_digit'))
        has_3d_last = sum(1 for d in results if d.get('three_digit_last'))
        has_3d_first = sum(1 for d in results if d.get('three_digit_first'))
        has_p2 = sum(1 for d in results if d.get('second_prize'))
        has_p5 = sum(1 for d in results if d.get('prize_5'))
        has_nearby = sum(1 for d in results if d.get('nearby_1st'))
        
        print(f"\n  ความครบของข้อมูล:")
        print(f"    first_prize:     {has_p1}/{len(results)} ({has_p1/len(results)*100:.0f}%)")
        print(f"    two_digit:       {has_2d}/{len(results)} ({has_2d/len(results)*100:.0f}%)")
        print(f"    three_digit_last:{has_3d_last}/{len(results)} ({has_3d_last/len(results)*100:.0f}%)")
        print(f"    three_digit_first:{has_3d_first}/{len(results)} ({has_3d_first/len(results)*100:.0f}%)")
        print(f"    second_prize:    {has_p2}/{len(results)} ({has_p2/len(results)*100:.0f}%)")
        print(f"    prize_5:         {has_p5}/{len(results)} ({has_p5/len(results)*100:.0f}%)")
        print(f"    nearby_1st:      {has_nearby}/{len(results)} ({has_nearby/len(results)*100:.0f}%)")

if __name__ == '__main__':
    main()
