"""
LottoAI ML Model Trainer
Trains multiple ML models for 6-digit lottery prediction.
Uses walk-forward validation on last 100 draws.
"""

import json
import os
import sys
import pickle
import warnings
import numpy as np
import pandas as pd
from datetime import datetime
from collections import Counter

warnings.filterwarnings('ignore')

# ML Libraries
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("WARNING: XGBoost not installed. Installing...")
    os.system("pip install xgboost -q")
    import xgboost as xgb
    HAS_XGBOOST = True

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.callbacks import EarlyStopping
    tf.get_logger().setLevel('ERROR')
    HAS_TF = True
except ImportError:
    HAS_TF = False
    print("WARNING: TensorFlow not available. LSTM will be skipped.")

# ============================================================
# CONFIGURATION
# ============================================================
DATA_PATH = r"D:\lotto-ai\ml-models\data\scraped_all.json"
FORMULA_PATH = r"D:\lotto-ai\ml-models\formulas\formula_library_v2.json"
RESULTS_DIR = r"D:\lotto-ai\ml-models\results"
RESULTS_PATH = os.path.join(RESULTS_DIR, "ml_performance.json")
BEST_MODEL_PATH = os.path.join(RESULTS_DIR, "best_model.pkl")

WALKFORWARD_TEST_SIZE = 100
RANDOM_STATE = 42
NUM_DIGITS = 6
DIGIT_RANGE = 10  # 0-9

os.makedirs(RESULTS_DIR, exist_ok=True)

# ============================================================
# LOAD DATA
# ============================================================
print("=" * 70)
print("LOTTO AI - ML MODEL TRAINER")
print("=" * 70)

print("\n[1/7] Loading data...")
with open(DATA_PATH, 'r') as f:
    raw_data = json.load(f)

# Parse draws
draws = []
for entry in raw_data:
    fp = entry.get('first_prize', '')
    if len(fp) == 6 and fp.isdigit():
        digits = [int(d) for d in fp]
        draws.append({
            'draw_date': entry.get('draw_date', ''),
            'first_prize': fp,
            'digits': digits,
            'two_digit': entry.get('two_digit', ''),
        })

print(f"  Loaded {len(draws)} valid draws")
print(f"  Date range: {draws[0]['draw_date']} to {draws[-1]['draw_date']}")

# Sort by date
draws.sort(key=lambda x: x['draw_date'])

# ============================================================
# FEATURE ENGINEERING
# ============================================================
print("\n[2/7] Engineering features...")

def compute_digit_frequency(draws, position, window=50):
    """Compute digit frequency at a given position over a rolling window."""
    freq = np.zeros((len(draws), 10))
    for i in range(len(draws)):
        start = max(0, i - window)
        window_draws = draws[start:i]
        if window_draws:
            digits_at_pos = [d[position] for d in window_draws]
            counts = Counter(digits_at_pos)
            for d in range(10):
                freq[i, d] = counts.get(d, 0) / len(window_draws)
    return freq

def compute_gap(draws, position):
    """Compute gap since last appearance of each digit at position."""
    gap = np.zeros((len(draws), 10))
    for i in range(len(draws)):
        for d in range(10):
            last_seen = -1
            for j in range(i - 1, -1, -1):
                if draws[j]['digits'][position] == d:
                    last_seen = j
                    break
            if last_seen == -1:
                gap[i, d] = i  # Never seen
            else:
                gap[i, d] = i - last_seen
    return gap

def compute_recency(draws, position):
    """Compute recency (inverse of gap)."""
    gap = compute_gap(draws, position)
    recency = 1.0 / (1.0 + gap)
    return recency

def compute_position_features(draws):
    """Features based on digit positions."""
    features = np.zeros((len(draws), NUM_DIGITS))
    for i, draw in enumerate(draws):
        for pos in range(NUM_DIGITS):
            features[i, pos] = draw['digits'][pos] / 9.0
    return features

def compute_sum_features(draws):
    """Sum-based features."""
    features = np.zeros((len(draws), 4))
    for i, draw in enumerate(draws):
        digits = draw['digits']
        features[i, 0] = sum(digits) / 54.0  # Normalized sum
        features[i, 1] = sum(digits[:3]) / 27.0  # First half sum
        features[i, 2] = sum(digits[3:]) / 27.0  # Second half sum
        features[i, 3] = (sum(digits[:3]) - sum(digits[3:])) / 27.0  # Difference
    return features

