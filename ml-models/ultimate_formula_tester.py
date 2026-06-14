#!/usr/bin/env python3
"""
LottoAI — Ultimate Formula Tester
Walk-Forward Backtesting with 30+ formulas from Knowledge Base
ทดสอบทุกสูตรย้อนหลัง 776 งวด → หาสูตรที่ 10 ชุดถูกรางวัลทุกชุด
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
    return {
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

def check_prize(number_6digit, prizes):
    """Check which prize tier a 6-digit number wins. Returns prize name or None."""
    if not number_6digit or len(number_6digit) != 6:
        return None
    
    fp = prizes.get("first_prize", "")
    
    # รางวัลที่ 1
    if fp and number_6digit == fp:
        return "รางวัลที่ 1"
    
    # ข้างเคียง (±1)
    if fp and len(fp) == 6:
        try:
            if abs(int(number_6digit) - int(fp)) == 1:
                return "ข้างเคียง"
        except:
            pass
    
    # รางวัลที่ 2
    if number_6digit in prizes.get("second_prize", []):
        return "รางวัลที่ 2"
    
    # รางวัลที่ 3
    if number_6digit in prizes.get("third_prize", []):
        return "รางวัลที่ 3"
    
    # รางวัลที่ 4
    if number_6digit in prizes.get("prize_4", []):
        return "รางวัลที่ 4"
    
    # รางวัลที่ 5
    if number_6digit in prizes.get("prize_5", []):
        return "รางวัลที่ 5"
    
    # เลขท้าย 3 ตัว
    last3 = number_6digit[-3:]
    if last3 in prizes.get("three_digit_last", []):
        return "เลขท้าย 3"
    
    # เลขหน้า 3 ตัว
    first3 = number_6digit[:3]
    if first3 in prizes.get("three_digit_first", []):
        return "เลขหน้า 3"
    
    # เลขท้าย 2 ตัว
    last2 = number_6digit[-2:]
    target_2d = prizes.get("two_digit", "")
    if target_2d and last2 == target_2d:
        return "เลขท้าย 2"
    
    return None

def score_round(results):
    """Score: base 10 per winning set + bonus for higher tiers"""
    BONUS = {
        "รางวัลที่ 1": 50, "ข้างเคียง": 25, "รางวัลที่ 2": 30,
        "รางวัลที่ 3": 20, "รางวัลที่ 4": 15, "รางวัลที่ 5": 10,
        "เลขท้าย 3": 5, "เลขหน้า 3": 5, "เลขท้าย 2": 3,
    }
    sets_won = sum(1 for r in results if r is not None)
    base = sets_won * 10
    bonus = sum(BONUS.get(r, 0) for r in results if r)
    return base + bonus, sets_won

def generate_unique_numbers(seed_val, count=10):
    """Generate unique 6-digit numbers"""
    random.seed(seed_val)
    numbers = set()
    attempts = 0
    while len(numbers) < count and attempts < count * 100:
        num = str(random.randint(0, 999999)).zfill(6)
        numbers.add(num)
        attempts += 1
    # Fill remaining with deterministic numbers if random didn't produce enough
    while len(numbers) < count:
        num = str(seed_val * 1000 + len(numbers)).zfill(6)[-6:]
        numbers.add(num)
    return list(numbers)[:count]

# ── 30+ Formula Definitions ───────────────────────────────

def formula_frequency(train_draws, top_n=10):
    """1. Frequency Analysis — เลขที่ออกบ่อยที่สุด"""
    freq = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for digit in fp:
                freq[digit] += 1
    digits = [d for d, _ in freq.most_common(10)] or list("0123456789")
    numbers = []
    for i in range(top_n):
        random.seed(i + 1)
        num = ''.join(random.choices(digits[:6], k=6))
        numbers.append(num)
    return numbers

def formula_due_number(train_draws, top_n=10):
    """2. Due Number (Gap Analysis) — เลขที่ไม่ออกนาน"""
    last_seen = {}
    for idx, d in enumerate(train_draws):
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for digit in fp:
                if digit not in last_seen:
                    last_seen[digit] = idx
    gaps = {d: (len(train_draws) - last_seen[d]) if d in last_seen else len(train_draws) + 100 for d in "0123456789"}
    sorted_digits = sorted(gaps.keys(), key=lambda d: gaps[d], reverse=True)
    numbers = []
    for i in range(top_n):
        selected = sorted_digits[:6] if len(sorted_digits) >= 6 else list("0123456789")
        random.seed(i + 200)
        random.shuffle(selected)
        numbers.append(''.join(selected[:6]))
    return numbers

def formula_recency_weighted(train_draws, top_n=10):
    """3. Recency Weighted — เลขล่าสุดมีน้ำหนักมาก"""
    freq = Counter()
    for i, d in enumerate(train_draws):
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            weight = (i + 1) / max(len(train_draws), 1)
            for digit in fp:
                freq[digit] += weight
    digits = [d for d, _ in freq.most_common(10)] or list("0123456789")
    numbers = []
    for i in range(top_n):
        random.seed(i + 300)
        numbers.append(''.join(random.choices(digits[:6], k=6)))
    return numbers

def formula_digit_position(train_draws, top_n=10):
    """4. Digit Position Analysis — วิเคราะห์แต่ละตำแหน่ง"""
    pos_freq = [Counter() for _ in range(6)]
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for pos in range(6):
                pos_freq[pos][fp[pos]] += 1
    best_digits = []
    for pos in range(6):
        if pos_freq[pos]:
            best_digits.append(pos_freq[pos].most_common(1)[0][0])
        else:
            best_digits.append(str(pos))
    numbers = []
    base = ''.join(best_digits)
    numbers.append(base)
    for i in range(1, top_n):
        variant = list(base)
        for _ in range(random.randint(1, 2)):
            pos = random.randint(0, 5)
            variant[pos] = str(random.randint(0, 9))
        numbers.append(''.join(variant))
    return numbers

def formula_monte_carlo(train_draws, top_n=10, simulations=5000):
    """5. Monte Carlo Simulation"""
    freq = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for digit in fp:
                freq[digit] += 1
    digits = list("0123456789")
    weights = [freq.get(d, 1) for d in digits]
    if sum(weights) == 0:
        weights = [1] * 10
    generated = []
    for _ in range(simulations):
        num = ''.join(random.choices(digits, weights=weights, k=6))
        generated.append(num)
    counter = Counter(generated)
    return [num for num, _ in counter.most_common(top_n)]

def formula_markov_chain(train_draws, top_n=10):
    """6. Markov Chain — รูปแบบการเปลี่ยนเลข"""
    transitions = defaultdict(Counter)
    prev_fp = None
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            if prev_fp and len(prev_fp) == 6:
                for pos in range(6):
                    transitions[(pos, prev_fp[pos])][fp[pos]] += 1
            prev_fp = fp
    if not prev_fp:
        prev_fp = "000000"
    numbers = []
    for i in range(top_n):
        num = ""
        for pos in range(6):
            key = (pos, prev_fp[pos])
            if key in transitions and transitions[key]:
                next_digits = transitions[key].most_common(3)
                next_digit = random.choice([d for d, _ in next_digits])[0] if next_digits else str(random.randint(0, 9))
            else:
                next_digit = str(random.randint(0, 9))
            num += next_digit
        numbers.append(num)
    return numbers

def formula_bayesian(train_draws, top_n=10):
    """7. Bayesian Inference"""
    digit_counts = Counter()
    total = 0
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for digit in fp:
                digit_counts[digit] += 1
                total += 1
    posterior = {d: (digit_counts.get(d, 0) + 1) / (total + 10) for d in "0123456789"}
    digits = list("0123456789")
    weights = [posterior[d] for d in digits]
    numbers = []
    for i in range(top_n):
        random.seed(i + 700)
        numbers.append(''.join(random.choices(digits, weights=weights, k=6)))
    return numbers

def formula_hot_cold(train_draws, top_n=10):
    """8. Hot/Cold Analysis"""
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
    hot = [d for d, _ in recent.most_common(5)]
    cold = [d for d, _ in old.most_common(5) if d not in hot]
    combined = (hot + cold) or list("0123456789")
    numbers = []
    for i in range(top_n):
        random.seed(i + 800)
        shuffled = combined[:6] if len(combined) >= 6 else list("0123456789")
        random.shuffle(shuffled)
        numbers.append(''.join(shuffled[:6]))
    return numbers

def formula_sum_analysis(train_draws, top_n=10):
    """9. Sum Analysis — ผลรวมของเลข"""
    sums = []
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            sums.append(sum(int(c) for c in fp))
    if not sums:
        return generate_unique_numbers(900, top_n)
    avg_sum = sum(sums) / len(sums)
    target = int(avg_sum)
    numbers = []
    for i in range(top_n):
        digits = []
        remaining = target
        for pos in range(6):
            if pos == 5:
                d = max(0, min(9, remaining))
            else:
                avg_rem = remaining / (6 - pos)
                d = max(0, min(9, int(avg_rem + random.randint(-2, 2))))
            digits.append(str(d))
            remaining -= d
        numbers.append(''.join(digits))
    return numbers

def formula_pair_analysis(train_draws, top_n=10):
    """10. Pair Analysis — เลขที่ออกด้วยกัน"""
    pair_freq = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for i in range(len(fp)):
                for j in range(i+1, len(fp)):
                    pair_freq[(fp[i], fp[j])] += 1
    top_pairs = pair_freq.most_common(20)
    numbers = []
    for i in range(top_n):
        digits = []
        used = set()
        random.seed(i + 1000)
        shuffled_pairs = list(top_pairs)
        random.shuffle(shuffled_pairs)
        for (a, b), _ in shuffled_pairs:
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

def formula_benford(train_draws, top_n=10):
    """11. Benford's Law"""
    first_digit_freq = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6 and fp[0] != '0':
            first_digit_freq[fp[0]] += 1
    # Benford's expected: 1=30.1%, 2=17.6%, 3=12.5%, ...
    benford_weights = {'1': 301, '2': 176, '3': 125, '4': 97, '5': 79, '6': 67, '7': 58, '8': 51, '9': 46}
    # Use observed if enough data, else use theoretical
    if sum(first_digit_freq.values()) > 100:
        digits = list("123456789")
        weights = [first_digit_freq.get(d, 1) for d in digits]
    else:
        digits = list("123456789")
        weights = [benford_weights[d] for d in digits]
    
    numbers = []
    for i in range(top_n):
        random.seed(i + 1100)
        first = random.choices(digits, weights=weights, k=1)[0]
        rest = ''.join(str(random.randint(0, 9)) for _ in range(5))
        numbers.append(first + rest)
    return numbers

