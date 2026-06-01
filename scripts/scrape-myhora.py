#!/usr/bin/env python3
"""
Scraper ข้อมูลหวยรัฐบาลไทยจาก myhora.com
ดึงข้อมูลทุกงวด + รางวัลครบทุกประเภท
"""
import re, json, os, time, random, sys
from datetime import datetime
import urllib.request, urllib.error

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'th-TH,th;q=0.9,en;q=0.8',
}

def fetch_page(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read().decode('utf-8', errors='replace')
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
        except Exception:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
    return None

def parse_prize_page(html, date_str):
    if not html:
        return None

    result = {'draw_date': date_str}

    # ---- รางวัลที่ 1 ----
    first_match = re.search(r'รางวัลที่หนึ่ง[^0-9]*?(\d{6})', html, re.DOTALL)
    if not first_match:
        first_match = re.search(r'รางวัลที่ 1[^(]*\((\d{6})\)', html)
    result['first_prize'] = first_match.group(1) if first_match else ''

    # ---- เลขหน้า 3 + เลขท้าย 3 + เลขท้าย 2 ----
    # หา lot-dc blocks (รางวัลที่1, หน้า3, ท้าย3, ท้าย2 เรียงตำแหน่ง)
    lotdc = re.findall(r"class='lot-dc lotto-fxl py-20'[^>]*>([^<]*)</div>", html)

    if not lotdc:
        # fallback: regex กว้างขึ้น
        lotdc = re.findall(r'lot-dc[^>]*>([^<]+)</div>', html)

    if lotdc:
        # block[0] = รางวัลที่1 (6 หลัก)
        # block[1] = เลขหน้า 3 (อาจว่างถ้า display:none ในงวดเก่า)
        # block[2] = เลขท้าย 3
        # block[3] = เลขท้าย 2

        # เลขหน้า 3
        if len(lotdc) > 1 and lotdc[1].strip():
            front3_nums = re.findall(r'\d{3}', lotdc[1])
            result['front_3'] = front3_nums[:2]
        else:
            result['front_3'] = []

        # เลขท้าย 3
        if len(lotdc) > 2 and lotdc[2].strip():
            last3_nums = re.findall(r'\d{3}', lotdc[2])
            result['last_3'] = last3_nums[:2]
        else:
            result['last_3'] = []

        # เลขท้าย 2
        if len(lotdc) > 3 and lotdc[3].strip():
            last2_match = re.search(r'\b(\d{2})\b', lotdc[3])
            result['last_2'] = last2_match.group(1) if last2_match else ''
        else:
            result['last_2'] = ''

    # Fallback: หาจาก meta description (งวดใหม่ format)
    if not result.get('front_3') or not result.get('last_3'):
        meta = re.search(
            r'3 ตัวหน้า\((\d+)&nbsp;\s*(\d+)\).*?เลขท้าย 3 ตัว\((\d+)&nbsp;\s*(\d+)\).*?เลขท้าย 2 ตัว\((\d+)\)',
            html
        )
        if meta:
            if not result.get('front_3'):
                result['front_3'] = [meta.group(1), meta.group(2)]
            if not result.get('last_3'):
                result['last_3'] = [meta.group(3), meta.group(4)]
            if not result.get('last_2'):
                result['last_2'] = meta.group(5)

    # Fallback เลขท้าย 2 จาก meta
    if not result.get('last_2'):
        meta2 = re.search(r'เลขท้าย 2 ตัว\((\d+)\)', html)
        if meta2:
            result['last_2'] = meta2.group(1)

    # ---- รางวัลข้างเคียง ----
    nearby_section = re.search(r'รางวัลข้างเคียง(.*?)(?=รางวัลที่ 2|เลขหน้า)', html, re.DOTALL)
    if nearby_section:
        result['nearby_1st'] = re.findall(r'\b(\d{6})\b', nearby_section.group(1))[:2]
    else:
        result['nearby_1st'] = []

    # ---- รางวัลที่ 2 ----
    p2 = re.search(r'รางวัลที่ 2(.*?)(?=รางวัลที่ 3)', html, re.DOTALL)
    result['prize_2'] = re.findall(r'\b(\d{6})\b', p2.group(1))[:5] if p2 else []

    # ---- รางวัลที่ 3 ----
    p3 = re.search(r'รางวัลที่ 3(.*?)(?=รางวัลที่ 4)', html, re.DOTALL)
    result['prize_3'] = re.findall(r'\b(\d{6})\b', p3.group(1))[:10] if p3 else []

    # ---- รางวัลที่ 4 ----
    p4 = re.search(r'รางวัลที่ 4(.*?)(?=รางวัลที่ 5)', html, re.DOTALL)
    result['prize_4'] = re.findall(r'\b(\d{6})\b', p4.group(1))[:50] if p4 else []

    # ---- รางวัลที่ 5 ----
    p5 = re.search(r'รางวัลที่ 5(.*?)(?=สามตรง|เลขหน้า|เลขท้าย|$)', html, re.DOTALL)
    result['prize_5'] = re.findall(r'\b(\d{6})\b', p5.group(1))[:100] if p5 else []

    return result

def generate_dates(start_year=2006):
    dates = []
    end_year = datetime.now().year + 1
    for y in range(start_year, end_year + 1):
        for m in range(1, 13):
            for d in [1, 16]:
                dt = f"{y}-{m:02d}-{d:02d}"
                if dt <= datetime.now().strftime('%Y-%m-%d'):
                    dates.append(dt)
    return sorted(set(dates))

def date_to_url(date_str):
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    by = dt.year + 543
    return f"https://myhora.com/lottery/result-{dt.day:02d}-{dt.month:02d}-{by}.aspx"

def main():
    print("=" * 60)
    print("  Thai Lottery Scraper — myhora.com")
    print("=" * 60)

    dates = generate_dates(2006)
    print(f"ทั้งหมด {len(dates)} งวด")

    out_dir = '/tmp/myhora-lotto'
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, 'all_prizes.json')

    # Load existing
    existing = {}
    if os.path.exists(out_file):
        with open(out_file) as f:
            for item in json.load(f):
                existing[item['draw_date']] = item
        print(f"มีข้อมูลเก่า {len(existing)} งวด")

    pending = [d for d in dates if d not in existing]
    print(f"ต้องดึงเพิ่ม {len(pending)} งวด\n")

    ok = fail = 0
    for i, date_str in enumerate(pending):
        url = date_to_url(date_str)
        html = fetch_page(url)
        data = parse_prize_page(html, date_str) if html else None

        if data and data.get('first_prize'):
            existing[date_str] = data
            ok += 1
        else:
            fail += 1

        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{len(pending)} — ok={ok}, fail={fail}")
            # Save checkpoint
            with open(out_file, 'w') as f:
                json.dump(list(existing.values()), f, ensure_ascii=False)

        time.sleep(random.uniform(0.3, 0.8))

    # Final save
    with open(out_file, 'w') as f:
        json.dump(list(existing.values()), f, ensure_ascii=False)

    print(f"\n=== เสร็จ ===")
    print(f"รวม: {len(existing)} งวด | ใหม่: {ok} | ล้มเหลว: {fail}")

    # Validate: count prizes
    p2_full = sum(1 for v in existing.values() if len(v.get('prize_2', [])) == 5)
    p3_full = sum(1 for v in existing.values() if len(v.get('prize_3', [])) == 10)
    p4_full = sum(1 for v in existing.values() if len(v.get('prize_4', [])) == 50)
    p5_full = sum(1 for v in existing.values() if len(v.get('prize_5', [])) == 100)
    print(f"\nความครบของรางวัล:")
    print(f"  รางวัลที่ 2 (5ตัว): {p2_full}/{len(existing)}")
    print(f"  รางวัลที่ 3 (10ตัว): {p3_full}/{len(existing)}")
    print(f"  รางวัลที่ 4 (50ตัว): {p4_full}/{len(existing)}")
    print(f"  รางวัลที่ 5 (100ตัว): {p5_full}/{len(existing)}")

    # Sample
    sample = list(existing.values())[-1]
    print(f"\nตัวอย่างล่าสุด ({sample['draw_date']}):")
    for k, v in sample.items():
        if k != 'draw_date':
            print(f"  {k}: {v}")

if __name__ == '__main__':
    main()