def compute_odd_even_features(draws):
    """Odd/even ratio features."""
    features = np.zeros((len(draws), 3))
    for i, draw in enumerate(draws):
        digits = draw['digits']
        odd_count = sum(1 for d in digits if d % 2 == 1)
        features[i, 0] = odd_count / 6.0
        features[i, 1] = sum(1 for d in digits[:3] if d % 2 == 1) / 3.0
        features[i, 2] = sum(1 for d in digits[3:] if d % 2 == 1) / 3.0
    return features

def compute_consecutive_features(draws):
    """Consecutive digit features."""
    features = np.zeros((len(draws), 3))
    for i, draw in enumerate(draws):
        digits = draw['digits']
        # Count consecutive pairs
        consec = sum(1 for j in range(len(digits)-1) if abs(digits[j] - digits[j+1]) == 1)
        # Count repeated digits
        unique = len(set(digits))
        # Max consecutive run
        max_run = 1
        current_run = 1
        for j in range(1, len(digits)):
            if digits[j] == digits[j-1]:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 1
        features[i, 0] = consec / 5.0
        features[i, 1] = unique / 6.0
        features[i, 2] = max_run / 6.0
    return features

def compute_hot_cold_features(draws):
    """Hot/cold digit features."""
    features = np.zeros((len(draws), 10))
    for i in range(len(draws)):
        start = max(0, i - 30)
        window_draws = draws[start:i]
        if window_draws:
            all_digits = [d for draw in window_draws for d in draw['digits']]
            counts = Counter(all_digits)
            total = len(all_digits)
            for d in range(10):
                features[i, d] = counts.get(d, 0) / total if total > 0 else 0.1
    return features

def compute_transition_features(draws):
    """Digit transition features."""
    features = np.zeros((len(draws), NUM_DIGITS - 1))
    for i, draw in enumerate(draws):
        digits = draw['digits']
        for j in range(NUM_DIGITS - 1):
            features[i, j] = abs(digits[j] - digits[j+1]) / 9.0
    return features

def build_feature_matrix(draws):
    """Build complete feature matrix."""
    all_features = []
    
    # Per-position frequency, gap, recency
    for pos in range(NUM_DIGITS):
        freq = compute_digit_frequency(draws, pos, window=30)
        gap = compute_gap(draws, pos)
        recency = compute_recency(draws, pos)
        all_features.append(freq)
        all_features.append(gap / 100.0)  # Normalize
        all_features.append(recency)
    
    # Position features
    all_features.append(compute_position_features(draws))
    
    # Sum features
    all_features.append(compute_sum_features(draws))
    
    # Odd/even features
    all_features.append(compute_odd_even_features(draws))
    
    # Consecutive features
    all_features.append(compute_consecutive_features(draws))
    
    # Hot/cold features
    all_features.append(compute_hot_cold_features(draws))
    
    # Transition features
    all_features.append(compute_transition_features(draws))
    
    # Historical digit values (last 5 draws)
    history = np.zeros((len(draws), NUM_DIGITS * 5))
    for i in range(len(draws)):
        for h in range(1, 6):
            if i >= h:
                for pos in range(NUM_DIGITS):
                    history[i, (h-1) * NUM_DIGITS + pos] = draws[i-h]['digits'][pos] / 9.0
    all_features.append(history)
    
    return np.hstack(all_features)

# Build features
X_all = build_feature_matrix(draws)
print(f"  Feature matrix shape: {X_all.shape}")

# Build targets (one per digit position)
y_all = np.array([draw['digits'] for draw in draws])  # (N, 6)

# ============================================================
# WALK-FORWARD VALIDATION SPLIT
# ============================================================
print("\n[3/7] Setting up walk-forward validation...")

train_end = len(draws) - WALKFORWARD_TEST_SIZE
X_train = X_all[:train_end]
X_test = X_all[train_end:]
y_train = y_all[:train_end]
y_test = y_all[train_end:]

print(f"  Training set: {train_end} draws")
print(f"  Test set: {WALKFORWARD_TEST_SIZE} draws")
print(f"  Test period: {draws[train_end]['draw_date']} to {draws[-1]['draw_date']}")

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ============================================================
# MODEL TRAINING
# ============================================================
print("\n[4/7] Training models...")

results = {}

