#!/usr/bin/env python3
#!/usr/bin/env python3
"""
LottoAI v2.0.0 â€” Iterative Mathematical Sandbox
Orchestrator Script (Controller)
à¹€à¸‚à¸µà¸¢à¸™à¹‚à¸”à¸¢: OWL (Default Agent) à¸ªà¸³à¸«à¸£à¸±à¸šà¸—à¸µà¸¡ LottoAI
à¸§à¸±à¸™à¸—à¸µà¹ˆ: 2026-06-24
"""

import sys, os, io
# Fix encoding for Windows PM2
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import random
import math
import math
import os
import sys
from datetime import datetime
from collections import Counter, defaultdict

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONFIGURATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

CONFIG = {
    "MAX_ITERATIONS": 1000000,
    "CONVERGENCE_THRESHOLD": 100000,
    "TEST_DRAW_STRATEGY": "random",
    "POPULATION_SIZE": 30,
    "ELITE_RATIO": 0.2,
    "MUTATION_RATE": 0.1,
    "NUM_SETS": 10,
    "DIGITS": 6,
    "DATA_FILE": r"D:\lotto-ai\ml-models\data\scraped_all.json",
    "RESULTS_FILE": r"D:\lotto-ai\ml-models\results\results_database.json",
    "FORMULA_LIB": r"D:\lotto-ai\ml-models\formulas\formula_library.json",
    "REPORT_DIR": r"D:\lotto-ai\ml-models\results",
    "LOG_DIR": r"D:\lotto-ai\logs",
    "ELITE_SCORE_THRESHOLD": 5.0,
    "EARLY_STOP_CHECK_INTERVAL": 10000,
    "RANDOM_BASELINE_SCORE": 3.0,
    "SAVE_EVERY": 1000,
    "REPORT_EVERY": 10000,
}

SCORING = {
    "base_per_set": 10,
    "à¸£à¸²à¸‡à¸§à¸±à¸¥à¸—à¸µà¹ˆ 1": 50,
    "à¸‚à¹‰à¸²à¸‡à¹€à¸„à¸µà¸¢à¸‡": 25,
    "à¸£à¸²à¸‡à¸§à¸±à¸¥à¸—à¸µà¹ˆ 2": 30,
    "à¸£à¸²à¸‡à¸§à¸±à¸¥à¸—à¸µà¹ˆ 3": 20,
    "à¸£à¸²à¸‡à¸§à¸±à¸¥à¸—à¸µà¹ˆ 4": 15,
    "à¸£à¸²à¸‡à¸§à¸±à¸¥à¸—à¸µà¹ˆ 5": 10,
    "à¹€à¸¥à¸‚à¸—à¹‰à¸²à¸¢ 3": 5,
    "à¹€à¸¥à¸‚à¸«à¸™à¹‰à¸² 3": 5,
    "à¹€à¸¥à¸‚à¸—à¹‰à¸²à¸¢ 2": 3,
}


