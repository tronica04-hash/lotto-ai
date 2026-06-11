#!/usr/bin/env python3
"""
LottoAI ML Engine — Phase 3: XGBoost + Random Forest + Advanced Features
- ใช้ข้อมูล 666 งวดที่มีอยู่ (1995-2026)
- เพิ่ม features: digit patterns, gaps, time cycles, positional analysis
- Train XGBoost + Random Forest + Extra Trees
- Walk-forward validation
"""
import json, os, math, random
from collections import Counter, defaultdict
from datetime import datetime

# Load Data
with open(r"D:\lotto-ai\ml-models\data\scraped_all.json", "r", encoding="utf-8") as f:
    draws = json.load(f)

print("=" * 60)
print("  LOTTO AI — PHASE 3: XGBoost + Random Forest")
print(f"  Draws: {len(draws)} | {draws[0]['draw_date']} -> {draws[-1]['draw_date']}")
print("=" * 60)

# ── Advanced Feature Engineering ─────────────────────────────
def safe_arr(v):
    if not v: return []
    if isinstance(v, list): return v
    try: return json.loads(v)
    except: return []

def extract_all_features(draw, history):
    """Extract comprehensive features"""
    f = {}
    dt = datetime.strptime(draw["draw_date"], "%Y-%m-%d")
    
    # Time features
    f["dow"] = dt.weekday()
    f["month"] = dt.month
    f["year"] = dt.year - 1995  # Normalize
    f["dom"] = dt.day  # 1 or 16
    f["is_1st"] = 1 if dt.day == 1 else 0  # วันที่ 1 หรือ 16
    
    # Cyclical time encoding
    f["month_sin"] = math.sin(2 * math.pi * dt.month / 12)
    f["month_cos"] = math.cos(2 * math.pi * dt.month / 12)
    f["dow_sin"] = math.sin(2 * math.pi * dt.weekday() / 7)
    f["dow_cos"] = math.cos(2 * math.pi * dt.weekday() / 7)
    
    fp = draw.get("first_prize", "")
    if not fp or len(fp) != 6:
        return None
    
    digits = [int(d) for d in fp]
    
    # Digit-level features
    for i, d in enumerate(digits):
        f[f"d{i+1}"] = d
    f["sum"] = sum(digits)
    f["mean"] = sum(digits) / 6
    f["std"] = math.sqrt(sum((d - f["mean"])**2 for d in digits) / 6) if digits else 0
    f["even"] = sum(1 for d in digits if d % 2 == 0)
    f["odd"] = 6 - f["even"]
    f["consec"] = sum(1 for i in range(5) if digits[i] + 1 == digits[i+1])
    f["repeat"] = 1 if len(set(digits)) < 6 else 0
    f["max_gap"] = max(digits) - min(digits)
    f["first_last_diff"] = abs(digits[0] - digits[-1])
    f["d1_plus_d6"] = digits[0] + digits[-1]
    f["d2_plus_d5"] = digits[1] + digits[-2]
    f["d3_plus_d4"] = digits[2] + digits[-3]
    f["product"] = math.prod(max(d, 1) for d in digits) % 100  # Product mod 100
    
    # Pair features
    f["pair_12"] = int(fp[:2])
    f["pair_34"] = int(fp[2:4])
    f["pair_56"] = int(fp[4:6])
    f["pair_13"] = int(fp[0] + fp[2])
    f["pair_24"] = int(fp[1] + fp[3])
    
    # Last-2, Last-3, First-2, First-3
    f["last2"] = int(fp[-2:])
    f["last3"] = int(fp[-3:])
    f["first2"] = int(fp[:2])
    f["first3"] = int(fp[:3])
    f["mid2"] = int(fp[2:4])
    
    # Sum of pairs
    f["sum_first2"] = sum(int(d) for d in fp[:2])
    f["sum_last2"] = sum(int(d) for d in fp[-2:])
    f["sum_first3"] = sum(int(d) for d in fp[:3])
    f["sum_last3"] = sum(int(d) for d in fp[-3:])
    
    # Two digit target
    two_d = draw.get("two_digit", "")
    f["target"] = int(two_d) if two_d and two_d.isdigit() else -1
    
    # History-based features (from previous draws)
    if history:
        # Last draw features
        last = history[-1]
        last_fp = last.get("first_prize", "")
        if last_fp and len(last_fp) == 6:
            last_digits = [int(d) for d in last_fp]
            f["last_sum"] = sum(last_digits)
            f["last_last2"] = int(last_fp[-2:])
            f["diff_last2"] = f["last2"] - f["last_last2"] if f["last2"] >= 0 else 0
            f["same_as_last"] = 1 if fp[-2:] == last_fp[-2:] else 0
        
        # Gap since each digit was seen at each position
        for pos in range(6):
            for back in range(1, min(11, len(history)+1)):
                hfp = history[-back].get("first_prize", "")
                if hfp and len(hfp) == 6 and int(hfp[pos]) == digits[pos]:
                    f[f"gap_pos{pos+1}"] = back
                    break
            else:
                f[f"gap_pos{pos+1}"] = 10
        
        # Frequency in last 10, 30, 50 draws
        for window_name, window_size in [("10", 10), ("30", 30), ("50", 50)]:
            recent = history[-window_size:] if len(history) >= window_size else history
            recent_last2 = [d.get("two_digit", "") for d in recent if d.get("two_digit")]
            freq = Counter(recent_last2)
            target_str = fp[-2:]
            f[f"freq_{window_name}"] = freq.get(target_str, 0)
        
        # Consecutive appearances of same last-2
        consec = 0
        for back in range(1, min(6, len(history)+1)):
            hfp = history[-back].get("first_prize", "")
            if hfp and len(hfp) == 6 and hfp[-2:] == fp[-2:]:
                consec += 1
            else:
                break
        f["consec_last2"] = consec
    else:
        f["last_sum"] = 0
        f["last_last2"] = 0
        f["diff_last2"] = 0
        f["same_as_last"] = 0
        for pos in range(6):
            f[f"gap_pos{pos+1}"] = 10
        for w in ["10", "30", "50"]:
            f[f"freq_{w}"] = 0
        f["consec_last2"] = 0
    
    return f

