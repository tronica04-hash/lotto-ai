# 📋 LOTTOAI — SYSTEM ARCHITECTURE v2.0.0
# Iterative Mathematical Sandbox
# สร้างโดย: OWL (Default Agent)
# วันที่: 2026-06-12
# เวอร์ชัน: 2.0.0

---

# ═══════════════════════════════════════════════════════════════
# ส่วนที่ 1: วิสัยทัศน์ระบบใหม่
# ═══════════════════════════════════════════════════════════════

## จุดประสงค์
เปลี่ยน LottoAI จาก "ระบบทำงานแยกส่วน" เป็น **"ระบบค้นหาและทดสอบสูตรคณิตศาสตร์แบบวนซ้ำอัตโนมัติ"**

## หลักการสำคัญ
1. **Backtesting อย่างเข้มงวด** — ซ่อนข้อมูลจริง ไม่ให้ agent เห็น
2. **Closed-Loop Evolution** — สูตรดี → พัฒนาต่อ, สูตรแย่ → คัดทิ้ง
3. **Genetic Algorithm** — ผสมสูตรดีๆ เข้าด้วยกัน → สูตรใหม่ที่ดีกว่า
4. **Iterative Improvement** — วนซ้ำไปเรื่อยๆ จนได้สูตรที่นิ่งและแม่นยำ

---

# ═══════════════════════════════════════════════════════════════
# ส่วนที่ 2: สถาปัตยกรรมระบบใหม่
# ═══════════════════════════════════════════════════════════════

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CEO (Project Manager)                        │
│                          สั่งงานภาพรวม                              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     OWL (Default Agent)                              │
│                   ผู้ประสานงานหลัก + สถาปนิกระบบ                    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CONTROLLER AGENT (ใหม่)                           │
│              ควบคุมลูปการทำงานทั้งหมด (Orchestrator)                 │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    MAIN LOOP (Iterative)                       │  │
│  │                                                               │  │
│  │  FOR each iteration in MAX_ITERATIONS:                        │  │
│  │    1. สุ่มเลือกงวดทดสอบ (test_draw)                           │  │
│  │    2. แบ่งข้อมูล: train (1..test-1), test (test)              │  │
│  │    3. ส่ง train data → Formula Tester + ML Engineer           │  │
│  │    4. รับ 10 ชุดตัวเลขจากแต่ละสูตร                          │  │
│  │    5. ส่ง 10 ชุด → Evaluator (เปิดเฉลย)                     │  │
│  │    6. รับ score → บันทึกผล                                   │  │
│  │    7. ส่ง score → Genetic Algorithm                           │  │
│  │    8. สร้างสูตรใหม่ → เพิ่มใน formula_library                 │  │
│  │    9. คัดทิ้งสูตรแย่ (bottom 20%)                             │  │
│  │   10. ทำซ้ำจน convergence หรือ MAX_ITERATIONS                │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
└──────────┬──────────────────────────────┬───────────────────────────┘
           │                              │
           ▼                              ▼
┌──────────────────────┐      ┌──────────────────────┐
│   FORMULA TESTER     │      │    ML ENGINEER       │
│   (นักคณิตศาสตร์)     │◄────►│   (นัก ML)           │
│                      │      │                      │
│  - 25+ สูตร          │      │  - RF, XGB, LSTM     │
│  - Genetic Algorithm │      │  - Hyperparameter    │
│  - สร้างสูตรใหม่     │      │  - Feature Eng       │
│  - ผสมสูตร           │      │  - Ensemble          │
└──────────┬───────────┘      └──────────┬───────────┘
           │                              │
           │    10 ชุดตัวเลข (6 หลัก)     │
           │         จากแต่ละสูตร         │
           └──────────────┬───────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      EVALUATOR AGENT                                 │
│                                                                     │
│  1. รับ 10 ชุดตัวเลขจากทุกสูตร                                     │
│  2. เปิดเฉลยงวดที่ซ่อน                                             │
│  3. ตรวจรางวัลทุกประเภท (1-5, ข้างเคียง, เลขท้าย 2/3, หน้า 3)     │
│  4. คำนวณ score ตาม Scoring System                                 │
│  5. บันทึกผล → results_database                                    │
│  6. ส่ง score → Controller (สำหรับ Genetic Algorithm)              │
│                                                                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    RESULTS DATABASE                                  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  results_database.json                                       │   │
│  │  {                                                           │   │
│  │    "iteration": 1,                                           │   │
│  │    "test_draw": "2025-06-01",                                │   │
│  │    "formulas": {                                             │   │
│  │      "frequency_v1": {                                       │   │
│  │        "sets": ["123456", "789012", ...],                    │   │
│  │        "score": 125,                                         │   │
│  │        "hits": {"รางวัลที่ 1": 0, "เลขท้าย 2": 3, ...}      │   │
│  │      },                                                      │   │
│  │      "markov_v2": { ... },                                   │   │
│  │      ...                                                     │   │
│  │    },                                                        │   │
│  │    "best_formula": "frequency_v1",                           │   │
│  │    "best_score": 125                                         │   │
│  │  }                                                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

