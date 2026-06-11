#!/usr/bin/env python3
"""
LottoAI — Ensemble Prediction API
รวมผลจากทุก model เป็น prediction เดียว
"""
import json, os, math
from collections import Counter
from datetime import datetime

# Load latest results
results_dir = r"D:\lotto-ai\ml-models\results"
with open(os.path.join(results_dir, "all_models.json"), "r") as f:
    phase1 = json.load(f)

with open(os.path.join(results_dir, "phase2.json"), "r") as f:
    phase2 = json.load(f)

with open(os.path.join(results_dir, "phase3.json"), "r") as f:
    phase3 = json.load(f)

# Load data for real-time features
with open(r"D:\lotto-ai\ml-models\data\scraped_all.json", "r", encoding="utf-8") as f:
    draws = json.load(f)

print("=" * 60)
print("  LOTTO AI — ENSEMBLE PREDICTION")
print("=" * 60)

# ── Build Ensemble ──────────────────────────────────────────
# Weight each model by its backtest hit rate
model_weights = {
    "digit_position": 0.522,  # Phase 1 best
    "monte_carlo": 0.142,
    "frequency": 0.127,
    "neural_net": 0.180,  # Phase 2
    "random_forest": 0.089,  # Phase 3
}

# Get predictions from each model
all_predictions = phase1.get("predictions", {})

# Score each number 00-99
ensemble_scores = Counter()

for model_name, weight in model_weights.items():
    preds = all_predictions.get(model_name.replace("_", "_"), [])
    if not preds:
        # Try alternate names
        for key in all_predictions:
            if model_name in key.lower():
                preds = all_predictions[key]
                break
    
    for num in preds:
        ensemble_scores[num] += weight

# Get top 10
top10 = ensemble_scores.most_common(10)
print(f"\n  Ensemble Predictions (Next Draw):")
for num, score in top10:
    print(f"    {num}: score {score:.3f}")

# ── Real-time Analysis ──────────────────────────────────────
print(f"\n  Real-time Analysis (Latest Draw: {draws[-1]['draw_date']}):")
latest = draws[-1]
print(f"    First Prize: {latest.get('first_prize', 'N/A')}")
print(f"    Two Digit: {latest.get('two_digit', 'N/A')}")

# Frequency of last 2 digits in recent draws
recent_2d = [d.get("two_digit", "") for d in draws[-50:] if d.get("two_digit")]
freq_50 = Counter(recent_2d)
print(f"\n    Hot numbers (last 50 draws):")
for num, count in freq_50.most_common(5):
    print(f"      {num}: {count} times")

# Due numbers
last_seen = {}
for i, d in enumerate(draws):
    td = d.get("two_digit", "")
    if td:
        last_seen[td] = i

current = len(draws)
due_list = []
for num in [f"{i:02d}" for i in range(100)]:
    gap = current - last_seen.get(num, 0)
    due_list.append((num, gap))
due_list.sort(key=lambda x: -x[1])

print(f"\n    Due numbers (not seen longest):")
for num, gap in due_list[:5]:
    print(f"      {num}: {gap} draws")

# ── Save Prediction ─────────────────────────────────────────
prediction = {
    "generated_at": datetime.now().isoformat(),
    "latest_draw": draws[-1]["draw_date"],
    "ensemble_top10": [{"number": num, "score": round(score, 3)} for num, score in top10],
    "hot_50": [{"number": num, "count": count} for num, count in freq_50.most_common(10)],
    "due_top10": [{"number": num, "gap": gap} for num, gap in due_list[:10]],
    "model_weights": model_weights,
}

os.makedirs(r"D:\lotto-ai\ml-models\results", exist_ok=True)
with open(r"D:\lotto-ai\ml-models\results\ensemble_prediction.json", "w") as f:
    json.dump(prediction, f, ensure_ascii=False, indent=2)

print(f"\n  Saved: D:\\lotto-ai\\ml-models\\results\\ensemble_prediction.json")