# Extract features
all_features = []
for i, draw in enumerate(draws):
    history = draws[max(0, i-50):i]
    feats = extract_all_features(draw, history)
    if feats and feats["target"] >= 0:
        all_features.append(feats)

print(f"\nFeatures extracted: {len(all_features)} draws")
print(f"Feature count: {len(all_features[0]) if all_features else 0}")

# ── Prepare Data for ML ─────────────────────────────────────
# Get feature keys (exclude target)
feature_keys = [k for k in all_features[0].keys() if k != "target"]
print(f"ML features: {len(feature_keys)}")

X = [[f[k] for k in feature_keys] for f in all_features]
y = [f["target"] for f in all_features]

# Normalize features
from copy import deepcopy
X_norm = deepcopy(X)
feature_mins = []
feature_maxs = []
for j in range(len(feature_keys)):
    col = [X[i][j] for i in range(len(X))]
    mn, mx = min(col), max(col)
    feature_mins.append(mn)
    feature_maxs.append(mx)
    for i in range(len(X)):
        X_norm[i][j] = (X[i][j] - mn) / (mx - mn) if mx > mn else 0

print(f"Data: {len(X_norm)} samples, {len(X_norm[0])} features")

# ── Random Forest (from scratch) ────────────────────────────
print(f"\n{'━'*50}")
print("🌲 RANDOM FOREST (from scratch)")
print(f"{'━'*50}")

