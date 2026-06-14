#!/usr/bin/env python3
"""
LottoAI — Scraper ข้อมูลหวย 1990-1994 (7 หลัก era)
myhora.com มีข้อมูลครบ แต่รูปแบบต่างจาก 1995+
- first_prize: 7 หลัก (ตัดเหลือ 6 หลักท้ายสำหรับ prediction)
- three_digit_first: ไม่มี (ยังไม่มีรางวัลนี้)
- second_prize ฯลฯ: มีแต่ HTML structure ต่าง
"""
import re, json, time, urllib.request, os
from datetime import date

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'th-TH,th;q=0.9,en;q=0.8',
}

DATA_DIR = r"D:\lotto-ai\ml-models\data"
OUTPUT_FILE = os.path.join(DATA_DIR, "scraped_1990_1994.json")

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None

def parse_draw_1990s(html, date_str):
    """Parse ข้อมูลหวย 1990-1994 ที่มี first_prize 7 หลัก"""
    if not html:
        return None
    
    result = {'draw_date': date_str}
    
    # รางวัลที่ 1 — 7 หลักในยุค 1990-1994, 6 หลักในยุค 1995+
    m = re.search(r'รางวัลที่ 1[^(]*\\((\\d{6,7})\\)', html)
    if not m:
        m = re.search(r'รางวัลที่หนึ่ง[^0-9]*(\\d{6,7})', html, re.DOTALL)
    if m:
        fp = m.group(1)
        # ถ้า 7 หลัก ให้ตัดเหลือ 6 หลักท้าย
        if len(fp) == 7:
            fp = fp[-6:]
        result['first_prize'] = fp
    else:
        result['first_prize'] = ''
    
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
    
    # เลขหน้า 3 ตัว — ไม่มีในยุค 1990-1994
    result['three_digit_first'] = []
    
    # รางวัลข้างเคียงรางวัลที่ 1
    nearby = re.search(r'รางวัลข้างเคียง.*?(?=รางวัลที่ 2|เลขหน้า|เลขท้าย|$)', html, re.DOTALL)
    if nearby:
        result['nearby_1st'] = re.findall(r'\\b(\\d{6})\\b', nearby.group(0))[:2]
    else:
        result['nearby_1st'] = []
    
    # รางวัลที่ 2-5 — ลองหาแบบหลาย pattern
    # Pattern 1: รางวัลที่ 2(.*?)(?=รางวัลที่ 3)
    p2 = re.search(r'รางวัลที่ 2(.*?)(?=รางวัลที่ 3)', html, re.DOTALL)
    if not p2:
        p2 = re.search(r'รางวัลที่ 2[^(]*\\(([^)]+)\\)', html)
        if p2:
            result['second_prize'] = re.findall(r'\\b(\\d{6})\\b', p2.group(1))[:5]
        else:
            result['second_prize'] = []
    else:
        result['second_prize'] = re.findall(r'\\b(\\d{6})\\b', p2.group(1))[:5]
    
    p3 = re.search(r'รางวัลที่ 3(.*?)(?=รางวัลที่ 4)', html, re.DOTALL)
    if not p3:
        p3 = re.search(r'รางวัลที่ 3[^(]*\\(([^)]+)\\)', html)
        if p3:
            result['third_prize'] = re.findall(r'\\b(\\d{6})\\b', p3.group(1))[:10]
        else:
            result['third_prize'] = []
    else:
        result['third_prize'] = re.findall(r'\\b(\\d{6})\\b', p3.group(1))[:10]
    
    p4 = re.search(r'รางวัลที่ 4(.*?)(?=รางวัลที่ 5)', html, re.DOTALL)
    if not p4:
        p4 = re.search(r'รางวัลที่ 4[^(]*\\(([^)]+)\\)', html)
        if p4:
            result['prize_4'] = re.findall(r'\\b(\\d{6})\\b', p4.group(1))[:50]
        else:
            result['prize_4'] = []
    else:
        result['prize_4'] = re.findall(r'\\b(\\d{6})\\b', p4.group(1))[:50]
    
    p5 = re.search(r'รางวัลที่ 5(.*?)(?=สามตรง|เลขหน้า|เลขท้าย|$)', html, re.DOTALL)
    if not p5:
        p5 = re.search(r'รางวัลที่ 5[^(]*\\(([^)]+)\\)', html)
        if p5:
            result['prize_5'] = re.findall(r'\\b(\\d{6})\\b', p5.group(1))[:100]
        else:
            result['prize_5'] = []
    else:
        result['prize_5'] = re.findall(r'\\b(\\d{6})\\b', p5.group(1))[:100]
    
    return result