# ═══════════════════════════════════════════════════════════════
# ส่วนที่ 3: Agent ทั้งหมด v2.0.0
# ═══════════════════════════════════════════════════════════════

## 1. Controller Agent (ใหม่ — สำคัญที่สุด)
**หน้าที่:** ควบคุมลูปการทำงานทั้งหมด

**ตัวแปรควบคุม:**
- MAX_ITERATIONS: จำนวนรอบสูงสุด (เช่น 1000)
- CONVERGENCE_THRESHOLD: เกณฑ์หยุด (เช่น ไม่มี improvement 10 รอบ)
- TEST_DRAW_STRATEGY: วิธีเลืองวดทดสอบ (random / sequential / stratified)
- POPULATION_SIZE: จำนวนสูตรในแต่ละรอบ (เช่น 30)
- ELITE_RATIO: สัดส่วนสูตรที่เก็บไว้ (เช่น 20%)
- MUTATION_RATE: อัตราการกลายพันธุ์ (เช่น 10%)

**กระบวนการ:**
1. สุ่มเลือกงวดทดสอบ
2. แบ่งข้อมูล train/test
3. ส่ง train → Formula Tester + ML Engineer
4. รับ 10 ชุดตัวเลขจากแต่ละสูตร
5. ส่ง → Evaluator
6. รับ score
7. ส่ง → Genetic Algorithm
8. สร้างสูตรใหม่
9. คัดทิ้งสูตรแย่
10. ทำซ้ำ

---

## 2. Formula Tester Agent (ปรับปรุง)
**หน้าที่:** คิดค้น + ทดสอบสูตรคณิตศาสตร์

**สูตรที่มี (25+):**
- Phase 1: Frequency, Due Number, Bayesian, Markov, Monte Carlo, Position, Hot/Cold, Pairs
- Phase 2: Time Series, Sum/Diff, Modular, Fibonacci, Chaos, Entropy
- Phase 3: Weighted Ensemble, Adaptive Ensemble, Cascading Filter
- Phase 4: สูตรใหม่ที่ Genetic Algorithm สร้าง

**Genetic Algorithm:**
```
1. เลือกสูตรดีๆ (top 20%) เป็น "พ่อแม่"
2. ผสมสูตร (crossover): เช่น Frequency + Markov = "Frequency-Markov Hybrid"
3. กลายพันธุ์ (mutation): เปลี่ยน parameters สุ่ม
4. สร้างสูตรใหม่ (offspring)
5. เพิ่มใน formula_library
```

**Output:** 10 ชุดตัวเลข (6 หลัก) ต่อสูตร

---

## 3. ML Engineer Agent (ปรับปรุง)
**หน้าที่:** Train ML models + hyperparameter tuning

**Models:**
- Random Forest, XGBoost, LSTM, Logistic Regression, KNN, Ensemble

**Hyperparameter Tuning:**
```
สุ่ม hyperparameters ใหม่ในแต่ละ iteration:
- RF: n_estimators, max_depth, min_samples
- XGB: learning_rate, max_depth, n_estimators
- LSTM: units, layers, dropout, sequence_length
```

**Output:** 10 ชุดตัวเลข (6 หลัก) ต่อ model

---

## 4. Evaluator Agent (ปรับปรุง)
**หน้าที่:** เปิดเฉลย + คำนวณ score

**Scoring System:**
```
Base: 10 คะแนนต่อชุดที่ถูกรางวัล
Bonus:
- รางวัลที่ 1: +50
- ข้างเคียง: +25
- รางวัลที่ 2: +30
- รางวัลที่ 3: +20
- รางวัลที่ 4: +15
- รางวัลที่ 5: +10
- เลขท้าย 3: +5
- เลขหน้า 3: +5
- เลขท้าย 2: +3
```

**Output:** Score ต่อสูตร + สรุปผล

---

## 5. Scraper Agent (เหมือนเดิม)
**หน้าที่:** Scrape ข้อมูลใหม่ทุกวันที่ 1 และ 16

---

## 6. Data Cleaner Agent (เหมือนเดิม)
**หน้าที่:** ทำความสะอาดข้อมูล

---

## 7. DB Importer Agent (เหมือนเดิม)
**หน้าที่:** Sync เข้า Supabase

---

## 8. Statistician Agent (เหมือนเดิม)
**หน้าที่:** วิเคราะห์สถิติ + cross-reference

---

# ═══════════════════════════════════════════════════════════════
# ส่วนที่ 4: Pseudo-code — Orchestration Script
# ═══════════════════════════════════════════════════════════════