def formula_day_of_week(train_draws, top_n=10):
    """12. Day of Week Analysis — แยกตามวัน"""
    from datetime import datetime as dt
    day_freq = defaultdict(Counter)
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            try:
                date_obj = dt.strptime(d["draw_date"], "%Y-%m-%d")
                dow = date_obj.weekday()
                for digit in fp:
                    day_freq[dow][digit] += 1
            except:
                pass
    
    # Use the most common day pattern (or overall if no day data)
    target_dow = 2  # Wednesday (งวดวันที่ 1 และ 16 มักเป็นวันพุธ)
    freq = day_freq.get(target_dow, Counter())
    if not freq:
        for d in train_draws:
            fp = safe_str(d.get("first_prize"))
            if fp and len(fp) == 6:
                for digit in fp:
                    freq[digit] += 1
    
    digits = [d for d, _ in freq.most_common(10)] or list("0123456789")
    numbers = []
    for i in range(top_n):
        random.seed(i + 1200)
        numbers.append(''.join(random.choices(digits[:6], k=6)))
    return numbers

def formula_month_analysis(train_draws, top_n=10):
    """13. Month Analysis — แยกตามเดือน"""
    month_freq = defaultdict(Counter)
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            try:
                month = int(d["draw_date"].split("-")[1])
                for digit in fp:
                    month_freq[month][digit] += 1
            except:
                pass
    
    target_month = 6  # June
    freq = month_freq.get(target_month, Counter())
    if not freq:
        for d in train_draws:
            fp = safe_str(d.get("first_prize"))
            if fp and len(fp) == 6:
                for digit in fp:
                    freq[digit] += 1
    
    digits = [d for d, _ in freq.most_common(10)] or list("0123456789")
    numbers = []
    for i in range(top_n):
        random.seed(i + 1300)
        numbers.append(''.join(random.choices(digits[:6], k=6)))
    return numbers