class LottoAIController:
    def __init__(self, config):
        self.config = config
        self.data = self.load_data()
        self.formula_library = self.load_formula_library()
        self.results_db = self.load_results_database()
        self.iteration = 0
        self.best_score_ever = 0
        self.no_improvement_count = 0
        os.makedirs(self.config["REPORT_DIR"], exist_ok=True)
        os.makedirs(self.config["LOG_DIR"], exist_ok=True)
        os.makedirs(os.path.dirname(self.config["FORMULA_LIB"]), exist_ok=True)

    def load_data(self):
        with open(self.config["DATA_FILE"], "r", encoding="utf-8") as f:
            return json.load(f)

    def load_formula_library(self):
        path = self.config["FORMULA_LIB"]
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # à¸£à¸­à¸‡à¸£à¸±à¸šà¸—à¸±à¹‰à¸‡ list à¹à¸¥à¸° dict format
            if isinstance(data, list):
                # à¹à¸›à¸¥à¸‡ list â†’ dict
                lib = {}
                for i, item in enumerate(data):
                    fid = item.get("id", f"formula_{i}")
                    lib[fid] = {
                        "name": item.get("name", f"Formula {i}"),
                        "phase": item.get("phase", 1),
                        "type": item.get("type", "statistical"),
                        "params": item.get("params", {}),
                        "created": item.get("created", datetime.now().isoformat()),
                        "generation": item.get("generation", 0),
                        "avg_score": item.get("avg_score", 0),
                        "total_rounds": item.get("total_rounds", 0)
                    }
                return lib
            return data
        return self.initialize_formula_library()

    def initialize_formula_library(self):
        formulas = {}
        for i in range(1, 9):
            formulas[f"freq_v{i}"] = {
                "name": f"Frequency v{i}", "phase": 1, "type": "statistical",
                "params": {"window": 20 * i, "top_n": 10},
                "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0
            }
        for i in range(1, 5):
            formulas[f"due_v{i}"] = {
                "name": f"Due Number v{i}", "phase": 1, "type": "statistical",
                "params": {"top_n": 5 * i, "min_gap": 10 * i},
                "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0
            }
        formulas["bayesian_v1"] = {"name": "Bayesian v1", "phase": 1, "type": "statistical", "params": {"prior_strength": 1, "window": 100}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["markov_v1"] = {"name": "Markov v1", "phase": 1, "type": "statistical", "params": {"order": 1}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["monte_carlo_v1"] = {"name": "Monte Carlo v1", "phase": 1, "type": "statistical", "params": {"simulations": 10000}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["positional_v1"] = {"name": "Positional v1", "phase": 1, "type": "statistical", "params": {"top_per_pos": 3}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["hot_cold_v1"] = {"name": "Hot/Cold v1", "phase": 1, "type": "statistical", "params": {"hot_window": 20, "cold_window": 100}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["pairs_v1"] = {"name": "Pairs v1", "phase": 1, "type": "statistical", "params": {"min_cooccurrence": 3}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["time_series_v1"] = {"name": "Time Series v1", "phase": 2, "type": "advanced", "params": {"seasonality": "monthly", "trend_window": 50}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["sum_diff_v1"] = {"name": "Sum/Diff v1", "phase": 2, "type": "advanced", "params": {"target_sum": 27, "tolerance": 5}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["modular_v1"] = {"name": "Modular v1", "phase": 2, "type": "advanced", "params": {"moduli": [3, 7, 9]}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["fibonacci_v1"] = {"name": "Fibonacci v1", "phase": 2, "type": "advanced", "params": {"sequence": "fibonacci"}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["chaos_v1"] = {"name": "Chaos v1", "phase": 2, "type": "advanced", "params": {"lookback": 20}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["entropy_v1"] = {"name": "Entropy v1", "phase": 2, "type": "advanced", "params": {"window": 50}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["rf_v1"] = {"name": "Random Forest v1", "phase": 3, "type": "ml", "params": {"n_estimators": 100, "max_depth": 10}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["xgb_v1"] = {"name": "XGBoost v1", "phase": 3, "type": "ml", "params": {"learning_rate": 0.1, "max_depth": 6}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["lstm_v1"] = {"name": "LSTM v1", "phase": 3, "type": "ml", "params": {"units": 128, "sequence_length": 20}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["logistic_v1"] = {"name": "Logistic v1", "phase": 3, "type": "ml", "params": {"C": 1.0}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["knn_v1"] = {"name": "KNN v1", "phase": 3, "type": "ml", "params": {"k": 10}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        formulas["ensemble_v1"] = {"name": "Ensemble v1", "phase": 3, "type": "ml", "params": {"weight_strategy": "performance"}, "created": datetime.now().isoformat(), "generation": 0, "avg_score": 0, "total_rounds": 0}
        return formulas

    def load_results_database(self):
        path = self.config["RESULTS_FILE"]
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data
            except (json.JSONDecodeError, Exception):
                return {"iterations": [], "best_formula": None, "best_score": 0}
        return {"iterations": [], "best_formula": None, "best_score": 0}

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # MAIN LOOP
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def run(self):
        print("=" * 60)
        print("  LOTTOAI v2.0.0 â€” Iterative Mathematical Sandbox")
        print("=" * 60)
        print(f"Data: {len(self.data)} draws")
        print(f"Formulas: {len(self.formula_library)}")
        print()

        # Resume state: get last iteration from DB
        start_iter = len(self.results_db.get("iterations", []))
        if start_iter > 0:
            print(f"Resuming from iteration {start_iter + 1}")
            # Restore best score and no_improvement_count from DB
            last_iter = self.results_db["iterations"][-1]
            self.best_score_ever = max(it["best_score"] for it in self.results_db["iterations"])
            # Count no improvement from recent iterations
            recent = self.results_db["iterations"][-self.config["CONVERGENCE_THRESHOLD"]:]
            self.no_improvement_count = sum(1 for it in recent if it["best_score"] < self.best_score_ever)
            print(f"Best score so far: {self.best_score_ever}")
            print(f"No improvement count: {self.no_improvement_count}")
            print()

        for i in range(start_iter, self.config["MAX_ITERATIONS"]):
            self.iteration = i + 1
            print(f"\n{'â”' * 50}")
            print(f"  ITERATION {self.iteration}/{self.config['MAX_ITERATIONS']}")
            print(f"{'â”' * 50}")

            test_draw = self.select_test_draw()
            print(f"  Test draw: {test_draw['draw_date']}")

            train_data, test_data = self.split_data(test_draw)
            print(f"  Train: {len(train_data)} draws")

            all_sets = self.run_formulas(train_data)
            results = self.evaluate(all_sets, test_data)
            self.save_results(results, test_draw)
            self.evolve_formulas(results)

            # Smart Early Stopping check
            if self.iteration % self.config["EARLY_STOP_CHECK_INTERVAL"] == 0:
                if self.check_early_stop():
                    print(f"\n  EARLY STOP at iteration {self.iteration}")
                    print(f"     Elite avg too low â€” no pattern found")
                    break

            if self.check_convergence():
                print(f"\n  CONVERGENCE at iteration {self.iteration}")
                break

        self.print_final_report()

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # STEP 1: à¸ªà¸¸à¹ˆà¸¡à¹€à¸¥à¸·à¸­à¸à¸‡à¸§à¸”à¸—à¸”à¸ªà¸­à¸š
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def select_test_draw(self):
        strategy = self.config["TEST_DRAW_STRATEGY"]
        if strategy == "random":
            idx = random.randint(100, len(self.data) - 1)
        elif strategy == "sequential":
            idx = (self.iteration % (len(self.data) - 100)) + 100
        else:  # stratified
            chunk_size = (len(self.data) - 100) // 10
            chunk = self.iteration % 10
            idx = 100 + (chunk * chunk_size) + random.randint(0, chunk_size - 1)
            idx = min(idx, len(self.data) - 1)
        return self.data[idx]

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # STEP 2: à¹à¸šà¹ˆà¸‡à¸‚à¹‰à¸­à¸¡à¸¹à¸¥
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def split_data(self, test_draw):
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

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # STEP 3: à¸£à¸±à¸™à¸ªà¸¹à¸•à¸£à¸—à¸±à¹‰à¸‡à¸«à¸¡à¸”
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def run_formulas(self, train_data):
        all_sets = {}
        for fid, formula in self.formula_library.items():
            try:
                sets = self.apply_formula(formula, train_data)
                all_sets[fid] = {"sets": sets, "formula": formula["name"]}
            except Exception as e:
                all_sets[fid] = {"sets": self.generate_random_sets(), "formula": formula["name"], "error": str(e)}
        return all_sets

    def apply_formula(self, formula, train_data):
        t = formula["type"]
        if t == "statistical":
            return self.apply_statistical_formula(formula, train_data)
        elif t == "advanced":
            return self.apply_advanced_formula(formula, train_data)
        elif t == "ml":
            return self.apply_ml_formula(formula, train_data)
        elif t == "genetic":
            return self.apply_genetic_formula(formula, train_data)
        return self.generate_random_sets()

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # STATISTICAL FORMULAS (Phase 1)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def apply_statistical_formula(self, formula, train_data):
        fid = formula["id"]
        p = formula["params"]
        if "freq" in fid:
            return self.freq_formula(train_data, p)
        elif "due" in fid:
            return self.due_formula(train_data, p)
        elif "bayesian" in fid:
            return self.bayesian_formula(train_data, p)
        elif "markov" in fid:
            return self.markov_formula(train_data, p)
        elif "monte_carlo" in fid:
            return self.monte_carlo_formula(train_data, p)
        elif "positional" in fid:
            return self.positional_formula(train_data, p)
        elif "hot_cold" in fid:
            return self.hot_cold_formula(train_data, p)
        elif "pairs" in fid:
            return self.pairs_formula(train_data, p)
        return self.generate_random_sets()

    def freq_formula(self, train_data, p):
        window = p.get("window", 50)
        recent = train_data[-window:]
        freq = Counter(d.get("two_digit", "") for d in recent if d.get("two_digit"))
        top = [n for n, _ in freq.most_common(10)]
        return [f"{random.randint(0, 9999):04d}{top[i]}" if i < len(top) else f"{random.randint(0, 999999):06d}" for i in range(10)]

    def due_formula(self, train_data, p):
        top_n = p.get("top_n", 10)
        last_seen = {}
        for i, d in enumerate(train_data):
            td = d.get("two_digit", "")
            if td:
                last_seen[td] = i
        train_pos = len(train_data)
        due = [(n, train_pos - last_seen.get(n, 0)) for n in [f"{i:02d}" for i in range(10)]]
        due.sort(key=lambda x: -x[1])
        top = [n for n, _ in due[:top_n]]
        return [f"{random.randint(0, 9999):04d}{top[i]}" if i < len(top) else f"{random.randint(0, 999999):06d}" for i in range(10)]

    def bayesian_formula(self, train_data, p):
        window = p.get("window", 100)
        recent = train_data[-window:]
        freq = Counter(d.get("two_digit", "") for d in recent if d.get("two_digit"))
        total = sum(freq.values()) + 100  # Laplace smoothing
        posterior = {f"{i:02d}": (freq.get(f"{i:02d}", 0) + 1) / total for i in range(100)}
        top = sorted(posterior.keys(), key=lambda x: -posterior[x])[:10]
        return [f"{random.randint(0, 9999):04d}{top[i]}" if i < len(top) else f"{random.randint(0, 999999):06d}" for i in range(10)]

    def markov_formula(self, train_data, p):
        order = p.get("order", 1)
        trans = defaultdict(Counter)
        tds = [d.get("two_digit", "") for d in train_data if d.get("two_digit")]
        for i in range(len(tds) - order):
            state = tuple(tds[i:i + order])
            trans[state][tds[i + order]] += 1
        state = tuple(tds[-order:]) if len(tds) >= order else tuple(["00"] * order)
        if state in trans:
            top = [n for n, _ in trans[state].most_common(10)]
        else:
            top = [n for n, _ in Counter(tds[-50:]).most_common(10)]
        return [f"{random.randint(0, 9999):04d}{top[i]}" if i < len(top) else f"{random.randint(0, 999999):06d}" for i in range(10)]

    def monte_carlo_formula(self, train_data, p):
        sims = p.get("simulations", 10000)
        freq = Counter(d.get("two_digit", "") for d in train_data if d.get("two_digit"))
        if not freq:
            return self.generate_random_sets()
        nums, weights = list(freq.keys()), list(freq.values())
        results = Counter(random.choices(nums, weights=weights, k=sims))
        top = [n for n, _ in results.most_common(10)]
        return [f"{random.randint(0, 9999):04d}{top[i]}" if i < len(top) else f"{random.randint(0, 999999):06d}" for i in range(10)]

    def positional_formula(self, train_data, p):
        top_per = p.get("top_per_pos", 3)
        pos_freq = [Counter() for _ in range(6)]
        for d in train_data:
            fp = d.get("first_prize", "")
            if fp and len(fp) == 6:
                for i, ch in enumerate(fp):
                    pos_freq[i][ch] += 1
        pos_top = [sorted(f.keys(), key=lambda x: -f[x])[:top_per] for f in pos_freq]
        sets = []
        for i in range(10):
            num = ""
            for p_idx in range(6):
                if pos_top[p_idx]:
                    num += pos_top[p_idx][i % len(pos_top[p_idx])]
                else:
                    num += str(random.randint(0, 9))
            sets.append(num)
        return sets

    def hot_cold_formula(self, train_data, p):
        hot_w = p.get("hot_window", 20)
        cold_w = p.get("cold_window", 100)
        hot = Counter(d.get("two_digit", "") for d in train_data[-hot_w:] if d.get("two_digit"))
        cold = Counter(d.get("two_digit", "") for d in train_data[-cold_w:] if d.get("two_digit"))
        scores = {}
        for n in [f"{i:02d}" for i in range(100)]:
            h = hot.get(n, 0) / max(hot_w, 1)
            c = cold.get(n, 0) / max(cold_w, 1)
            scores[n] = h - c
        top = sorted(scores.keys(), key=lambda x: -scores[x])[:10]
        return [f"{random.randint(0, 9999):04d}{top[i]}" if i < len(top) else f"{random.randint(0, 999999):06d}" for i in range(10)]

    def pairs_formula(self, train_data, p):
        min_co = p.get("min_cooccurrence", 3)
        cooccur = defaultdict(Counter)
        tds = [d.get("two_digit", "") for d in train_data if d.get("two_digit")]
        for i, td1 in enumerate(tds):
            for td2 in tds[i + 1:i + 20]:
                if td1 != td2:
                    cooccur[td1][td2] += 1
        scores = Counter()
        for n, others in cooccur.items():
            for other, cnt in others.items():
                if cnt >= min_co:
                    scores[n] += cnt
        top = [n for n, _ in scores.most_common(10)]
        if len(top) < 10:
            freq = Counter(tds[-50:])
            for n, _ in freq.most_common(10 - len(top)):
                if n not in top:
                    top.append(n)
        return [f"{random.randint(0, 9999):04d}{top[i]}" if i < len(top) else f"{random.randint(0, 999999):06d}" for i in range(10)]

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ADVANCED FORMULAS (Phase 2)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def apply_advanced_formula(self, formula, train_data):
        fid = formula["id"]
        p = formula["params"]
        if "time_series" in fid:
            return self.time_series_formula(train_data, p)
        elif "sum_diff" in fid:
            return self.sum_diff_formula(train_data, p)
        elif "modular" in fid:
            return self.modular_formula(train_data, p)
        elif "fibonacci" in fid:
            return self.fibonacci_formula(train_data, p)
        elif "chaos" in fid:
            return self.chaos_formula(train_data, p)
        elif "entropy" in fid:
            return self.entropy_formula(train_data, p)
        return self.generate_random_sets()

    def time_series_formula(self, train_data, p):
        """Time Series Patterns â€” à¸§à¸´à¹€à¸„à¸£à¸²à¸°à¸«à¹Œ pattern à¸•à¸²à¸¡à¹€à¸”à¸·à¸­à¸™ + trend"""
        trend_w = p.get("trend_window", 50)

        # à¹à¸¢à¸à¸•à¸²à¸¡à¹€à¸”à¸·à¸­à¸™
        monthly = defaultdict(Counter)
        for d in train_data:
            td = d.get("two_digit", "")
            if td:
                month = d["draw_date"][5:7]
                monthly[month][td] += 1

        current_month = train_data[-1]["draw_date"][5:7] if train_data else "01"
        month_freq = monthly.get(current_month, Counter())

        # Trend: recent vs older
        recent = train_data[-trend_w // 2:]
        older = train_data[-trend_w:-trend_w // 2] if len(train_data) > trend_w // 2 else train_data[:max(1, trend_w // 2)]

        recent_freq = Counter(d.get("two_digit", "") for d in recent if d.get("two_digit"))
        older_freq = Counter(d.get("two_digit", "") for d in older if d.get("two_digit"))

        scores = {}
        for n in [f"{i:02d}" for i in range(100)]:
            ms = month_freq.get(n, 0)
            ts = recent_freq.get(n, 0) - older_freq.get(n, 0)
            scores[n] = ms + ts * 2

        top = sorted(scores.keys(), key=lambda x: -scores[x])[:10]
        return [f"{random.randint(0, 9999):04d}{top[i]}" if i < len(top) else f"{random.randint(0, 999999):06d}" for i in range(10)]

    def sum_diff_formula(self, train_data, p):
        """Sum/Difference Analysis â€” à¸œà¸¥à¸£à¸§à¸¡à¸•à¸±à¸§à¹€à¸¥à¸‚"""
        target = p.get("target_sum", 27)
        tol = p.get("tolerance", 5)

        valid_sums = []
        for d in train_data:
            fp = d.get("first_prize", "")
            if fp and len(fp) == 6 and fp.isdigit():
                valid_sums.append(sum(int(c) for c in fp))

        if not valid_sums:
            return self.generate_random_sets()

        sum_freq = Counter(valid_sums)
        target_sums = [(s, sum_freq[s]) for s in range(target - tol, target + tol + 1) if sum_freq.get(s, 0) > 0]
        target_sums.sort(key=lambda x: -x[1])

        sets = []
        for ts, _ in target_sums[:10]:
            remaining = ts
            digits = []
            for i in range(6):
                if i == 5:
                    d = max(0, min(9, remaining))
                else:
                    avg = remaining // (6 - i)
                    d = max(0, min(9, avg + random.randint(-2, 2)))
                digits.append(str(d))
                remaining -= d
            num = "".join(digits)
            if len(num) == 6:
                sets.append(num)

        while len(sets) < 10:
            sets.append(f"{random.randint(0, 999999):06d}")
        return sets[:10]

    def modular_formula(self, train_data, p):
        """Modular Arithmetic â€” à¸§à¸´à¹€à¸„à¸£à¸²à¸°à¸«à¹Œ modulo"""
        moduli = p.get("moduli", [3, 7, 9])

        residue_freq = {mod: Counter() for mod in moduli}
        for d in train_data:
            td = d.get("two_digit", "")
            if td and td.isdigit():
                num = int(td)
                for mod in moduli:
                    residue_freq[mod][num % mod] += 1

        scores = Counter()
        for num in range(100):
            score = 0
            for mod in moduli:
                r = num % mod
                score += residue_freq[mod].get(r, 0)
            scores[f"{num:02d}"] = score

        top = [n for n, _ in scores.most_common(10)]
        return [f"{random.randint(0, 9999):04d}{top[i]}" if i < len(top) else f"{random.randint(0, 999999):06d}" for i in range(10)]

    def fibonacci_formula(self, train_data, p):
        """Fibonacci/Prime Number Theory"""
        seq = p.get("sequence", "fibonacci")

        fib = [1, 1]
        for _ in range(50):
            fib.append((fib[-1] + fib[-2]) % 100)

        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0:
                    return False
            return True

        primes = [i for i in range(100) if is_prime(i)]

        if seq == "fibonacci":
            sorted_nums = sorted(set(fib), key=lambda x: -fib.count(x))
            pool = fib
        else:
            sorted_nums = sorted(set(primes), key=lambda x: -primes.count(x) if x in primes else 0)
            pool = primes

        # à¹€à¸•à¸´à¸¡à¸ˆà¸²à¸ frequency à¸–à¹‰à¸²à¹„à¸¡à¹ˆà¸„à¸£à¸š
        freq = Counter(d.get("two_digit", "") for d in train_data[-50:] if d.get("two_digit"))
        for n, _ in freq.most_common(20):
            if n not in sorted_nums:
                sorted_nums.append(n)

        top = [f"{int(n):02d}" for n in sorted_nums[:10]]
        return [f"{random.randint(0, 9999):04d}{top[i]}" if i < len(top) else f"{random.randint(0, 999999):06d}" for i in range(10)]

    def chaos_formula(self, train_data, p):
        """Chaos Theory â€” autocorrelation"""
        lookback = p.get("lookback", 20)
        recent = train_data[-lookback:]
        tds = [d.get("two_digit", "") for d in recent if d.get("two_digit")]

        if len(tds) < 5:
            return self.generate_random_sets()

        # Autocorrelation
        autocorr = {}
        for lag in range(1, min(10, len(tds) // 2)):
            matches = sum(1 for i in range(len(tds) - lag) if tds[i] == tds[i + lag])
            autocorr[lag] = matches / (len(tds) - lag)

        best_lag = max(autocorr.keys(), key=lambda x: autocorr[x]) if autocorr else 1
        base = tds[-best_lag] if len(tds) > best_lag else "00"

        sets = []
        for i in range(10):
            digits = list(base.zfill(6))
            for j in range(6):
                if random.random() < 0.3:
                    digits[j] = str(random.randint(0, 9))
            sets.append("".join(digits))
        return sets

    def entropy_formula(self, train_data, p):
        """Entropy Analysis â€” Shannon entropy"""
        window = p.get("window", 50)
        recent = train_data[-window:]

        pos_freq = [Counter() for _ in range(6)]
        for d in recent:
            fp = d.get("first_prize", "")
            if fp and len(fp) == 6:
                for i, ch in enumerate(fp):
                    pos_freq[i][ch] += 1

        pos_entropy = []
        for f in pos_freq:
            total = sum(f.values())
            if total > 0:
                e = -sum((c / total) * math.log2(c / total) for c in f.values() if c > 0)
                pos_entropy.append(e)
            else:
                pos_entropy.append(0)

        sets = []
        for i in range(10):
            num = ""
            for pos in range(6):
                if pos_freq[pos]:
                    best = max(pos_freq[pos].keys(), key=lambda x: pos_freq[pos][x])
                    if random.random() < pos_entropy[pos] / 3.0:
                        best = str(random.randint(0, 9))
                    num += best
                else:
                    num += str(random.randint(0, 9))
            sets.append(num)
        return sets

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ML FORMULAS (Phase 3) â€” à¸žà¸£à¹‰à¸­à¸¡ Hyperparameter Tuning
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def apply_ml_formula(self, formula, train_data):
        fid = formula["id"]
        p = formula["params"]

        # Hyperparameter tuning â€” à¸ªà¸¸à¹ˆà¸¡à¸„à¹ˆà¸²à¹ƒà¸«à¸¡à¹ˆà¹ƒà¸™à¹à¸•à¹ˆà¸¥à¸°à¸£à¸­à¸š
        tuned = dict(p)
        if "rf" in fid:
            tuned["freq_weight"] = random.uniform(0.5, 2.0)
            tuned["gap_weight"] = random.uniform(0.1, 1.0)
            tuned["pos_weight"] = random.uniform(0.1, 0.5)
            top = self._ml_predict(train_data, tuned, "rf")
        elif "xgb" in fid:
            tuned["freq_weight"] = random.uniform(0.8, 2.5)
            tuned["gap_weight"] = random.uniform(0.2, 0.8)
            tuned["pos_weight"] = random.uniform(0.2, 0.6)
            top = self._ml_predict(train_data, tuned, "xgb")
        elif "lstm" in fid:
            tuned["freq_weight"] = random.uniform(0.5, 1.5)
            tuned["gap_weight"] = random.uniform(0.1, 0.5)
            tuned["seq_weight"] = random.uniform(0.1, 0.5)
            top = self._ml_predict(train_data, tuned, "lstm")
        elif "logistic" in fid:
            tuned["freq_weight"] = random.uniform(0.5, 2.0)
            tuned["gap_weight"] = random.uniform(0.1, 1.0)
            top = self._ml_predict(train_data, tuned, "logistic")
        elif "knn" in fid:
            tuned["freq_weight"] = random.uniform(0.5, 2.0)
            tuned["k"] = random.randint(5, 20)
            top = self._ml_predict(train_data, tuned, "knn")
        elif "ensemble" in fid:
            top = self._ml_predict(train_data, tuned, "ensemble")
        else:
            return self.generate_random_sets()

        return [f"{random.randint(0, 9999):04d}{top[i]}" if i < len(top) else f"{random.randint(0, 999999):06d}" for i in range(10)]

    def _ml_predict(self, train_data, params, model_type):
        """ML prediction â€” extract features + score"""
        window = params.get("window", 50)
        recent = train_data[-window:]

        # Frequency
        freq = Counter(d.get("two_digit", "") for d in recent if d.get("two_digit"))

        # Gap
        last_seen = {}
        for i, d in enumerate(train_data):
            td = d.get("two_digit", "")
            if td:
                last_seen[td] = i
        train_pos = len(train_data)

        # Position
        pos_freq = [Counter() for _ in range(6)]
        for d in recent:
            fp = d.get("first_prize", "")
            if fp and len(fp) == 6:
                for p in range(6):
                    pos_freq[p][fp[p]] += 1

        fw = params.get("freq_weight", 1.0)
        gw = params.get("gap_weight", 0.5)
        pw = params.get("pos_weight", 0.3)
        sw = params.get("seq_weight", 0.3)

        scores = {}
        for num in [f"{n:02d}" for n in range(100)]:
            score = 0
            score += freq.get(num, 0) * fw
            score += (train_pos - last_seen.get(num, 0)) * gw

            for p in range(6):
                score += pos_freq[p].get(num[-1], 0) * pw

            # Model-specific
            if model_type == "rf":
                score *= random.uniform(0.8, 1.2)
            elif model_type == "xgb":
                score += freq.get(num, 0) * 0.5
            elif model_type == "lstm":
                seq_score = 0
                for j in range(1, min(4, len(train_data))):
                    seq_score += 1 if train_data[-j].get("two_digit") == num else 0
                score += seq_score * sw
            elif model_type == "logistic":
                score = 1 / (1 + math.exp(-score / 10)) if score != 0 else 0.5
            elif model_type == "knn":
                k = params.get("k", 10)
                knn_score = 0
                for d in train_data[-k:]:
                    if d.get("two_digit") == num:
                        knn_score += 1
                score = knn_score
            elif model_type == "ensemble":
                score += freq.get(num, 0) * 0.5 + (train_pos - last_seen.get(num, 0)) * 0.3

            scores[num] = score

        sorted_nums = sorted(scores.keys(), key=lambda x: -scores[x])
        return sorted_nums[:10]

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # GENETIC FORMULA (Phase 4)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def apply_genetic_formula(self, formula, train_data):
        """à¸ªà¸¹à¸•à¸£à¸—à¸µà¹ˆ Genetic Algorithm à¸ªà¸£à¹‰à¸²à¸‡"""
        parents = formula.get("params", {}).get("parents", [])
        if not parents:
            return self.generate_random_sets()

        # à¸œà¸ªà¸¡à¸ªà¸¹à¸•à¸£à¸ˆà¸²à¸à¸žà¹ˆà¸­à¹à¸¡à¹ˆ
        parent1_train = self.apply_formula(self.formula_library.get(parents[0], {}), train_data) if parents[0] in self.formula_library else self.generate_random_sets()
        parent2_train = self.apply_formula(self.formula_library.get(parents[1], {}), train_data) if parents[1] in self.formula_library else self.generate_random_sets()

        # Crossover: à¸ªà¸¥à¸±à¸šà¹€à¸¥à¸‚à¸£à¸°à¸«à¸§à¹ˆà¸²à¸‡à¸žà¹ˆà¸­à¹à¸¡à¹ˆ
        sets = []
        for i in range(10):
            if i < len(parent1_train) and i < len(parent2_train):
                p1 = parent1_train[i]
                p2 = parent2_train[i]
                # à¸ªà¸¥à¸±à¸šà¸„à¸£à¸¶à¹ˆà¸‡à¹à¸£à¸à¸à¸±à¸šà¸„à¸£à¸¶à¹ˆà¸‡à¸«à¸¥à¸±à¸‡
                if random.random() < 0.5:
                    child = p1[:3] + p2[3:]
                else:
                    child = p2[:3] + p1[3:]

                # Mutation: à¹€à¸›à¸¥à¸µà¹ˆà¸¢à¸™ 1-2 à¸«à¸¥à¸±à¸
                child_digits = list(child)
                for _ in range(random.randint(1, 2)):
                    pos = random.randint(0, 5)
                    child_digits[pos] = str(random.randint(0, 9))
                sets.append("".join(child_digits))
            elif i < len(parent1_train):
                sets.append(parent1_train[i])
            elif i < len(parent2_train):
                sets.append(parent2_train[i])
            else:
                sets.append(f"{random.randint(0, 999999):06d}")

        return sets[:10]

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # STEP 4: EVALUATE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def evaluate(self, all_sets, test_data):
        results = {}
        actual_first = test_data.get("first_prize", "")
        actual_two = test_data.get("two_digit", "")
        actual_3last = test_data.get("three_digit_last", [])
        actual_3first = test_data.get("three_digit_first", [])
        actual_nearby = test_data.get("nearby_1st", [])
        actual_p2 = test_data.get("second_prize", [])
        actual_p3 = test_data.get("third_prize", [])
        actual_p4 = test_data.get("prize_4", [])
        actual_p5 = test_data.get("prize_5", [])

        for fid, data in all_sets.items():
            score = 0
            hits = {k: 0 for k in SCORING.keys() if k != "base_per_set"}

            for num in data["sets"]:
                if num == actual_first:
                    score += SCORING["à¸£à¸²à¸‡à¸§à¸±à¸¥à¸—à¸µà¹ˆ 1"]
                    hits["à¸£à¸²à¸‡à¸§à¸±à¸¥à¸—à¸µà¹ˆ 1"] += 1
                if num in actual_nearby:
                    score += SCORING["à¸‚à¹‰à¸²à¸‡à¹€à¸„à¸µà¸¢à¸‡"]
                    hits["à¸‚à¹‰à¸²à¸‡à¹€à¸„à¸µà¸¢à¸‡"] += 1
                if num in actual_p2:
                    score += SCORING["à¸£à¸²à¸‡à¸§à¸±à¸¥à¸—à¸µà¹ˆ 2"]
                    hits["à¸£à¸²à¸‡à¸§à¸±à¸¥à¸—à¸µà¹ˆ 2"] += 1
                if num in actual_p3:
                    score += SCORING["à¸£à¸²à¸‡à¸§à¸±à¸¥à¸—à¸µà¹ˆ 3"]
                    hits["à¸£à¸²à¸‡à¸§à¸±à¸¥à¸—à¸µà¹ˆ 3"] += 1
                if num in actual_p4:
                    score += SCORING["à¸£à¸²à¸‡à¸§à¸±à¸¥à¸—à¸µà¹ˆ 4"]
                    hits["à¸£à¸²à¸‡à¸§à¸±à¸¥à¸—à¸µà¹ˆ 4"] += 1
                if num in actual_p5:
                    score += SCORING["à¸£à¸²à¸‡à¸§à¸±à¸¥à¸—à¸µà¹ˆ 5"]
                    hits["à¸£à¸²à¸‡à¸§à¸±à¸¥à¸—à¸µà¹ˆ 5"] += 1
                if num[-3:] in actual_3last:
                    score += SCORING["à¹€à¸¥à¸‚à¸—à¹‰à¸²à¸¢ 3"]
                    hits["à¹€à¸¥à¸‚à¸—à¹‰à¸²à¸¢ 3"] += 1
                if num[:3] in actual_3first:
                    score += SCORING["à¹€à¸¥à¸‚à¸«à¸™à¹‰à¸² 3"]
                    hits["à¹€à¸¥à¸‚à¸«à¸™à¹‰à¸² 3"] += 1
                if num[-2:] == actual_two:
                    score += SCORING["à¹€à¸¥à¸‚à¸—à¹‰à¸²à¸¢ 2"]
                    hits["à¹€à¸¥à¸‚à¸—à¹‰à¸²à¸¢ 2"] += 1

                if any(v > 0 for v in hits.values()):
                    score += SCORING["base_per_set"]

            results[fid] = {"formula": data["formula"], "sets": data["sets"], "score": score, "hits": hits}

        return results

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # STEP 5: SAVE RESULTS
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def save_results(self, results, test_draw):
        best_f = max(results.keys(), key=lambda k: results[k]["score"])
        worst_f = min(results.keys(), key=lambda k: results[k]["score"])
        best_s = results[best_f]["score"]
        worst_s = results[worst_f]["score"]
        avg_s = sum(r["score"] for r in results.values()) / len(results)

        # à¸”à¸¶à¸‡ sets à¸‚à¸­à¸‡à¸ªà¸¹à¸•à¸£à¸—à¸µà¹ˆà¸”à¸µà¸—à¸µà¹ˆà¸ªà¸¸à¸”
        best_sets = results[best_f].get("sets", [])

        iteration_result = {
            "iteration": self.iteration,
            "test_draw": test_draw["draw_date"],
            "timestamp": datetime.now().isoformat(),
            "results": {k: {"formula": v["formula"], "score": v["score"], "hits": v["hits"]} for k, v in results.items()},
            "best_formula": best_f,
            "best_score": best_s,
            "best_sets": best_sets,
            "worst_formula": worst_f,
            "worst_score": worst_s,
            "avg_score": avg_s
        }

        self.results_db["iterations"].append(iteration_result)

        if best_s > self.best_score_ever:
            self.best_score_ever = best_s
            self.no_improvement_count = 0
            print(f"  NEW BEST: {best_s}")
        else:
            self.no_improvement_count += 1

        # Atomic Save: write to temp file first, then replace
        temp_path = self.config["RESULTS_FILE"] + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(self.results_db, f, ensure_ascii=False, indent=2)
        os.replace(temp_path, self.config["RESULTS_FILE"])

        print(f"  Best: {best_f} = {best_s}")
        print(f"  Worst: {worst_f} = {worst_s}")
        print(f"  Avg: {avg_s:.1f}")
        print(f"  No improvement: {self.no_improvement_count}")

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # STEP 6: GENETIC ALGORITHM
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def evolve_formulas(self, results):
        sorted_f = sorted(results.keys(), key=lambda k: -results[k]["score"])
        n_elite = max(2, int(len(sorted_f) * self.config["ELITE_RATIO"]))
        elite = sorted_f[:n_elite]
        bottom = sorted_f[-n_elite:]

        print(f"  Elite: {len(elite)}, Prune: {len(bottom)}")

        # à¸„à¸±à¸”à¸—à¸´à¹‰à¸‡à¸ªà¸¹à¸•à¸£à¹à¸¢à¹ˆ
        for fid in bottom:
            if fid in self.formula_library and not fid.startswith("freq_v1"):  # à¹€à¸à¹‡à¸š freq_v1 à¹„à¸§à¹‰à¹€à¸ªà¸¡à¸­
                del self.formula_library[fid]

        # à¸ªà¸£à¹‰à¸²à¸‡à¸ªà¸¹à¸•à¸£à¹ƒà¸«à¸¡à¹ˆ (crossover + mutation)
        for _ in range(len(bottom)):
            p1 = random.choice(elite)
            p2 = random.choice(elite)
            new_id = f"gen_g{self.iteration}_{random.randint(1000, 9999)}"

            # Crossover params
            p1_params = self.formula_library.get(p1, {}).get("params", {})
            p2_params = self.formula_library.get(p2, {}).get("params", {})
            mixed = {}
            for k in set(list(p1_params.keys()) + list(p2_params.keys())):
                if random.random() < 0.5:
                    mixed[k] = p1_params.get(k, p2_params.get(k))
                else:
                    mixed[k] = p2_params.get(k, p1_params.get(k))

            # Mutation 10%
            for k in mixed:
                if random.random() < self.config["MUTATION_RATE"]:
                    if isinstance(mixed[k], int):
                        mixed[k] = random.randint(1, 100)
                    elif isinstance(mixed[k], float):
                        mixed[k] = random.uniform(0.01, 1.0)

            self.formula_library[new_id] = {
                "name": f"Gen({p1[:6]}x{p2[:6]})",
                "phase": 4, "type": "genetic",
                "params": {"parents": [p1, p2], **mixed},
                "created": datetime.now().isoformat(),
                "generation": self.iteration,
                "avg_score": 0, "total_rounds": 0
            }

        with open(self.config["FORMULA_LIB"], "w", encoding="utf-8") as f:
            json.dump(self.formula_library, f, ensure_ascii=False, indent=2)

        print(f"  Library: {len(self.formula_library)} formulas")

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # SMART EARLY STOPPING
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def check_early_stop(self):
        """à¸•à¸£à¸§à¸ˆà¸ªà¸­à¸šà¸§à¹ˆà¸²à¸„à¸§à¸£à¸«à¸¢à¸¸à¸”à¸£à¸±à¸™à¸à¹ˆà¸­à¸™à¸«à¸£à¸·à¸­à¹„à¸¡à¹ˆ"""
        if len(self.results_db["iterations"]) < self.config["EARLY_STOP_CHECK_INTERVAL"]:
            return False

        # à¸„à¸³à¸™à¸§à¸“ average score à¸‚à¸­à¸‡ elite group à¹ƒà¸™ N à¸£à¸­à¸šà¸¥à¹ˆà¸²à¸ªà¸¸à¸”
        recent = self.results_db["iterations"][-self.config["EARLY_STOP_CHECK_INTERVAL"]:]

        elite_scores = []
        for it in recent:
            sorted_f = sorted(it["results"].keys(), key=lambda k: -it["results"][k]["score"])
            n_elite = max(2, int(len(sorted_f) * self.config["ELITE_RATIO"]))
            elite = sorted_f[:n_elite]
            for fid in elite:
                elite_scores.append(it["results"][fid]["score"])

        if not elite_scores:
            return False

        elite_avg = sum(elite_scores) / len(elite_scores)
        baseline = self.config["RANDOM_BASELINE_SCORE"]

        print(f"  ðŸ“Š Elite avg score (last {self.config['EARLY_STOP_CHECK_INTERVAL']} rounds): {elite_avg:.1f}")
        print(f"     Baseline: {baseline:.1f}")
        print(f"     Ratio: {elite_avg / max(baseline, 0.01):.2f}x")

        if elite_avg < baseline:
            print(f"  Elite avg ({elite_avg:.1f}) < baseline ({baseline:.1f})")
            return True

        return False

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # CONVERGENCE CHECK
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def check_convergence(self):
        if self.no_improvement_count >= self.config["CONVERGENCE_THRESHOLD"]:
            return True
        if len(self.results_db["iterations"]) >= 20:
            recent = [r["best_score"] for r in self.results_db["iterations"][-20:]]
            if max(recent) == min(recent):
                return True
        return False

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # FINAL REPORT
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def print_final_report(self):
        print("\n" + "=" * 60)
        print("  ðŸ“Š FINAL REPORT")
        print("=" * 60)

        formula_avg = {}
        for it in self.results_db["iterations"]:
            for fid, r in it["results"].items():
                if fid not in formula_avg:
                    formula_avg[fid] = []
                formula_avg[fid].append(r["score"])

        for fid in formula_avg:
            formula_avg[fid] = sum(formula_avg[fid]) / len(formula_avg[fid])

        sorted_f = sorted(formula_avg.keys(), key=lambda k: -formula_avg[k])

        print(f"\n  Total iterations: {len(self.results_db['iterations'])}")
        print(f"  Best score ever: {self.best_score_ever}")
        print(f"  Final library: {len(self.formula_library)} formulas")

        print(f"\n  TOP 10:")
        for i, fid in enumerate(sorted_f[:10]):
            name = self.formula_library.get(fid, {}).get("name", fid)
            print(f"    {i+1}. {name}: {formula_avg[fid]:.1f}")

        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        # THE CHOSEN 10 SETS
        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        
        # à¸«à¸²à¸ªà¸¹à¸•à¸£à¸—à¸µà¹ˆà¸”à¸µà¸—à¸µà¹ˆà¸ªà¸¸à¸”à¸ˆà¸²à¸à¸—à¸¸à¸ iteration
        best_overall_fid = sorted_f[0] if sorted_f else None
        
        # à¹€à¸à¹‡à¸š sets à¸ˆà¸²à¸à¸—à¸¸à¸ iteration à¸‚à¸­à¸‡à¸ªà¸¹à¸•à¸£à¸—à¸µà¹ˆà¸”à¸µà¸—à¸µà¹ˆà¸ªà¸¸à¸”
        all_chosen_sets = []
        for it in self.results_db["iterations"]:
            if best_overall_fid in it["results"]:
                sets = it.get("best_sets", [])
                if sets:
                    all_chosen_sets.extend(sets)
        
        # à¸–à¹‰à¸²à¸¡à¸µ sets â€” à¹€à¸¥à¸·à¸­à¸ 10 à¸Šà¸¸à¸”à¸ªà¸¸à¸”à¸—à¹‰à¸²à¸¢ (à¸ˆà¸²à¸ iteration à¸¥à¹ˆà¸²à¸ªà¸¸à¸”)
        chosen_10 = []
        if all_chosen_sets:
            # à¹€à¸­à¸² 10 à¸Šà¸¸à¸”à¸ªà¸¸à¸”à¸—à¹‰à¸²à¸¢
            chosen_10 = all_chosen_sets[-10:]
        elif best_overall_fid and best_overall_fid in self.formula_library:
            # Fallback: à¸ªà¸£à¹‰à¸²à¸‡ sets à¸ˆà¸²à¸à¸ªà¸¹à¸•à¸£à¸—à¸µà¹ˆà¸”à¸µà¸—à¸µà¹ˆà¸ªà¸¸à¸”
            formula = self.formula_library[best_overall_fid]
            try:
                chosen_10 = self.apply_formula(formula, self.data[-100:])
            except:
                chosen_10 = [f"{random.randint(0, 999999):06d}" for _ in range(10)]

        print(f"\n  THE CHOSEN 10 SETS (from: {best_overall_fid}):")
        for i, s in enumerate(chosen_10, 1):
            formatted = f"{s[:3]}-{s[3:]}" if len(s) == 6 else s
            print(f"    {i:2d}. {formatted}")

        report = {
            "generated": datetime.now().isoformat(),
            "total_iterations": len(self.results_db["iterations"]),
            "best_score_ever": self.best_score_ever,
            "final_formula_count": len(self.formula_library),
            "top_10": [{"id": fid, "name": self.formula_library.get(fid, {}).get("name", fid), "avg_score": formula_avg[fid]} for fid in sorted_f[:10]],
            "the_chosen_10_sets": chosen_10,
            "best_formula_id": best_overall_fid,
            "best_formula_name": self.formula_library.get(best_overall_fid, {}).get("name", "N/A"),
        }

        path = os.path.join(self.config["REPORT_DIR"], "final_report.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n  Report: {path}")

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # UTILITY
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def generate_random_sets(self):
        return [f"{random.randint(0, 999999):06d}" for _ in range(10)]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ENTRY POINT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

if __name__ == "__main__":
    controller = LottoAIController(CONFIG)
    controller.run()