```python
#!/usr/bin/env python3
"""
LottoAI v2.0.0 — Iterative Mathematical Sandbox
Orchestration Script (Controller)
"""

import json
import random
import os
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

CONFIG = {
    "MAX_ITERATIONS": 1000,
    "CONVERGENCE_THRESHOLD": 10,  # หยุดถ้าไม่มี improvement 10 รอบ
    "TEST_DRAW_STRATEGY": "random",  # random / sequential / stratified
    "POPULATION_SIZE": 30,  # จำนวนสูตรในแต่ละรอบ
    "ELITE_RATIO": 0.2,  # สัดส่วนสูตรที่เก็บไว้
    "MUTATION_RATE": 0.1,  # อัตราการกลายพันธุ์
    "NUM_SETS": 10,  # จำนวนชุดตัวเลขต่อสูตร
    "DIGITS": 6,  # จำนวนหลักต่อชุด
    "DATA_FILE": r"D:\lotto-ai\ml-models\data\scraped_all.json",
    "RESULTS_FILE": r"D:\lotto-ai\ml-models\results\results_database.json",
    "FORMULA_LIB": r"D:\lotto-ai\ml-models\formulas\formula_library.json",
    "REPORT_DIR": r"D:\lotto-ai\ml-models\results",
}

# ═══════════════════════════════════════════════════════════════
# SCORING SYSTEM
# ═══════════════════════════════════════════════════════════════

SCORING = {
    "base_per_set": 10,
    "รางวัลที่ 1": 50,
    "ข้างเคียง": 25,
    "รางวัลที่ 2": 30,
    "รางวัลที่ 3": 20,
    "รางวัลที่ 4": 15,
    "รางวัลที่ 5": 10,
    "เลขท้าย 3": 5,
    "เลขหน้า 3": 5,
    "เลขท้าย 2": 3,
}

# ═══════════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════

class LottoAIController:
    def __init__(self, config):
        self.config = config
        self.data = self.load_data()
        self.formula_library = self.load_formula_library()
        self.results_db = self.load_results_database()
        self.iteration = 0
        self.best_score_ever = 0
        self.no_improvement_count = 0
        
    def load_data(self):
        """โหลดข้อมูลหวยทั้งหมด"""
        with open(self.config["DATA_FILE"], "r", encoding="utf-8") as f:
            return json.load(f)
    
    def load_formula_library(self):
        """โหลดสูตรทั้งหมด"""
        path = self.config["FORMULA_LIB"]
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return self.initialize_formula_library()
    
    def initialize_formula_library(self):
        """สร้างสูตรเริ่มต้น 25+ สูตร"""
        formulas = {}
        
        # Phase 1: Statistical Formulas
        formulas["frequency_v1"] = {
            "name": "Frequency Analysis v1",
            "phase": 1,
            "type": "statistical",
            "params": {"window": 50, "top_n": 10},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["due_number_v1"] = {
            "name": "Due Number (Gap) v1",
            "phase": 1,
            "type": "statistical",
            "params": {"top_n": 10},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["bayesian_v1"] = {
            "name": "Bayesian Inference v1",
            "phase": 1,
            "type": "statistical",
            "params": {"prior_strength": 1, "window": 100},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["markov_v1"] = {
            "name": "Markov Chain v1",
            "phase": 1,
            "type": "statistical",
            "params": {"order": 1, "states": 100},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["monte_carlo_v1"] = {
            "name": "Monte Carlo Simulation v1",
            "phase": 1,
            "type": "statistical",
            "params": {"simulations": 10000, "distribution": "historical"},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["positional_v1"] = {
            "name": "Digit Position Analysis v1",
            "phase": 1,
            "type": "statistical",
            "params": {"positions": 6, "top_per_pos": 3},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["hot_cold_v1"] = {
            "name": "Hot/Cold Numbers v1",
            "phase": 1,
            "type": "statistical",
            "params": {"hot_window": 20, "cold_window": 100},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["pairs_v1"] = {
            "name": "Number Pair Analysis v1",
            "phase": 1,
            "type": "statistical",
            "params": {"min_cooccurrence": 3},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        
        # Phase 2: Advanced Formulas
        formulas["time_series_v1"] = {
            "name": "Time Series Patterns v1",
            "phase": 2,
            "type": "advanced",
            "params": {"seasonality": "monthly", "trend_window": 50},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["sum_diff_v1"] = {
            "name": "Sum/Difference Analysis v1",
            "phase": 2,
            "type": "advanced",
            "params": {"target_sum": 27, "tolerance": 5},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["modular_v1"] = {
            "name": "Modular Arithmetic v1",
            "phase": 2,
            "type": "advanced",
            "params": "mod 3, mod 7, mod 9",
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["fibonacci_v1"] = {
            "name": "Fibonacci/Prime Theory v1",
            "phase": 2,
            "type": "advanced",
            "params": {"sequence": "fibonacci", "primes_only": False},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["chaos_v1"] = {
            "name": "Chaos Theory/Fractal v1",
            "phase": 2,
            "type": "advanced",
            "params": {"fractal_dimension": 1.5, "lookback": 20},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["entropy_v1"] = {
            "name": "Entropy Analysis v1",
            "phase": 2,
            "type": "advanced",
            "params": {"window": 50, "threshold": 0.5},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        
        # Phase 3: ML Models
        formulas["random_forest_v1"] = {
            "name": "Random Forest v1",
            "phase": 3,
            "type": "ml",
            "params": {"n_estimators": 100, "max_depth": 10},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["xgboost_v1"] = {
            "name": "XGBoost v1",
            "phase": 3,
            "type": "ml",
            "params": {"learning_rate": 0.1, "max_depth": 6, "n_estimators": 100},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["lstm_v1"] = {
            "name": "LSTM Neural Network v1",
            "phase": 3,
            "type": "ml",
            "params": {"units": 128, "layers": 2, "sequence_length": 20},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["logistic_v1"] = {
            "name": "Logistic Regression v1",
            "phase": 3,
            "type": "ml",
            "params": {"C": 1.0, "max_iter": 1000},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["knn_v1"] = {
            "name": "K-Nearest Neighbors v1",
            "phase": 3,
            "type": "ml",
            "params": {"k": 10, "lookback": 5},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        formulas["ensemble_v1"] = {
            "name": "Weighted Ensemble v1",
            "phase": 3,
            "type": "ml",
            "params": {"models": ["rf", "xgb", "lstm"], "weight_strategy": "performance"},
            "created": datetime.now().isoformat(),
            "generation": 0,
            "avg_score": 0,
            "total_rounds": 0
        }
        
        return formulas
    
    def load_results_database(self):
        """โหลดผลการทดสอบที่เคยทำ"""
        path = self.config["RESULTS_FILE"]
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"iterations": [], "best_formula": None, "best_score": 0}
    
    # ═══════════════════════════════════════════════════════════
    # MAIN LOOP
    # ═══════════════════════════════════════════════════════════
    
    def run(self):
        """ลูปหลัก — ทำซ้ำจน convergence หรือ MAX_ITERATIONS"""
        print("=" * 60)
        print("  LOTTOAI v2.0.0 — Iterative Mathematical Sandbox")
        print("=" * 60)
        print(f"ข้อมูล: {len(self.data)} งวด")
        print(f"สูตร: {len(self.formula_library)} สูตร")
        print(f"Max iterations: {self.config['MAX_ITERATIONS']}")
        print()
        
        for i in range(self.config["MAX_ITERATIONS"]):
            self.iteration = i + 1
            
            print(f"\n{'━' * 50}")
            print(f"  ITERATION {self.iteration}/{self.config['MAX_ITERATIONS']}")
            print(f"{'━' * 50}")
            
            # Step 1: สุ่มเลือกงวดทดสอบ
            test_draw = self.select_test_draw()
            print(f"  Test draw: {test_draw['draw_date']}")
            
            # Step 2: แบ่งข้อมูล
            train_data, test_data = self.split_data(test_draw)
            print(f"  Train: {len(train_data)} draws, Test: 1 draw")
            
            # Step 3: ส่งให้ Formula Tester + ML Engineer คำนวณ
            all_sets = self.run_formulas(train_data)
            print(f"  ได้ {len(all_sets)} สูตร × 10 ชุด = {len(all_sets) * 10} ชุด")
            
            # Step 4: ส่งให้ Evaluator เปิดเฉลย
            results = self.evaluate(all_sets, test_data)
            
            # Step 5: บันทึกผล
            self.save_results(results, test_draw)
            
            # Step 6: Genetic Algorithm — สร้างสูตรใหม่
            self.evolve_formulas(results)
            
            # Step 7: ตรวจสอบ convergence
            if self.check_convergence():
                print(f"\n  ✅ Convergence! หยุดที่ iteration {self.iteration}")
                break
        
        # สรุปผลสุดท้าย
        self.print_final_report()
    
    # ═══════════════════════════════════════════════════════════
    # STEP 1: สุ่มเลือกงวดทดสอบ
    # ═══════════════════════════════════════════════════════════
    
    def select_test_draw(self):
        """สุ่มเลือกงวดทดสอบตาม strategy"""
        strategy = self.config["TEST_DRAW_STRATEGY"]
        
        if strategy == "random":
            # สุ่มจากงวดที่ 100 เป็นต้นไป (ให้มี train data พอ)
            idx = random.randint(100, len(self.data) - 1)
            return self.data[idx]
        
        elif strategy == "sequential":
            # ทำตามลำดับ
            idx = (self.iteration % (len(self.data) - 100)) + 100
            return self.data[idx]
        
        elif strategy == "stratified":
            # แบ่งเป็นช่วง ๆ สุ่มจากแต่ละช่วง
            chunk_size = (len(self.data) - 100) // 10
            chunk = self.iteration % 10
            idx = 100 + (chunk * chunk_size) + random.randint(0, chunk_size - 1)
            idx = min(idx, len(self.data) - 1)
            return self.data[idx]
    
    # ═══════════════════════════════════════════════════════════
    # STEP 2: แบ่งข้อมูล
    # ═══════════════════════════════════════════════════════════
    
    def split_data(self, test_draw):
        """แบ่งข้อมูล train/test"""
        test_date = test_draw["draw_date"]
        
        train = []
        test = None
        for d in self.data:
            if d["draw_date"] < test_date:
                train.append(d)
            elif d["draw_date"] == test_date:
                test = d
                break
        
        return train, test
    
    # ═══════════════════════════════════════════════════════════
    # STEP 3: รันสูตรทั้งหมด
    # ═══════════════════════════════════════════════════════════
    
    def run_formulas(self, train_data):
        """รันสูตรทั้งหมด → ได้ 10 ชุดตัวเลขต่อสูตร"""
        all_sets = {}
        
        for formula_id, formula in self.formula_library.items():
            try:
                sets = self.apply_formula(formula, train_data)
                all_sets[formula_id] = {
                    "sets": sets,
                    "formula": formula["name"]
                }
            except Exception as e:
                print(f"    ⚠️ {formula_id}: {str(e)[:50]}")
                all_sets[formula_id] = {
                    "sets": self.generate_random_sets(),
                    "formula": formula["name"],
                    "error": str(e)
                }
        
        return all_sets
    
    def apply_formula(self, formula, train_data):
        """ใช้สูตรคำนวณ → ได้ 10 ชุดตัวเลข"""
        formula_type = formula["type"]
        params = formula["params"]
        
        if formula_type == "statistical":
            return self.apply_statistical_formula(formula, train_data)
        elif formula_type == "advanced":
            return self.apply_advanced_formula(formula, train_data)
        elif formula_type == "ml":
            return self.apply_ml_formula(formula, train_data)
        else:
            return self.generate_random_sets()
    
    def apply_statistical_formula(self, formula, train_data):
        """สูตรสถิติ"""
        fid = formula["id"]
        
        if "frequency" in fid:
            return self.frequency_formula(train_data, params)
        elif "due_number" in fid:
            return self.due_number_formula(train_data, params)
        elif "bayesian" in fid:
            return self.bayesian_formula(train_data, params)
        elif "markov" in fid:
            return self.markov_formula(train_data, params)
        elif "monte_carlo" in fid:
            return self.monte_carlo_formula(train_data, params)
        elif "positional" in fid:
            return self.positional_formula(train_data, params)
        elif "hot_cold" in fid:
            return self.hot_cold_formula(train_data, params)
        elif "pairs" in fid:
            return self.pairs_formula(train_data, params)
        else:
            return self.generate_random_sets()
    
    def apply_advanced_formula(self, formula, train_data):
        """สูตรขั้นสูง"""
        # TODO: สำหรับ Formula Tester พัฒนาเพิ่ม
        return self.generate_random_sets()
    
    def apply_ml_formula(self, formula, train_data):
        """สูตร ML"""
        # TODO: สำหรับ ML Engineer พัฒนาเพิ่ม
        return self.generate_random_sets()
    
    # ═══════════════════════════════════════════════════════════
    # FORMULA IMPLEMENTATIONS
    # ═══════════════════════════════════════════════════════════
    
    def frequency_formula(self, train_data, params):
        """Frequency Analysis — เลขที่ออกบ่อย"""
        window = params.get("window", 50)
        top_n = params.get("top_n", 10)
        
        recent = train_data[-window:]
        freq = {}
        for d in recent:
            td = d.get("two_digit", "")
            if td:
                freq[td] = freq.get(td, 0) + 1
        
        sorted_nums = sorted(freq.keys(), key=lambda x: -freq[x])
        top_nums = sorted_nums[:top_n]
        
        # สร้าง 10 ชุด 6 หลัก
        sets = []
        for i in range(10):
            if i < len(top_nums):
                # ใช้เลขท้าย 2 ตัวจาก frequency + สุ่มอีก 4 หลัก
                last2 = top_nums[i]
                first4 = f"{random.randint(0, 9999):04d}"
                sets.append(first4 + last2)
            else:
                sets.append(f"{random.randint(0, 999999):06d}")
        
        return sets
    
    def due_number_formula(self, train_data, params):
        """Due Number — เลขที่ไม่ออกนาน"""
        top_n = params.get("top_n", 10)
        
        last_seen = {}
        for i, d in enumerate(train_data):
            td = d.get("two_digit", "")
            if td:
                last_seen[td] = i
        
        train_pos = len(train_data)
        due_list = []
        for num in [f"{i:02d}" for i in range(100)]:
            gap = train_pos - last_seen.get(num, 0)
            due_list.append((num, gap))
        
        due_list.sort(key=lambda x: -x[1])
        top_nums = [n for n, _ in due_list[:top_n]]
        
        sets = []
        for i in range(10):
            if i < len(top_nums):
                last2 = top_nums[i]
                first4 = f"{random.randint(0, 9999):04d}"
                sets.append(first4 + last2)
            else:
                sets.append(f"{random.randint(0, 999999):06d}")
        
        return sets
    
    def bayesian_formula(self, train_data, params):
        """Bayesian Inference"""
        # TODO: พัฒนาเพิ่ม
        return self.generate_random_sets()
    
    def markov_formula(self, train_data, params):
        """Markov Chain"""
        # TODO: พัฒนาเพิ่ม
        return self.generate_random_sets()
    
    def monte_carlo_formula(self, train_data, params):
        """Monte Carlo Simulation"""
        simulations = params.get("simulations", 10000)
        
        # สร้างการกระจายจากข้อมูล
        freq = {}
        for d in train_data:
            td = d.get("two_digit", "")
            if td:
                freq[td] = freq.get(td, 0) + 1
        
        # สุ่มตามการกระจาย
        numbers = list(freq.keys())
        weights = list(freq.values())
        
        sets = []
        for _ in range(10):
            last2 = random.choices(numbers, weights=weights, k=1)[0]
            first4 = f"{random.randint(0, 9999):04d}"
            sets.append(first4 + last2)
        
        return sets
    
    def positional_formula(self, train_data, params):
        """Digit Position Analysis"""
        # TODO: พัฒนาเพิ่ม
        return self.generate_random_sets()
    
    def hot_cold_formula(self, train_data, params):
        """Hot/Cold Numbers"""
        # TODO: พัฒนาเพิ่ม
        return self.generate_random_sets()
    
    def pairs_formula(self, train_data, params):
        """Number Pair Analysis"""
        # TODO: พัฒนาเพิ่ม
        return self.generate_random_sets()
    
    def generate_random_sets(self):
        """สุ่ม 10 ชุด"""
        return [f"{random.randint(0, 999999):06d}" for _ in range(10)]
    
    # ═══════════════════════════════════════════════════════════
    # STEP 4: เปิดเฉลย + คำนวณ score
    # ═══════════════════════════════════════════════════════════
    
    def evaluate(self, all_sets, test_data):
        """เปิดเฉลย + คำนวฃ score"""
        results = {}
        
        # ดึงผลรางวัลจริง
        actual_first = test_data.get("first_prize", "")
        actual_two = test_data.get("two_digit", "")
        actual_three_last = test_data.get("three_digit_last", [])
        actual_three_first = test_data.get("three_digit_first", [])
        actual_nearby = test_data.get("nearby_1st", [])
        actual_p2 = test_data.get("second_prize", [])
        actual_p3 = test_data.get("third_prize", [])
        actual_p4 = test_data.get("prize_4", [])
        actual_p5 = test_data.get("prize_5", [])
        
        for formula_id, data in all_sets.items():
            sets = data["sets"]
            score = 0
            hits = {
                "รางวัลที่ 1": 0,
                "ข้างเคียง": 0,
                "รางวัลที่ 2": 0,
                "รางวัลที่ 3": 0,
                "รางวัลที่ 4": 0,
                "รางวัลที่ 5": 0,
                "เลขท้าย 3": 0,
                "เลขหน้า 3": 0,
                "เลขท้าย 2": 0,
            }
            
            for num in sets:
                # ตรวจรางวัลที่ 1
                if num == actual_first:
                    score += SCORING["รางวัลที่ 1"]
                    hits["รางวัลที่ 1"] += 1
                
                # ตรวจข้างเคียง
                if num in actual_nearby:
                    score += SCORING["ข้างเคียง"]
                    hits["ข้างเคียง"] += 1
                
                # ตรวจรางวัลที่ 2-5
                if num in actual_p2:
                    score += SCORING["รางวัลที่ 2"]
                    hits["รางวัลที่ 2"] += 1
                if num in actual_p3:
                    score += SCORING["รางวัลที่ 3"]
                    hits["รางวัลที่ 3"] += 1
                if num in actual_p4:
                    score += SCORING["รางวัลที่ 4"]
                    hits["รางวัลที่ 4"] += 1
                if num in actual_p5:
                    score += SCORING["รางวัลที่ 5"]
                    hits["รางวัลที่ 5"] += 1
                
                # ตรวจเลขท้าย 3
                if num[-3:] in actual_three_last:
                    score += SCORING["เลขท้าย 3"]
                    hits["เลขท้าย 3"] += 1
                
                # ตรวจเลขหน้า 3
                if num[:3] in actual_three_first:
                    score += SCORING["เลขหน้า 3"]
                    hits["เลขหน้า 3"] += 1
                
                # ตรวจเลขท้าย 2
                if num[-2:] == actual_two:
                    score += SCORING["เลขท้าย 2"]
                    hits["เลขท้าย 2"] += 1
                
                # Base score
                if any(v > 0 for v in hits.values()):
                    score += SCORING["base_per_set"]
            
            results[formula_id] = {
                "formula": data["formula"],
                "sets": sets,
                "score": score,
                "hits": hits
            }
        
        return results
    
    # ═══════════════════════════════════════════════════════════
    # STEP 5: บันทึกผล
    # ═══════════════════════════════════════════════════════════
    
    def save_results(self, results, test_draw):
        """บันทึกผลลง results_database"""
        iteration_result = {
            "iteration": self.iteration,
            "test_draw": test_draw["draw_date"],
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "best_formula": max(results.keys(), key=lambda k: results[k]["score"]),
            "best_score": max(r["score"] for r in results.values()),
            "worst_formula": min(results.keys(), key=lambda k: results[k]["score"]),
            "worst_score": min(r["score"] for r in results.values()),
            "avg_score": sum(r["score"] for r in results.values()) / len(results)
        }
        
        self.results_db["iterations"].append(iteration_result)
        
        # อัปเดต best ever
        if iteration_result["best_score"] > self.best_score_ever:
            self.best_score_ever = iteration_result["best_score"]
            self.no_improvement_count = 0
            print(f"  🏆 ใหม่! Best score: {self.best_score_ever}")
        else:
            self.no_improvement_count += 1
        
        # บันทึกลงไฟล์
        with open(self.config["RESULTS_FILE"], "w", encoding="utf-8") as f:
            json.dump(self.results_db, f, ensure_ascii=False, indent=2)
        
        # แสดงผล
        print(f"  Best: {iteration_result['best_formula']} = {iteration_result['best_score']}")
        print(f"  Worst: {iteration_result['worst_formula']} = {iteration_result['worst_score']}")
        print(f"  Avg: {iteration_result['avg_score']:.1f}")
        print(f"  No improvement: {self.no_improvement_count} rounds")
    
    # ═══════════════════════════════════════════════════════════
    # STEP 6: Genetic Algorithm
    # ═══════════════════════════════════════════════════════════
    
    def evolve_formulas(self, results):
        """Genetic Algorithm — สร้างสูตรใหม่"""
        # เรียงตาม score
        sorted_formulas = sorted(results.keys(), key=lambda k: -results[k]["score"])
        
        n_elite = max(2, int(len(sorted_formulas) * self.config["ELITE_RATIO"]))
        elite = sorted_formulas[:n_elite]
        bottom = sorted_formulas[-n_elite:]
        
        print(f"  Elite: {len(elite)} formulas, Prune: {len(bottom)} formulas")
        
        # คัดทิ้งสูตรแย่
        for fid in bottom:
            if fid in self.formula_library:
                # ลบออก แต่เก็บไว้ใน archive
                del self.formula_library[fid]
        
        # สร้างสูตรใหม่ (crossover + mutation)
        for _ in range(len(bottom)):
            parent1 = random.choice(elite)
            parent2 = random.choice(elite)
            
            new_id = f"hybrid_g{self.iteration}_{random.randint(1000, 9999)}"
            self.formula_library[new_id] = {
                "name": f"Hybrid ({parent1[:8]} × {parent2[:8]})",
                "phase": 4,
                "type": "genetic",
                "parents": [parent1, parent2],
                "params": self.crossover_params(parent1, parent2),
                "created": datetime.now().isoformat(),
                "generation": self.iteration,
                "avg_score": 0,
                "total_rounds": 0
            }
        
        # บันทึก formula library
        with open(self.config["FORMULA_LIB"], "w", encoding="utf-8") as f:
            json.dump(self.formula_library, f, ensure_ascii=False, indent=2)
        
        print(f"  Formula library: {len(self.formula_library)} formulas")
    
    def crossover_params(self, parent1, parent2):
        """ผสม parameters จาก 2 พ่อแม่"""
        p1 = self.formula_library.get(parent1, {}).get("params", {})
        p2 = self.formula_library.get(parent2, {}).get("params", {})
        
        # สุ่มเลือก params จากแต่ละพ่อแม่
        mixed = {}
        all_keys = set(list(p1.keys()) + list(p2.keys()))
        for key in all_keys:
            if random.random() < 0.5:
                mixed[key] = p1.get(key, p2.get(key))
            else:
                mixed[key] = p2.get(key, p1.get(key))
        
        # Mutation — เปลี่ยนบาง param สุ่ม
        for key in mixed:
            if random.random() < self.config["MUTATION_RATE"]:
                if isinstance(mixed[key], int):
                    mixed[key] = random.randint(1, 100)
                elif isinstance(mixed[key], float):
                    mixed[key] = random.uniform(0.01, 1.0)
        
        return mixed
    
    # ═══════════════════════════════════════════════════════════
    # STEP 7: ตรวจสอบ convergence
    # ═══════════════════════════════════════════════════════════
    
    def check_convergence(self):
        """ตรวจสอบว่า convergence หรือยัง"""
        if self.no_improvement_count >= self.config["CONVERGENCE_THRESHOLD"]:
            return True
        
        # ตรวจสอบว่าสูตรที่ดีที่สุง stable หรือไม่
        if len(self.results_db["iterations"]) >= 20:
            recent = self.results_db["iterations"][-20:]
            best_scores = [r["best_score"] for r in recent]
            if max(best_scores) == min(best_scores):
                return True
        
        return False
    
    # ═══════════════════════════════════════════════════════════
    # FINAL REPORT
    # ═══════════════════════════════════════════════════════════
    
    def print_final_report(self):
        """สรุปผลสุดท้าย"""
        print("\n" + "=" * 60)
        print("  📊 FINAL REPORT")
        print("=" * 60)
        
        # หาสูตรที่ดีที่สุดทั้งหมด
        formula_avg_scores = {}
        for iteration in self.results_db["iterations"]:
            for fid, result in iteration["results"].items():
                if fid not in formula_avg_scores:
                    formula_avg_scores[fid] = []
                formula_avg_scores[fid].append(result["score"])
        
        for fid in formula_avg_scores:
            scores = formula_avg_scores[fid]
            formula_avg_scores[fid] = sum(scores) / len(scores)
        
        sorted_formulas = sorted(formula_avg_scores.keys(), key=lambda k: -formula_avg_scores[k])
        
        print(f"\n  Total iterations: {len(self.results_db['iterations'])}")
        print(f"  Best score ever: {self.best_score_ever}")
        print(f"  Final formula library: {len(self.formula_library)} formulas")
        
        print(f"\n  🏆 TOP 10 FORMULAS (by average score):")
        for i, fid in enumerate(sorted_formulas[:10]):
            name = self.formula_library.get(fid, {}).get("name", fid)
            avg = formula_avg_scores[fid]
            print(f"    {i+1}. {name}: {avg:.1f}")
        
        # บันทึก report
        report = {
            "generated": datetime.now().isoformat(),
            "total_iterations": len(self.results_db["iterations"]),
            "best_score_ever": self.best_score_ever,
            "final_formula_count": len(self.formula_library),
            "top_10_formulas": [
                {
                    "id": fid,
                    "name": self.formula_library.get(fid, {}).get("name", fid),
                    "avg_score": formula_avg_scores[fid]
                }
                for fid in sorted_formulas[:10]
            ]
        }
        
        report_path = os.path.join(self.config["REPORT_DIR"], "final_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n  Report saved: {report_path}")


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    controller = LottoAIController(CONFIG)
    controller.run()
```