def formula_pattern_recognition(train_draws, top_n=10):
    """14. Pattern Recognition — เลขคู่-คี่, เลขเรียง"""
    even_odd_patterns = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            pattern = ''.join('E' if int(c) % 2 == 0 else 'O' for c in fp)
            even_odd_patterns[pattern] += 1
    
    # Most common pattern
    if even_odd_patterns:
        best_pattern = even_odd_patterns.most_common(1)[0][0]
    else:
        best_pattern = "EOEOEO"
    
    numbers = []
    for i in range(top_n):
        num = ""
        for c in best_pattern:
            if c == 'E':
                num += str(random.choice([0, 2, 4, 6, 8]))
            else:
                num += str(random.choice([1, 3, 5, 7, 9]))
        numbers.append(num)
    return numbers

def formula_regression_mean(train_draws, top_n=10):
    """15. Regression to the Mean — เลขที่ออกบ่อยจะพัก"""
    freq = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for digit in fp:
                freq[digit] += 1
    
    # Expected frequency per digit
    total_draws = len(train_draws)
    expected = total_draws * 6 / 10  # Each digit expected to appear this many times
    
    # Find digits that appeared MORE than expected (hot → should regress)
    # and digits that appeared LESS than expected (cold → should regress up)
    regression_scores = {}
    for d in "0123456789":
        observed = freq.get(d, 0)
        # Digits that are "due" to appear more
        regression_scores[d] = expected - observed  # Higher = more due
    
    sorted_digits = sorted(regression_scores.keys(), key=lambda d: regression_scores[d], reverse=True)
    numbers = []
    for i in range(top_n):
        selected = sorted_digits[:6] if len(sorted_digits) >= 6 else list("0123456789")
        random.seed(i + 1500)
        random.shuffle(selected)
        numbers.append(''.join(selected[:6]))
    return numbers

