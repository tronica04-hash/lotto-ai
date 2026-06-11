#!/usr/bin/env python3
"""
LottoAI ML Engine - Phase 1: Statistical Models
Tests multiple prediction models on Thai lottery data (779 draws)
"""
import json
import os
import statistics
import math
import random
from collections import Counter, defaultdict
from datetime import datetime

# ── Load Data ────────────────────────────────────────────────
data_path = r"D:\lotto-ai\ml-models\data\lotto_all.json"
with open(data_path, "r", encoding="utf-8") as f:
    draws = json.load(f)

print(f"{'='*60}")
print(f"  LOTTO AI — ML ENGINE PHASE 1: STATISTICAL MODELS")
print(f"  Total draws loaded: {len(draws)}")
print(f"  Date range: {draws[0]['draw_date']} -> {draws[-1]['draw_date']}")
print(f"{'='*60}\n")

# ── Prepare Data ─────────────────────────────────────────────
# Extract two_digit results
two_digit_draws = [(d["draw_date"], d.get("two_digit")) for d in draws if d.get("two_digit")]

# Extract first_prize last 2 digits
first_prize_2d = []
for d in draws:
    fp = d.get("first_prize", "")
    if fp and len(fp) >= 2:
        first_prize_2d.append((d["draw_date"], fp[-2:]))

# Extract three_digit_last
three_digit_draws = []
for d in draws:
    td = d.get("three_digit_last", [])
    if td and isinstance(td, list) and len(td) > 0:
        three_digit_draws.append((d["draw_date"], td))

print(f"Two-digit data points: {len(two_digit_draws)}")
print(f"First-prize (2d) data points: {len(first_prize_2d)}")
print(f"Three-digit data points: {len(three_digit_draws)}\n")

# ═══════════════════════════════════════════════════════════════
# MODEL 1: Simple Frequency Analysis (Two Digit)
# ═══════════════════════════════════════════════════════════════
print("━" * 50)
print("📊 MODEL 1: FREQUENCY ANALYSIS (เลขท้าย 2 ตัว)")
print("━" * 50)

freq_2d = Counter()
for _, num in two_digit_draws:
    if num:
        freq_2d[num] += 1

print("\n🔝 Top 10 เลขร้อน (Hot Numbers):")
for num, count in freq_2d.most_common(10):
    pct = count / len(two_digit_draws) * 100
    expected = len(two_digit_draws) / 100
    ratio = count / expected if expected > 0 else 0
    print(f"   {num}: {count} ครั้ง ({pct:.1f}%) | vs คาดหวัง: {ratio:.2f}x")

print("\n🔻 Bottom 10 เลขเย็น (Cold Numbers):")
for num, count in freq_2d.most_common()[-10:]:
    pct = count / len(two_digit_draws) * 100
    expected = len(two_digit_draws) / 100
    ratio = count / expected if expected > 0 else 0
    print(f"   {num}: {count} ครั้ง ({pct:.1f}%) | vs คาดหวัง: {ratio:.2f}x")

# ═══════════════════════════════════════════════════════════════
# MODEL 2: Due Number Analysis (Gap-based)
# ═══════════════════════════════════════════════════════════════
print(f"\n{'━' * 50}")
print("📊 MODEL 2: DUE NUMBER ANALYSIS (เลขนาย)")
print("━" * 50)

last_seen = {}
for i, (date, num) in enumerate(two_digit_draws):
    if num:
        last_seen[num] = i

current_pos = len(two_digit_draws)
due_list = []
for num in [f"{i:02d}" for i in range(100)]:
    if num in last_seen:
        gap = current_pos - last_seen[num]
    else:
        gap = current_pos  # Never seen
    due_list.append((num, gap))

due_list.sort(key=lambda x: -x[1])

print("\n🔝 Top 10 เลขนาย (Due — ไม่ออกนานสุด):")
for num, gap in due_list[:10]:
    print(f"   {num}: ไม่ออกมาแล้ว {gap} งวด")

print("\n🔻 Bottom 10 เลขออกล่าสุด:")
for num, gap in due_list[-10:]:
    print(f"   {num}: ออกล่าสุดเมื่อ {gap} งวดก่อน")

# ═══════════════════════════════════════════════════════════════
# MODEL 3: Recency-Weighted Frequency
# ═══════════════════════════════════════════════════════════════
print(f"\n{'━' * 50}")
print("📊 MODEL 3: RECENCY-WEIGHTED FREQUENCY")
print("━" * 50)

weighted_freq = Counter()
total = len(two_digit_draws)
for i, (date, num) in enumerate(two_digit_draws):
    if num:
        # More recent = higher weight (linear decay)
        weight = (i + 1) / total  # 0 to 1
        weighted_freq[num] += weight

print("\n🔝 Top 10 เลขร้อน (ถ่วงน้ำหนักล่าสุด):")
for num, score in weighted_freq.most_common(10):
    print(f"   {num}: score {score:.2f}")

# ═══════════════════════════════════════════════════════════════
# MODEL 4: First Prize Last-2-Digit Analysis
# ═══════════════════════════════════════════════════════════════
print(f"\n{'━' * 50}")
print("📊 MODEL 4: FIRST PRIZE LAST-2-DIGIT ANALYSIS")
print("━" * 50)

