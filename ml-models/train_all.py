#!/usr/bin/env python3
"""
LottoAI ML Engine — Full Pipeline
Train & backtest 10 prediction models on 666 draws
"""
import json, os, math, random
from collections import Counter, defaultdict

# ── Load Data ────────────────────────────────────────────────
data_path = r"D:\lotto-ai\ml-models\data\scraped_all.json"
with open(data_path, "r", encoding="utf-8") as f:
    draws = json.load(f)

print("=" * 60)
print("  LOTTO AI — ML ENGINE FULL PIPELINE")
print(f"  Total draws: {len(draws)}")
print(f"  Range: {draws[0]['draw_date']} -> {draws[-1]['draw_date']}")
print("=" * 60)

# ── Prepare Data ─────────────────────────────────────────────
two_digit = [(d["draw_date"], d.get("two_drize", "") or d.get("two_digit", "")) for d in draws]
two_digit = [(dt, num) for dt, num in two_digit if num and len(num) >= 2]

first_prize = [(d["draw_date"], d.get("first_prize", "")) for d in draws if d.get("first_prize")]

# Last 2 digits from first prize
fp_last2 = [(dt, fp[-2:]) for dt, fp in first_prize if len(fp) >= 2]

# Last 3 digits from first prize
fp_last3 = [(dt, fp[-3:]) for dt, fp in first_prize if len(fp) >= 3]

print(f"\nData points:")
print(f"  two_digit: {len(two_digit)}")
print(f"  first_prize: {len(first_prize)}")
print(f"  fp_last2: {len(fp_last2)}")
print(f"  fp_last3: {len(fp_last3)}")

# ── Train/Test Split ────────────────────────────────────────
split_idx = int(len(two_digit) * 0.8)
train_2d = two_digit[:split_idx]
test_2d = two_digit[split_idx:]

split_fp = int(len(fp_last2) * 0.8)
train_fp = fp_last2[:split_fp]
test_fp = fp_last2[split_fp:]

print(f"\nTrain/Test split:")
print(f"  2-digit: {len(train_2d)} train / {len(test_2d)} test")
print(f"  FP last2: {len(train_fp)} train / {len(test_fp)} test")

# ═══════════════════════════════════════════════════════════════
# MODEL 1: Simple Frequency
# ═══════════════════════════════════════════════════════════════
print(f"\n{'━'*50}")
print("📊 MODEL 1: SIMPLE FREQUENCY")
print(f"{'━'*50}")

freq = Counter()
for _, num in train_2d:
    freq[num] += 1

predicted = [n for n, _ in freq.most_common(10)]
hits = sum(1 for _, actual in test_2d if actual in predicted)
hit_rate = hits / len(test_2d) * 100 if test_2d else 0
baseline = 10  # 10 numbers out of 100

print(f"  Top 10: {predicted}")
print(f"  Hit rate: {hits}/{len(test_2d)} = {hit_rate:.1f}%")
print(f"  vs Random: {hit_rate - baseline:+.1f}%")

# ═══════════════════════════════════════════════════════════════
# MODEL 2: Due Number (Gap Analysis)
# ═══════════════════════════════════════════════════════════════
print(f"\n{'━'*50}")
print("📊 MODEL 2: DUE NUMBER (GAP)")
print(f"{'━'*50}")

last_seen = {}
for i, (_, num) in enumerate(train_2d):
    if num:
        last_seen[num] = i

train_pos = len(train_2d)
due_list = []
for num in [f"{i:02d}" for i in range(100)]:
    gap = train_pos - last_seen.get(num, 0)
    due_list.append((num, gap))
due_list.sort(key=lambda x: -x[1])

predicted_due = [n for n, _ in due_list[:10]]
hits_due = sum(1 for _, actual in test_2d if actual in predicted_due)
hit_rate_due = hits_due / len(test_2d) * 100 if test_2d else 0

print(f"  Top 10 Due: {predicted_due}")
print(f"  Hit rate: {hits_due}/{len(test_2d)} = {hit_rate_due:.1f}%")
print(f"  vs Random: {hit_rate_due - baseline:+.1f}%")

