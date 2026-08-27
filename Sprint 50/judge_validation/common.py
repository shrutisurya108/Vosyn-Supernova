"""
Shared helpers used across the gold-set builders, judge runner, and aggregator.
Pure standard library only (no numpy/pandas/scipy) so it runs on a bare
Python 3.14 install with nothing pre-installed.
"""

import json
import math
import random

from config import SEVERITY_WEIGHTS


def read_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def human_mqm_score(spans, weights=None):
    """
    Deterministic, code-computed (never LLM-computed) gold score from a list of
    error spans, each with an 'error_severity' key ('Minor'/'Major'/'Critical').
    100 = perfect, penalties subtract, floor at 0.
    """
    weights = weights or SEVERITY_WEIGHTS
    penalty = 0
    for s in spans:
        sev = (s.get("error_severity") or "minor").strip().lower()
        penalty += weights.get(sev, 1)
    return max(0, 100 - penalty)


def bucket_of(score, buckets):
    for lo, hi, name in buckets:
        if lo <= score < hi:
            return name
    return buckets[-1][2]


def stratified_sample(rows, score_fn, n_target, seed=42, n_bins=4):
    """
    Sample n_target rows spread across the human-score range instead of picking
    randomly (which for Cantonese would give you almost nothing but 'bad'
    sentences, and for clean corpora could give you almost nothing but 'perfect'
    ones). Buckets scores into n_bins equal-width bins across the observed
    range and draws as evenly as possible from each bin.
    """
    rng = random.Random(seed)
    scored = [(score_fn(r), r) for r in rows]
    lo = min(s for s, _ in scored)
    hi = max(s for s, _ in scored)
    if hi == lo:
        hi = lo + 1
    width = (hi - lo) / n_bins

    bins = [[] for _ in range(n_bins)]
    for s, r in scored:
        idx = min(n_bins - 1, int((s - lo) / width))
        bins[idx].append(r)

    for b in bins:
        rng.shuffle(b)

    per_bin = max(1, n_target // n_bins)
    picked = []
    for b in bins:
        picked.extend(b[:per_bin])

    # top up / trim to hit the exact target, pulling extras from whichever
    # bins still have spare rows
    if len(picked) < n_target:
        leftovers = []
        for b in bins:
            leftovers.extend(b[per_bin:])
        rng.shuffle(leftovers)
        picked.extend(leftovers[: n_target - len(picked)])
    picked = picked[:n_target]
    rng.shuffle(picked)
    return picked


# ---------- pure-stdlib statistics (no scipy/numpy needed) ----------

def mean(xs):
    return sum(xs) / len(xs)


def pearson_r(xs, ys):
    n = len(xs)
    if n < 2:
        return float("nan")
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    deny = math.sqrt(sum((y - my) ** 2 for y in ys))
    if denx == 0 or deny == 0:
        return float("nan")
    return num / (denx * deny)


def _rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg_rank = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    return ranks


def spearman_rho(xs, ys):
    if len(xs) < 2:
        return float("nan")
    rx, ry = _rank(xs), _rank(ys)
    return pearson_r(rx, ry)


def mae(xs, ys):
    return mean([abs(x - y) for x, y in zip(xs, ys)])
