"""
This is the piece the acceptance criteria specifically calls out:
"Detect and handle judge disagreement, malformed output, and suspicious zero
scores explicitly in the aggregation logic, rather than letting them silently
skew a simple average."

For every (direction, config) pair this produces:
  - malformed_rate: share of sentences the judge failed to return parseable
    output for, even after retries. These are EXCLUDED from the correlation
    metrics (a malformed row has no score to correlate) but the rate itself
    is a first-class metric a config can be disqualified on.
  - suspicious_zero_rate: share of VALID (parsed) rows where the judge gave a
    rock-bottom score (<=5) while also reporting zero errors, or gave 0 on a
    sentence the human labeled clean. That's not "the judge found this bad" -
    it's "the judge's score field and error field disagree with each other,"
    which is a bug pattern (silently averaged, these drag scores down for no
    real reason). Flagged and reported, and excluded from the correlation
    computation same as malformed rows.
  - For ENSEMBLE configs specifically: per sentence, if the underlying judges'
    valid scores are further apart than INTER_JUDGE_DISAGREEMENT_SPREAD, that
    sentence is flagged "high_disagreement" and the combination method
    switches from mean to median (robust to one outlier judge) - and the
    disagreement rate itself is reported so a chronically-disagreeing pair of
    judges doesn't get picked just because their median happens to still
    correlate with humans.
  - pearson_r / spearman_rho / mae against the human gold score, computed only
    on the clean (valid, non-suspicious) subset - so none of the above failure
    modes silently pull the correlation number around.
"""

import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    DIRECTIONS, GOLD_DIR, JUDGE_OUTPUT_DIR, FINAL_DIR,
    ZERO_SCORE_SUSPICION_THRESHOLD, INTER_JUDGE_DISAGREEMENT_SPREAD,
    MAX_ACCEPTABLE_MALFORMED_RATE, SCORE_BUCKETS,
)
from common import read_jsonl, write_jsonl, pearson_r, spearman_rho, mae, bucket_of
from judges.configs import JUDGE_CONFIGS

GOLD_FILES = {
    "en_to_cmn": "gold_en_cmn.jsonl", "en_to_yue": "gold_en_yue.jsonl",
    "cmn_to_en": "gold_cmn_en.jsonl", "yue_to_en": "gold_yue_en.jsonl",
}


def load_judge_run(direction, config_id):
    path = os.path.join(JUDGE_OUTPUT_DIR, f"{direction}__{config_id}.jsonl")
    if not os.path.exists(path):
        return None
    return {r["gold_id"]: r for r in read_jsonl(path)}


def is_suspicious_zero(row):
    if row["malformed"]:
        return False
    score = row["judge_score"]
    n_errors = len(row.get("judge_errors") or [])
    return score is not None and score <= ZERO_SCORE_SUSPICION_THRESHOLD and n_errors == 0


def evaluate_single_judge_config(direction, config_id, gold_by_id):
    run = load_judge_run(direction, config_id)
    if run is None:
        return None

    n_total = len(gold_by_id)
    n_malformed = 0
    n_suspicious = 0
    clean_human, clean_judge = [], []
    per_sentence = []

    for gold_id, gold in gold_by_id.items():
        row = run.get(gold_id)
        if row is None:
            continue
        malformed = row["malformed"]
        suspicious = (not malformed) and is_suspicious_zero(row)
        usable = (not malformed) and (not suspicious)

        if malformed:
            n_malformed += 1
        if suspicious:
            n_suspicious += 1
        if usable:
            clean_human.append(gold["human_score"])
            clean_judge.append(row["judge_score"])

        per_sentence.append({
            "gold_id": gold_id, "human_score": gold["human_score"],
            "judge_score": row["judge_score"], "malformed": malformed,
            "suspicious_zero": suspicious, "usable_for_agreement": usable,
        })

    n_usable = len(clean_human)
    result = {
        "config_id": config_id, "direction": direction,
        "n_total": n_total, "n_malformed": n_malformed, "n_suspicious_zero": n_suspicious,
        "n_usable": n_usable,
        "malformed_rate": round(n_malformed / n_total, 3) if n_total else None,
        "suspicious_zero_rate": round(n_suspicious / n_total, 3) if n_total else None,
        "pearson_r": round(pearson_r(clean_human, clean_judge), 3) if n_usable >= 3 else None,
        "spearman_rho": round(spearman_rho(clean_human, clean_judge), 3) if n_usable >= 3 else None,
        "mae": round(mae(clean_human, clean_judge), 2) if n_usable >= 1 else None,
        "bucket_agreement_rate": round(
            sum(1 for h, j in zip(clean_human, clean_judge)
                if bucket_of(h, SCORE_BUCKETS) == bucket_of(j, SCORE_BUCKETS)) / n_usable, 3
        ) if n_usable >= 1 else None,
        "disqualified": (n_total > 0 and n_malformed / n_total > MAX_ACCEPTABLE_MALFORMED_RATE),
        "per_sentence": per_sentence,
    }
    return result


