#!/usr/bin/env python3
"""
LottoAI — Formula Tester Agent
Walk-Forward Backtesting Engine
ทดลองทุกสูตรย้อนหลัง 750 งวด → หาสูตรที่ 10 ชุดถูกรางวัลทุกชุด
"""
import json, os, re, math, random
from collections import Counter, defaultdict
from datetime import datetime

DATA_DIR = r"D:\lotto-ai\ml-models\data"
FORMULA_DIR = r"D:\lotto-ai\ml-models\formulas"
RESULTS_DIR = r"D:\lotto-ai\ml-models\results"

os.makedirs(FORMULA_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ── Load Data ──────────────────────────────────────────────
with open(os.path.join(DATA_DIR, "scraped_all.json"), "r", encoding="utf-8") as f:
    all_draws = json.load(f)

all_draws.sort(key=lambda d: d["draw_date"])
print(f"โหลดข้อมูล: {len(all_draws)} งวด ({all_draws[0]['draw_date']} → {all_draws[-1]['draw_date']})")

# ── Helper Functions ──────────────────────────────────────
def safe_list(v):
    if not v: return []
    if isinstance(v, list): return v
    try: return json.loads(v)
    except: return []

def safe_str(v):
    if not v: return ""
    return str(v)

def get_prize_values(draw):
    """Extract all prize values from a draw"""
    prizes = {
        "first_prize": safe_str(draw.get("first_prize")),
        "nearby_1st": safe_list(draw.get("nearby_1st")),
        "second_prize": safe_list(draw.get("second_prize")),
        "third_prize": safe_list(draw.get("third_prize")),
        "prize_4": safe_list(draw.get("prize_4")),
        "prize_5": safe_list(draw.get("prize_5")),
        "three_digit_last": safe_list(draw.get("three_digit_last")),
        "three_digit_first": safe_list(draw.get("three_digit_first")),
        "two_digit": safe_str(draw.get("two_digit")),
    }
    return prizes

def check_prize(number_6digit, prizes):
    """Check which prize tier a 6-digit number wins"""
    if not number_6digit or len(number_6digit) != 6:
        return None
    
    # รางวัลที่ 1
    if number_6digit == prizes["first_prize"]:
        return "รางวัลที่ 1"
    
    # รางวัลข้างเคียง (±1)
    fp = prizes["first_prize"]
    if fp and len(fp) == 6:
        try:
            fp_int = int(fp)
            num_int = int(number_6digit)
            if abs(num_int - fp_int) == 1:
                return "ข้างเคียง"
        except:
            pass
    
    # รางวัลที่ 2
    if number_6digit in prizes["second_prize"]:
        return "รางวัลที่ 2"
    
    # รางวัลที่ 3
    if number_6digit in prizes["third_prize"]:
        return "รางวัลที่ 3"
    
    # รางวัลที่ 4
    if number_6digit in prizes["prize_4"]:
        return "รางวัลที่ 4"
    
    # รางวัลที่ 5
    if number_6digit in prizes["prize_5"]:
        return "รางวัลที่ 5"
    
    # เลขท้าย 3 ตัว
    last3 = number_6digit[-3:]
    if last3 in prizes["three_digit_last"]:
        return "เลขท้าย 3"
    
    # เลขหน้า 3 ตัว
    first3 = number_6digit[:3]
    if first3 in prizes["three_digit_first"]:
        return "เลขหน้า 3"
    
    # เลขท้าย 2 ตัว
    last2 = number_6digit[-2:]
    target_2d = prizes["two_digit"]
    if target_2d and last2 == target_2d:
        return "เลขท้าย 2"
    
    return None  # ไม่ถูกรางวัล

def score_round(results):
    """Score a single test round"""
    sets_won = sum(1 for r in results if r is not None)
    base_score = sets_won * 10
    
    bonus = 0
    for r in results:
        if r == "รางวัลที่ 1": bonus += 50
        elif r == "ข้างเคียง": bonus += 25
        elif r == "รางวัลที่ 2": bonus += 30
        elif r == "รางวัลที่ 3": bonus += 20
        elif r == "รางวัลที่ 4": bonus += 15
        elif r == "รางวัลที่ 5": bonus += 10
        elif r == "เลขท้าย 3": bonus += 5
        elif r == "เลขหน้า 3": bonus += 5
        elif r == "เลขท้าย 2": bonus += 3
    
    return base_score + bonus, sets_won

# ── Formula Definitions ───────────────────────────────────

def freq_analysis(train_draws, top_n=10):
    """Frequency Analysis — เลขที่ออกบ่อยที่สุด"""
    freq = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for digit in fp:
                freq[digit] += 1
    
    # Generate numbers from most frequent digits
    digits = [d for d, _ in freq.most_common(10)]
    if len(digits) < 6:
        digits = list("0123456789")
    
    numbers = []
    for i in range(top_n):
        random.seed(i)
        num = ''.join(random.choices(digits[:6], k=6))
        numbers.append(num)
    
    return numbers

def due_number_analysis(train_draws, top_n=10):
    """Due Number — เลขที่ไม่ออกนาน"""
    last_seen = {}
    for idx, d in enumerate(train_draws):
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for digit in fp:
                if digit not in last_seen:
                    last_seen[digit] = idx
    
    # Numbers not seen recently (highest gap)
    gaps = {}
    for digit in "0123456789":
        if digit in last_seen:
            gaps[digit] = len(train_draws) - last_seen[digit]
        else:
            gaps[digit] = len(train_draws) + 100
    
    sorted_digits = sorted(gaps.keys(), key=lambda d: gaps[d], reverse=True)
    
    numbers = []
    for i in range(top_n):
        selected = sorted_digits[:6] if len(sorted_digits) >= 6 else list("0123456789")
        random.seed(i + 100)
        random.shuffle(selected)
        num = ''.join(selected[:6])
        numbers.append(num)
    
    return numbers

def recency_weighted(train_draws, top_n=10):
    """Recency Weighted — เลขที่ออกบ่อยในช่วงล่าสุด"""
    freq = Counter()
    for i, d in enumerate(train_draws):
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            weight = (i + 1) / len(train_draws)  # Recent draws get higher weight
            for digit in fp:
                freq[digit] += weight
    
    digits = [d for d, _ in freq.most_common(10)]
    if len(digits) < 6:
        digits = list("0123456789")
    
    numbers = []
    for i in range(top_n):
        random.seed(i + 200)
        num = ''.join(random.choices(digits[:6], k=6))
        numbers.append(num)
    
    return numbers

def digit_position_analysis(train_draws, top_n=10):
    """Digit Position Analysis — วิเคราะห์แต่ละตำแหน่ง"""
    pos_freq = [Counter() for _ in range(6)]
    
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for pos in range(6):
                pos_freq[pos][fp[pos]] += 1
    
    # For each position, pick the most frequent digit
    best_digits = []
    for pos in range(6):
        if pos_freq[pos]:
            best_digits.append(pos_freq[pos].most_common(1)[0][0])
        else:
            best_digits.append(str(pos))
    
    numbers = []
    base = ''.join(best_digits)
    numbers.append(base)
    
    # Generate variations
    for i in range(1, top_n):
        variant = list(base)
        # Randomly change 1-2 positions
        for _ in range(random.randint(1, 2)):
            pos = random.randint(0, 5)
            variant[pos] = str(random.randint(0, 9))
        numbers.append(''.join(variant))
    
    return numbers

def monte_carlo_simulation(train_draws, top_n=10, simulations=10000):
    """Monte Carlo — สุ่มตามกฎสถิติ"""
    freq = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for digit in fp:
                freq[digit] += 1
    
    digits = list("0123456789")
    weights = [freq.get(d, 1) for d in digits]
    
    best_numbers = []
    for _ in range(simulations):
        num = ''.join(random.choices(digits, weights=weights, k=6))
        best_numbers.append(num)
    
    # Return most common generated numbers
    counter = Counter(best_numbers)
    return [num for num, _ in counter.most_common(top_n)]

def markov_chain(train_draws, top_n=10):
    """Markov Chain — รูปแบบการเปลี่ยนเลข"""
    transitions = defaultdict(Counter)
    
    prev_fp = None
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            if prev_fp and len(prev_fp) == 6:
                for pos in range(6):
                    transitions[(pos, prev_fp[pos])][fp[pos]] += 1
            prev_fp = fp
    
    # Generate numbers based on transitions
    last_fp = prev_fp if last_fp else "000000"
    numbers = []
    
    for i in range(top_n):
        num = ""
        for pos in range(6):
            key = (pos, last_fp[pos])
            if key in transitions and transitions[key]:
                next_digit = transitions[key].most_common(1)[0][0]
            else:
                next_digit = str(random.randint(0, 9))
            num += next_digit
        numbers.append(num)
    
    return numbers

def bayesian_inference(train_draws, top_n=10):
    """Bayesian — ความน่าจะเป็น posterior"""
    # Prior: uniform distribution
    # Likelihood: observed frequency
    # Posterior: updated probability
    
    digit_counts = Counter()
    total_digits = 0
    
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for digit in fp:
                digit_counts[digit] += 1
                total_digits += 1
    
    # Posterior probability for each digit
    posterior = {}
    for digit in "0123456789":
        # Laplace smoothing
        posterior[digit] = (digit_counts.get(digit, 0) + 1) / (total_digits + 10)
    
    # Generate numbers from posterior distribution
    digits = list("0123456789")
    weights = [posterior[d] for d in digits]
    
    numbers = []
    for i in range(top_n):
        random.seed(i + 300)
        num = ''.join(random.choices(digits, weights=weights, k=6))
        numbers.append(num)
    
    return numbers

def hot_cold_analysis(train_draws, top_n=10):
    """Hot/Cold — เลขร้อนเย็น"""
    recent = Counter()
    old = Counter()
    
    split = len(train_draws) // 2
    
    for d in train_draws[:split]:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for digit in set(fp):
                old[digit] += 1
    
    for d in train_draws[split:]:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for digit in set(fp):
                recent[digit] += 1
    
    # Hot numbers: high recent frequency
    hot = [d for d, _ in recent.most_common(5)]
    # Cold numbers: high old frequency but low recent
    cold = [d for d, _ in old.most_common(5) if d not in hot]
    
    combined = hot + cold
    if len(combined) < 6:
        combined = list("0123456789")
    
    numbers = []
    for i in range(top_n):
        random.seed(i + 400)
        random.shuffle(combined)
        num = ''.join(combined[:6])
        numbers.append(num)
    
    return numbers

def sum_analysis(train_draws, top_n=10):
    """Sum Analysis — ผลรวมของเลข"""
    sums = []
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            s = sum(int(c) for c in fp)
            sums.append(s)
    
    if not sums:
        return [str(random.randint(100000, 999999)).zfill(6) for _ in range(top_n)]
    
    avg_sum = sum(sums) / len(sums)
    target_sum = int(avg_sum)
    
    numbers = []
    for i in range(top_n):
        # Generate numbers with sum close to target
        digits = []
        remaining = target_sum
        for pos in range(6):
            if pos == 5:
                d = max(0, min(9, remaining))
            else:
                avg_remaining = remaining / (6 - pos)
                d = max(0, min(9, int(avg_remaining + random.randint(-2, 2))))
            digits.append(str(d))
            remaining -= d
        numbers.append(''.join(digits))
    
    return numbers

def pair_analysis(train_draws, top_n=10):
    """Pair Analysis — เลขที่ออกด้วยกัน"""
    pair_freq = Counter()
    
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for i in range(len(fp)):
                for j in range(i+1, len(fp)):
                    pair_freq[(fp[i], fp[j])] += 1
    
    # Get top pairs
    top_pairs = pair_freq.most_common(20)
    
    numbers = []
    for i in range(top_n):
        digits = []
        used = set()
        for (a, b), _ in top_pairs:
            if a not in used and len(digits) < 6:
                digits.append(a)
                used.add(a)
            if b not in used and len(digits) < 6:
                digits.append(b)
                used.add(b)
            if len(digits) >= 6:
                break
        
        while len(digits) < 6:
            for d in "0123456789":
                if d not in used:
                    digits.append(d)
                    used.add(d)
                    break
        
        numbers.append(''.join(digits[:6]))
    
    return numbers

def ensemble_formula(train_draws, top_n=10):
    """Ensemble — รวมทุกสูตร"""
    all_numbers = []
    
    all_numbers.extend(freq_analysis(train_draws, 3))
    all_numbers.extend(due_number_analysis(train_draws, 3))
    all_numbers.extend(recency_weighted(train_draws, 3))
    all_numbers.extend(digit_position_analysis(train_draws, 3))
    all_numbers.extend(monte_carlo_simulation(train_draws, 3))
    all_numbers.extend(markov_chain(train_draws, 3))
    all_numbers.extend(bayesian_inference(train_draws, 3))
    all_numbers.extend(hot_cold_analysis(train_draws, 3))
    all_numbers.extend(sum_analysis(train_draws, 3))
    all_numbers.extend(pair_analysis(train_draws, 3))
    
    # Score each number by how many formulas generated it
    counter = Counter(all_numbers)
    return [num for num, _ in counter.most_common(top_n)]

# ── Formula Registry ──────────────────────────────────────
FORMULAS = {
    "1. Frequency Analysis": freq_analysis,
    "2. Due Number": due_number_analysis,
    "3. Recency Weighted": recency_weighted,
    "4. Digit Position": digit_position_analysis,
    "5. Monte Carlo": monte_carlo_simulation,
    "6. Markov Chain": markov_chain,
    "7. Bayesian Inference": bayesian_inference,
    "8. Hot/Cold Analysis": hot_cold_analysis,
    "9. Sum Analysis": sum_analysis,
    "10. Pair Analysis": pair_analysis,
    "11. Ensemble": ensemble_formula,
}

# ── Walk-Forward Backtesting ──────────────────────────────
print(f"\nเริ่ม Walk-Forward Backtesting...")
print(f"สูตรที่ทดสอบ: {len(FORMULAS)} สูตร")
print(f"จำนวนรอบทดสอบ: {len(all_draws) - 1} รอบ")
print()

# Results storage
formula_results = {name: {
    "total_score": 0,
    "total_rounds": 0,
    "perfect_rounds": 0,
    "sets_won_total": 0,
    "prize_counts": defaultdict(int),
    "best_round": None,
    "best_round_score": 0,
} for name in FORMULAS}

# Walk-forward: start from draw 100 (need minimum history)
START_IDX = 100
test_rounds = 0

for test_idx in range(START_IDX, len(all_draws)):
    train_draws = all_draws[:test_idx]
    test_draw = all_draws[test_idx]
    test_date = test_draw["draw_date"]
    prizes = get_prize_values(test_draw)
    
    test_rounds += 1
    
    for formula_name, formula_fn in FORMULAS.items():
        try:
            # Generate 10 number sets
            numbers = formula_fn(train_draws, top_n=10)
            
            # Check each number against prizes
            results = []
            for num in numbers:
                prize = check_prize(num, prizes)
                results.append(prize)
            
            # Score
            score, sets_won = score_round(results)
            
            # Record
            r = formula_results[formula_name]
            r["total_score"] += score
            r["total_rounds"] += 1
            r["sets_won_total"] += sets_won
            
            if sets_won == 10:
                r["perfect_rounds"] += 1
            
            for prize in results:
                if prize:
                    r["prize_counts"][prize] += 1
            
            if score > r["best_round_score"]:
                r["best_round_score"] = score
                r["best_round"] = {
                    "date": test_date,
                    "numbers": numbers,
                    "results": results,
                    "score": score
                }
        
        except Exception as e:
            pass  # Skip failed formulas
    
    # Progress
    if test_rounds % 50 == 0 or test_idx == len(all_draws) - 1:
        elapsed = test_rounds
        total = len(all_draws) - START_IDX
        pct = elapsed / total * 100
        print(f"  [{elapsed}/{total}] ({pct:.0f}%) — ทดสอบถึง {test_date}")

# ── Generate Report ──────────────────────────────────────
print(f"\n{'='*60}")
print(f"  FORMULA TEST REPORT")
print(f"{'='*60}")
print(f"ช่วงทดสอบ: {all_draws[START_IDX]['draw_date']} → {all_draws[-1]['draw_date']}")
print(f"จำนวนรอบทดสอบ: {test_rounds} รอบ")
print(f"จำนวนสูตร: {len(FORMULAS)} สูตร")
print()

# Rank formulas
ranked = sorted(formula_results.items(), key=lambda x: x[1]["total_score"], reverse=True)

print(f"🏆 อันดับสูตร (เรียงจากดีที่สุด):")
print()

for rank, (name, r) in enumerate(ranked, 1):
    avg_score = r["total_score"] / r["total_rounds"] if r["total_rounds"] > 0 else 0
    avg_sets = r["sets_won_total"] / r["total_rounds"] if r["total_rounds"] > 0 else 0
    perfect_pct = r["perfect_rounds"] / r["total_rounds"] * 100 if r["total_rounds"] > 0 else 0
    
    print(f"{rank}. {name}")
    print(f"   คะแนนรวม: {r['total_score']:,}")
    print(f"   เฉลี่ย: {avg_sets:.1f}/10 ชุด ถูกรางวัลต่องวด")
    print(f"   Perfect rounds (10/10): {r['perfect_rounds']} งวด ({perfect_pct:.1f}%)")
    
    # Prize breakdown
    if r["prize_counts"]:
        prize_str = ", ".join(f"{k}: {v}" for k, v in sorted(r["prize_counts"].items(), key=lambda x: x[1], reverse=True)[:5])
        print(f"   รางวัลที่ถูก: {prize_str}")
    
    # Best round
    if r["best_round"]:
        print(f"   งวดที่ดีที่สุด: {r['best_round']['date']} (คะแนน {r['best_round']['score']})")
    
    print()

# Best formula
best_name, best_r = ranked[0]
print(f"🏆 สูตรที่ดีที่สุด: {best_name}")
print(f"   คะแนนรวม: {best_r['total_score']:,}")
print(f"   เฉลี่ย: {best_r['sets_won_total']/best_r['total_rounds']:.1f}/10 ชุด ถูกรางวัล")

# Generate recommended numbers for next draw
print(f"\n📝 เลข 10 ชุดแนะนำสำหรับงวดถัดไป:")
best_fn = FORMULAS[best_name]
recommended = best_fn(all_draws, top_n=10)
for i, num in enumerate(recommended, 1):
    print(f"   ชุด {i}: {num}")

# ── Save Results ──────────────────────────────────────────
# Formula library
formula_library = []
for name, r in ranked:
    formula_library.append({
        "name": name,
        "total_score": r["total_score"],
        "avg_sets_won": r["sets_won_total"]/r["total_rounds"] if r["total_rounds"] > 0 else 0,
        "perfect_rounds": r["perfect_rounds"],
        "perfect_rate": r["perfect_rounds"]/r["total_rounds"]*100 if r["total_rounds"] > 0 else 0,
        "prize_counts": dict(r["prize_counts"]),
        "best_round": r["best_round"],
    })

with open(os.path.join(FORMULA_DIR, "formula_library.json"), "w", encoding="utf-8") as f:
    json.dump(formula_library, f, ensure_ascii=False, indent=2)

# Full results
with open(os.path.join(RESULTS_DIR, "walk_forward_results.json"), "w", encoding="utf-8") as f:
    json.dump({
        "test_date": datetime.now().isoformat(),
        "total_rounds": test_rounds,
        "formulas_tested": len(FORMULAS),
        "results": {name: {
            "total_score": r["total_score"],
            "total_rounds": r["total_rounds"],
            "perfect_rounds": r["perfect_rounds"],
            "avg_sets_won": r["sets_won_total"]/r["total_rounds"] if r["total_rounds"] > 0 else 0,
            "prize_counts": dict(r["prize_counts"]),
        } for name, r in formula_results.items()},
        "best_formula": best_name,
        "recommended_numbers": recommended,
    }, f, ensure_ascii=False, indent=2)

print(f"\n💾 บันทึกผล:")
print(f"   Formula Library: {os.path.join(FORMULA_DIR, 'formula_library.json')}")
print(f"   Results: {os.path.join(RESULTS_DIR, 'walk_forward_results.json')}")
print(f"\n✅ เสร็จสิ้น!")