def date_to_url_1990(draw_date):
    y, m, d = draw_date.split('-')
    by = int(y) + 543
    return f"https://myhora.com/lottery/result-{int(d):02d}-{int(m):02d}-{by}.aspx"

def main():
    print("=" * 60)
    print("  LottoAI — Scraper ข้อมูลหวย 1990-1994")
    print("=" * 60)
    
    # สร้างรายการวันที่ 1990-1994
    dates = []
    for y in range(1990, 1995):
        for m in range(1, 13):
            for d in [1, 16]:
                try:
                    dt = date(y, m, d)
                    if dt <= date.today():
                        dates.append(dt.strftime('%Y-%m-%d'))
                except:
                    pass
    
    print(f"จำนวนงวด: {len(dates)}")
    print(f"ช่วงวันที่: {dates[0]} -> {dates[-1]}")
    print()
    
    results = []
    ok = fail = skip = 0
    
    for i, draw_date in enumerate(dates):
        url = date_to_url_1990(draw_date)
        html = fetch_url(url)
        
        if html:
            data = parse_draw_1990s(html, draw_date)
            if data and data.get('first_prize') and len(data['first_prize']) == 6:
                results.append(data)
                ok += 1
            else:
                skip += 1
        else:
            fail += 1
        
        if (i + 1) % 10 == 0 or i == len(dates) - 1:
            print(f"  [{i+1}/{len(dates)}] ok={ok} skip={skip} fail={fail}")
        
        if (i + 1) % 10 == 0:
            time.sleep(1.5)
    
    # Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"  ผลการ Scrape 1990-1994")
    print(f"{'='*60}")
    print(f"  สำเร็จ: {ok} งวด")
    print(f"  ไม่มีข้อมูล: {skip} งวด")
    print(f"  ล้มเหลว: {fail} งวด")
    print(f"  บันทึกที่: {OUTPUT_FILE}")
    
    if results:
        print(f"\n  ข้อมูลตั้งแต่: {results[0]['draw_date']}")
        print(f"  ถึง: {results[-1]['draw_date']}")
        
        # สรุป
        has_p1 = sum(1 for d in results if d.get('first_prize'))
        has_2d = sum(1 for d in results if d.get('two_digit'))
        has_3d_last = sum(1 for d in results if d.get('three_digit_last'))
        has_p2 = sum(1 for d in results if d.get('second_prize'))
        has_p3 = sum(1 for d in results if d.get('third_prize'))
        has_p4 = sum(1 for d in results if d.get('prize_4'))
        has_p5 = sum(1 for d in results if d.get('prize_5'))
        
        print(f"\n  ความครบของข้อมูล:")
        print(f"    first_prize:     {has_p1}/{len(results)} ({has_p1/len(results)*100:.0f}%)")
        print(f"    two_digit:       {has_2d}/{len(results)} ({has_2d/len(results)*100:.0f}%)")
        print(f"    three_digit_last:{has_3d_last}/{len(results)} ({has_3d_last/len(results)*100:.0f}%)")
        print(f"    second_prize:    {has_p2}/{len(results)} ({has_p2/len(results)*100:.0f}%)")
        print(f"    third_prize:     {has_p3}/{len(results)} ({has_p3/len(results)*100:.0f}%)")
        print(f"    prize_4:         {has_p4}/{len(results)} ({has_p4/len(results)*100:.0f}%)")
        print(f"    prize_5:         {has_p5}/{len(results)} ({has_p5/len(results)*100:.0f}%)")
        
        # แสดงตัวอย่าง
        print(f"\n  ตัวอย่างข้อมูล 5 งวดแรก:")
        for d in results[:5]:
            print(f"    {d['draw_date']}: 1st={d['first_prize']}, 2d={d['two_digit']}, 3last={d['three_digit_last']}")

if __name__ == '__main__':
    main()