def formula_modular(train_draws, top_n=10):
    """16. Modular Arithmetic — รูปแบบ mod 3, mod 7"""
    mod_freq = defaultdict(Counter)
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            try:
                num_int = int(fp)
                mod_freq['mod3'][num_int % 3] += 1
                mod_freq['mod7'][num_int % 7] += 1
            except:
                pass
    
    # Find most common mod values
    best_mod3 = mod_freq['mod3'].most_common(1)[0][0] if mod_freq['mod3'] else 0
    best_mod7 = mod_freq['mod7'].most_common(1)[0][0] if mod_freq['mod7'] else 0
    
    numbers = []
    for i in range(top_n):
        random.seed(i + 1600)
        # Generate numbers that match the mod pattern
        while True:
            num = str(random.randint(0, 999999)).zfill(6)
            try:
                if int(num) % 3 == best_mod3 and int(num) % 7 == best_mod7:
                    numbers.append(num)
                    break
            except:
                pass
            if len(numbers) < i + 1:
                numbers.append(num)
                break
    return numbers[:top_n]

def formula_fibonacci(train_draws, top_n=10):
    """17. Fibonacci/Prime Number Theory"""
    fib_digits = [0, 1, 1, 2, 3, 5, 8]  # Fibonacci sequence digits
    prime_digits = [2, 3, 5, 7]  # Prime digits
    
    combined = list(set(fib_digits + prime_digits))
    digits = [str(d) for d in combined]
    
    if len(digits) < 6:
        digits = list("0123456789")
    
    numbers = []
    for i in range(top_n):
        random.seed(i + 1700)
        numbers.append(''.join(random.choices(digits, k=6)))
    return numbers

def formula_entropy(train_draws, top_n=10):
    """18. Entropy Analysis — ทฤษฎีข้อมูล"""
    # Calculate entropy of digit distribution
    freq = Counter()
    total = 0
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for digit in fp:
                freq[digit] += 1
                total += 1
    
    if total == 0:
        return generate_unique_numbers(1800, top_n)
    
    # Entropy = -sum(p * log2(p))
    entropy = 0
    for d in "0123456789":
        p = freq.get(d, 0) / total
        if p > 0:
            entropy -= p * math.log2(p)
    
    # High entropy = more uniform = harder to predict
    # Low entropy = some digits dominate = easier to predict
    # Use the least entropic (most predictable) digits
    sorted_by_freq = sorted(freq.keys(), key=lambda d: freq[d], reverse=True)
    digits = sorted_by_freq[:6] if len(sorted_by_freq) >= 6 else list("0123456789")
    
    numbers = []
    for i in range(top_n):
        random.seed(i + 1800)
        random.shuffle(digits)
        numbers.append(''.join(digits[:6]))
    return numbers