# ═══════════════════════════════════════════════════════════════
# MODEL 3: Recency-Weighted Frequency
# ═══════════════════════════════════════════════════════════════
print(f"\n{'━'*50}")
print("📊 MODEL 3: RECENCY-WEIGHTED FREQUENCY")
print(f"{'━'*50}")

weighted = Counter()
total = len(train_2d)
for i, (_, num) in enumerate(train_2d):
    if num:
        weight = (i + 1) / total  # Linear recency
        weighted[num] += weight

predicted_w = [n for n, _ in weighted.most_common(10)]
hits_w = sum(1 for _, actual in test_2d if actual in predicted_w)
hit_rate_w = hits_w / len(test_2d) * 100 if test_2d else 0

print(f"  Top 10: {predicted_w}")
print(f"  Hit rate: {hits_w}/{len(test_2d)} = {hit_rate_w:.1f}%")
print(f"  vs Random: {hit_rate_w - baseline:+.1f}%")

# ═══════════════════════════════════════════════════════════════
# MODEL 4: Bayesian Inference
# ═══════════════════════════════════════════════════════════════
print(f"\n{'━'*50}")
print("📊 MODEL 4: BAYESIAN INFERENCE")
print(f"{'━'*50}")

# P(number | history) ∝ P(history | number) * P(number)
# Prior: uniform 1/100
# Likelihood: frequency in training data
prior = 1.0 / 100
bayes_scores = {}
for num in [f"{i:02d}" for i in range(100)]:
    count = freq.get(num, 0)
    # Posterior ∝ likelihood * prior
    likelihood = (count + 1) / (len(train_2d) + 100)  # Laplace smoothing
    bayes_scores[num] = likelihood * prior

predicted_bayes = sorted(bayes_scores, key=bayes_scores.get, reverse=True)[:10]
hits_bayes = sum(1 for _, actual in test_2d if actual in predicted_bayes)
hit_rate_bayes = hits_bayes / len(test_2d) * 100 if test_2d else 0

print(f"  Top 10: {predicted_bayes}")
print(f"  Hit rate: {hits_bayes}/{len(test_2d)} = {hit_rate_bayes:.1f}%")
print(f"  vs Random: {hit_rate_bayes - baseline:+.1f}%")

# ═══════════════════════════════════════════════════════════════
# MODEL 5: Markov Chain (Transition Probabilities)
# ═══════════════════════════════════════════════════════════════
print(f"\n{'━'*50}")
print("📊 MODEL 5: MARKOV CHAIN")
print(f"{'━'*50}")

# Build transition matrix: P(next_num | current_num)
transitions = defaultdict(Counter)
nums_only = [num for _, num in train_2d if num]
for i in range(len(nums_only) - 1):
    current = nums_only[i]
    next_num = nums_only[i + 1]
    transitions[current][next_num] += 1

# Predict: given last number, what's most likely next?
last_train_num = nums_only[-1] if nums_only else "00"
markov_preds = []
if last_train_num in transitions:
    markov_preds = [n for n, _ in transitions[last_train_num].most_common(10)]
else:
    markov_preds = [n for n, _ in freq.most_common(10)]

hits_markov = sum(1 for _, actual in test_2d if actual in markov_preds)
hit_rate_markov = hits_markov / len(test_2d) * 100 if test_2d else 0

print(f"  Last number: {last_train_num}")
print(f"  Top 10 predictions: {markov_preds}")
print(f"  Hit rate: {hits_markov}/{len(test_2d)} = {hit_rate_markov:.1f}%")
print(f"  vs Random: {hit_rate_markov - baseline:+.1f}%")

# ═══════════════════════════════════════════════════════════════
# MODEL 6: Monte Carlo Simulation
# ═══════════════════════════════════════════════════════════════
print(f"\n{'━'*50}")
print("📊 MODEL 6: MONTE CARLO SIMULATION")
print(f"{'━'*50}")