# --- 4a. Random Forest (6 models, one per position) ---
print("\n  [4a] Training Random Forest (6 position models)...")
rf_results = {'per_position': [], 'overall_correct': 0, 'total_predictions': 0}
rf_models = []
rf_test_preds = np.zeros_like(y_test)

for pos in range(NUM_DIGITS):
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )
    rf.fit(X_train_scaled, y_train[:, pos])
    preds = rf.predict(X_test_scaled)
    rf_test_preds[:, pos] = preds
    acc = accuracy_score(y_test[:, pos], preds)
    rf_results['per_position'].append({
        'position': pos,
        'accuracy': float(acc),
    })
    rf_models.append(rf)
    print(f"    Position {pos}: accuracy = {acc:.4f}")

# Overall: count draws where all 6 digits match
rf_exact = np.all(rf_test_preds == y_test, axis=1).sum()
rf_results['exact_match'] = int(rf_exact)
rf_results['exact_match_rate'] = float(rf_exact / WALKFORWARD_TEST_SIZE)
rf_results['avg_position_accuracy'] = float(np.mean([r['accuracy'] for r in rf_results['per_position']]))
print(f"    Overall exact match: {rf_exact}/{WALKFORWARD_TEST_SIZE} ({rf_results['exact_match_rate']:.4f})")
print(f"    Avg position accuracy: {rf_results['avg_position_accuracy']:.4f}")
results['random_forest'] = rf_results

# --- 4b. XGBoost (6 models, one per position) ---
print("\n  [4b] Training XGBoost (6 position models)...")
xgb_results = {'per_position': [], 'exact_match': 0, 'exact_match_rate': 0}
xgb_models = []
xgb_test_preds = np.zeros_like(y_test)

for pos in range(NUM_DIGITS):
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_STATE,
        use_label_encoder=False,
        eval_metric='mlogloss',
        verbosity=0
    )
    model.fit(X_train_scaled, y_train[:, pos])
    preds = model.predict(X_test_scaled)
    xgb_test_preds[:, pos] = preds
    acc = accuracy_score(y_test[:, pos], preds)
    xgb_results['per_position'].append({
        'position': pos,
        'accuracy': float(acc),
    })
    xgb_models.append(model)
    print(f"    Position {pos}: accuracy = {acc:.4f}")

xgb_exact = np.all(xgb_test_preds == y_test, axis=1).sum()
xgb_results['exact_match'] = int(xgb_exact)
xgb_results['exact_match_rate'] = float(xgb_exact / WALKFORWARD_TEST_SIZE)
xgb_results['avg_position_accuracy'] = float(np.mean([r['accuracy'] for r in xgb_results['per_position']]))
print(f"    Overall exact match: {xgb_exact}/{WALKFORWARD_TEST_SIZE} ({xgb_results['exact_match_rate']:.4f})")
print(f"    Avg position accuracy: {xgb_results['avg_position_accuracy']:.4f}")
results['xgboost'] = xgb_results

# --- 4c. Logistic Regression (baseline) ---
print("\n  [4c] Training Logistic Regression (6 position models)...")
lr_results = {'per_position': [], 'exact_match': 0, 'exact_match_rate': 0}
lr_models = []
lr_test_preds = np.zeros_like(y_test)

for pos in range(NUM_DIGITS):
    lr = LogisticRegression(
        max_iter=1000,
        C=1.0,
        solver='lbfgs',
        multi_class='multinomial',
        random_state=RANDOM_STATE
    )
    lr.fit(X_train_scaled, y_train[:, pos])
    preds = lr.predict(X_test_scaled)
    lr_test_preds[:, pos] = preds
    acc = accuracy_score(y_test[:, pos], preds)
    lr_results['per_position'].append({
        'position': pos,
        'accuracy': float(acc),
    })
    lr_models.append(lr)
    print(f"    Position {pos}: accuracy = {acc:.4f}")

lr_exact = np.all(lr_test_preds == y_test, axis=1).sum()
lr_results['exact_match'] = int(lr_exact)
lr_results['exact_match_rate'] = float(lr_exact / WALKFORWARD_TEST_SIZE)
lr_results['avg_position_accuracy'] = float(np.mean([r['accuracy'] for r in lr_results['per_position']]))
print(f"    Overall exact match: {lr_exact}/{WALKFORWARD_TEST_SIZE} ({lr_results['exact_match_rate']:.4f})")
print(f"    Avg position accuracy: {lr_results['avg_position_accuracy']:.4f}")
results['logistic_regression'] = lr_results

