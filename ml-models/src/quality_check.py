import json, re, sys
from datetime import datetime, timedelta
from collections import defaultdict

INPUT = r"D:\lotto-ai\ml-models\data\scraped_all.json"
OUTPUT = r"D:\lotto-ai\ml-models\data\data_quality_report.json"

with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

total = len(data)
report_lines = []

def log(s=""):
    report_lines.append(s)
    print(s)

log("=" * 60)
log("DATA QUALITY ANALYSIS REPORT")
log("=" * 60)

# 1. Basic stats
log(f"\n1. TOTAL DRAWS: {total}")
log(f"   Expected: 776+ draws (1990-2026)")

# 2. Date range
dates = [d["draw_date"] for d in data]
log(f"\n2. DATE RANGE:")
log(f"   First: {dates[0]}")
log(f"   Last:  {dates[-1]}")

# 3. Check duplicates
date_counts = defaultdict(int)
for d in data:
    date_counts[d["draw_date"]] += 1
dupes = {k: v for k, v in date_counts.items() if v > 1}
log(f"\n3. DUPLICATE DATES: {len(dupes)}")
if dupes:
    for d, c in sorted(dupes.items()):
        log(f"   WARNING: {d} appears {c} times")

# 4. Gap detection
log(f"\n4. GAP DETECTION:")
all_dates = sorted(dates)
gaps = []
for i in range(len(all_dates) - 1):
    d1 = datetime.strptime(all_dates[i], "%Y-%m-%d")
    d2 = datetime.strptime(all_dates[i + 1], "%Y-%m-%d")
    diff = (d2 - d1).days
    if diff > 33:
        gaps.append((all_dates[i], all_dates[i + 1], diff))
log(f"   Large gaps (>33 days): {len(gaps)}")
for g in gaps[:20]:
    log(f"   GAP: {g[0]} -> {g[1]} ({g[2]} days)")
if len(gaps) > 20:
    log(f"   ... and {len(gaps) - 20} more gaps")

# 5-6. Field validation and completeness
log(f"\n5. FIELD VALIDATION:")

mandatory_fields = [
    "first_prize", "two_digit", "three_digit_last",
    "three_digit_first", "nearby_1st", "second_prize",
    "third_prize", "prize_4", "prize_5"
]

field_stats = {}
format_issues = defaultdict(list)

