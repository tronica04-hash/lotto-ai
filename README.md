# LottoAI

เว็บวิเคราะห์หวยรัฐบาลไทยด้วย AI

## Stack

- **Frontend:** Next.js 16 + React 19 + Tailwind CSS 4
- **Backend:** Next.js API Routes
- **Database:** Supabase (PostgreSQL)
- **Auth:** Supabase Auth
- **Deploy:** Vercel (frontend) + Supabase (DB)

## โครงสรคไฟล์

```
lotto-ai/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── dashboard/page.tsx
│   │   ├── api/
│   │   │   ├── lotto/analyze/route.ts
│   │   │   └── scraper/run/route.ts
│   │   └── page.tsx (landing)
│   ├── components/
│   ├── lib/
│   │   ├── supabase.ts
│   │   ├── analyzer.ts
│   │   └── scraper.ts
│   └── types/
│       └── index.ts
├── supabase/
│   └── schema.sql
├── scripts/
│   └── import-lotto.ts
├── .env.example
└── package.json
```

## ขั้นตอนติดตั้ง

### 1. ติดตั้ง Supabase

1. ไปที่ https://supabase.com สร้าง project ใหม่ (ฟรี)
2. ใน SQL Editor รัน `supabase/schema.sql`
3. คัดลอง `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
4. วางลงใน `.env.local`

### 2. ติดตั้ง dependencies

```bash
cd D:\lotto-ai
npm install
```

### 3. รัน dev server

```bash
npm run dev
```

เปิด http://localhost:3000

### 4. Import ข้อมูลหวย

```bash
# จาก CSV
npx tsx scripts/import-lotto.ts --csv=data.csv

# จาก JSON
npx tsx scripts/import-lotto.ts --json=data.json
```

### 5. Deploy บน Vercel

```bash
npx vercel
```

## ฟีเจอร์

- ✅ Landing page + Auth (login/register)
- ✅ Dashboard แสดงสถิติหวย
- ✅ AI analysis engine (hot/cold/due/prediction)
- ✅ ระบบ import ข้อมูล
- ❌ ระบบเงิน (Phase 2)
- ❌ ระบบ scraper ดึงข้อมูลอัตโนมัติ (Phase 2)
- ❌ ระบบ premium/vip (Phase 2)
