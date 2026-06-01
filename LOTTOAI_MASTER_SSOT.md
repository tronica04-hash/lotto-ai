# LOTTOAI — MASTER SSOT (Single Source of Truth)

> **เวอร์ชัน:** 2.0.0
> **อัปเดตล่าสุด:** 2026-06-02
> **เจ้าของ:** กิจ (Kritt Jangkjang)
> **ภาษาสื่อสาร:** ภาษาไทย
> **ความรู้ coding ของเจ้าของ:** ศูนย์ — อธิบายทีละขั้นเป็นภาษาไทย

---

## 📋 สารบัญ

1. [ภาพรวมโปรเจค](#1-ภาพรวมโปรเจค)
2. [Tech Stack](#2-tech-stack)
3. [โครงสร้างไฟล์](#3-โครงสร้างไฟล์)
4. [Database Schema](#4-database-schema)
5. [API Endpoints](#5-api-endpoints)
6. [Authentication](#6-authentication)
7. [Business Logic](#7-business-logic)
8. [Data Sources](#8-data-sources)
9. [Design System](#9-design-system)
10. [UI/UX — เปรียบเทียบกับเว็บหวยอื่น](#10-uiux--เปรียบเทียบกับเว็บหวยอื่น)
11. [Deployment](#11-deployment)
12. [Roadmap](#12-roadmap)
13. [Known Issues](#13-known-issues)
14. [Environment Variables](#14-environment-variables)
15. [Supabase Configuration](#15-supabase-configuration)

---

## 1. ภาพรวมโปรเจค

### คืออะไร
LottoAI คือเว็บแอปพลิเคชันวิเคราะห์สลากกินแบ่งรัฐบาลไทย (หวย) ด้วย AI + สถิตย์
- ดึงข้อมูลหวยย้อนหลัง **779 งวด (1990-2026)** — 36 ปี
- วิเคราะห์สถิติ: เลขร้อน, เลขเย็น, เลข Due, ความถี่
- AI ทำนายเลข + ทำนายฝัน + เช็คเลข
- ระบบ Dashboard หลังล็อกอิน (6 tabs)
- Freemium model: ใช้ฟรี / Premium เต็มรูปแบบ

### สถานะปัจจุบัน (Phase 2 ✅ เสร็จ)
- ✅ Landing page + Login/Register + Dashboard 6 tabs
- ✅ Supabase Auth (email/password)
- ✅ Database: **779 งวด (1990-2026)**
- ✅ Analyzer engine: เลขร้อน/เย็น/Due + AI prediction
- ✅ ทำนายฝัน (44 คำ)
- ✅ เช็คเลข (6 หลัก, ตรวงกับรางวัลทุกประเภท)
- ✅ Re-scrape ข้อมูลเก่า 1990-2005 (เพิ่ม 347 งวด)
- ✅ สร้าง views ใน Supabase (v_lotto_stats)
- ✅ สร้าง RPC function (import_lotto_data) สำหรับ import ข้อมูล
- ❌ ยังไม่ได้ deploy บน Vercel
- ❌ ยังไม่มีระบบ Premium
- ❌ ยังไม่มี auto update ข้อมูล

---

## 2. Tech Stack

| ส่วน | เทคโนโลยี | หมายเหตุ |
|------|-----------|----------|
| Frontend | Next.js 16.2.6 + React 19 + TypeScript | Turbopack |
| Styling | Inline CSS เท่านั้น | Tailwind compile มีปัญหาบน production |
| Backend | Supabase (PostgreSQL) | Free tier |
| Auth | Supabase Auth | Email/password |
| Database | PostgreSQL via Supabase | Tables: lotto_results, user_profiles, query_logs, payments |
| Scraper | Python 3 + urllib + regex | ASP.NET site ต้องใช้ regex |
| Hosting | WSL local + PM2 | `npx next start --hostname 0.0.0.0 --port 3000` |
| Hosting (เป้าหมาย) | Vercel + Supabase | Free tier |

### เหตุผลที่ใช้ Inline CSS
Tailwind CSS 4 บน Next.js 16 + Turbopack มีปัญหา: CSS ถูก inject ผ่าน JavaScript ถ้า JS ไม่โหลด CSS ก็ไม่มี ทำให้หน้าเว็บ "เละ" ทุกหน้าจึงใช้ `style={{...}}` inline แทน — **ห้ามเปลี่ยนเป็น Tailwind classes**

---

## 3. โครงสร้างไฟล์

```
D:\lotto-ai\
├── src\
│   ├── app\
│   │   ├── (auth)\
│   │   │   ├── login/page.tsx          # หน้า login
│   │   │   └── register/page.tsx       # หน้า register
│   │   ├── dashboard/page.tsx          # Dashboard หลัก — 6 tabs (ภาพรวม/สถิติ/AI/ฝัน/ผลหวย/เช็คเลข)
│   │   ├── dream/page.tsx              # ทำนายฝัน (public)
│   │   ├── results/page.tsx            # ผลหวยย้อนหลังทั้งหมด (public)
│   │   ├── stats/
│   │   │   ├── hot-cold/page.tsx       # สถิติ Hot/Cold/Due (public)
│   │   │   └── ai/page.tsx             # AI prediction (public)
│   │   ├── api/
│   │   │   ├── check/route.ts          # API: เช็คเลข
│   │   │   ├── lotto/analyze/route.ts  # API: วิเคราะห์ (ยังไม่ได้ใช้)
│   │   │   └── scraper/run/route.ts    # API: รัน scraper (ยังไม่ได้ใช้)
│   │   ├── layout.tsx                  # Root layout
│   │   ├── page.tsx                    # Landing page
│   │   └── globals.css                 # CSS พื้นฐาน
│   └── lib\
│       ├── supabase.ts                 # Supabase client
│       ├── analyzer.ts                 # Analyzer engine (ยังไม่ได้ใช้ — logic อยู่ใน dashboard)
│       └── scraper.ts                  # Scraper utility
├── supabase\
│   ├── schema.sql                      # Database schema
│   ├── import-script.sql               # Import function + views
│   └── migrate-xxx.sql                 # Migration scripts
├── scripts\
│   ├── scrape-myhora.py               # Scraper myhora (รุ่นเก่า)
│   ├── scrape-full.py                 # Scraper เต็ม (parse ทุกรางวัล)
│   ├── scrape-older.py                # Scrape ย้อนหลัง (ก่อน 2006)
│   ├── merge-vicha.py                 # Merge myhora + vicha-w
│   └── import-final.py                # Import ข้อมูลเข้า Supabase
├── LOTTOAI_MASTER_SSOT.md              # ไฟล์นี้
├── .env.local
├── package.json
├── tailwind.config.ts                  # มีแต่ไม่ได้ใช้
├── postcss.config.mjs
└── next.config.ts
```

### ไฟล์ข้อมูล (temp)
```
/tmp/myhora-lotto/all_prizes.json       # ข้อมูลหวยรวม 779 งวด (ไฟล์หลัก)
```

### ข้อมูลในแต่ละสถานะ (สรุป)
```
- Web display: วันที่ 1 และ 16 ของทุกเดือน (งวด)
- Buddhist Year = CE + 543
- Total: 779 งวด
- First: 1990-01-16
- Last:  2026-06-01
```

---

## 4. Database Schema

### Table: `lotto_results`
ข้อมูลผลหวยแต่ละงวด

| Column | Type | Default | คำอธิบาย |
|--------|------|---------|----------|
| id | BIGINT | AUTO | Primary key |
| draw_date | DATE | NOT NULL | วันที่ออกรางวัล (YYYY-MM-DD) |
| draw_number | TEXT | | เลขชุด (YYMMDD) |
| first_prize | TEXT | | รางวัลที่ 1 (6 หลัก) |
| nearby_1st | JSONB | '[]' | รางวัลข้างเคียง (2 ตัว) |
| second_prize | JSONB | '[]' | รางวัลที่ 2 (5 ตัว) |
| third_prize | JSONB | '[]' | รางวัลที่ 3 (10 ตัว) |
| prize_4 | JSONB | '[]' | รางวัลที่ 4 (50 ตัว) |
| prize_5 | JSONB | '[]' | รางวัลที่ 5 (100 ตัว) |
| two_digit | TEXT | | เลขท้าย 2 ตัว |
| three_digit_first | JSONB | '[]' | เลขหน้า 3 ตัว |
| three_digit_last | JSONB | '[]' | เลขท้าย 3 ตัว (2 ตัว ปัจจุบัน, 4 ตัว เก่า) |
| created_at | TIMESTAMPTZ | NOW() | |
| updated_at | TIMESTAMPTZ | NOW() | |

**Indexes:** `idx_lotto_draw_date` (draw_date DESC), `idx_lotto_draw_number`
**Unique:** `draw_date`

### Views

| View | คำอธิบาย |
|------|----------|
| `v_lotto_stats` | สรุปสถิติ: total_draws, first_draw, last_draw, has_first_prize, has_two_digit, has_three_digit_first, has_three_digit_last |
| `v_hot_2digit` | เลขร้อน 2 ตัว (top 10 ตามความถี่) |
| `v_hot_3digit_first` | เลขร้อน 3 ตัวหน้า (top 10) |
| `v_hot_3digit_last` | เลขร้อน 3 ตัวท้าย (top 10) |
| `v_due_2digit` | เลขนาย 2 ตัว (ไม่ออกนานสุด top 10) |

### RPC Functions

| Function | คำอธิบาย |
|----------|----------|
| `import_lotto_data(data_json JSONB)` | Upsert ข้อมูลหวยเป็น batch — ใช้จาก Python script |
| `reset_daily_queries()` | รีเซ็ต queries_today (ยังไม่ได้ schedule) |

### Table: `user_profiles`

| Column | Type | Default |
|--------|------|---------|
| id | UUID | PK → auth.users |
| email | TEXT | |
| plan | TEXT | 'free' |
| queries_today | INTEGER | 0 |
| queries_limit | INTEGER | 5 |
| last_query_date | DATE | CURRENT_DATE |

### Table: `query_logs` / `payments`
ยังไม่ได้ใช้งานจริง

---

## 5. API Endpoints

| Route | Method | คำอธิบาย | สถานะ |
|-------|--------|----------|-------|
| `/` | GET | Landing page | ✅ |
| `/login` | GET | หน้า login | ✅ |
| `/register` | GET | หน้า register | ✅ |
| `/dashboard` | GET | Dashboard หลัก (6 tabs) — ต้องล็อกอิน | ✅ |
| `/results` | GET | ผลหวยย้อนหลังทั้งหมด + filter ปี/เดือน | ✅ |
| `/stats/hot-cold` | GET | สถิติ Hot/Cold/Due + กราฟ | ✅ |
| `/stats/ai` | GET | AI prediction | ✅ |
| `/dream` | GET | ทำนายฝัน | ✅ |
| `/api/check` | POST | เช็คเลข 6 หลัก | ✅ |
| `/api/lotto/analyze` | GET | วิเคราะห์ (ยังไม่ได้ใช้) | ⚠️ |
| `/api/scraper/run` | POST | รัน scraper (ยังไม่ได้ใช้) | ❌ |

---

## 6. Authentication

- **วิธี:** Supabase Auth (email/password)
- **Trigger:** `on_auth_user_created` — สร้าง user_profiles อัตโนมัติ
- **RLS:** เปิดสำหรับ user_profiles, query_logs, payments
- **Redirect URLs:** `http://localhost:3000`, `http://192.168.33.110:3000`

---

## 7. Business Logic

### Dashboard Tabs (6 tabs)

| Tab | ฟีเจอร์ |
|-----|---------|
| 📊 ภาพรวม | สรุปสถิติ + AI prediction + เลขร้อน/เย็น/Due tables |
| 🔥 สถิติ | กราฟ frequency bar (hot/cold/due) |
| 🤖 AI | AI ทำนาย + confidence score |
| 💭 ทำนายฝัน | พจนานุกรม 44 คำ + ค้นหา + partial match |
| 📋 ผลหวย | ตารางผล + filter ปี/เดือน |
| 🔍 เช็คเลข | กรอก 6 หลัก → เช็ครางวัลทุกประเภท |

### Analyzer Engine
- **Two-digit frequency:** นับความถี่ 00-99
- **Hot/Cold/Due:** เรียงตามความถี่ + gap
- **AI Prediction:** Weighted score (freq × 0.6 + due × 0.4)
- **Confidence:** 15-45% (ไม่เกิน 50% เพราะเป็นสถิติ)

### Scraper Logic
- **URL:** `https://myhora.com/lottery/result-{DD}-{MM}-{BY}.aspx`
- **งวด:** ทุกวันที่ 1 และ 16
- **ข้อมูลครบ:** ปี 2002+ (รางวัล 1-5 + ข้างเคียง + หน้า/ท้าย 3)
- **ข้อมูลบางส่วน:** ปี 1990-2001 (รางวัล 1 + ท้าย 2/3)

### ข้อมูลความครบใน Database

| รางวัล | จำนวน | อัตรา |
|--------|-------|-------|
| first_prize | 779 | 100% |
| two_digit | 779 | 100% |
| three_digit_last | 779 | 100% |
| second_prize | 555 | 71% (ปี 2002+) |
| third_prize | 555 | 71% |
| prize_4 | 555 | 71% |
| prize_5 | 555 | 71% |
| nearby_1st | 555 | 71% |
| three_digit_first | ~400 | ~51% |

---

## 8. Data Sources

### แหล่งหลัก: myhora.com (Scrape)
- **ข้อมูล:** 779 งวด (1990-2002)
- **Format:** ASP.NET HTML → parse ด้วย regex
- **ความน่าเชื่อถือ:** สูง

### แหล่งเสริม: vicha-w/thai-lotto-archive (GitHub)
- **ข้อมูล:** 463 งวด (2006-2002)
- **Format:** Text files (structured)
- **ใช้เพิ่ม:** เลขหน้า 3, รางวัลที่ 2-5 สำหรับงวดที่ myhora ไม่มี
- **Merge แล้ว:** ทุกข้อมูลอยู่ใน `all_prizes.json` และ Supabase

### แหล่งที่ไม่ใช้

| แหล่ง | เหตุผล |
|-------|--------|
| heart/Data-Set-Thai-Lotto | ข้อมูลเพี้ยน |
| lotto.co.th (official) | ไม่มีข้อมูลย้อนหลัง |

---

## 9. Design System

### สี
| สี | ค่า | ใช้สำหรับ |
|----|-----|-----------|
| Background | `linear-gradient(135deg, #0f172a, #581c87, #0f172a)` | พื้นหลัง |
| Card BG | `rgba(30,41,59,0.5)` | การ์ด |
| Card Border | `rgba(148,163,184,0.12-0.2)` | ขอบการ์ด |
| Primary | `#9333ea` | ปุ่ม, active |
| Text | `#e2e8f0` | ตัวอักษรหลัก |
| Text secondary | `#94a3b8` | ตัวอักษรรอง |
| Text muted | `#64748b` / `#475569` | ตัวอักษรเบา |
| Hot | `#f87171` + `rgba(239,68,68,0.1-0.15)` bg | เลขร้อน |
| Cold | `#60a5fa` + `rgba(59,130,246,0.1-0.15)` bg | เลขเย็น |
| Due | `#fbbf24` + `rgba(245,158,11,0.1-0.15)` bg | เลข Due |
| Prediction | `#c084fc` | ตัวเลขทำนาย |
| Gold | `#fbbf24` | รางวัลที่ 1 |

### Typography
- Font: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- ไม่ใช้ Google Fonts

### Components
- **การ์ด:** `background:rgba(30,41,59,0.5); border:1px solid rgba(148,163,184,0.12); border-radius:10-16px; padding:16-22px`
- **Chip:** `padding:3-5px 8-12px; border-radius:4-6px; font-family:monospace; font-weight:bold; font-size:13-14px`
- **ตาราง:** `border-collapse:collapse; width:100%; font-size:12-13px`

### Responsive
- Grid: `grid-template-columns: repeat(auto-fit, minmax(220-260px, 1fr))`
- Mobile: ซ่อนตาราง แสดง cards

---

## 10. UI/UX — เปรียบเทียบกับเว็บหวยอื่น

### สำรวจเว็บหวยไทยที่คนใช้มาก

| เว็บ | จุดเด่น | จุดด้อย | เราต้องมี? |
|------|---------|---------|------------|
| **sanook** | แปลฝันดี, filter งวด, วิเคราะห์, หวยลาว, LINE share | ไม่มีฐานข้อมูลลึก | ✅ แปลฝัน, ✅ filter, ✅ หวยลาว (ในอนาคต) |
| **thairath** | สถิติลึก (แยกวัน/เดือน), AI prediction, Archive แยกปี | ไม่มีฟรีแถมต้องสมัคร | ✅ สถิติลึก, ✅ AI, ✅ Archive |
| **myhora** | dropdown เลือกงวด, เช็คเลข, สถิติถี่ | UI เก่า, ไมอ mobile-friendly | ✅ dropdown, ✅ เช็คเลข, ✅ สถิติ |
| **siamlotto** | ฟีเจอร์ครบ, หวยนอก, VIP system | UI รก, โฆษณาเยอะ | ❌ หมดความจำเป็น — เราทำให้กว่า |
| **huayalliance** | ตรวจผล, สถิติ, ทีเด็ด | ต้องสมัคร | ✅ สถิติฟรี |

### Features ที่เว็บอื่นมี แต่เรายังไม่มี

| Feature | อธิบาย | ลำดับ |
|---------|--------|-------|
| **ปฏิทินหวย** | แสดงวันหวย, ปฏิทินเดือน | 🔜 ต้องทำ |
| **แชร์ Social** | แชร์ผล LINE/Facebook/Twitter | 🔜 ต้องทำ |
| **เลขจากฝัน** | แปลฝันเป็นเลข (สำหรับแต่ละเว็บ) | ✅ มีแล้ว |
| **วิเคราะห์ Pattern** | วิเคราะห์ pattern เลขออก | 🔜 ต้องทำ |
| **หวยนอก/หวยลาว** | ข้อมูลหวยลาว/หวยนอก | 🔜 Phase 3 |
| **VIP system** | สมาชิกพิเศษ | 🔜 Phase 3 |
| **ระบบแจ้งเตือน** | LINE/Telegram แจ้งผล | 🔜 Phase 3 |
| **API ให้ใช้ภายนอก** | API สำหรับนักพัฒนา | 🔜 Phase 3 |
| **กราฟ interactive** | กราฟแสดงข้อมูลแบบ interactive | 🔜 ต้องทำ |
| **เทียบเลขหวย** | เทียบเลขที่ซื้อกับผลรางวัล (ตรวจชุด) | 🔜 ต้องทำ |

### Features ที่เรามีแล้ว (vs คู่แข่ง)

| Feature | สถานะ |
|---------|-------|
| Dashboard หลังล็อกอิน | ✅ 6 tabs |
| เช็คเลข 6 หลัก | ✅ เช็คทุกรางวัล |
| สถิติ Hot/Cold/Due | ✅ กราฟ bar |
| AI ทำนาย | ✅ confidence score |
| ทำนายฝัน | ✅ 44 คำ + partial match |
| ผลหวยย้อนหลัง | ✅ filter ปี/เดือน |
| Database ย้อนหลัง 36 ปี | ✅ 779 งวด |
| Mobile responsive | ✅ |

---

## 11. Deployment

### ปัจจุบัน
- **รันบน:** WSL (Windows Subsystem for Linux)
- **คือคำสั่ง:**
  ```bash
  cd /mnt/d/lotto-ai
  npx next build
  npx next start --hostname 0.0.0.0 --port 3000
  ```
- **เข้าถึง:** `http://192.168.33.110:3000`

### เป้าหมาย (ยังไม่ทำ)
- **Frontend:** Vercel (free)
- **Backend:** Supabase
- **ขั้นตอน:** สร้าง Git repo → Push → เชื่อม Vercel

---

## 12. Roadmap

### Phase 1-2: ✅ เสร็จแล้ว
- Landing, Auth, Dashboard 6 tabs
- Database 779 งวด (1990-2026)
- Analyzer + AI + ทำนายฝัน
- Scraper + Import pipeline

### Phase 3: ต้องทำต่อ
| งาน | รายละเอียด | ลำดับ |
|-----|------------|-------|
| ปฏิทินหวย | แสดงวันหวย, ปฏิทินเดือน | 🔜 สำคัญ |
| แชร์ Social | แชร์ผล LINE/Facebook | 🔜 สำคัญ |
| เทียบเลข (check set) | อัพโหลด/วางเลขหลายตัว เช็คพร้อมกัน | 🔜 สำคัญ |
| กราฟ interactive | กราฟ frequency + time series | 🔜 สำคัญ |
| ระบบเงิน | Stripe/PromptPay | 🔜 Phase 3 |
| Deploy Vercel | Auto deploy จาก Git | 🔜 Phase 3 |
| LINE/Telegram bot | แจ้งเตือนผลหวย | 🔜 Phase 3 |
| หวยนอก/ลาว | ข้อมูลหวยลาว | 🔜 Phase 3 |
| VIP system | สมาชิกพิเศษ | 🔜 Phase 3 |
| SEO | ปรับแต่ง SEO | 🔜 Phase 3 |

---

## 13. Known Issues

| ปัญหา | สาเหตุ | สถานะ |
|-------|--------|-------|
| Tailwind CSS ไม่ทำงานบน production | Turbopack inject CSS ผ่าน JS | ✅ แก้แล้ว (inline style) |
| myhora บางงวดไม่มีข้อมูล | งวดเก่ามาก / ไม่ใช่วันหวยจริง | ✅ ข้อมูลเก่าบางส่วนไม่สมบูรณ์ — ยอมรับได้ |
| `nearby_1st`, `prize_4`, `prize_5` บางงวดว่าง | ข้อมูลเก่าไม่มีในเว็บต้นฉบับ | ✅ ยอมรับได้ |
| Port 3000 ไม่ว่าง | WSL process เก่าครอง | ✅ แก้ด้วย `fuser -k 3000/tcp` |
| Supabase rate limit | Insert เร็วเกินไป | ✅ แก้ด้วย delay + batch |
| SSOT ไม่อัพเดต | ลืมอัปเดต | ✅ อัปเดตแล้ว (ปัจจุบัน) |

---

## 14. Environment Variables

ไฟล์ `.env.local`

```
NEXT_PUBLIC_SUPABASE_URL=https://jiulxmylgwaaygdytdfj.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbG...uvns (truncated — ดูในไฟล์จริง)
```

**Supabase Project Ref:** `jiulxmylgwaaygdytdfj`
**Supabase Dashboard:** `https://supabase.com/dashboard/project/jiulxmylgwaaygdytdfj`

> ⚠️ **สำคัญ:** `SUPABASE_SERVICE_ROLE_KEY` ไม่ได้เก็บใน `.env.local` — ใช้แค่ตอน import ข้อมูลผ่าน Python script (จะลบทิ้งหลังใช้)

---

## 15. Supabase Configuration

### RLS Policies
- `user_profiles`: เจ้าของอ่าน/แก้ไขได้
- `query_logs`: เจ้าของ insert/select ได้
- `payments`: เจ้าของ insert/select ได้
- `lotto_results`: public read (ทุกคนอ่านได้)

### Triggers
- `on_auth_user_created`: สร้าง user_profiles อัตโนมัติ

### Functions
- `import_lotto_data(data_json)`: Upsert batch ข้อมูลหวย
- `reset_daily_queries()`: รีเซ็ต query count (ยังไม่ได้ schedule)

---

## 📝 Notes สำหรับ AI ที่มาทำต่อ

1. **อย่าลบ inline style** — ทุกหน้าใช้ inline CSS เพราะ Tailwind มีปัญหา
2. **Supabase client** — URL + key อยู่ใน `src/lib/supabase.ts` พร้อม fallback
3. **รัน server:**
   ```bash
   cd /mnt/d/lotto-ai
   npx next build
   npx next start --hostname 0.0.0.0 --port 3000
   ```
4. **เข้าเว็บจาก Windows:** `http://192.168.33.110:3000`
5. **Supabase SQL Editor:** https://supabase.com/dashboard/project/jiulxmylgwaaygdytdfj/sql
6. **ข้อมูลหวย:** 779 งวดใน table `lotto_results`
7. **Scraper:** `scripts/scrape-full.py` (รันด้วย `python3 scripts/scrape-full.py`)
8. **Import:** `scripts/import-final.py` (รันด้วย `python3 scripts/import-final.py`)
9. **ห้าม commit service role key** — key นี้ลบได้เลยจาก Supabase dashboard ถ้าต้องการ
10. **Git:** ยังไม่มี Git repo — ถ้าจะ deploy ต้องสร้างก่อน

---

*อัปเดตล่าสุด: 2026-06-02 by OWL (Hermes Agent)*
*หมายเหตุ: เอกสารนี้ควรอัปเดตทุกครั้งที่มีการเปลี่ยนแปลงสำคัญ*