def formula_cascading_filter(train_draws, top_n=10):
    """19. Cascading Filter — กรองหลายชั้น"""
    # Step 1: Frequency filter — get top 10 digits
    freq = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for digit in fp:
                freq[digit] += 1
    top_digits = [d for d, _ in freq.most_common(10)] or list("0123456789")
    
    # Step 2: Position filter — for each position, pick from top digits
    pos_freq = [Counter() for _ in range(6)]
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for pos in range(6):
                if fp[pos] in top_digits:
                    pos_freq[pos][fp[pos]] += 1
    
    # Step 3: Generate numbers using both filters
    numbers = []
    for i in range(top_n):
        num = ""
        for pos in range(6):
            if pos_freq[pos]:
                candidates = [d for d, _ in pos_freq[pos].most_common(3)]
                num += random.choice(candidates) if candidates else random.choice(top_digits)
            else:
                num += random.choice(top_digits)
        numbers.append(num)
    return numbers

def formula_adaptive_ensemble(train_draws, top_n=10):
    """20. Adaptive Ensemble — น้ำหนักเปลี่ยนตามผลล่าสุด"""
    # Weight recent performance more
    recent_draws = train_draws[-20:]  # Last 20 draws
    older_draws = train_draws[:-20] if len(train_draws) > 20 else train_draws
    
    # Recent frequency
    recent_freq = Counter()
    for d in recent_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for digit in fp:
                recent_freq[digit] += 2  # Higher weight for recent
    
    # Older frequency
    older_freq = Counter()
    for d in older_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for digit in fp:
                older_freq[digit] += 1
    
    # Combined
    combined = Counter()
    for d in "0123456789":
        combined[d] = recent_freq.get(d, 0) + older_freq.get(d, 0)
    
    digits = [d for d, _ in combined.most_common(10)] or list("0123456789")
    numbers = []
    for i in range(top_n):
        random.seed(i + 2000)
        numbers.append(''.join(random.choices(digits[:6], k=6)))
    return numbers

def formula_odd_even_ratio(train_draws, top_n=10):
    """21. Odd/Even Ratio Analysis"""
    ratio_freq = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            odd_count = sum(1 for c in fp if int(c) % 2 == 1)
            even_count = 6 - odd_count
            ratio_freq[(odd_count, even_count)] += 1
    
    if ratio_freq:
        best_ratio = ratio_freq.most_common(1)[0][0]
        odd_target, even_target = best_ratio
    else:
        odd_target, even_target = 3, 3
    
    odds = [1, 3, 5, 7, 9]
    evens = [0, 2, 4, 6, 8]
    
    numbers = []
    for i in range(top_n):
        random.seed(i + 2100)
        selected = random.sample(odds, min(odd_target, 5)) + random.sample(evens, min(even_target, 5))
        random.shuffle(selected)
        num = ''.join(str(d) for d in selected[:6])
        numbers.append(num.zfill(6))
    return numbers

def formula_high_low(train_draws, top_n=10):
    """22. High/Low Analysis — เลขสูง(5-9) vs เลขต่ำ(0-4)"""
    hl_freq = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            high_count = sum(1 for c in fp if int(c) >= 5)
            low_count = 6 - high_count
            hl_freq[(high_count, low_count)] += 1
    
    if hl_freq:
        best = hl_freq.most_common(1)[0][0]
        high_target, low_target = best
    else:
        high_target, low_target = 3, 3
    
    highs = [5, 6, 7, 8, 9]
    lows = [0, 1, 2, 3, 4]
    
    numbers = []
    for i in range(top_n):
        random.seed(i + 2200)
        selected = random.sample(highs, min(high_target, 5)) + random.sample(lows, min(low_target, 5))
        random.shuffle(selected)
        numbers.append(''.join(str(d) for d in selected[:6]))
    return numbers