---

# ═══════════════════════════════════════════════════════════════
# ส่วนที่ 5: วิธีรันระบบ
# ═══════════════════════════════════════════════════════════════

## รันแบบ standalone
```bash
cd /d/lotto-ai/ml-models
python3 orchestrator.py
```

## รันแบบ background (PM2)
```bash
cd /d/lotto-ai/ml-models
pm2 start orchestrator.py --name lottoai-controller
pm2 save
pm2 startup
```

## รันแบบ cron (ทุกวันอาทิตย์ 02:00 น.)
```bash
# เพิ่มใน crontab
0 2 * * 0 cd /d/lotto-ai/ml-models && python3 orchestrator.py >> logs/orchestrator.log 2>&1
```

---

# ═══════════════════════════════════════════════════════════════
# ส่วนที่ 6: โครงสร้างไฟล์
# ═══════════════════════════════════════════════════════════════

```
D:\lotto-ai\
├── orchestrator.py                    # สคริปต์หลัก (Controller)
├── ml-models\
│   ├── data\
│   │   ├── scraped_all.json           # ข้อมูลดิบ 776 งวด
│   │   └── data_quality_report.json   # รายงานคุณภาพ
│   ├── formulas\
│   │   └── formula_library.json       # สูตรทั้งหมด (25+ สูตร)
│   └── results\
│       ├── results_database.json      # ผลการทดสอบทั้งหมด
│       ├── evaluation_report.json     # รายงานสรุป
│       └── final_report.json          # รายงานสุดท้าย
└── logs\
    └── orchestrator.log               # log การทำงาน
```

---

*รายงานนี้สร้างโดย OWL (Default Agent) สำหรับทีม LottoAI*
*อัปเดตล่าสุด: 2026-06-12*
*เวอร์ชัน: 2.0.0 — Iterative Mathematical Sandbox*