class DecisionTree:
    def __init__(self, max_depth=10, min_samples=5, max_features=None):
        self.max_depth = max_depth
        self.min_samples = min_samples
        self.max_features = max_features
        self.tree = None
    
    def _gini(self, y):
        if not y: return 0
        counts = Counter(y)
        return 1 - sum((c/len(y))**2 for c in counts.values())
    
    def _best_split(self, X, y):
        best_gini = float('inf')
        best_feature = None
        best_threshold = None
        
        n_features = len(X[0])
        features = list(range(n_features))
        if self.max_features:
            features = random.sample(features, min(self.max_features, n_features))
        
        for feat in features:
            values = sorted(set(row[feat] for row in X))
            for thresh in values[:20]:  # Limit thresholds
                left_y = [y[i] for i in range(len(X)) if X[i][feat] <= thresh]
                right_y = [y[i] for i in range(len(X)) if X[i][feat] > thresh]
                if not left_y or not right_y:
                    continue
                gini = (len(left_y) * self._gini(left_y) + len(right_y) * self._gini(right_y)) / len(y)
                if gini < best_gini:
                    best_gini = gini
                    best_feature = feat
                    best_threshold = thresh
        
        return best_feature, best_threshold
    
    def _build(self, X, y, depth=0):
        if depth >= self.max_depth or len(y) < self.min_samples or len(set(y)) == 1:
            return {"leaf": True, "pred": Counter(y).most_common(1)[0][0] if y else 0}
        
        feat, thresh = self._best_split(X, y)
        if feat is None:
            return {"leaf": True, "pred": Counter(y).most_common(1)[0][0] if y else 0}
        
        left_X = [X[i] for i in range(len(X)) if X[i][feat] <= thresh]
        left_y = [y[i] for i in range(len(X)) if X[i][feat] <= thresh]
        right_X = [X[i] for i in range(len(X)) if X[i][feat] > thresh]
        right_y = [y[i] for i in range(len(X)) if X[i][feat] > thresh]
        
        return {
            "leaf": False,
            "feature": feat,
            "threshold": thresh,
            "left": self._build(left_X, left_y, depth+1),
            "right": self._build(right_X, right_y, depth+1),
        }
    
    def fit(self, X, y):
        self.tree = self._build(X, y)
    
    def _predict_one(self, x, node):
        if node["leaf"]:
            return node["pred"]
        if x[node["feature"]] <= node["threshold"]:
            return self._predict_one(x, node["left"])
        return self._predict_one(x, node["right"])
    
    def predict(self, X):
        return [self._predict_one(x, self.tree) for x in X]

class RandomForestScratch:
    def __init__(self, n_trees=20, max_depth=8, min_samples=10, max_features=None):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.min_samples = min_samples
        self.max_features = max_features
        self.trees = []
    
    def fit(self, X, y):
        self.trees = []
        for i in range(self.n_trees):
            # Bootstrap sample
            idxs = [random.randint(0, len(X)-1) for _ in range(len(X))]
            X_boot = [X[j] for j in idxs]
            y_boot = [y[j] for j in idxs]
            
            tree = DecisionTree(max_depth=self.max_depth, min_samples=self.min_samples, max_features=self.max_features)
            tree.fit(X_boot, y_boot)
            self.trees.append(tree)
            if (i+1) % 5 == 0:
                print(f"  Tree {i+1}/{self.n_trees}")
    
    def predict(self, X):
        predictions = []
        for x in X:
            votes = Counter(tree.predict([x])[0] for tree in self.trees)
            predictions.append(votes.most_common(1)[0][0])
        return predictions
    
    def predict_top_n(self, X, n=10):
        """Return top N predictions per sample"""
        all_top = []
        for x in X:
            votes = Counter()
            for tree in self.trees:
                pred = tree.predict([x])[0]
                votes[pred] += 1
            top = [k for k, _ in votes.most_common(n)]
            all_top.append(top)
        return all_top

# Walk-forward validation for Random Forest
print("\n  Walk-Forward Validation (Random Forest)...")
window = 300
step = 20
rf_hits = 0
rf_total = 0

for i in range(window, len(X_norm) - step, step):
    X_train = X_norm[max(0, i-window):i]
    y_train = y[max(0, i-window):i]
    X_test = X_norm[i:i+step]
    y_test = y[i:i+step]
    
    rf = RandomForestScratch(n_trees=10, max_depth=6, min_samples=15, max_features=int(math.sqrt(len(feature_keys))))
    rf.fit(X_train, y_train)
    
    top_preds = rf.predict_top_n(X_test, 10)
    for preds, actual in zip(top_preds, y_test):
        if actual in preds:
            rf_hits += 1
        rf_total += 1
    
    if (i - window) % 100 == 0:
        print(f"    Progress: {i}/{len(X_norm)}")

rf_hit_rate = rf_hits / rf_total * 100 if rf_total > 0 else 0
print(f"\n  Random Forest: {rf_hits}/{rf_total} = {rf_hit_rate:.1f}% (vs 10% = {rf_hit_rate-10:+.1f}%)")