for draw in data:
    dd = draw.get("draw_date", "")

    # first_prize: exactly 6 digits or empty
    fp = draw.get("first_prize", "")
    if fp:
        if "first_prize" not in field_stats:
            field_stats["first_prize"] = {"filled": 0}
        field_stats["first_prize"]["filled"] += 1
        if not re.match(r"^\d{6}$", str(fp)):
            format_issues["first_prize"].append({"date": dd, "value": fp, "reason": "invalid format"})
    else:
        if "first_prize" not in field_stats:
            field_stats["first_prize"] = {"filled": 0}

    # two_digit: exactly 2 digits or empty
    td = draw.get("two_digit", "")
    if td:
        if "two_digit" not in field_stats:
            field_stats["two_digit"] = {"filled": 0}
        field_stats["two_digit"]["filled"] += 1
        if not re.match(r"^\d{2}$", str(td)):
            format_issues["two_digit"].append({"date": dd, "value": td, "reason": "invalid format"})
    else:
        if "two_digit" not in field_stats:
            field_stats["two_digit"] = {"filled": 0}

    # three_digit_last: array of 2-4 three-digit strings
    tdl = draw.get("three_digit_last", [])
    if tdl:
        if "three_digit_last" not in field_stats:
            field_stats["three_digit_last"] = {"filled": 0}
        field_stats["three_digit_last"]["filled"] += 1
        bad = [x for x in tdl if not re.match(r"^\d{3}$", str(x))]
        if bad:
            format_issues["three_digit_last"].append({"date": dd, "value": bad, "reason": "invalid items"})
    else:
        if "three_digit_last" not in field_stats:
            field_stats["three_digit_last"] = {"filled": 0}

    # three_digit_first
    tdf = draw.get("three_digit_first", [])
    if tdf:
        if "three_digit_first" not in field_stats:
            field_stats["three_digit_first"] = {"filled": 0}
        field_stats["three_digit_first"]["filled"] += 1
        bad = [x for x in tdf if not re.match(r"^\d{3}$", str(x))]
        if bad:
            format_issues["three_digit_first"].append({"date": dd, "value": bad, "reason": "invalid items"})
    else:
        if "three_digit_first" not in field_stats:
            field_stats["three_digit_first"] = {"filled": 0}

    # nearby_1st: 0-2 six-digit strings
    n1 = draw.get("nearby_1st", [])
    if n1:
        if "nearby_1st" not in field_stats:
            field_stats["nearby_1st"] = {"filled": 0}
        field_stats["nearby_1st"]["filled"] += 1
        bad = [x for x in n1 if not re.match(r"^\d{6}$", str(x))]
        if bad:
            format_issues["nearby_1st"].append({"date": dd, "value": bad, "reason": "invalid items"})
    else:
        if "nearby_1st" not in field_stats:
            field_stats["nearby_1st"] = {"filled": 0}

    # second_prize
    sp = draw.get("second_prize", [])
    if sp:
        if "second_prize" not in field_stats:
            field_stats["second_prize"] = {"filled": 0}
        field_stats["second_prize"]["filled"] += 1
        bad = [x for x in sp if not re.match(r"^\d{6}$", str(x))]
        if bad:
            format_issues["second_prize"].append({"date": dd, "value": bad, "reason": "invalid items"})
    else:
        if "second_prize" not in field_stats:
            field_stats["second_prize"] = {"filled": 0}

    # third_prize
    tp = draw.get("third_prize", [])
    if tp:
        if "third_prize" not in field_stats:
            field_stats["third_prize"] = {"filled": 0}
        field_stats["third_prize"]["filled"] += 1
        bad = [x for x in tp if not re.match(r"^\d{6}$", str(x))]
        if bad:
            format_issues["third_prize"].append({"date": dd, "value": bad, "reason": "invalid items"})
    else:
        if "third_prize" not in field_stats:
            field_stats["third_prize"] = {"filled": 0}

    # prize_4
    p4 = draw.get("prize_4", [])
    if p4:
        if "prize_4" not in field_stats:
            field_stats["prize_4"] = {"filled": 0}
        field_stats["prize_4"]["filled"] += 1
        bad = [x for x in p4 if not re.match(r"^\d{6}$", str(x))]
        if bad:
            format_issues["prize_4"].append({"date": dd, "value": bad, "reason": "invalid items"})
    else:
        if "prize_4" not in field_stats:
            field_stats["prize_4"] = {"filled": 0}

    # prize_5
    p5 = draw.get("prize_5", [])
    if p5:
        if "prize_5" not in field_stats:
            field_stats["prize_5"] = {"filled": 0}
        field_stats["prize_5"]["filled"] += 1
        bad = [x for x in p5 if not re.match(r"^\d{6}$", str(x))]
        if bad:
            format_issues["prize_5"].append({"date": dd, "value": bad, "reason": "invalid items"})
    else:
        if "prize_5" not in field_stats:
            field_stats["prize_5"] = {"filled": 0}

log(f"\n6. FIELD COMPLETENESS:")
field_completeness = {}
for field in mandatory_fields:
    stats = field_stats.get(field, {"filled": 0})
    filled = stats["filled"]
    pct = (filled / total) * 100
    field_completeness[field] = round(pct, 1)
    log(f"   {field}: {filled}/{total} ({pct:.1f}%)")

log(f"\n7. FORMAT ISSUES:")
for field in mandatory_fields:
    issues = format_issues.get(field, [])
    log(f"   {field}: {len(issues)} issues")
    for issue in issues[:5]:
        val = str(issue["value"])[:100]
        log(f"      {issue['date']}: {val} ({issue['reason']})")
    if len(issues) > 5:
        log(f"      ... and {len(issues) - 5} more")

# 8. Completeness scoring
log(f"\n8. COMPLETENESS SCORING:")
weights = {
    "first_prize": 0.25,
    "two_digit": 0.15,
    "three_digit_last": 0.15,
    "three_digit_first": 0.10,
    "nearby_1st": 0.10,
    "second_prize": 0.10,
    "third_prize": 0.05,
    "prize_4": 0.05,
    "prize_5": 0.05,
}
scores = []
for draw in data:
    score = 0
    if draw.get("first_prize"):
        score += 0.25
    if draw.get("two_digit"):
        score += 0.15
    if draw.get("three_digit_last"):
        score += 0.15
    if draw.get("three_digit_first"):
        score += 0.10
    if draw.get("nearby_1st"):
        score += 0.10
    if draw.get("second_prize"):
        score += 0.10
    if draw.get("third_prize"):
        score += 0.05
    if draw.get("prize_4"):
        score += 0.05
    if draw.get("prize_5"):
        score += 0.05
    scores.append(score)