# --- 4d. K-Nearest Neighbors ---
print("\n  [4d] Training KNN (6 position models)...")
knn_results = {'per_position': [], 'exact_match': 0, 'exact_match_rate': 0}
knn_models = []
knn_test_preds = np.zeros_like(y_test)

for pos in range(NUM_DIGITS):
    knn = KNeighborsClassifier(
        n_neighbors=15,
        weights='distance',
        metric='euclidean',
        n_jobs=-1
    )
    knn.fit(X_train_scaled, y_train[:, pos])
    preds = knn.predict(X_test_scaled)
    knn_test_preds[:, pos] = preds
    acc = accuracy_score(y_test[:, pos], preds)
    knn_results['per_position'].append({
        'position': pos,
        'accuracy': float(acc),
    })
    knn_models.append(knn)
    print(f"    Position {pos}: accuracy = {acc:.4f}")

knn_exact = np.all(knn_test_preds == y_test, axis=1).sum()
knn_results['exact_match'] = int(knn_exact)
knn_results['exact_match_rate'] = float(knn_exact / WALKFORWARD_TEST_SIZE)
knn_results['avg_position_accuracy'] = float(np.mean([r['accuracy'] for r in knn_results['per_position']]))
print(f"    Overall exact match: {knn_exact}/{WALKFORWARD_TEST_SIZE} ({knn_results['exact_match_rate']:.4f})")
print(f"    Avg position accuracy: {knn_results['avg_position_accuracy']:.4f}")
results['knn'] = knn_results

# --- 4e. LSTM Neural Network ---
print("\n  [4e] Training LSTM Neural Network...")
lstm_results = {'per_position': [], 'exact_match': 0, 'exact_match_rate': 0}

if HAS_TF:
    # Prepare sequence data for LSTM
    SEQ_LENGTH = 10
    
    def create_sequences(data, seq_length):
        X_seq, y_seq = [], []
        for i in range(seq_length, len(data)):
            X_seq.append(data[i-seq_length:i])
            y_seq.append(data[i])
        return np.array(X_seq), np.array(y_seq)
    
    # Use raw digit sequences as input for LSTM
    digit_sequences = np.array([draw['digits'] for draw in draws])  # (N, 6)
    
    # Normalize to [0, 1]
    digit_sequences_norm = digit_sequences / 9.0
    
    X_seq, y_seq = create_sequences(digit_sequences_norm, SEQ_LENGTH)
    # y_seq is (N, 6), each value 0-9 normalized
    
    # Split
    train_seq_end = len(X_seq) - WALKFORWARD_TEST_SIZE
    if train_seq_end > 0:
        X_seq_train = X_seq[:train_seq_end]
        X_seq_test = X_seq[train_seq_end:]
        y_seq_train = y_seq[:train_seq_end]
        y_seq_test = y_seq[train_seq_end:]
        
        # Build LSTM model
        model_lstm = Sequential([
            LSTM(128, input_shape=(SEQ_LENGTH, 6), return_sequences=True),
            Dropout(0.3),
            BatchNormalization(),
            LSTM(64, return_sequences=False),
            Dropout(0.3),
            Dense(64, activation='relu'),
            Dense(32, activation='relu'),
            Dense(6, activation='sigmoid')  # 6 outputs, each 0-1
        ])
        
        model_lstm.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        print("    Training LSTM...")
        history = model_lstm.fit(
            X_seq_train, y_seq_train,
            epochs=100,
            batch_size=32,
            validation_split=0.15,
            callbacks=[early_stop],
            verbose=0
        )
        
        # Predict
        lstm_preds_norm = model_lstm.predict(X_seq_test, verbose=0)
        lstm_preds = np.round(lstm_preds_norm * 9).astype(int)
        lstm_preds = np.clip(lstm_preds, 0, 9)
        
        # Evaluate per position
        for pos in range(NUM_DIGITS):
            acc = accuracy_score(y_seq_test[:, pos] * 9, lstm_preds[:, pos])
            lstm_results['per_position'].append({
                'position': pos,
                'accuracy': float(acc),
            })
            print(f"    Position {pos}: accuracy = {acc:.4f}")
        
        lstm_exact = np.all(lstm_preds == np.round(y_seq_test * 9).astype(int), axis=1).sum()
        lstm_results['exact_match'] = int(lstm_exact)
        lstm_results['exact_match_rate'] = float(lstm_exact / len(y_seq_test))
        lstm_results['avg_position_accuracy'] = float(np.mean([r['accuracy'] for r in lstm_results['per_position']]))
        lstm_results['training_epochs'] = len(history.history['loss'])
        print(f"    Overall exact match: {lstm_exact}/{len(y_seq_test)} ({lstm_results['exact_match_rate']:.4f})")
        print(f"    Avg position accuracy: {lstm_results['avg_position_accuracy']:.4f}")
        print(f"    Training epochs: {lstm_results['training_epochs']}")
        
        # Save LSTM model
        model_lstm.save(os.path.join(RESULTS_DIR, "lstm_model.keras"))
    else:
        print("    Not enough data for LSTM sequences")
        lstm_results['error'] = 'Not enough data'