# Simulate 10000 draws based on historical distribution
random.seed(42)
mc_results = Counter()
for _ in range(10000):
    # Weighted random choice based on frequency
    numbers = list(freq.keys())
    weights = list(freq.values())
    if numbers:
        chosen = random.choices(numbers, weights=weights, k=1)[0]
        mc_results[chosen] += 1

predicted_mc = [n for n, _ in mc_results.most_common(10)]
hits_mc = sum(1 for _, actual in test_2d if actual in predicted_mc)
hit_rate_mc = hits_mc / len(test_2d) * 100 if test_2d else 0

print(f"  Top 10: {predicted_mc}")
print(f"  Hit rate: {hits_mc}/{len(test_2d)} = {hit_rate_mc:.1f}%")
print(f"  vs Random: {hit_rate_mc - baseline:+.1f}%")

# ═══════════════════════════════════════════════════════════════
# MODEL 7: First Prize Last-2 Pattern
# ═══════════════════════════════════════════════════════════════
print(f"\n{'━'*50}")
print("📊 MODEL 7: FIRST PRIZE LAST-2 PATTERN")
print(f"{'━'*50}")

fp_freq = Counter()
for _, num in train_fp:
    fp_freq[num] += 1

predicted_fp = [n for n, _ in fp_freq.most_common(10)]
hits_fp = sum(1 for _, actual in test_2d if actual in predicted_fp)
hit_rate_fp = hits_fp / len(test_2d) * 100 if test_2d else 0

print(f"  Top 10: {predicted_fp}")
print(f"  Hit rate: {hits_fp}/{len(test_2d)} = {hit_rate_fp:.1f}%")
print(f"  vs Random: {hit_rate_fp - baseline:+.1f}%")

# ═══════════════════════════════════════════════════════════════
# MODEL 8: Combined Score (Frequency + Due + Recency)
# ═══════════════════════════════════════════════════════════════
print(f"\n{'━'*50}")
print("📊 MODEL 8: COMBINED SCORE (Freq + Due + Recency)")
print(f"{'━'*50}")

combined = {}
max_freq = max(freq.values()) if freq else 1
max_gap = max(g for _, g in due_list) if due_list else 1
max_w = max(weighted.values()) if weighted else 1

for num in [f"{i:02d}" for i in range(100)]:
    f_score = freq.get(num, 0) / max_freq
    g_score = (train_pos - last_seen.get(num, 0)) / max_gap
    r_score = weighted.get(num, 0) / max_w
    combined[num] = 0.4 * f_score + 0.35 * g_score + 0.25 * r_score

predicted_comb = sorted(combined, key=combined.get, reverse=True)[:10]
hits_comb = sum(1 for _, actual in test_2d if actual in predicted_comb)
hit_rate_comb = hits_comb / len(test_2d) * 100 if test_2d else 0

print(f"  Top 10: {predicted_comb}")
print(f"  Hit rate: {hits_comb}/{len(test_2d)} = {hit_rate_comb:.1f}%")
print(f"  vs Random: {hit_rate_comb - baseline:+.1f}%")

# ═══════════════════════════════════════════════════════════════
# MODEL 9: Digit Position Analysis (from first_prize)
# ═══════════════════════════════════════════════════════════════
print(f"\n{'━'*50}")
print("📊 MODEL 9: DIGIT POSITION ANALYSIS")
print(f"{'━'*50}")

# Analyze each position (1st, 2nd, 3rd, 4th, 5th, 6th digit)
position_freq = [Counter() for _ in range(6)]
for _, fp in first_prize[:split_fp]:
    for i, ch in enumerate(fp[:6]):
        position_freq[i][ch] += 1

# Predict: most frequent digit at each position
predicted_digits = []
for i in range(6):
    top = position_freq[i].most_common(3)
    predicted_digits.append([d for d, _ in top])

print(f"  Top digits per position:")
for i, digits in enumerate(predicted_digits):
    print(f"    Position {i+1}: {digits}")