avg_score = sum(scores) / len(scores) * 100
min_score = min(scores) * 100
max_score = max(scores) * 100
low_comp_draws = [
    {"date": data[i]["draw_date"], "score": round(s * 100, 1)}
    for i, s in enumerate(scores)
    if s < 0.5
]

log(f"   Average completeness: {avg_score:.1f}%")
log(f"   Min completeness: {min_score:.1f}%")
log(f"   Max completeness: {max_score:.1f}%")
log(f"   Draws with <50% completeness: {len(low_comp_draws)}")
for lc in low_comp_draws[:10]:
    draw = next(d for d in data if d["draw_date"] == lc["date"])
    filled_fields = [k for k in mandatory_fields if draw.get(k)]
    empty_fields = [k for k in mandatory_fields if not draw.get(k)]
    log(f"      {lc['date']}: {lc['score']:.0f}% - empty: {', '.join(empty_fields[:5])}")

# 9. Array size validation
log(f"\n9. ARRAY SIZE VALIDATION:")
array_limits = {
    "nearby_1st": 2,
    "second_prize": 5,
    "third_prize": 10,
    "prize_4": 50,
    "prize_5": 100,
}
for field, limit in array_limits.items():
    exceed = [
        {"date": d["draw_date"], "size": len(d.get(field, []))}
        for d in data
        if len(d.get(field, [])) > limit
    ]
    log(f"   {field} (max {limit}): {len(exceed)} draws exceed limit")
    for e in exceed[:3]:
        log(f"      {e['date']}: {e['size']} items")
    if len(exceed) > 3:
        log(f"      ... and {len(exceed) - 3} more")

# 10. Outlier detection
log(f"\n10. OUTLIER DETECTION:")
outliers = []
for draw in data:
    dd = draw.get("draw_date", "")
    fp = draw.get("first_prize", "")
    td = draw.get("two_digit", "")

    if fp and not re.match(r"^\d{6}$", str(fp)):
        outliers.append({"date": dd, "field": "first_prize", "value": str(fp), "reason": "not 6 digits"})
    if td and not re.match(r"^\d{2}$", str(td)):
        outliers.append({"date": dd, "field": "two_digit", "value": str(td), "reason": "not 2 digits"})

log(f"   Total outliers detected: {len(outliers)}")
for o in outliers[:10]:
    log(f"      {o['date']} | {o['field']}: '{o['value']}' ({o['reason']})")
if len(outliers) > 10:
    log(f"      ... and {len(outliers) - 10} more")

# Build JSON report
json_report = {
    "report_date": datetime.now().strftime("%Y-%m-%d"),
    "total_draws": total,
    "expected_draws": "776+ (1990-2026)",
    "date_range": {"first": dates[0], "last": dates[-1]},
    "completeness_avg": round(avg_score, 1),
    "completeness_min": round(min_score, 1),
    "completeness_max": round(max_score, 1),
    "duplicates_found": len(dupes),
    "duplicate_dates": [{"date": d, "count": c} for d, c in sorted(dupes.items())],
    "gaps_found": len(gaps),
    "gaps": [{"from": g[0], "to": g[1], "days": g[2]} for g in gaps],
    "field_completeness": field_completeness,
    "low_completeness_draws": low_comp_draws[:25],
    "outliers": outliers[:25],
    "format_issues": {
        field: [{"date": i["date"], "reason": i["reason"]} for i in issues[:10]]
        for field, issues in format_issues.items()
    },
    "array_size_violations": {
        field: len([d for d in data if len(d.get(field, [])) > limit])
        for field, limit in array_limits.items()
    },
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(json_report, f, ensure_ascii=False, indent=2)

log(f"\n{'=' * 60}")
log(f"REPORT SAVED TO: {OUTPUT}")
log(f"{'=' * 60}")

# Save text log too
LOG_OUTPUT = r"D:\lotto-ai\ml-models\data\data_quality_report.txt"
with open(LOG_OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))
log(f"TEXT LOG SAVED TO: {LOG_OUTPUT}")