else:
    lstm_results['error'] = 'TensorFlow not available'
    print("    SKIPPED: TensorFlow not available")

results['lstm'] = lstm_results

# --- 4f. Ensemble (weighted combination) ---
print("\n  [4f] Building Ensemble model...")

# Use probability-based ensemble from RF, XGB, LR, KNN
# For each position, combine predictions weighted by validation accuracy

ensemble_test_preds = np.zeros_like(y_test)

for pos in range(NUM_DIGITS):
    # Get probability predictions from each model
    rf_proba = rf_models[pos].predict_proba(X_test_scaled)
    xgb_proba = xgb_models[pos].predict_proba(X_test_scaled)
    lr_proba = lr_models[pos].predict_proba(X_test_scaled)
    knn_proba = knn_models[pos].predict_proba(X_test_scaled)
    
    # Weights based on training accuracy (use position accuracy as proxy)
    w_rf = rf_results['per_position'][pos]['accuracy']
    w_xgb = xgb_results['per_position'][pos]['accuracy']
    w_lr = lr_results['per_position'][pos]['accuracy']
    w_knn = knn_results['per_position'][pos]['accuracy']
    
    # Normalize weights
    total_w = w_rf + w_xgb + w_lr + w_knn
    if total_w > 0:
        w_rf /= total_w
        w_xgb /= total_w
        w_lr /= total_w
        w_knn /= total_w
    else:
        w_rf = w_xgb = w_lr = w_knn = 0.25
    
    # Weighted average of probabilities
    # Ensure all have same classes
    classes = rf_models[pos].classes_
    n_classes = len(classes)
    
    combined_proba = (
        w_rf * rf_proba +
        w_xgb * xgb_proba +
        w_lr * lr_proba +
        w_knn * knn_proba
    )
    
    # Get prediction
    pred_indices = np.argmax(combined_proba, axis=1)
    ensemble_test_preds[:, pos] = classes[pred_indices]

ensemble_results = {'per_position': []}
for pos in range(NUM_DIGITS):
    acc = accuracy_score(y_test[:, pos], ensemble_test_preds[:, pos])
    ensemble_results['per_position'].append({
        'position': pos,
        'accuracy': float(acc),
    })
    print(f"    Position {pos}: accuracy = {acc:.4f}")

ensemble_exact = np.all(ensemble_test_preds == y_test, axis=1).sum()
ensemble_results['exact_match'] = int(ensemble_exact)
ensemble_results['exact_match_rate'] = float(ensemble_exact / WALKFORWARD_TEST_SIZE)
ensemble_results['avg_position_accuracy'] = float(np.mean([r['accuracy'] for r in ensemble_results['per_position']]))
print(f"    Overall exact match: {ensemble_exact}/{WALKFORWARD_TEST_SIZE} ({ensemble_results['exact_match_rate']:.4f})")
print(f"    Avg position accuracy: {ensemble_results['avg_position_accuracy']:.4f}")
results['ensemble'] = ensemble_results

# ============================================================
# LOAD FORMULA RESULTS FOR COMPARISON
# ============================================================
print("\n[5/7] Loading formula results for comparison...")

with open(FORMULA_PATH, 'r') as f:
    formula_data = json.load(f)

# Parse formula results
formula_results = []
for f in formula_data:
    formula_results.append({
        'name': f.get('name', ''),
        'total_score': f.get('total_score', 0),
        'avg_sets_won': f.get('avg_sets_won', 0),
        'perfect_rounds': f.get('perfect_rounds', 0),
        'prize_counts': f.get('prize_counts', {}),
    })