def formula_consecutive(train_draws, top_n=10):
    """23. Consecutive Number Analysis"""
    consec_freq = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            has_consec = any(abs(int(fp[i]) - int(fp[i+1])) == 1 for i in range(5))
            consec_freq[has_consec] += 1
    
    # Generate numbers with/without consecutive digits based on frequency
    prefer_consec = consec_freq.get(True, 0) > consec_freq.get(False, 0)
    
    numbers = []
    for i in range(top_n):
        random.seed(i + 2300)
        if prefer_consec:
            # Generate with consecutive digits
            start = random.randint(0, 4)
            num = ''.join(str((start + j) % 10) for j in range(6))
        else:
            # Generate without consecutive digits
            digits = []
            prev = -2
            for _ in range(6):
                d = random.randint(0, 9)
                while abs(d - prev) == 1:
                    d = random.randint(0, 9)
                digits.append(str(d))
                prev = d
            num = ''.join(digits)
        numbers.append(num)
    return numbers

def formula_mirror(train_draws, top_n=10):
    """24. Mirror Number Analysis — เลขกลับด้าน"""
    mirror_freq = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            mirror = fp[::-1]
            for digit in mirror:
                mirror_freq[digit] += 1
    
    digits = [d for d, _ in mirror_freq.most_common(10)] or list("0123456789")
    numbers = []
    for i in range(top_n):
        random.seed(i + 2400)
        numbers.append(''.join(random.choices(digits[:6], k=6)))
    return numbers

def formula_last_digit_sum(train_draws, top_n=10):
    """25. Last Digit Sum Analysis"""
    last_digit_sums = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            last_two_sum = int(fp[-1]) + int(fp[-2])
            last_digit_sums[last_two_sum] += 1
    
    if last_digit_sums:
        target_sum = last_digit_sums.most_common(1)[0][0]
    else:
        target_sum = 9
    
    numbers = []
    for i in range(top_n):
        random.seed(i + 2500)
        # Generate numbers where last 2 digits sum to target
        d5 = random.randint(0, 9)
        d6 = target_sum - d5
        if d6 < 0 or d6 > 9:
            d6 = random.randint(0, 9)
        prefix = ''.join(str(random.randint(0, 9)) for _ in range(4))
        numbers.append(prefix + str(d5) + str(d6))
    return numbers

def formula_digit_gap(train_draws, top_n=10):
    """26. Digit Gap Analysis — ระยะห่างระหว่างเลข"""
    gap_freq = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for i in range(5):
                gap = abs(int(fp[i]) - int(fp[i+1]))
                gap_freq[gap] += 1
    
    # Most common gap
    if gap_freq:
        target_gap = gap_freq.most_common(1)[0][0]
    else:
        target_gap = 3
    
    numbers = []
    for i in range(top_n):
        random.seed(i + 2600)
        digits = [random.randint(0, 9)]
        for _ in range(5):
            next_d = (digits[-1] + random.choice([-1, 1]) * target_gap) % 10
            digits.append(next_d)
        numbers.append(''.join(str(d) for d in digits))
    return numbers

def formula_prime_position(train_draws, top_n=10):
    """27. Prime Position Analysis — เลขศูนย์ในตำแหน่งที่เป็น prime"""
    prime_positions = [2, 3, 5]  # 0-indexed: positions 2, 3, 5
    pos_freq = [Counter() for _ in range(6)]
    
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            for pos in range(6):
                pos_freq[pos][fp[pos]] += 1
    
    numbers = []
    for i in range(top_n):
        num = ""
        for pos in range(6):
            if pos in prime_positions:
                # Use most frequent digit for prime positions
                if pos_freq[pos]:
                    candidates = [d for d, _ in pos_freq[pos].most_common(3)]
                    num += random.choice(candidates)
                else:
                    num += str(random.randint(0, 9))
            else:
                num += str(random.randint(0, 9))
        numbers.append(num)
    return numbers

def formula_alternating(train_draws, top_n=10):
    """28. Alternating Pattern — เลขสลับ สูง-ต่ำ-สูง-ต่ำ"""
    alt_freq = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            is_alt = all(
                (int(fp[i]) > int(fp[i+1]) and int(fp[i+1]) < int(fp[i+2])) or
                (int(fp[i]) < int(fp[i+1]) and int(fp[i+1]) > int(fp[i+2]))
                for i in range(4)
            )
            alt_freq[is_alt] += 1
    
    prefer_alt = alt_freq.get(True, 0) > alt_freq.get(False, 0)
    
    numbers = []
    for i in range(top_n):
        random.seed(i + 2800)
        if prefer_alt:
            digits = [random.randint(0, 9)]
            for j in range(5):
                if j % 2 == 0:
                    d = random.randint(digits[-1]+1, 9) if digits[-1] < 9 else random.randint(0, 9)
                else:
                    d = random.randint(0, digits[-1]-1) if digits[-1] > 0 else random.randint(0, 9)
                digits.append(d)
            numbers.append(''.join(str(d) for d in digits))
        else:
            numbers.append(''.join(str(random.randint(0, 9)) for _ in range(6)))
    return numbers

