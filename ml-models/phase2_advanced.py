#!/usr/bin/env python3
"""
LottoAI ML Engine — Phase 2: Advanced Features + Neural Net
- Features: day_of_week, month, year, digit gaps, position frequencies
- Walk-forward validation
- Simple 2-layer neural network
"""
import json, os, math, random
from collections import Counter, defaultdict
from datetime import datetime

# Load Data
data_path = r"D:\lotto-ai\ml-models\data\scraped_all.json"
with open(data_path, "r", encoding="utf-8") as f:
    draws = json.load(f)

print("=" * 60)
print("  LOTTO AI — ML ENGINE PHASE 2: ADVANCED")
print(f"  Draws: {len(draws)} | {draws[0]['draw_date']} -> {draws[-1]['draw_date']}")
print("=" * 60)

# ── Feature Engineering ──────────────────────────────────────
def extract_features(draw, prev_draws):
    features = {}
    dt = datetime.strptime(draw["draw_date"], "%Y-%m-%d")
    
    features["day_of_week"] = dt.weekday()
    features["month"] = dt.month
    features["year"] = dt.year
    features["day_of_month"] = dt.day
    
    fp = draw.get("first_prize", "")
    if fp and len(fp) == 6:
        digits = [int(d) for d in fp]
        for i, d in enumerate(digits):
            features[f"fp_d{i+1}"] = d
        features["fp_sum"] = sum(digits)
        features["fp_even"] = sum(1 for d in digits if d % 2 == 0)
        features["fp_odd"] = sum(1 for d in digits if d % 2 == 1)
        features["fp_consec"] = sum(1 for i in range(5) if abs(digits[i] - digits[i+1]) == 1)
        features["fp_repeat"] = 1 if len(set(digits)) < 6 else 0
        features["fp_max_gap"] = max(digits) - min(digits)
        features["fp_first_last_diff"] = abs(digits[0] - digits[-1])
        features["fp_last2"] = fp[-2:]
        features["fp_last3"] = fp[-3:]
        features["fp_first2"] = fp[:2]
        features["fp_first3"] = fp[:3]
    else:
        return None
    
    features["gap_days"] = 0
    if prev_draws:
        prev_dt = datetime.strptime(prev_draws[-1]["draw_date"], "%Y-%m-%d")
        features["gap_days"] = (dt - prev_dt).days
    
    features["target_2d"] = draw.get("two_digit", "") or None
    return features

all_features = []
for i, draw in enumerate(draws):
    prev = draws[max(0, i-10):i]
    feats = extract_features(draw, prev)
    if feats:
        all_features.append(feats)

print(f"\nFeatures: {len(all_features)} draws, {len(all_features[0])} features each")

# ── Helper Functions ────────────────────────────────────────
def train_freq(feats):
    f = Counter()
    for x in feats:
        if x.get("target_2d"):
            f[x["target_2d"]] += 1
    return f

def train_pos(feats):
    pf = [Counter() for _ in range(6)]
    for x in feats:
        for i in range(6):
            v = x.get(f"fp_d{i+1}")
            if v is not None:
                pf[i][v] += 1
    return pf

def top_n(counter, n=10):
    return [k for k, _ in counter.most_common(n)]

# ── Walk-Forward Validation ─────────────────────────────────
print(f"\n{'━'*50}")
print("🔬 WALK-FORWARD VALIDATION")
print(f"{'━'*50}")

window = 200
step = 10
results = {"freq": {"h": 0, "t": 0}, "pos": {"h": 0, "t": 0}, "combo": {"h": 0, "t": 0}}

for i in range(window, len(all_features) - step, step):
    train = all_features[max(0, i-window):i]
    test = all_features[i:i+step]
    
    freq = train_freq(train)
    pos = train_pos(train)
    
    for tf in test:
        actual = tf.get("target_2d")
        if not actual:
            continue
        
        # Frequency
        if actual in top_n(freq, 10):
            results["freq"]["h"] += 1
        results["freq"]["t"] += 1
        
        # Position: score each 2-digit number by position frequency
        pos_scores = Counter()
        for num in [f"{n:02d}" for n in range(100)]:
            s = 0
            for p in range(2):
                d = int(num[p])
                s += pos[p].get(d, 0)
            pos_scores[num] = s
        if actual in top_n(pos_scores, 10):
            results["pos"]["h"] += 1
        results["pos"]["t"] += 1
        
        # Combined
        max_f = max(freq.values()) if freq else 1
        max_p = max(pos_scores.values()) if pos_scores else 1
        combo = {}
        for num in [f"{n:02d}" for n in range(100)]:
            combo[num] = 0.5 * freq.get(num, 0) / max_f + 0.5 * pos_scores.get(num, 0) / max_p
        if actual in top_n(Counter(combo), 10):
            results["combo"]["h"] += 1
        results["combo"]["t"] += 1

baseline = 10.0
print(f"\n  Results (window={window}, step={step}):")
for name, r in results.items():
    if r["t"] > 0:
        hr = r["h"] / r["t"] * 100
        print(f"    {name}: {r['h']}/{r['t']} = {hr:.1f}% (vs {baseline:.0f}% = {hr-baseline:+.1f}%)")

