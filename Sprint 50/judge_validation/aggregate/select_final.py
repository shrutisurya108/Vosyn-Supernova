"""
Picks ONE final judge configuration per language direction and writes it to
a single place the team can reference (final_judge_config.json +
FINAL_JUDGE_CONFIG.md), replacing the competing recommendations.

Selection rule, applied in this order:
  1. Disqualify any config with malformed_rate above the threshold in
     config.py (an unreliable judge, however well it correlates when it
     *does* parse, isn't usable in an automated GEPA loop).
  2. Among the rest, rank by Spearman rho against the human gold score
     (rank correlation is what GEPA actually needs - it's optimizing which
     candidate is BETTER, not matching an absolute scale).
  3. Tie-break by MAE (lower is better), then by malformed_rate (lower).

Run (after aggregate.py has been run):
    python3 aggregate/select_final.py
"""

import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DIRECTIONS, DIRECTION_DISPLAY, GOLD_SOURCE, FINAL_DIR, SEVERITY_WEIGHTS
from judges.configs import JUDGE_CONFIGS

CONFIG_BY_ID = {c["config_id"]: c for c in JUDGE_CONFIGS}


def rank_key(res):
    rho = res["spearman_rho"] if res["spearman_rho"] is not None else -1
    mae_val = res["mae"] if res["mae"] is not None else 999
    return (-rho, mae_val, res["malformed_rate"])


def select_winner(direction_results):
    eligible = {cid: r for cid, r in direction_results.items() if not r["disqualified"] and r["n_usable"] >= 3}
    if not eligible:
        return None, "ALL CONFIGS DISQUALIFIED - malformed_rate too high, or too few usable sentences. Do not deploy any config for this direction; re-run with a larger/cleaner gold set or fix the judge prompt first."
    winner_id = min(eligible, key=lambda cid: rank_key(eligible[cid]))
    return winner_id, None


def describe_config(config_id):
    c = CONFIG_BY_ID[config_id]
    if "ensemble_of" in c:
        return f"Ensemble of {', '.join(c['ensemble_of'])}, combined by median score (robust to a single outlier judge)"
    return f"model={c['model']}, scoring_method={c['scoring_method']}, temperature={c.get('temperature', 0.0)}"


def main():
    detail_path = os.path.join(FINAL_DIR, "agreement_detail.json")
    if not os.path.exists(detail_path):
        print("Run aggregate/aggregate.py first.")
        return
    all_results = json.load(open(detail_path, encoding="utf-8"))

    final = {}
    notes = {}
    for direction in DIRECTIONS:
        direction_results = all_results.get(direction, {})
        if not direction_results:
            final[direction] = None
            notes[direction] = "No gold set / no judge runs found for this direction yet."
            continue
        winner_id, note = select_winner(direction_results)
        final[direction] = winner_id
        notes[direction] = note

    final_json_path = os.path.join(FINAL_DIR, "final_judge_config.json")
    with open(final_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_date": str(date.today()),
            "selection_rule": "disqualify malformed_rate > threshold, then rank by spearman_rho desc, tie-break MAE asc then malformed_rate asc",
            "severity_weights": SEVERITY_WEIGHTS,
            "final_config_per_direction": final,
        }, f, ensure_ascii=False, indent=2)
    print(f"Wrote {final_json_path}")

    # --- Markdown doc for the team ---
    lines = []
    lines.append("# Final Judge Configuration\n")
    lines.append(f"_Generated {date.today()}. Selection method, gold sets, and full per-sentence scores are in `agreement_detail.json` and `final_judge_config.json` next to this file._\n")
    lines.append("## Summary\n")
    lines.append("| Direction | Final judge config | Spearman rho vs human | MAE | Malformed rate | Gold set size |")
    lines.append("|---|---|---|---|---|---|")
    for direction in DIRECTIONS:
        winner_id = final[direction]
        if winner_id is None:
            lines.append(f"| {DIRECTION_DISPLAY[direction]} | **NONE SELECTED** | - | - | - | - |")
            continue
        r = all_results[direction][winner_id]
        lines.append(f"| {DIRECTION_DISPLAY[direction]} | `{winner_id}` | {r['spearman_rho']} | {r['mae']} | {r['malformed_rate']} | {r['n_total']} |")
    lines.append("")

    for direction in DIRECTIONS:
        lines.append(f"## {DIRECTION_DISPLAY[direction]} (`{direction}`)\n")
        lines.append(f"**Gold set source:** {GOLD_SOURCE[direction]}\n")
        winner_id = final[direction]
        if winner_id is None:
            lines.append(f"**No config selected.** {notes[direction]}\n")
            continue
        lines.append(f"**Selected config:** `{winner_id}` — {describe_config(winner_id)}\n")
        lines.append("**All configs evaluated on this direction's gold set:**\n")
        lines.append("| Config | Spearman rho | Pearson r | MAE | Bucket agreement | Malformed % | Suspicious-zero % | Disagreement % | Disqualified |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        direction_results = all_results.get(direction, {})
        for cid, r in sorted(direction_results.items(), key=lambda kv: rank_key(kv[1]) if not kv[1]["disqualified"] else (999, 999, 999)):
            flag = "**YES**" if r["disqualified"] else ("<- selected" if cid == winner_id else "")
            lines.append(f"| `{cid}` | {r['spearman_rho']} | {r['pearson_r']} | {r['mae']} | {r['bucket_agreement_rate']} | "
                         f"{r['malformed_rate']} | {r['suspicious_zero_rate']} | {r.get('high_disagreement_rate', 0.0) or 0.0} | {flag} |")
        lines.append("")

    lines.append("## Aggregation guardrails applied\n")
    lines.append("- **Malformed output:** any judge response that fails to parse as valid JSON after retries is excluded from correlation math and counted separately as `malformed_rate`. A config with malformed_rate above the threshold in `config.py` is automatically disqualified, regardless of how well it scores when it does work.")
    lines.append("- **Suspicious zero scores:** a score <= 5 with zero reported error spans is a self-contradiction (the judge's number and its own reasoning disagree) and is excluded from correlation math, tracked separately as `suspicious_zero_rate`.")
    lines.append("- **Judge disagreement (ensemble configs only):** per sentence, if the underlying judges' valid scores differ by more than the configured spread, the sentence is flagged `high_disagreement` and the ensemble score is the median (not the mean) of valid judge scores, so one outlier judge can't silently skew the combined score. The disagreement rate is reported per config.")
    lines.append("- **Selection is by rank correlation (Spearman), not raw score matching**, since what matters for GEPA is that the judge ranks better/worse translations correctly, not that its 0-100 scale matches the human MQM formula exactly.\n")

    md_path = os.path.join(FINAL_DIR, "FINAL_JUDGE_CONFIG.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