fp_freq = Counter()
for _, num in first_prize_2d:
    fp_freq[num] += 1

print("\n🔝 Top 10 เลขท้าย 2 ตัว จากรางวัลที่ 1:")
for num, count in fp_freq.most_common(10):
    pct = count / len(first_prize_2d) * 100
    print(f"   {num}: {count} ครั้ง ({pct:.1f}%)")

# ═══════════════════════════════════════════════════════════════
# MODEL 5: Three-Digit-Last Frequency
# ═══════════════════════════════════════════════════════════════
print(f"\n{'━' * 50}")
print("📊 MODEL 5: THREE-DIGIT-LAST FREQUENCY")
print("━" * 50)

td_freq = Counter()
for _, nums in three_digit_draws:
    for n in nums:
        if n and len(n) == 3:
            td_freq[n] += 1

print(f"\n🔝 Top 10 เลขท้าย 3 ตัว (ทั้งหมด {len(td_freq)} เลข):")
for num, count in td_freq.most_common(10):
    pct = count / len(three_digit_draws) * 100
    print(f"   {num}: {count} ครั้ง ({pct:.1f}%)")

# ═══════════════════════════════════════════════════════════════
# BACKTEST: Simple prediction on last 50 draws
# ═══════════════════════════════════════════════════════════════
print(f"\n{'━' * 50}")
print("🔬 BACKTEST: ทดสอบทำนาย 50 งวดล่าสุด")
print("━" * 50)

# Use first 729 draws as training, last 50 as test
train_data = two_digit_draws[:-50]
test_data = two_digit_draws[-50:]

print(f"Training: {len(train_data)} draws | Testing: {len(test_data)} draws")

# Build frequency from training
train_freq = Counter()
for _, num in train_data:
    if num:
        train_freq[num] += 1

# Predict top 10 hot numbers
predicted_hot = [num for num, _ in train_freq.most_common(10)]

# Check how many test draws had their two_digit in predicted top 10
hits = 0
for date, actual in test_data:
    if actual and actual in predicted_hot:
        hits += 1

hit_rate = hits / len(test_data) * 100 if test_data else 0
random_baseline = 10 / 100 * 100  # 10 numbers out of 100 possible

print(f"\n📈 Frequency Model (Top 10 Hot):")
print(f"   Predicted: {predicted_hot}")
print(f"   Hits: {hits}/{len(test_data)} ({hit_rate:.1f}%)")
print(f"   Random baseline: {random_baseline:.1f}%")
print(f"   vs Random: {hit_rate - random_baseline:+.1f}%")

# Due number prediction
train_last_seen = {}
for i, (date, num) in enumerate(train_data):
    if num:
        train_last_seen[num] = i

train_pos = len(train_data)
due_predictions = []
for num in [f"{i:02d}" for i in range(100)]:
    gap = train_pos - train_last_seen.get(num, 0)
    due_predictions.append((num, gap))
due_predictions.sort(key=lambda x: -x[1])
predicted_due = [num for num, _ in due_predictions[:10]]

hits_due = 0
for date, actual in test_data:
    if actual and actual in predicted_due:
        hits_due += 1

hit_rate_due = hits_due / len(test_data) * 100 if test_data else 0

print(f"\n📈 Due Number Model (Top 10 Due):")
print(f"   Predicted: {predicted_due}")
print(f"   Hits: {hits_due}/{len(test_data)} ({hit_rate_due:.1f}%)")
print(f"   vs Random: {hit_rate_due - random_baseline:+.1f}%")

# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print("📋 SUMMARY — ผลการวิเคราะห์เบื้องต้น")
print(f"{'='*60}")
print(f"""
ข้อมูล: {len(draws)} งวด ({draws[0]['draw_date']} → {draws[-1]['draw_date']})
เลขท้าย 2 ตัว มีข้อมูล: {len(two_digit_draws)} งวด

ผล Backtest (50 งวดล่าสุด):
  • Frequency Model: {hit_rate:.1f}% (random: {random_baseline:.1f}%) → {hit_rate - random_baseline:+.1f}%
  • Due Number Model: {hit_rate_due:.1f}% (random: {random_baseline:.1f}%) → {hit_rate_due - random_baseline:+.1f}%

⚠️ หมายเหตุ: ทั้งสองโมเดลยังไม่ดีกว่า random มากนัก
   ต้องทำ feature engineering เพิ่มและลอง ML models ต่อ
""")

# Save results
results = {
    "total_draws": len(draws),
    "date_range": f"{draws[0]['draw_date']} -> {draws[-1]['draw_date']}",
    "hot_2digit": dict(freq_2d.most_common(10)),
    "cold_2digit": dict(freq_2d.most_common()[-10:]),
    "due_2digit": dict(due_list[:10]),
    "backtest": {
        "frequency_model": {"hit_rate": hit_rate, "vs_random": hit_rate - random_baseline},
        "due_model": {"hit_rate": hit_rate_due, "vs_random": hit_rate_due - random_baseline}
    }
}

results_path = r"D:\lotto-ai\ml-models\results\phase1_stats.json"
os.makedirs(os.path.dirname(results_path), exist_ok=True)
with open(results_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"Results saved to: {results_path}")