# ── Neural Network (2-layer, from scratch) ─────────────────
print(f"\n{'━'*50}")
print("🧠 NEURAL NETWORK (2-Layer)")
print(f"{'━'*50}")

SEQ_LEN = 5

def make_sequences(feats, seq_len):
    xs, ys = [], []
    for i in range(seq_len, len(feats)):
        x = []
        for s in feats[i-seq_len:i]:
            digits = [s.get(f"fp_d{d}", 0) / 9.0 for d in range(1, 7)]
            time_f = [s.get("day_of_week", 0) / 6.0, s.get("month", 0) / 12.0, s.get("gap_days", 0) / 30.0]
            x.extend(digits + time_f)
        tgt = feats[i].get("target_2d")
        if tgt:
            try:
                xs.append(x)
                ys.append(int(tgt))
            except:
                pass
    return xs, ys

xs, ys = make_sequences(all_features, SEQ_LEN)
print(f"  Sequences: {len(xs)}, Input dim: {len(xs[0]) if xs else 0}")

if len(xs) < 50:
    print("  ⚠️ Not enough data")
    nn_best = 0
else:
    random.seed(42)
    IN = len(xs[0])
    HID = 64
    OUT = 100
    
    # Xavier init
    w1 = [[random.gauss(0, math.sqrt(2.0/IN)) for _ in range(HID)] for _ in range(IN)]
    b1 = [0.0] * HID
    w2 = [[random.gauss(0, math.sqrt(2.0/HID)) for _ in range(OUT)] for _ in range(HID)]
    b2 = [0.0] * OUT
    
    def forward(x):
        h = [max(0, sum(x[i]*w1[i][j] for i in range(IN)) + b1[j]) for j in range(HID)]
        o = [sum(h[j]*w2[j][k] for j in range(HID)) + b2[k] for k in range(OUT)]
        mx = max(o)
        ex = [math.exp(v-mx) for v in o]
        s = sum(ex)
        return [e/s for e in ex], h
    
    split = int(len(xs) * 0.8)
    x_tr, y_tr = xs[:split], ys[:split]
    x_te, y_te = xs[split:], ys[split:]
    
    print(f"  Train: {len(x_tr)}, Test: {len(x_te)}")
    print(f"  Arch: {IN} -> {HID} -> {OUT}")
    
    lr = 0.005
    epochs = 100
    nn_best = 0
    
    for ep in range(epochs):
        idxs = list(range(len(x_tr)))
        random.shuffle(idxs)
        loss = 0
        
        for idx in idxs:
            x = x_tr[idx]
            t = y_tr[idx]
            probs, h = forward(x)
            loss += -math.log(max(probs[t], 1e-10))
            
            # Backprop
            do = probs[:]
            do[t] -= 1
            
            for j in range(HID):
                for k in range(OUT):
                    w2[j][k] -= lr * h[j] * do[k]
            for k in range(OUT):
                b2[k] -= lr * do[k]
            
            dh = [0.0] * HID
            for j in range(HID):
                for k in range(OUT):
                    dh[j] += do[k] * w2[j][k]
                dh[j] *= 1 if h[j] > 0 else 0
            
            for i in range(IN):
                for j in range(HID):
                    w1[i][j] -= lr * x[i] * dh[j]
            for j in range(HID):
                b1[j] -= lr * dh[j]
        
        if (ep+1) % 20 == 0:
            hits = sum(1 for x,y in zip(x_te[:50], y_te[:50]) if y in sorted(range(100), key=lambda k: forward(x)[0][k], reverse=True)[:10])
            acc = hits / min(50, len(x_te)) * 100
            print(f"    Epoch {ep+1:3d}: Loss={loss/len(x_tr):.4f}, Test Top-10={acc:.1f}%")
            if acc > nn_best:
                nn_best = acc
    
    print(f"\n  🏆 Neural Net Best: {nn_best:.1f}%")

# ── Final Summary ───────────────────────────────────────────
print(f"\n{'='*60}")
print("  PHASE 2 FINAL SUMMARY")
print(f"{'='*60}")
print(f"Data: {len(draws)} draws (1995-2026)")
print(f"Features: {len(all_features[0])} per draw")
print(f"\nWalk-Forward Results:")
for name, r in results.items():
    if r["t"] > 0:
        hr = r["h"] / r["t"] * 100
        print(f"  {name}: {hr:.1f}% (vs {baseline:.0f}% = {hr-baseline:+.1f}%)")
print(f"\nNeural Net: {nn_best:.1f}% top-10 accuracy")

out = {
    "phase": 2,
    "draws": len(draws),
    "walk_forward": {k: {"hit_rate": v["h"]/v["t"]*100 if v["t"] > 0 else 0} for k, v in results.items()},
    "neural_net": nn_best,
}
with open(r"D:\lotto-ai\ml-models\results\phase2.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"\nSaved: D:\\lotto-ai\\ml-models\\results\\phase2.json")