def formula_repeated_digits(train_draws, top_n=10):
    """29. Repeated Digit Analysis — เลขซ้ำ"""
    repeat_freq = Counter()
    for d in train_draws:
        fp = safe_str(d.get("first_prize"))
        if fp and len(fp) == 6:
            unique_count = len(set(fp))
            repeat_freq[unique_count] += 1
    
    # Most common unique digit count
    if repeat_freq:
        target_unique = repeat_freq.most_common(1)[0][0]
    else:
        target_unique = 4
    
    numbers = []
    for i in range(top_n):
        random.seed(i + 2900)
        # Generate numbers with target_unique unique digits
        base_digits = random.sample(list("0123456789"), min(target_unique, 10))
        digits = list(base_digits)
        while len(digits) < 6:
            digits.append(random.choice(base_digits))
        random.shuffle(digits)
        numbers.append(''.join(digits[:6]))
    return numbers

def formula_weighted_ensemble(train_draws, top_n=10):
    """30. Weighted Ensemble — รวมทุกสูตรด้วยน้ำหนัก"""
    all_candidates = []
    
    # Collect candidates from multiple formulas
    all_candidates.extend(formula_frequency(train_draws, 5))
    all_candidates.extend(formula_due_number(train_draws, 5))
    all_candidates.extend(formula_recency_weighted(train_draws, 5))
    all_candidates.extend(formula_digit_position(train_draws, 5))
    all_candidates.extend(formula_monte_carlo(train_draws, 5))
    all_candidates.extend(formula_bayesian(train_draws, 5))
    all_candidates.extend(formula_hot_cold(train_draws, 5))
    all_candidates.extend(formula_sum_analysis(train_draws, 5))
    all_candidates.extend(formula_pair_analysis(train_draws, 5))
    all_candidates.extend(formula_cascading_filter(train_draws, 5))
    
    # Score by frequency of appearance
    counter = Counter(all_candidates)
    return [num for num, _ in counter.most_common(top_n)]

# ── Formula Registry ──────────────────────────────────────
FORMULAS = {
    "1. Frequency Analysis": formula_frequency,
    "2. Due Number (Gap)": formula_due_number,
    "3. Recency Weighted": formula_recency_weighted,
    "4. Digit Position": formula_digit_position,
    "5. Monte Carlo": formula_monte_carlo,
    "6. Markov Chain": formula_markov_chain,
    "7. Bayesian Inference": formula_bayesian,
    "8. Hot/Cold Analysis": formula_hot_cold,
    "9. Sum Analysis": formula_sum_analysis,
    "10. Pair Analysis": formula_pair_analysis,
    "11. Benford's Law": formula_benford,
    "12. Day of Week": formula_day_of_week,
    "13. Month Analysis": formula_month_analysis,
    "14. Pattern Recognition": formula_pattern_recognition,
    "15. Regression to Mean": formula_regression_mean,
    "16. Modular Arithmetic": formula_modular,
    "17. Fibonacci/Prime": formula_fibonacci,
    "18. Entropy Analysis": formula_entropy,
    "19. Cascading Filter": formula_cascading_filter,
    "20. Adaptive Ensemble": formula_adaptive_ensemble,
    "21. Odd/Even Ratio": formula_odd_even_ratio,
    "22. High/Low Analysis": formula_high_low,
    "23. Consecutive": formula_consecutive,
    "24. Mirror Number": formula_mirror,
    "25. Last Digit Sum": formula_last_digit_sum,
    "26. Digit Gap": formula_digit_gap,
    "27. Prime Position": formula_prime_position,
    "28. Alternating": formula_alternating,
    "29. Repeated Digits": formula_repeated_digits,
    "30. Weighted Ensemble": formula_weighted_ensemble,
}

