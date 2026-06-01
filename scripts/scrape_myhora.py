#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI webhook + scraper for https://myhora.com/lottery
ดึงข้อมูลทุกงวด (วันที่ 1 และ 16 ของแต่ละเดือน) จนกว่าจะเจอ 404
"""

import re
import csv
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

import httpx  # async HTTP client (install via `pip install httpx fastapi uvicorn`)

# ----------------------------------------------------------------------
# 1️⃣ Regex patterns (ตาม HTML ของหน้า myhora)
# ----------------------------------------------------------------------
PATTERNS = {
    "draw_date": r"ตรวจหวย.*งวด\s+(\d{1,2}\s+[ก-ฮ]+?\s+\d{4})",          # ตัวอย่าง: 1 มิถุนายน 2569
    "first_prize": r"รางวัลที่\s+1\s*\((\d+)\)",
    "nearby_1st": r"ข้างเคียง\s*\((\d+)\)",
    "second_prize": r"รางวัลที่\s+2\s*\(([\d,]+)\)",
    "third_prize": r"รางวัลที่\s+3\s*\(([\d,]+)\)",
    "prize_4": r"รางวัลที่\s+4\s*\(([\d,]+)\)",
    "prize_5": r"รางวัลที่\s+5\s*\(([\d,]+)\)",
    "three_front": r"เลขหน้า\s+3\s+ตัว\s*\(([\d,]+)\)",
    "three_back": r"เลขท้าย\s+3\s+ตัว\s*\(([\d,]+)\)",
    "two_back": r"เลขท้าย\s+2\s+ตัว\s*\((\d+)\)",
}

# ----------------------------------------------------------------------
# 2️⃣ Helper: ดึงข้อมูลจากหน้าเดียว
# ----------------------------------------------------------------------
def parse_draw(html: str) -> Dict[str, Optional[str]]:
    data = {}
    for key, pat in PATTERNS.items():
        m = re.search(pat, html, re.IGNORECASE)
        data[key] = m.group(1).replace(",", "").strip() if m else None
    # แปลงวันที่เป็น ISO (yyyy-mm-dd)
    if data.get("draw_date"):
        try:
            th_months = {
                "มกราคม": "01", "กุมภาพันธ์": "02", "มีนาคม": "03",
                "เมษายน": "04", "พฤษภาคม": "05", "มิถุนายน": "06",
                "กรกฎาคม": "07", "สิงหาคม": "08", "กันยายน": "09",
                "ตุลาคม": "10", "พฤศจิกายน": "11", "ธันวาคม": "12",
            }
            d, m_th, y_th = data["draw_date"].split()
            m = th_months[m_th]
            y = str(int(y_th) - 543)
            data["draw_date_iso"] = f"{y}-{m}-{int(d):02d}"
        except Exception:
            data["draw_date_iso"] = None
    return data

# ----------------------------------------------------------------------
# 3️⃣ Scraper หนึ่งงวด (sync version – ใช้ใน loop ธรรมดา)
# ----------------------------------------------------------------------
def fetch_draw(date: datetime) -> Optional[Dict[str, str]]:
    url = f"https://myhora.com/lottery/result-{date.day:02d}-{date.month:02d}-{date.year + 543}.aspx"
    try:
        r = httpx.get(url, timeout=15)
        if r.status_code != 200:
            return None
        return parse_draw(r.text)
    except Exception as e:
        print(f"[ERROR] {url} → {e}")
        return None

# ----------------------------------------------------------------------
# 4️⃣ สร้าง CSV/JSON ทั้งหมด (ใช้ loop ปิดกั้นด้วย 404)
# ----------------------------------------------------------------------
def build_full_dataset(
    start_year: int = 1900,
    end_year: int = datetime.now().year,
    out_dir: Path = Path("tmp/lotto_myhora"),
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "lotto_myhora_full.csv"

    header = [
        "draw_date",
        "first_prize", "nearby_1st",
        "second_prize", "third_prize",
        "prize_4", "prize_5",
        "three_front", "three_back", "two_back",
    ]

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for yr in range(end_year, start_year - 1, -1):
            for month in range(1, 13):
                for day in (1, 16):
                    try_date = datetime(yr, month, day)
                    data = fetch_draw(try_date)
                    if not data:
                        continue
                    row = [
                        data.get("draw_date_iso"),
                        data.get("first_prize"),
                        data.get("nearby_1st"),
                        data.get("second_prize"),
                        data.get("third_prize"),
                        data.get("prize_4"),
                        data.get("prize_5"),
                        data.get("three_front"),
                        data.get("three_back"),
                        data.get("two_back"),
                    ]
                    writer.writerow(row)
    return csv_path

# ----------------------------------------------------------------------
# 5️⃣ FastAPI Webhook
# ----------------------------------------------------------------------
from fastapi import FastAPI, Body, HTTPException

app = FastAPI(
    title="myhora‑lottery‑scraper",
    version="1.0.0",
    description="Webhook ที่ดึงข้อมูลหวยจาก myhora.com ทุกงวดหรือเฉพาะวันที่กำหนด",
)

@app.post("/api/scrape_myhora", summary="ดึงข้อมูลจาก myhora")
async def scrape_myhora(payload: Dict = Body(...)):
    date_str = payload.get("date")
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(400, "date must be ISO format YYYY-MM-DD")
        data = fetch_draw(dt)
        if not data:
            raise HTTPException(404, f"ข้อมูลสำหรับ {date_str} ไม่พบ")
        return {"status": "ok", "rows": 1, "data": data}
    else:
        csv_path = build_full_dataset()
        static_url = f"/static/{csv_path.name}"
        return {
            "status": "ok",
            "rows": sum(1 for _ in open(csv_path, "r", encoding="utf-8")) - 1,
            "file_url": static_url,
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "scripts.scrape_myhora:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
