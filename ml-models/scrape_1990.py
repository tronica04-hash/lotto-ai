#!/usr/bin/env python3
"""
Scrape ข้อมูลหวย 1990-1994 จากแหล่งอื่น
myhora.com ไม่มีข้อมูลก่อน 1995 ต้องหาจากแหล่งอื่น
"""
import urllib.request, json, re, os

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode('utf-8', errors='replace')
    except:
        return None

# ลอง lotto.sanook.com
print("ลอง lotto.sanook.com...")
html = fetch_url("https://lotto.sanook.com/result/")
if html:
    # หา pattern ข้อมูลหวย
    dates = re.findall(r'(\d{1,2}/\d{1,2}/\d{4})', html)
    numbers = re.findall(r'\b(\d{6})\b', html)
    print(f"  Found {len(dates)} dates, {len(numbers)} 6-digit numbers")
    if dates:
        print(f"  Sample dates: {dates[:5]}")
    if numbers:
        print(f"  Sample numbers: {numbers[:5]}")

# ลอง lotto.thai
print("\nลอง lotto.thai...")
html = fetch_url("https://www.lotto.thai/")
if html:
    print(f"  Length: {len(html)}")
else:
    print("  ไม่สามารถเข้าถึงได้")

# ลอง web archive
print("\nลอง web.archive.org...")
html = fetch_url("https://web.archive.org/web/2020/https://www.mylotto.co.th/")
if html:
    print(f"  Length: {len(html)}")
else:
    print("  ไม่สามารถเข้าถึงได้")

# ลองข้อมูลจาก GitHub API
print("\nลองค้นหาข้อมูลจาก GitHub...")
try:
    url = "https://api.github.com/search/repositories?q=thai+lotto+1990+archive&sort=stars"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        j = json.loads(r.read().decode())
        items = j.get('items', [])
        print(f"  Found {len(items)} repos")
        for item in items[:5]:
            print(f"    - {item['full_name']}: {item.get('description', '')[:60]}")
except Exception as e:
    print(f"  Error: {e}")

# ลองดึงจาก GitHub raw content
print("\nลองดึงข้อมูลจาก GitHub repos ที่เจอ...")
github_urls = [
    "https://raw.githubusercontent.com/siwadon/thai-lotto/master/data/lotto_results.json",
    "https://raw.githubusercontent.com/siwadon/thai-lotto/main/data/lotto_results.json",
]

for url in github_urls:
    html = fetch_url(url)
    if html:
        print(f"  OK: {url[:60]}... -> {len(html)} bytes")
        try:
            j = json.loads(html)
            if isinstance(j, list) and len(j) > 0:
                print(f"    Items: {len(j)}")
                first = j[0]
                if isinstance(first, dict):
                    print(f"    Keys: {list(first.keys())[:10]}")
                    dates = [item.get('draw_date', item.get('date', '')) for item in j if isinstance(item, dict)]
                    dates = [d for d in dates if d]
                    if dates:
                        print(f"    Date range: {min(dates)} -> {max(dates)}")
                        old = [d for d in dates if d < '1995-01-01']
                        print(f"    Before 1995: {len(old)}")
        except:
            print(f"    First 200: {html[:200]}")
    else:
        print(f"  FAIL: {url[:60]}...")

print("\n--- สรุป ---")
print("myhora.com ไม่มีข้อมูลก่อน 1995")
print("ต้องหาแหล่งอื่นหรือใช้ข้อมูลจากหนังสือพิมพ์/archive")