# ── Walk-Forward Backtesting ──────────────────────────────
print(f"\n{'='*60}")
print(f"  ULTIMATE FORMULA TESTER — Walk-Forward Backtesting")
print(f"{'='*60}")
print(f"สูตรที่ทดสอบ: {len(FORMULAS)} สูตร")
print(f"จำนวนรอบทดสอบ: {len(all_draws) - 100} รอบ")
print()

formula_results = {name: {
    "total_score": 0, "total_rounds": 0, "perfect_rounds": 0,
    "sets_won_total": 0, "prize_counts": defaultdict(int),
    "best_round": None, "best_round_score": 0,
} for name in FORMULAS}

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
            numbers = formula_fn(train_draws, top_n=10)
            results = [check_prize(num, prizes) for num in numbers]
            score, sets_won = score_round(results)
            
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
                r["best_round"] = {"date": test_date, "numbers": numbers, "results": results, "score": score}
        except Exception as e:
            pass
    
    if test_rounds % 100 == 0 or test_idx == len(all_draws) - 1:
        print(f"  [{test_rounds}/{len(all_draws)-START_IDX}] ทดสอบถึง {test_date}")

# ── Report ────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"  FORMULA TEST REPORT")
print(f"{'='*60}")
print(f"ช่วงทดสอบ: {all_draws[START_IDX]['draw_date']} → {all_draws[-1]['draw_date']}")
print(f"จำนวนรอบ: {test_rounds} | สูตร: {len(FORMULAS)}")
print()

ranked = sorted(formula_results.items(), key=lambda x: x[1]["total_score"], reverse=True)

print(f"🏆 อันดับสูตร:")
for rank, (name, r) in enumerate(ranked, 1):
    avg = r["sets_won_total"] / r["total_rounds"] if r["total_rounds"] > 0 else 0
    perfect_pct = r["perfect_rounds"] / r["total_rounds"] * 100 if r["total_rounds"] > 0 else 0
    print(f"{rank}. {name}")
    print(f"   คะแนน: {r['total_score']:,} | เฉลี่ย: {avg:.2f}/10 ชุด | Perfect: {r['perfect_rounds']} ({perfect_pct:.1f}%)")
    if r["prize_counts"]:
        top_prizes = sorted(r["prize_counts"].items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"   รางวัล: {', '.join(f'{k}:{v}' for k, v in top_prizes)}")
    print()

best_name, best_r = ranked[0]
print(f"🏆 สูตรที่ดีที่สุด: {best_name}")
print(f"   คะแนน: {best_r['total_score']:,} | เฉลี่ย: {best_r['sets_won_total']/best_r['total_rounds']:.2f}/10 ชุด")

print(f"\n📝 เลข 10 ชุดแนะนำ (งวดถัดไป):")
best_fn = FORMULAS[best_name]
recommended = best_fn(all_draws, top_n=10)
for i, num in enumerate(recommended, 1):
    print(f"   ชุด {i}: {num}")

# ── Save ──────────────────────────────────────────────────
formula_library = []
for name, r in ranked:
    formula_library.append({
        "name": name, "total_score": r["total_score"],
        "avg_sets_won": r["sets_won_total"]/r["total_rounds"] if r["total_rounds"] > 0 else 0,
        "perfect_rounds": r["perfect_rounds"],
        "prize_counts": dict(r["prize_counts"]),
    })

with open(os.path.join(FORMULA_DIR, "formula_library_v2.json"), "w", encoding="utf-8") as f:
    json.dump(formula_library, f, ensure_ascii=False, indent=2)

with open(os.path.join(RESULTS_DIR, "walk_forward_v2.json"), "w", encoding="utf-8") as f:
    json.dump({
        "test_date": datetime.now().isoformat(),
        "total_rounds": test_rounds, "formulas_tested": len(FORMULAS),
        "best_formula": best_name,
        "recommended_numbers": recommended,
        "results": {name: {
            "total_score": r["total_score"],
            "avg_sets_won": r["sets_won_total"]/r["total_rounds"] if r["total_rounds"] > 0 else 0,
            "perfect_rounds": r["perfect_rounds"],
            "prize_counts": dict(r["prize_counts"]),
        } for name, r in formula_results.items()}
    }, f, ensure_ascii=False, indent=2)

print(f"\n💾 บันทึก: {FORMULA_DIR}/formula_library_v2.json")
print(f"✅ เสร็จสิ้น!")
