# LOTTOAI — PROJECT SSOT (Single Source of Truth)

> **Version:** 3.0.0
> **Last Updated:** 2026-06-13
> **Author:** OWL (Lead Architect, Hermes Agent)
> **Language:** English (Technical) / Thai (Stakeholder Communication)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Technical Architecture](#2-technical-architecture)
3. [Logical Flow — How the System Works](#3-logical-flow--how-the-system-works)
4. [Data Schema](#4-data-schema)
5. [API & Integration](#5-api--integration)
6. [Formula Library — Prediction Models](#6-formula-library--prediction-models)
7. [Scoring System](#7-scoring-system)
8. [Genetic Algorithm — Evolution Engine](#8-genetic-algorithm--evolution-engine)
9. [Web Application (Next.js)](#9-web-application-nextjs)
10. [Deployment](#10-deployment)
11. [Future-Proofing — Extension Points](#11-future-proofing--extension-points)
12. [Known Issues & Technical Debt](#12-known-issues--technical-debt)
13. [Environment & Credentials](#13-environment--credentials)
14. [Glossary](#14-glossary)

---

## 1. Executive Summary

### What is LottoAI?

LottoAI is a **Thai Government Lottery (สลากกินแบ่งรัฐบาล) prediction system** that combines statistical analysis, machine learning, and genetic algorithms to generate lottery number predictions.

### Core Philosophy

> "Beat the game statistically — not by magic, but by rigorous mathematical exploration."

The system acknowledges that lottery draws are **random events with negative expected value** (avg loss ~74 baht per ticket). The goal is NOT to guarantee wins, but to:
1. Explore whether any statistical patterns exist in 36 years of historical data
2. Build a rigorous backtesting framework to validate any discovered patterns
3. Create a web application that makes lottery analysis accessible to everyone

### Project Status (as of 2026-06-13)

| Component | Status | Notes |
|-----------|--------|-------|
| Data Collection | ✅ Complete | 776 draws (1995-2026) in Supabase |
| Web Frontend | ✅ Complete | Next.js 16 + React 19 + TypeScript |
| Auth System | ✅ Complete | Supabase Auth (email/password) |
| Dashboard | ✅ Complete | 6 tabs: Overview/Stats/AI/Dream/Results/Check |
| Dream Prediction | ✅ Complete | 44 dream keywords |
| Number Checker | ✅ Complete | 6-digit check against all prize types |
| ML Pipeline | ✅ Running | orchestrator.py via PM2, ~687+ iterations |
| Formula Library | ✅ Active | 32 base formulas + genetic hybrids |
| Deploy (Vercel) | ❌ Not deployed | GitHub repo connected, needs env vars |
| Premium System | ❌ Not built | Schema exists, no payment integration |
| Auto Data Update | ❌ Not built | Manual scrape only |

### Key Metrics

- **Data:** 776 draws, 31 years (1995-06-01 to 2026-06-01)
- **Best Formula Score:** 113 (genetic hybrid)
- **Average Elite Score:** ~50-55
- **Target Iterations:** 1,000,000
- **Current Iterations:** ~687+ (as of last check)
- **The Chosen 10 Sets:** Generated from best-performing formula

---

## 2. Technical Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     CEO (Project Manager)                        │
│                    Thai Language Interface                       │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                  OWL (Default Agent / Lead Architect)            │
│              System Architect + Full-Stack Developer             │
│              Coordinates all agents and technical decisions      │
└──────────────────────────────┬──────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   ML ENGINEER    │ │  STATISTICIAN    │ │  WEB (Next.js)   │
│   (R&D Lead)     │ │  (Analysis)      │ │  (Frontend)      │
│                  │ │                  │ │                  │
│ - orchestrator   │ │ - Data analysis  │ │ - Dashboard      │
│ - ML models      │ │ - Validation     │ │ - Auth           │
│ - Genetic Algo   │ │ - Reporting      │ │ - API routes     │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Supabase       │  │  Local JSON     │  │  PM2 Process    │ │
│  │   (PostgreSQL)   │  │  (Backup)       │  │  (ML Pipeline)  │ │
│  │                  │  │                 │  │                  │ │
│  │ - lotto_results  │  │ - scraped_all   │  │ - orchestrator  │ │
│  │ - user_profiles  │  │ - results_db    │  │ - formula_lib   │ │
│  │ - query_logs     │  │ - final_report  │  │ - final_report  │ │
│  │ - payments       │  │                 │  │                  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology | Version | Notes |
|-------|-----------|---------|-------|
| Frontend | Next.js | 16.2.6 | App Router, Turbopack |
| UI Library | React | 19 | Client components |
| Language | TypeScript | 5.x | Strict mode |
| Styling | Inline CSS ONLY | — | Tailwind broken in production |
| Backend | Supabase | — | PostgreSQL + Auth + RLS |
| Auth | Supabase Auth | — | Email/password |
| ML Pipeline | Python 3 | — | orchestrator.js via PM2 |
| Process Manager | PM2 | — | autorestart: false |
| Hosting (current) | WSL (Windows) | — | Local only |
| Hosting (target) | Vercel | — | Connected to GitHub |
| Database | PostgreSQL | 15.x | Via Supabase |
| Version Control | Git | — | GitHub: tronica04-hash/lotto-ai |

### Why Inline CSS?

Tailwind CSS 4 on Next.js 16 + Turbopack has a critical bug: CSS is injected via JavaScript. If JS fails to load, ALL styling breaks. Every page uses `style={{...}}` inline styles. **Never change to Tailwind classes.**

### Project File Structure

```
D:\lotto-ai\
├── src/                          # Next.js Web Application
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx    # Login page
│   │   │   └── register/page.tsx # Register page
│   │   ├── dashboard/page.tsx    # Main dashboard (6 tabs)
│   │   ├── dream/page.tsx        # Dream prediction (public)
│   │   ├── results/page.tsx      # Historical results (public)
│   │   ├── stats/
│   │   │   ├── hot-cold/page.tsx # Hot/Cold/Due stats (public)
│   │   │   └── ai/page.tsx       # AI prediction display (public)
│   │   ├── api/
│   │   │   ├── check/route.ts    # Number checking API
│   │   │   ├── lotto/analyze/route.ts  # Analysis API (unused)
│   │   │   ├── lotto/local-data/route.ts # Local data fallback
│   │   │   └── scraper/run/route.ts     # Scraper trigger (unused)
│   │   ├── layout.tsx            # Root layout
│   │   ├── page.tsx              # Landing page
│   │   └── globals.css           # Minimal global CSS
│   ├── lib/
│   │   ├── supabase.ts           # Supabase client (with fallback)
│   │   ├── analyzer.ts           # Analysis engine (server-side)
│   │   └── scraper.ts            # Scraper utility
│   └── types/
│       └── index.ts              # TypeScript interfaces
├── ml-models/                    # ML Pipeline
│   ├── orchestrator.py           # Main ML loop (1052 lines)
│   ├── data/
│   │   ├── scraped_all.json      # 776 draws (1.8MB, primary data)
│   │   ├── lotto_all.json        # Alternative dataset
│   │   └── data_quality_report.json
│   ├── formulas/
│   │   ├── formula_library.json  # 32+ formulas (evolves over time)
│   │   └── formula_library_v2.json # Backup
│   ├── results/
│   │   ├── results_database.json # All iteration results (28MB!)
│   │   ├── results_database.json.tmp # Atomic save temp file
│   │   ├── final_report.json     # Latest run summary
│   │   ├── walk_forward_results.json
│   │   └── sets_test.json
│   └── [various analysis scripts] # phase1/2/3, train_all, etc.
├── supabase/
│   ├── schema.sql                # Full database schema
│   └── import-script.sql         # Import functions + views
├── scripts/                      # Data pipeline scripts
│   ├── scrape-myhora.py          # Primary scraper
│   ├── import-final.py           # Supabase import
│   └── [various utility scripts]
├── logs/
│   ├── pm2-out.log               # ML pipeline output (1.6MB)
│   └── pm2-error.log             # ML pipeline errors
├── public/
│   └── lotto-data.json           # Local fallback data (1.8MB)
├── ecosystem.config.js           # PM2 configuration
├── .env.local                    # Environment variables (SECRET)
├── .env.example                  # Template
├── package.json                  # Node.js dependencies
├── next.config.ts                # Next.js configuration
├── tsconfig.json                 # TypeScript config
├── LOTTO_BIBLE.md                # Lottery knowledge base
├── SYSTEM_ARCHITECTURE_V2.md     # Architecture documentation
├── LOTTOAI_MASTER_SSOT.md        # Previous SSOT (outdated)
└── PROJECT_SSOT.md               # This file
```

---

## 3. Logical Flow — How the System Works

### 3.1 ML Pipeline (orchestrator.py)

The core ML pipeline is a **single Python script** (`orchestrator.py`, 1052 lines) that runs as a persistent background process managed by PM2.

#### Main Loop (Iterative Mathematical Sandbox)

```
FOR each iteration from 1 to 1,000,000:
  │
  ├─ STEP 1: SELECT TEST DRAW
  │  Randomly pick one draw from the dataset (index 100..N-1)
  │  This draw becomes the "hidden answer" — formulas don't see it
  │
  ├─ STEP 2: SPLIT DATA
  │  train_data = all draws BEFORE test_draw (by date)
  │  test_data  = the test_draw itself (ground truth)
  │
  ├─ STEP 3: RUN ALL FORMULAS
  │  For each formula in formula_library:
  │    - Apply formula to train_data
  │    - Generate 10 sets of 6-digit numbers
  │  Result: {formula_id: {sets: [10 x 6-digit], formula: name}}
  │
  ├─ STEP 4: EVALUATE
  │  For each formula's 10 sets:
  │    - Compare against test_data's actual prizes
  │    - Score based on Scoring System (Section 7)
  │  Result: {formula_id: {score: N, hits: {...}}}
  │
  ├─ STEP 5: SAVE RESULTS
  │  - Append iteration result to results_database.json
  │  - ATOMIC SAVE: write to .tmp first, then os.replace()
  │  - Track best_score_ever and no_improvement_count
  │
  ├─ STEP 6: EVOLVE (Genetic Algorithm)
  │  - Sort formulas by score
  │  - Elite (top 20%): KEEP
  │  - Bottom (bottom 20%): DELETE
  │  - Create new formulas by crossover + mutation of elite pairs
  │  - Add new genetic formulas to library
  │
  ├─ CHECK: Early Stopping (every 10,000 iterations)
  │  If elite avg score < random baseline (3.0): STOP
  │
  └─ CHECK: Convergence
     If no improvement for 100,000 iterations: STOP
     If best score flat for 20 iterations: STOP

FINAL OUTPUT:
  - Print top 10 formulas by average score
  - Generate "The Chosen 10 Sets" from best formula
  - Save final_report.json
```

#### Resume State

The system **never loses progress**. On restart:
1. Load `results_database.json` → count existing iterations
2. Resume from `last_iteration + 1`
3. Restore `best_score_ever` from database
4. Formula library is preserved across restarts

#### Atomic Save

All file writes use **atomic save pattern**:
```python
temp_path = file_path + ".tmp"
with open(temp_path, "w") as f:
    json.dump(data, f)
os.replace(temp_path, file_path)  # Atomic on all OS
```
This prevents JSON corruption if the process crashes mid-write.

### 3.2 Data Flow

```
[myhora.com] ──scrape──> scraped_all.json ──import──> Supabase (lotto_results)
                                    │
                                    └──load──> orchestrator.py
                                                   │
                                                   ├─> formula_library.json (evolves)
                                                   ├─> results_database.json (grows)
                                                   └─> final_report.json (summary)
```

### 3.3 Web Application Flow

```
User ──> Landing Page (/)
  │
  ├─> /login or /register ──> Supabase Auth
  │
  └─> /dashboard (protected)
       │
       ├─ Tab 1: Overview ──> Supabase query + client-side analysis
       ├─ Tab 2: Statistics ──> Hot/Cold/Due from Supabase
       ├─ Tab 3: AI Prediction ──> Weighted score prediction
       ├─ Tab 4: Dream ──> 44-keyword dictionary lookup
       ├─ Tab 5: Results ──> Supabase query with filters
       └─ Tab 6: Check Number ──> Compare input vs latest draw

Fallback: If Supabase fails ──> load /lotto-data.json from public/
```

---

## 4. Data Schema

### 4.1 Supabase Tables

#### `lotto_results` — Primary lottery data

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGINT | AUTO PK | Primary key |
| draw_date | DATE | NOT NULL, UNIQUE | Draw date (YYYY-MM-DD) |
| draw_number | TEXT | | Draw number (YYMMDD) |
| first_prize | TEXT | | 1st prize (6 digits) |
| second_prize | JSONB | DEFAULT '[]' | 2nd prize (5 numbers) |
| third_prize | JSONB | DEFAULT '[]' | 3rd prize (10 numbers) |
| two_digit | TEXT | | Last 2 digits |
| three_digit_first | JSONB | DEFAULT '[]' | First 3 digits prize |
| three_digit_last | JSONB | DEFAULT '[]' | Last 3 digits prize |
| nearby_1st | JSONB | DEFAULT '[]' | Near 1st prize (2 numbers) |
| prize_4 | JSONB | DEFAULT '[]' | 4th prize (50 numbers) |
| prize_5 | JSONB | DEFAULT '[]' | 5th prize (100 numbers) |
| created_at | TIMESTAMPTZ | NOW() | Record creation |
| updated_at | TIMESTAMPTZ | NOW() | Last update |

**Indexes:** `idx_lotto_draw_date` (draw_date DESC), `idx_lotto_draw_number`
**RLS:** Public read, service role write

#### `user_profiles` — User accounts

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| id | UUID | PK → auth.users | User ID |
| email | TEXT | | Email address |
| plan | TEXT | 'free' | free/premium/vip |
| queries_today | INTEGER | 0 | Daily query count |
| queries_limit | INTEGER | 5 | Daily limit (5 free, 9999 premium) |
| last_query_date | DATE | CURRENT_DATE | For daily reset |
| created_at | TIMESTAMPTZ | NOW() | |
| updated_at | TIMESTAMPTZ | NOW() | |

**RLS:** Users can read/update own profile

#### `query_logs` — Usage tracking

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT PK | |
| user_id | UUID | → auth.users |
| query_type | TEXT | Type of query |
| input_data | JSONB | Input parameters |
| result_data | JSONB | Query results |
| created_at | TIMESTAMPTZ | |

#### `payments` — Payment records

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT PK | |
| user_id | UUID | → auth.users |
| plan | TEXT | Plan purchased |
| amount | INTEGER | Amount in baht |
| status | TEXT | pending/completed/failed |
| payment_method | TEXT | Payment method |
| payment_ref | TEXT | Reference number |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

### 4.2 Local JSON Data Formats

#### `scraped_all.json` — Raw lottery data (776 draws)

```json
[
  {
    "draw_date": "1995-01-01",
    "draw_number": "950101",
    "first_prize": "123456",
    "two_digit": "56",
    "three_digit_first": ["123"],
    "three_digit_last": ["456", "789"],
    "second_prize": ["12345", "67890"],
    "third_prize": ["11111", "22222", ...],
    "nearby_1st": ["123455", "123457"],
    "prize_4": ["11111", ...],
    "prize_5": ["22222", ...]
  },
  ...
]
```

#### `formula_library.json` — Prediction formulas

```json
{
  "freq_v1": {
    "name": "Frequency v1 (w=20)",
    "phase": 1,
    "type": "statistical",
    "params": {
      "window": 20,
      "top_n": 10,
      "freq_weight": 1.0,
      "gap_weight": 0.0,
      "pos_weight": 0.0
    },
    "created": "2026-06-24",
    "generation": 0,
    "avg_score": 0,
    "total_rounds": 0
  },
  "gen_g28_9239": {
    "name": "Gen(freq_v1xfreq_v2)",
    "phase": 4,
    "type": "genetic",
    "params": {
      "parents": ["freq_v1", "freq_v2"],
      "window": 20,
      "freq_weight": 1.2,
      "gap_weight": 0.3
    },
    "created": "2026-06-13T10:00:00",
    "generation": 28,
    "avg_score": 55.3,
    "total_rounds": 540
  }
}
```

#### `results_database.json` — All iteration results

```json
{
  "iterations": [
    {
      "iteration": 1,
      "test_draw": "2020-06-01",
      "timestamp": "2026-06-13T10:00:00",
      "results": {
        "freq_v1": {
          "formula": "Frequency v1 (w=20)",
          "score": 15,
          "hits": {
            "รางวัลที่ 1": 0,
            "เลขท้าย 2": 1,
            "เลขท้าย 3": 0
          }
        }
      },
      "best_formula": "freq_v1",
      "best_score": 15,
      "best_sets": ["123456", "789012", ...],
      "worst_formula": "monte_carlo_v1",
      "worst_score": 0,
      "avg_score": 7.5
    }
  ],
  "best_formula": "gen_g28_9239",
  "best_score": 113
}
```

#### `final_report.json` — Summary report

```json
{
  "generated": "2026-06-13T11:41:39",
  "total_iterations": 540,
  "best_score_ever": 113,
  "final_formula_count": 18,
  "top_10": [
    {"id": "gen_g28_9239", "name": "gen_g28_9239", "avg_score": 55.33}
  ],
  "the_chosen_10_sets": ["911292", "074568", "164191", ...],
  "best_formula_id": "gen_g28_9239",
  "best_formula_name": "N/A"
}
```

---

## 5. API & Integration

### 5.1 Next.js API Routes

| Route | Method | Auth | Description | Status |
|-------|--------|------|-------------|--------|
| `/api/check` | POST | No | Check 6-digit number against latest draw | ✅ Active |
| `/api/lotto/analyze` | GET | No | Statistical analysis (unused) | ⚠️ Stub |
| `/api/lotto/local-data` | GET | No | Serve local JSON fallback | ✅ Active |
| `/api/scraper/run` | POST | No | Trigger scraper (unused) | ❌ Stub |

### 5.2 Supabase Client Configuration

```typescript
// src/lib/supabase.ts
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL 
  || 'https://jiulxmylgwaaygdytdfj.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

// Safe client creation (returns null if config missing)
export const supabase = createSafeClient(supabaseUrl, supabaseAnonKey);

// Admin client (for server-side operations)
export const supabaseAdmin = supabaseServiceKey 
  ? createSafeClient(supabaseUrl, supabaseServiceKey) 
  : null;
```

### 5.3 Vercel Serverless Functions (Future)

When deployed to Vercel, the following serverless functions are planned:

```
/api/predict          → Run best formula → return The Chosen 10 Sets
/api/stats/hot-cold   → Query Supabase → return hot/cold/due numbers
/api/stats/frequency  → Query Supabase → return frequency analysis
/api/dream/:keyword   → Dictionary lookup → return numbers
/api/check            → Compare number → return prize matches
/api/admin/retrain    → Trigger orchestrator retrain (protected)
```

### 5.4 Supabase Views (SQL)

| View | Description |
|------|-------------|
| `v_lotto_stats` | Summary: total_draws, first_draw, last_draw, prize coverage |
| `v_hot_2digit` | Top 10 hot 2-digit numbers by frequency |
| `v_hot_3digit_first` | Top 10 hot 3-digit-first numbers |
| `v_hot_3digit_last` | Top 10 hot 3-digit-last numbers |
| `v_due_2digit` | Top 10 due 2-digit numbers (longest gap) |

### 5.5 Supabase RPC Functions

| Function | Description |
|----------|-------------|
| `import_lotto_data(data_json JSONB)` | Batch upsert lottery data |
| `reset_daily_queries()` | Reset daily query counts |

---

## 6. Formula Library — Prediction Models

### 6.1 Formula Types

The system has **4 phases** of formulas:

#### Phase 1: Statistical (12 formulas)

| ID | Name | Logic |
|----|------|-------|
| freq_v1-3 | Frequency v1-3 | Count 2-digit frequency in last N draws (w=20/40/60) |
| due_v1-2 | Due Number v1-2 | Find numbers that haven't appeared longest |
| bayesian_v1 | Bayesian | Laplace-smoothed posterior probability |
| markov_v1-2 | Markov Chain | Transition matrix (order 1 and 2) |
| monte_carlo_v1 | Monte Carlo | Weighted random sampling from frequency distribution |
| positional_v1 | Positional | Per-digit-position frequency analysis |
| hot_cold_v1 | Hot/Cold | Recent frequency minus long-term frequency |
| pairs_v1 | Pairs | Co-occurrence analysis of 2-digit numbers |

#### Phase 2: Advanced (6 formulas)

| ID | Name | Logic |
|----|------|-------|
| time_series_v1 | Time Series | Monthly seasonality + trend analysis |
| sum_diff_v1 | Sum/Difference | Target sum analysis (avg sum ≈ 27) |
| modular_v1 | Modular Arithmetic | Modulo 3, 7, 9 residue analysis |
| fibonacci_v1 | Fibonacci/Prime | Fibonacci sequence + prime number filtering |
| chaos_v1 | Chaos Theory | Autocorrelation of 2-digit sequences |
| entropy_v1 | Entropy | Shannon entropy per digit position |

#### Phase 3: Machine Learning (6 formulas)

| ID | Name | Logic |
|----|------|-------|
| rf_v1 | Random Forest | Feature-based scoring with random weight variation |
| xgb_v1 | XGBoost | Gradient boosted feature scoring |
| lstm_v1 | LSTM | Sequence-based scoring (simulated) |
| logistic_v1 | Logistic Regression | Sigmoid-transformed feature score |
| knn_v1 | K-Nearest Neighbors | KNN-based frequency scoring |
| ensemble_v1 | Ensemble | Weighted combination of all ML features |

#### Phase 4: Genetic (unlimited, evolves)

| ID Pattern | Name | Logic |
|------------|------|-------|
| gen_g{N}_{ID} | Gen(parent1 x parent2) | Crossover + mutation of parent formulas |

### 6.2 How Formulas Generate Numbers

Each formula produces **10 sets of 6-digit numbers**. The general approach:

1. **Analyze** train_data (historical draws before test date)
2. **Score** each possible 2-digit combination (00-99)
3. **Select** top 10 scoring 2-digit endings
4. **Generate** 6-digit numbers by combining random prefixes with selected endings
5. **Return** 10 complete 6-digit numbers

---

## 7. Scoring System

When a test draw is revealed, each formula's 10 sets are scored:

| Match Type | Points | Description |
|------------|--------|-------------|
| รางวัลที่ 1 | 50 | Exact match of 1st prize (6 digits) |
| ข้างเคียง | 25 | Match near-1st prize (±1) |
| รางวัลที่ 2 | 30 | Match 2nd prize (5 digits) |
| รางวัลที่ 3 | 20 | Match 3rd prize (5 digits) |
| รางวัลที่ 4 | 15 | Match 4th prize (5 digits) |
| รางวัลที่ 5 | 10 | Match 5th prize (5 digits) |
| เลขท้าย 3 | 5 | Match last 3 digits prize |
| เลขหน้า 3 | 5 | Match first 3 digits prize |
| เลขท้าย 2 | 3 | Match last 2 digits |
| base_per_set | 10 | Bonus if any prize matched |

**Maximum possible per set:** 50 (1st prize) + 25 (nearby) + 30 + 20 + 15 + 10 + 5 + 5 + 3 + 10 = **173 points**

**Random baseline:** ~3.0 (expected score from random guessing)

**Current best:** 113 points (genetic hybrid formula)

---

## 8. Genetic Algorithm — Evolution Engine

### 8.1 Evolution Process

Every iteration, after scoring:

1. **Rank** all formulas by score
2. **Elite selection:** Top 20% survive
3. **Pruning:** Bottom 20% are deleted from formula_library
4. **Reproduction:** For each deleted formula:
   - Pick 2 random elite parents
   - **Crossover:** Mix parameters (50/50 from each parent)
   - **Mutation:** 10% chance to randomize each parameter
   - Create new genetic formula with `gen_g{iteration}_{random_id}` ID
5. **Add** new formulas to library

### 8.2 Crossover Example

```
Parent 1 (freq_v1):  {window: 20, freq_weight: 1.0, gap_weight: 0.0}
Parent 2 (due_v1):   {top_n: 5, gap_weight: 1.0, min_gap: 5}
                     ↓ Crossover
Child (gen_g50_1234): {window: 20, freq_weight: 1.0, gap_weight: 1.0, min_gap: 5}
```

### 8.3 Mutation

Each parameter has 10% chance to mutate:
- Integer params: random value 1-100
- Float params: random value 0.01-1.0

---

## 9. Web Application (Next.js)

### 9.1 Pages

| Route | File | Auth | Description |
|-------|------|------|-------------|
| `/` | `src/app/page.tsx` | No | Landing page with features |
| `/login` | `src/app/(auth)/login/page.tsx` | No | Login form |
| `/register` | `src/app/(auth)/register/page.tsx` | No | Registration form |
| `/dashboard` | `src/app/dashboard/page.tsx` | Yes | Main dashboard (6 tabs) |
| `/dream` | `src/app/dream/page.tsx` | No | Dream prediction |
| `/results` | `src/app/results/page.tsx` | No | Historical results |
| `/stats/hot-cold` | `src/app/stats/hot-cold/page.tsx` | No | Hot/Cold/Due stats |
| `/stats/ai` | `src/app/stats/ai/page.tsx` | No | AI prediction display |

### 9.2 Dashboard Tabs

| Tab | Features |
|-----|----------|
| 📊 Overview | Summary stats + AI prediction + hot/cold/due tables |
| 🔥 Statistics | Frequency bar charts (hot/cold/due) |
| 🤖 AI | AI prediction with confidence scores |
| 💭 Dream | 44-keyword dream dictionary + partial match |
| 📋 Results | Historical results table + year/month filter |
| 🔍 Check | 6-digit number checker against all prize types |

### 9.3 Dream Dictionary

44 keywords mapping to 2-digit numbers:
```
งู→[65,28], ช้าง→[42,11], ม้า→[33,58], วัว→[19,70],
ไก่→[01,46], หมา→[52,37], แมว→[24,63], ปลา→[08,75],
นก→[13,49], เสือ→[56,21], กระต่าย→[38,67], ตุ๊กแก→[44,15],
เต่า→[72,03], ควาย→[29,54], หมู→[61,16], ลิง→[47,82,05],
... (44 total)
```

Supports partial match: typing "ง" finds "งู"

### 9.4 Design System

**Colors:**
- Background: `linear-gradient(135deg, #0f172a, #581c87, #0f172a)`
- Card BG: `rgba(30,41,59,0.5)`
- Card Border: `rgba(148,163,184,0.12-0.2)`
- Primary: `#9333ea`
- Text: `#e2e8f0`
- Hot: `#f87171` (red)
- Cold: `#60a5fa` (blue)
- Due: `#fbbf24` (yellow)
- Prediction: `#c084fc` (purple)
- Gold: `#fbbf24`

**Typography:** `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`

**Components:**
- Cards: `border-radius: 10-16px, padding: 16-22px`
- Chips: `padding: 3-5px 8-12px, border-radius: 4-6px, monospace`
- Tables: `border-collapse: collapse, font-size: 12-13px`

**Responsive:** `grid-template-columns: repeat(auto-fit, minmax(220px, 1fr))`

---

## 10. Deployment

### 10.1 Current State

- **Running on:** WSL (Windows Subsystem for Linux)
- **Command:** `cd /mnt/d/lotto-ai && npx next build && npx next start --hostname 0.0.0.0 --port 3000`
- **Access:** `http://192.168.33.110:3000` (local network only)
- **ML Pipeline:** PM2 process `lottoai-production` running `orchestrator.py`

### 10.2 Target Deployment (Vercel)

- **Frontend:** Vercel (free tier, auto-deploy from GitHub)
- **Backend:** Supabase (free tier)
- **ML Pipeline:** Remains on local Windows machine (PM2)
- **GitHub Repo:** `https://github.com/tronica04-hash/lotto-ai.git`

### 10.3 Environment Variables

Required in `.env.local` and Vercel:

```
NEXT_PUBLIC_SUPABASE_URL=https://jiulxmylgwaaygdytdfj.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>  # Server-side only, never expose
```

### 10.4 Vercel Deployment Steps

1. Ensure `.env.local` variables are set in Vercel dashboard
2. Push to GitHub → auto-deploy
3. Set redirect URLs in Supabase: `https://<vercel-url>/`
4. Test auth flow on production domain

---

## 11. Future-Proofing — Extension Points

### 11.1 For New AI Agents

If a new AI agent joins to continue development, here are the key extension points:

#### A. Add New Formulas

Edit `orchestrator.py` → add new method in `apply_statistical_formula()` or create new phase:

```python
def my_new_formula(self, train_data, p):
    # Your logic here
    return [f"{random.randint(0, 999999):06d}" for _ in range(10)]
```

Then register in `initialize_formula_library()`:
```python
formulas["my_new_v1"] = {
    "name": "My New Formula",
    "phase": 5,  # New phase
    "type": "custom",
    "params": {"param1": value1},
    ...
}
```

#### B. Add New Data Sources

1. Create scraper in `scripts/` folder
2. Output format must match `scraped_all.json` schema
3. Import via `scripts/import-final.py`
4. Update `CONFIG["DATA_FILE"]` in orchestrator.py

#### C. Add New API Routes

Create file in `src/app/api/`:
```typescript
// src/app/api/new-endpoint/route.ts
import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET(request: Request) {
  // Your logic
  return NextResponse.json({ data: result });
}
```

#### D. Add New Dashboard Tab

Edit `src/app/dashboard/page.tsx`:
1. Add new tab button
2. Add new conditional render section
3. Follow existing inline CSS patterns

### 11.2 Improvement Opportunities

| Area | Current State | Improvement |
|------|--------------|-------------|
| **ML Models** | Simulated (random weight variation) | Integrate real scikit-learn/TensorFlow |
| **Data** | 776 draws (1995-2026) | Add Laos lottery, Thai private lottery |
| **Scoring** | Static weights | Dynamic weight optimization |
| **Genetic Algorithm** | Simple crossover | Multi-point crossover, tournament selection |
| **Web UI** | Static display | Interactive charts (Chart.js/D3) |
| **Prediction API** | Not exposed | Create `/api/predict` endpoint |
| **Auto-update** | Manual scrape | Scheduled scrape on draw days (1st, 16th) |
| **Premium** | Schema only | Stripe/PromptPay integration |
| **Notification** | None | LINE/Telegram bot for results |
| **SEO** | None | Meta tags, sitemap, structured data |
| **Testing** | None | Add Jest/Playwright tests |
| **i18n** | Thai only | English language support |

### 11.3 Critical Files to Understand First

1. **`orchestrator.py`** — The brain of the ML system (1052 lines)
2. **`formula_library.json`** — All prediction formulas
3. **`dashboard/page.tsx`** — Main web interface (280 lines)
4. **`supabase/schema.sql`** — Database structure
5. **`src/lib/supabase.ts`** — Database client config

---

## 12. Known Issues & Technical Debt

### 12.1 Active Issues

| Issue | Impact | Workaround |
|-------|--------|------------|
| `results_database.json` grows unbounded (28MB+) | Slow load times, disk usage | Needs rotation strategy (archive old iterations) |
| PM2 process may stop silently | ML pipeline halts | Manual check: `pm2 list` |
| Supabase may pause (free tier) | Web app shows no data | Local JSON fallback (`/lotto-data.json`) |
| No real ML models | All "ML" formulas use random weights | Integrate scikit-learn for real predictions |
| Ghost Agent profiles in Hermes | UI clutter | Delete folders when gateway restarts |

### 12.2 Technical Debt

1. **results_database.json rotation:** File grows ~50KB per iteration. At 1M iterations = 50GB. Need to implement:
   - Archive iterations older than N days
   - Keep only summary statistics
   - Compress with gzip

2. **Formula library bloat:** Genetic formulas accumulate indefinitely. Need:
   - Max library size limit
   - Periodic cleanup of low-performing genetic formulas
   - Deduplication of similar formulas

3. **No test coverage:** Zero tests for both Python and TypeScript code

4. **No CI/CD:** Manual deployment process

5. **Hardcoded paths:** All file paths are Windows-specific (`D:\lotto-ai\...`)

### 12.3 Previous SSOT Comparison

The old `LOTTOAI_MASTER_SSOT.md` (2026-06-02) was outdated in several ways:

| Topic | Old SSOT | Current Reality |
|-------|----------|-----------------|
| Data count | 779 draws (1995-2026) | 776 draws (1995-2026) |
| ML Pipeline | Not mentioned | orchestrator.py running via PM2 |
| Formula Library | Not mentioned | 32+ formulas with genetic evolution |
| Git status | "No Git repo" | GitHub repo connected |
| Deployment | "Create Git repo → Push → Vercel" | GitHub connected, needs env vars |
| Agent structure | 8 agents (Ghost Trio + 5) | Elite Trio (OWL, ML Engineer, Statistician) |
| PM2 config | Not mentioned | autorestart: false, max_restarts: 0 |
| Atomic save | Not mentioned | Implemented with os.replace() |
| Resume state | Not mentioned | Implemented |

---

## 13. Environment & Credentials

### 13.1 Supabase

- **Project Ref:** `jiulxmylgwaaygdytdfj`
- **URL:** `https://jiulxmylgwaaygdytdfj.supabase.co`
- **Dashboard:** `https://supabase.com/dashboard/project/jiulxmylgwaaygdytdfj`
- **SQL Editor:** `https://supabase.com/dashboard/project/jiulxmylgwaaygdytdfj/sql`
- **Status:** Active (was paused once by CEO, resumed)

### 13.2 GitHub

- **Repo:** `https://github.com/tronica04-hash/lotto-ai.git`
- **Status:** Connected to Vercel for auto-deploy

### 13.3 Local Development

```bash
# Web app
cd D:\lotto-ai
npm install
npm run dev          # Development server
npm run build        # Production build
npm start            # Production server

# ML pipeline
cd D:\lotto-ai
python orchestrator.py              # Direct run
pm2 start ecosystem.config.js      # PM2 managed
pm2 logs lottoai-production        # View logs
pm2 stop lottoai-production        # Stop
pm2 delete lottoai-production      # Remove from PM2

# Data pipeline
python scripts/scrape-myhora.py    # Scrape new data
python scripts/import-final.py     # Import to Supabase
```

### 13.4 File Locations

| File | Path | Size |
|------|------|------|
| Main data | `D:\lotto-ai\ml-models\data\scraped_all.json` | 1.8MB |
| Results DB | `D:\lotto-ai\ml-models\results\results_database.json` | 28MB+ |
| Formula lib | `D:\lotto-ai\ml-models\formulas\formula_library.json` | 7KB |
| Final report | `D:\lotto-ai\ml-models\results\final_report.json` | 1.4KB |
| PM2 logs | `D:\lotto-ai\logs\pm2-out.log` | 1.6MB |
| Local fallback | `D:\lotto-ai\public\lotto-data.json` | 1.8MB |

---

## 14. Glossary

| Term | Definition |
|------|-----------|
| **Draw (งวด)** | A single lottery draw event, occurs on 1st and 16th of each month |
| **First Prize (รางวัลที่ 1)** | 6-digit number, 6,000,000 baht prize |
| **Two Digit (เลขท้าย 2)** | Last 2 digits of first prize, 2,000 baht prize |
| **Three Digit (เลขท้าย 3)** | Last 3 digits, 4,000 baht prize |
| **Due Number (เลขนาย)** | Number that hasn't appeared for the longest time |
| **Hot Number (เลขร้อน)** | Number that appears most frequently |
| **Cold Number (เลขเย็น)** | Number that appears least frequently |
| **Train Data** | Historical draws used for formula analysis |
| **Test Draw** | Hidden draw used for formula evaluation |
| **Elite** | Top 20% performing formulas |
| **Genetic Formula** | New formula created by crossover + mutation of parent formulas |
| **The Chosen 10 Sets** | Final 10 predicted 6-digit numbers from best formula |
| **Atomic Save** | Write to temp file first, then replace (prevents corruption) |
| **RLS** | Row Level Security (Supabase feature) |
| **SSOT** | Single Source of Truth |

---

## Quick Start for New AI Agents

1. **Read this file completely** — it's the SSOT
2. **Check PM2 status:** `pm2 list` (is orchestrator running?)
3. **Check Supabase:** Visit dashboard, verify data exists
4. **Check web app:** `npm run dev` → `http://localhost:3000`
5. **Review orchestrator.py** — understand the main loop
6. **Review formula_library.json** — understand current formulas
7. **Review dashboard/page.tsx** — understand the web UI
8. **Check logs:** `pm2 logs lottoai-production --lines 50`

---

*This document is the Single Source of Truth for the LottoAI project.*
*Update it whenever significant changes are made.*
*Last updated: 2026-06-13 by OWL (Lead Architect)*