# ── XGBoost-style (Gradient Boosting from scratch) ──────────
print(f"\n{'━'*50}")
print("🚀 GRADIENT BOOSTING (XGBoost-style)")
print(f"{'━'*50}")

class GradientBoostingPredictor:
    """Simple gradient boosting for classification"""
    def __init__(self, n_rounds=30, max_depth=4, lr=0.1):
        self.n_rounds = n_rounds
        self.max_depth = max_depth
        self.lr = lr
        self.trees_per_class = {}
    
    def fit(self, X, y):
        classes = list(set(y))
        for cls in classes[:20]:  # Limit to top 20 classes for speed
            # Binary: is this class or not?
            y_binary = [1 if v == cls else 0 for v in y]
            
            trees = []
            residuals = y_binary[:]
            
            for r in range(self.n_rounds):
                tree = DecisionTree(max_depth=self.max_depth, min_samples=20)
                tree.fit(X, residuals)
                preds = tree.predict(X)
                
                # Update residuals
                for i in range(len(residuals)):
                    residuals[i] -= self.lr * preds[i]
                
                trees.append(tree)
            
            self.trees_per_class[cls] = trees
    
    def predict_proba(self, x):
        scores = {}
        for cls, trees in self.trees_per_class.items():
            score = sum(tree.predict([x])[0] for tree in trees) * self.lr
            scores[cls] = score
        return scores
    
    def predict_top_n(self, X, n=10):
        results = []
        for x in X:
            scores = self.predict_proba(x)
            top = sorted(scores, key=scores.get, reverse=True)[:n]
            results.append(top)
        return results

print("  Training Gradient Boosting...")
# Use smaller dataset for GB (slower)
gb = GradientBoostingPredictor(n_rounds=10, max_depth=3, lr=0.1)
split_gb = min(400, len(X_norm))
gb.fit(X_norm[:split_gb], y[:split_gb])

print("  Walk-Forward Validation (Gradient Boosting)...")
gb_hits = 0
gb_total = 0
for i in range(split_gb, min(split_gb + 100, len(X_norm)), step):
    X_test = X_norm[i:i+step]
    y_test = y[i:i+step]
    
    top_preds = gb.predict_top_n(X_test, 10)
    for preds, actual in zip(top_preds, y_test):
        if actual in preds:
            gb_hits += 1
        gb_total += 1

gb_hit_rate = gb_hits / gb_total * 100 if gb_total > 0 else 0
print(f"\n  Gradient Boosting: {gb_hits}/{gb_total} = {gb_hit_rate:.1f}% (vs 10% = {gb_hit_rate-10:+.1f}%)")

# ── Final Summary ───────────────────────────────────────────
print(f"\n{'='*60}")
print("  PHASE 3 FINAL SUMMARY")
print(f"{'='*60}")
print(f"Data: {len(draws)} draws (1995-2026)")
print(f"Features: {len(feature_keys)} per draw")
print(f"\nResults:")
print(f"  Random Forest: {rf_hit_rate:.1f}% (vs 10% = {rf_hit_rate-10:+.1f}%)")
print(f"  Gradient Boosting: {gb_hit_rate:.1f}% (vs 10% = {gb_hit_rate-10:+.1f}%)")
print(f"\n  Phase 1 Best: Digit Position 52.2%")
print(f"  Phase 2 Best: Neural Net 18.0%")
print(f"  Phase 3 Best: Random Forest {rf_hit_rate:.1f}%")

# Save results
output = {
    "phase": 3,
    "draws": len(draws),
    "features": len(feature_keys),
    "random_forest": {"hit_rate": rf_hit_rate, "vs_random": rf_hit_rate - 10},
    "gradient_boosting": {"hit_rate": gb_hit_rate, "vs_random": gb_hit_rate - 10},
    "all_phases": {
        "phase1_digit_position": 52.2,
        "phase1_monte_carlo": 14.2,
        "phase2_neural_net": 18.0,
        "phase3_random_forest": rf_hit_rate,
        "phase3_gradient_boosting": gb_hit_rate,
    }
}

os.makedirs(r"D:\lotto-ai\ml-models\results", exist_ok=True)
with open(r"D:\lotto-ai\ml-models\results\phase3.json", "w") as f:
    json.dump(output, f, indent=2)
print(f"\nSaved: D:\\lotto-ai\\ml-models\\results\phase3.json")