# Sort by total score
formula_results.sort(key=lambda x: x['total_score'], reverse=True)

print(f"  Loaded {len(formula_results)} formula results")
print(f"  Best formula: {formula_results[0]['name']} (score: {formula_results[0]['total_score']})")

# ============================================================
# SCORING SYSTEM (match formula scoring)
# ============================================================
print("\n[6/7] Computing ML scores using formula scoring system...")

def compute_ml_score(predictions, actuals, draws_test):
    """
    Compute a score similar to the formula scoring system.
    Prize tiers:
    - 3last: last 3 digits match
    - 2digit: 2-digit number matches
    - 3first: first 3 digits match
    - nearby: within ±1 of any digit
    - exact: all 6 digits match
    """
    total_score = 0
    prize_counts = {
        'exact_6': 0,
        '3last': 0,
        '3first': 0,
        '2digit': 0,
        'nearby': 0,
        '4_digit': 0,
        '5_digit': 0,
    }
    
    for i in range(len(predictions)):
        pred = predictions[i]
        actual = actuals[i]
        draw = draws_test[i]
        
        # Exact 6-digit match
        if np.all(pred == actual):
            total_score += 100000
            prize_counts['exact_6'] += 1
            continue
        
        # 5-digit match (any 5 of 6)
        matches = np.sum(pred == actual)
        if matches >= 5:
            total_score += 10000
            prize_counts['5_digit'] += 1
            continue
        
        # 4-digit match
        if matches >= 4:
            total_score += 1000
            prize_counts['4_digit'] += 1
            continue
        
        # First 3 digits
        if np.all(pred[:3] == actual[:3]):
            total_score += 5000
            prize_counts['3first'] += 1
        
        # Last 3 digits
        if np.all(pred[3:] == actual[3:]):
            total_score += 5000
            prize_counts['3last'] += 1
        
        # 2-digit (last 2 digits of first prize)
        pred_2digit = int(f"{pred[4]}{pred[5]}")
        actual_2digit = int(draw.get('two_digit', f"{actual[4]}{actual[5]}"))
        if pred_2digit == actual_2digit:
            total_score += 100
            prize_counts['2digit'] += 1
        
        # Nearby (any digit within ±1)
        nearby_match = False
        for p, a in zip(pred, actual):
            if abs(p - a) <= 1:
                nearby_match = True
                break
        if nearby_match:
            total_score += 10
            prize_counts['nearby'] += 1
    
    return total_score, prize_counts

# Compute scores for each ML model
print("\n  Scoring Random Forest...")
rf_score, rf_prizes = compute_ml_score(rf_test_preds, y_test, draws[train_end:])
results['random_forest']['total_score'] = rf_score
results['random_forest']['prize_counts'] = rf_prizes
print(f"    Score: {rf_score}")

print("  Scoring XGBoost...")
xgb_score, xgb_prizes = compute_ml_score(xgb_test_preds, y_test, draws[train_end:])
results['xgboost']['total_score'] = xgb_score
results['xgboost']['prize_counts'] = xgb_prizes
print(f"    Score: {xgb_score}")

print("  Scoring Logistic Regression...")
lr_score, lr_prizes = compute_ml_score(lr_test_preds, y_test, draws[train_end:])
results['logistic_regression']['total_score'] = lr_score
results['logistic_regression']['prize_counts'] = lr_prizes
print(f"    Score: {lr_score}")

print("  Scoring KNN...")
knn_score, knn_prizes = compute_ml_score(knn_test_preds, y_test, draws[train_end:])
results['knn']['total_score'] = knn_score
results['knn']['prize_counts'] = knn_prizes
print(f"    Score: {knn_score}")

print("  Scoring Ensemble...")
ens_score, ens_prizes = compute_ml_score(ensemble_test_preds, y_test, draws[train_end:])
results['ensemble']['total_score'] = ens_score
results['ensemble']['prize_counts'] = ens_prizes
print(f"    Score: {ens_score}")

# ============================================================
# SAVE RESULTS
# ============================================================
print("\n[7/7] Saving results...")

