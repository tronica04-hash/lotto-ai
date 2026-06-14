#!/usr/bin/env python3
"""
LottoAI — Fix ข้อมูล 1990-1994
แก้ไข two_digit ที่ขาดในข้อมูล 1990-1994
"""
import json, os, re, time
import urllib.request

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
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

def date_to_url(draw_date):
    y, m, d = draw_date.split('-')
    by = int(y) + 543
    return f"https://myhora.com/lottery/result-{int(d):02d}-{int(m):02d}-{by}.aspx"

def fix_1990s_data():
    scraped_file = os.path.join(DATA_DIR, "scraped_all.json")
    with open(scraped_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find 1990-1994 draws missing two_digit
    to_fix = [d for d in data if d['draw_date'][:4] in ['1990','1991','1992','1993','1994'] 
              and (not d.get('two_digit') or d['two_digit'] == '')]
    
    print(f"ข้อมูล 1990-1994 ที่ต้องแก้ two_digit: {len(to_fix)} งวด")
    
    fixed = 0
    for i, draw in enumerate(to_fix):
        draw_date = draw['draw_date']
        url = date_to_url(draw_date)
        html = fetch_url(url)
        
        if html:
            # Find main_lotto section
            main = re.search(r'id="main_lotto">(.*?)(?=<div class="cls"></div>\s*<div id="p_result2"|<div id="p_share_image2"|$)', html, re.DOTALL)
            if main:
                section = main.group(1)
                all_dcs = re.findall(r"<div class='lot-dc[^']*'[^>]*>(.*?)</div>", section, re.DOTALL)
                all_dcs = [re.sub(r'<[^>]+>', '', v).strip().replace('&nbsp;', ' ').strip() for v in all_dcs]
                
                # Find this draw's two_digit
                # Pattern: [fp, empty, 3last, 2d, fp2, empty, 3last2, 2d2, ...]
                # Find the index of this draw's first_prize
                fp = draw['first_prize']
                for j in range(len(all_dcs)):
                    val = re.sub(r'\s+', '', all_dcs[j])
                    if val[-6:] == fp or val == fp:
                        # Found first_prize at index j
                        # two_digit should be at index j+3
                        if j + 3 < len(all_dcs):
                            two_digit = re.sub(r'\s+', '', all_dcs[j+3])
                            if re.match(r'^\d{2}$', two_digit):
                                # Update
                                idx = next(k for k, d in enumerate(data) if d['draw_date'] == draw_date)
                                data[idx]['two_digit'] = two_digit
                                fixed += 1
                        break
        
        if (i + 1) % 10 == 0 or i == len(to_fix) - 1:
            print(f"  [{i+1}/{len(to_fix)}] fixed={fixed}", flush=True)
        
        if (i + 1) % 10 == 0:
            time.sleep(1.5)
    
    # Save
    with open(scraped_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nแก้ไขเสร็จ: {fixed} งวด")
    
    # Verify
    still_missing = sum(1 for d in data if d['draw_date'][:4] in ['1990','1991','1992','1993','1994'] 
                        and (not d.get('two_digit') or d['two_digit'] == ''))
    print(f"ยังขาด two_digit: {still_missing} งวด")

if __name__ == '__main__':
    fix_1990s_data()