# Check: how many test first_prizes have last 2 digits matching position freq
hits_pos = 0
for _, actual in test_fp:
    if len(actual) == 2:
        d4 = actual[0] if len(actual) > 0 else ""
        d5 = actual[1] if len(actual) > 1 else ""
        if d4 in predicted_digits[4] or d5 in predicted_digits[5]:
            hits_pos += 1

hit_rate_pos = hits_pos / len(test_fp) * 100 if test_fp else 0
print(f"  Hit rate (pos 5-6 match): {hits_pos}/{len(test_fp)} = {hit_rate_pos:.1f}%")

# ═══════════════════════════════════════════════════════════════
# MODEL 10: Ensemble (All Models Combined)
# ═══════════════════════════════════════════════════════════════
print(f"\n{'━'*50}")
print("📊 MODEL 10: ENSEMBLE (ALL MODELS)")
print(f"{'━'*50}")

# Combine all predictions with weights based on backtest performance
all_predictions = {
    "frequency": (predicted, hit_rate),
    "due": (predicted_due, hit_rate_due),
    "recency": (predicted_w, hit_rate_w),
    "bayesian": (predicted_bayes, hit_rate_bayes),
    "markov": (markov_preds, hit_rate_markov),
    "monte_carlo": (predicted_mc, hit_rate_mc),
    "fp_pattern": (predicted_fp, hit_rate_fp),
    "combined": (predicted_comb, hit_rate_comb),
}

# Score each number by weighted vote
ensemble_scores = Counter()
for model_name, (preds, hr) in all_predictions.items():
    weight = max(hr, 1)  # Use hit rate as weight
    for num in preds:
        ensemble_scores[num] += weight

predicted_ensemble = [n for n, _ in ensemble_scores.most_common(10)]
hits_ens = sum(1 for _, actual in test_2d if actual in predicted_ensemble)
hit_rate_ens = hits_ens / len(test_2d) * 100 if test_2d else 0

print(f"  Top 10: {predicted_ensemble}")
print(f"  Hit rate: {hits_ens}/{len(test_2d)} = {hit_rate_ens:.1f}%")
print(f"  vs Random: {hit_rate_ens - baseline:+.1f}%")

# ═══════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print("📋 FINAL RESULTS — MODEL COMPARISON")
print(f"{'='*60}")
print(f"{'Model':<25} {'Hit Rate':>10} {'vs Random':>10}")
print(f"{'─'*45}")

results = [
    ("1. Frequency", hit_rate),
    ("2. Due Number", hit_rate_due),
    ("3. Recency-Weighted", hit_rate_w),
    ("4. Bayesian", hit_rate_bayes),
    ("5. Markov Chain", hit_rate_markov),
    ("6. Monte Carlo", hit_rate_mc),
    ("7. FP Last-2 Pattern", hit_rate_fp),
    ("8. Combined Score", hit_rate_comb),
    ("9. Digit Position", hit_rate_pos),
    ("10. Ensemble", hit_rate_ens),
]

for name, hr in sorted(results, key=lambda x: -x[1]):
    marker = " 🏆" if hr == max(r[1] for r in results) else ""
    print(f"{name:<25} {hr:>9.1f}% {hr - baseline:>+9.1f}%{marker}")

best = max(results, key=lambda x: x[1])
print(f"\n🏆 Best Model: {best[0]} — {best[1]:.1f}% (vs random {best[1]-baseline:+.1f}%)")

# Save results
output = {
    "total_draws": len(draws),
    "train_size": len(train_2d),
    "test_size": len(test_2d),
    "models": {name: {"hit_rate": hr, "vs_random": hr - baseline} for name, hr in results},
    "best_model": best[0],
    "best_hit_rate": best[1],
    "predictions": {
        "frequency": predicted,
        "due": predicted_due,
        "recency": predicted_w,
        "bayesian": predicted_bayes,
        "markov": markov_preds,
        "monte_carlo": predicted_mc,
        "fp_pattern": predicted_fp,
        "combined": predicted_comb,
        "ensemble": predicted_ensemble,
    }
}

out_path = r"D:\lotto-ai\ml-models\results\all_models.json"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"\nResults saved to: {out_path}")