# Add metadata
output = {
    'timestamp': datetime.now().isoformat(),
    'data_info': {
        'total_draws': len(draws),
        'train_draws': train_end,
        'test_draws': WALKFORWARD_TEST_SIZE,
        'date_range': f"{draws[0]['draw_date']} to {draws[-1]['draw_date']}",
        'test_range': f"{draws[train_end]['draw_date']} to {draws[-1]['draw_date']}",
        'feature_dimensions': int(X_all.shape[1]),
    },
    'ml_results': results,
    'formula_results': formula_results[:10],  # Top 10 formulas
    'comparison': {
        'best_ml_model': max(
            ['random_forest', 'xgboost', 'logistic_regression', 'knn', 'ensemble'],
            key=lambda m: results[m]['total_score']
        ),
        'best_ml_score': max(
            results[m]['total_score'] 
            for m in ['random_forest', 'xgboost', 'logistic_regression', 'knn', 'ensemble']
        ),
        'best_formula': formula_results[0]['name'],
        'best_formula_score': formula_results[0]['total_score'],
    }
}

with open(RESULTS_PATH, 'w') as f:
    json.dump(output, f, indent=2)

print(f"  Results saved to: {RESULTS_PATH}")

# Save best model (the ensemble components + scaler)
best_model_name = output['comparison']['best_ml_model']
print(f"  Best ML model: {best_model_name}")

best_model_data = {
    'model_name': best_model_name,
    'scaler': scaler,
    'rf_models': rf_models,
    'xgb_models': xgb_models,
    'lr_models': lr_models,
    'knn_models': knn_models,
    'results': results[best_model_name],
}

with open(BEST_MODEL_PATH, 'wb') as f:
    pickle.dump(best_model_data, f)

print(f"  Best model saved to: {BEST_MODEL_PATH}")

# ============================================================
# FINAL COMPARISON REPORT
# ============================================================
print("\n" + "=" * 70)
print("FINAL COMPARISON REPORT")
print("=" * 70)

print("\n--- ML Model Performance (Walk-Forward, last 100 draws) ---")
print(f"{'Model':<25} {'Avg Pos Acc':>12} {'Exact Match':>12} {'Total Score':>12}")
print("-" * 65)

ml_models = ['random_forest', 'xgboost', 'logistic_regression', 'knn', 'ensemble']
model_display = {
    'random_forest': 'Random Forest',
    'xgboost': 'XGBoost',
    'logistic_regression': 'Logistic Regression',
    'knn': 'KNN',
    'ensemble': 'Ensemble',
}

for m in ml_models:
    r = results[m]
    print(f"{model_display[m]:<25} {r['avg_position_accuracy']:>12.4f} {r['exact_match']:>12} {r['total_score']:>12}")

if 'lstm' in results and 'avg_position_accuracy' in results['lstm']:
    r = results['lstm']
    print(f"{'LSTM':<25} {r['avg_position_accuracy']:>12.4f} {r['exact_match']:>12} {'N/A':>12}")

print("\n--- Top Formula Performance ---")
print(f"{'Formula':<30} {'Total Score':>12} {'Avg Sets Won':>14} {'Perfect':>10}")
print("-" * 70)
for f in formula_results[:10]:
    print(f"{f['name']:<30} {f['total_score']:>12} {f['avg_sets_won']:>14.4f} {f['perfect_rounds']:>10}")

print("\n--- Head-to-Head: Best ML vs Best Formula ---")
best_ml = output['comparison']['best_ml_model']
best_ml_score = output['comparison']['best_ml_score']
best_formula = output['comparison']['best_formula']
best_formula_score = output['comparison']['best_formula_score']

print(f"  Best ML:     {model_display.get(best_ml, best_ml)} (score: {best_ml_score})")
print(f"  Best Formula: {best_formula} (score: {best_formula_score})")

if best_ml_score > best_formula_score:
    print(f"\n  🏆 ML WINS by {best_ml_score - best_formula_score} points!")
else:
    print(f"\n  🏆 Formula WINS by {best_formula_score - best_ml_score} points!")

# Per-position accuracy summary
print("\n--- Per-Position Accuracy Summary ---")
print(f"{'Position':>8}", end="")
for m in ml_models:
    print(f"  {model_display[m][:6]:>8}", end="")
print()
print("-" * 55)
for pos in range(NUM_DIGITS):
    print(f"{'P' + str(pos):>8}", end="")
    for m in ml_models:
        acc = results[m]['per_position'][pos]['accuracy']
        print(f"  {acc:>8.4f}", end="")
    print()

print("\n" + "=" * 70)
print("TRAINING COMPLETE")
print("=" * 70)