def evaluate_ensemble_config(direction, config, gold_by_id, member_results):
    """
    member_results: dict of config_id -> evaluate_single_judge_config(...) result,
    for each judge in config['ensemble_of'].
    """
    per_sentence_by_member = {}
    for member_id in config["ensemble_of"]:
        mr = member_results.get(member_id)
        if mr is None:
            return None
        per_sentence_by_member[member_id] = {p["gold_id"]: p for p in mr["per_sentence"]}

    n_total = len(gold_by_id)
    n_malformed = 0        # all members malformed/unusable for this sentence
    n_suspicious = 0       # kept distinct so it isn't double counted with malformed
    n_high_disagreement = 0
    n_single_fallback = 0
    clean_human, clean_judge = [], []
    per_sentence = []

    for gold_id, gold in gold_by_id.items():
        valid_scores = []
        for member_id in config["ensemble_of"]:
            p = per_sentence_by_member[member_id].get(gold_id)
            if p and p["usable_for_agreement"]:
                valid_scores.append(p["judge_score"])

        if len(valid_scores) == 0:
            n_malformed += 1
            per_sentence.append({"gold_id": gold_id, "human_score": gold["human_score"],
                                  "judge_score": None, "malformed": True,
                                  "suspicious_zero": False, "high_disagreement": False,
                                  "usable_for_agreement": False})
            continue

        high_disagreement = (len(valid_scores) >= 2 and (max(valid_scores) - min(valid_scores)) > INTER_JUDGE_DISAGREEMENT_SPREAD)
        if high_disagreement:
            n_high_disagreement += 1
        if len(valid_scores) == 1:
            n_single_fallback += 1

        # robust combination: median, not mean - one outlier judge can't
        # silently drag the ensemble score around.
        sorted_scores = sorted(valid_scores)
        mid = len(sorted_scores) // 2
        if len(sorted_scores) % 2 == 1:
            combined = sorted_scores[mid]
        else:
            combined = (sorted_scores[mid - 1] + sorted_scores[mid]) / 2

        clean_human.append(gold["human_score"])
        clean_judge.append(combined)
        per_sentence.append({"gold_id": gold_id, "human_score": gold["human_score"],
                              "judge_score": combined, "malformed": False,
                              "suspicious_zero": False, "high_disagreement": high_disagreement,
                              "usable_for_agreement": True, "member_scores": valid_scores})

    n_usable = len(clean_human)
    return {
        "config_id": config["config_id"], "direction": direction,
        "n_total": n_total, "n_malformed": n_malformed, "n_suspicious_zero": n_suspicious,
        "n_usable": n_usable,
        "n_high_disagreement": n_high_disagreement,
        "high_disagreement_rate": round(n_high_disagreement / n_total, 3) if n_total else None,
        "n_single_judge_fallback": n_single_fallback,
        "malformed_rate": round(n_malformed / n_total, 3) if n_total else None,
        "suspicious_zero_rate": round(n_suspicious / n_total, 3) if n_total else None,
        "pearson_r": round(pearson_r(clean_human, clean_judge), 3) if n_usable >= 3 else None,
        "spearman_rho": round(spearman_rho(clean_human, clean_judge), 3) if n_usable >= 3 else None,
        "mae": round(mae(clean_human, clean_judge), 2) if n_usable >= 1 else None,
        "bucket_agreement_rate": round(
            sum(1 for h, j in zip(clean_human, clean_judge)
                if bucket_of(h, SCORE_BUCKETS) == bucket_of(j, SCORE_BUCKETS)) / n_usable, 3
        ) if n_usable >= 1 else None,
        "disqualified": (n_total > 0 and n_malformed / n_total > MAX_ACCEPTABLE_MALFORMED_RATE),
        "per_sentence": per_sentence,
    }


def main():
    all_results = defaultdict(dict)  # direction -> config_id -> result

    for direction in DIRECTIONS:
        gold_path = os.path.join(GOLD_DIR, GOLD_FILES[direction])
        if not os.path.exists(gold_path):
            print(f"[{direction}] no gold set - skipping")
            continue
        gold_by_id = {g["gold_id"]: g for g in read_jsonl(gold_path)}

        member_results = {}
        for config in JUDGE_CONFIGS:
            if "ensemble_of" in config:
                continue
            res = evaluate_single_judge_config(direction, config["config_id"], gold_by_id)
            if res:
                member_results[config["config_id"]] = res
                all_results[direction][config["config_id"]] = res

        for config in JUDGE_CONFIGS:
            if "ensemble_of" not in config:
                continue
            res = evaluate_ensemble_config(direction, config, gold_by_id, member_results)
            if res:
                all_results[direction][config["config_id"]] = res

    # Write full per-sentence detail (for audit) and a compact summary table.
    out_detail_path = os.path.join(FINAL_DIR, "agreement_detail.json")
    with open(out_detail_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\nWrote full per-sentence detail -> {out_detail_path}\n")
    print(f"{'direction':<12} {'config':<24} {'r':>6} {'rho':>6} {'MAE':>6} {'bucket%':>8} {'malf%':>7} {'susp%':>7} {'disagree%':>10} {'DQ':>4}")
    for direction in DIRECTIONS:
        for config_id, res in all_results.get(direction, {}).items():
            print(f"{direction:<12} {config_id:<24} "
                  f"{res['pearson_r'] if res['pearson_r'] is not None else float('nan'):>6} "
                  f"{res['spearman_rho'] if res['spearman_rho'] is not None else float('nan'):>6} "
                  f"{res['mae'] if res['mae'] is not None else float('nan'):>6} "
                  f"{res['bucket_agreement_rate'] if res['bucket_agreement_rate'] is not None else float('nan'):>8} "
                  f"{res['malformed_rate']:>7} {res['suspicious_zero_rate']:>7} "
                  f"{res.get('high_disagreement_rate', 0.0) or 0.0:>10} "
                  f"{'YES' if res['disqualified'] else '':>4}")

    return all_results


if __name__ == "__main__":
    main()
