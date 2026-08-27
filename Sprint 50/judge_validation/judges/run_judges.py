"""
Scores every gold-set sentence with every (non-ensemble) judge config.
Handles malformed JSON with retries, and records raw output + failure reason
for anything that still can't be parsed - nothing is silently dropped here,
that happens explicitly later in aggregate.py.

Run for real (needs Ollama running locally with the models pulled):
    python3 judges/run_judges.py

Run in mock mode (no Ollama needed - generates synthetic judge output,
including deliberately malformed and suspicious-zero cases, so you can see
the whole pipeline including aggregate.py work end-to-end before spending
real inference time):
    python3 judges/run_judges.py --mock
"""

import argparse
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DIRECTIONS, GOLD_DIR, JUDGE_OUTPUT_DIR, JUDGE_MAX_RETRIES, SEVERITY_WEIGHTS
from common import read_jsonl, write_jsonl, human_mqm_score
from judges.configs import JUDGE_CONFIGS, prompt_for
from ollama_client import ollama_generate, check_ollama_available

JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def extract_json(text):
    """Best-effort pull of the first {...} blob out of a model response."""
    m = JSON_RE.search(text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def score_from_parsed(parsed, scoring_method):
    if scoring_method == "flat":
        score = parsed.get("score")
        if not isinstance(score, (int, float)):
            return None, []
        return max(0, min(100, int(score))), []
    else:  # mqm
        errors = parsed.get("errors")
        if errors is None or not isinstance(errors, list):
            return None, []
        norm_errors = []
        for e in errors:
            if not isinstance(e, dict):
                continue
            norm_errors.append({
                "error_text_segment": e.get("text", ""),
                "error_type": e.get("type", "Unknown"),
                "error_severity": (e.get("severity") or "minor").capitalize(),
            })
        return human_mqm_score(norm_errors), norm_errors


def call_judge_real(config, source, mt, direction):
    """
    Calls Ollama with retries. Network/timeout errors are caught here and
    treated the same as a bad-JSON response (i.e. another retry, then
    eventually 'malformed') - they must NOT propagate up and kill the whole
    run, since a single slow call would otherwise take down every sentence
    still queued behind it.
    """
    prompt = prompt_for(config, source, mt, direction)
    last_raw = None
    for attempt in range(1, JUDGE_MAX_RETRIES + 1):
        try:
            raw = ollama_generate(config["model"], prompt, temperature=config.get("temperature", 0.0))
        except Exception as e:
            last_raw = f"[request failed on attempt {attempt}: {type(e).__name__}: {e}]"
            continue
        last_raw = raw
        parsed = extract_json(raw)
        if parsed is not None:
            score, errors = score_from_parsed(parsed, config["scoring_method"])
            if score is not None:
                return {"raw_response": raw, "malformed": False, "judge_score": score,
                        "judge_errors": errors, "attempts": attempt}
    return {"raw_response": last_raw, "malformed": True, "judge_score": None,
            "judge_errors": [], "attempts": JUDGE_MAX_RETRIES}


def call_judge_mock(config, gold_row, rng):
    """
    Synthetic stand-in for Ollama so the rest of the pipeline can be tested
    without any model installed. Deliberately injects some malformed output
    and some suspicious zero-scores so aggregate.py has real cases to catch.
    """
    human_score = gold_row["human_score"]
    r = rng.random()
    if r < 0.04:
        return {"raw_response": "Sure, I'd rate this... hmm let me think", "malformed": True,
                "judge_score": None, "judge_errors": [], "attempts": 3}
    if r < 0.07:
        # suspicious: score of 0 but claims no errors found - contradiction
        return {"raw_response": '{"errors": []}', "malformed": False, "judge_score": 0,
                "judge_errors": [], "attempts": 1}

    noise = rng.gauss(0, 8)
    model_bias = {"glm4": 2, "qwen2.5:7b": -3}.get(config.get("model"), 0)
    score = max(0, min(100, round(human_score + noise + model_bias)))
    if config["scoring_method"] == "flat":
        return {"raw_response": json.dumps({"score": score}), "malformed": False,
                "judge_score": score, "judge_errors": [], "attempts": 1}
    else:
        n_errors = max(0, round((100 - score) / 5))
        errors = [{"error_text_segment": "x", "error_type": "Mistranslation",
                   "error_severity": rng.choice(["Minor", "Major"])} for _ in range(n_errors)]
        computed_score = human_mqm_score(errors)
        return {"raw_response": json.dumps({"errors": errors}), "malformed": False,
                "judge_score": computed_score, "judge_errors": errors, "attempts": 1}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true", help="use synthetic judge output instead of calling Ollama")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    if not args.mock:
        ok, info = check_ollama_available()
        if not ok:
            print("Could not reach Ollama. Start it, or pass --mock to test the pipeline without it.")
            print(f"(detail: {info})")
            return
        print(f"Ollama up. Models installed: {info}")

    rng = random.Random(args.seed)
    real_configs = [c for c in JUDGE_CONFIGS if "ensemble_of" not in c]

    gold_files = {
        "en_to_cmn": "gold_en_cmn.jsonl", "en_to_yue": "gold_en_yue.jsonl",
        "cmn_to_en": "gold_cmn_en.jsonl", "yue_to_en": "gold_yue_en.jsonl",
    }

    for direction in DIRECTIONS:
        gold_path = os.path.join(GOLD_DIR, gold_files[direction])
        if not os.path.exists(gold_path):
            print(f"[{direction}] no gold set yet ({gold_path}) - skipping")
            continue
        gold_rows = read_jsonl(gold_path)
        print(f"\n[{direction}] {len(gold_rows)} gold sentences")

        for config in real_configs:
            out_path = os.path.join(JUDGE_OUTPUT_DIR, f"{direction}__{config['config_id']}.jsonl")

            # Resume support: if this config was partially run before (crash,
            # Ctrl+C, closed terminal), pick up where it left off instead of
            # re-calling the model for sentences already scored.
            done_by_id = {}
            if os.path.exists(out_path) and not args.mock:
                for r in read_jsonl(out_path):
                    done_by_id[r["gold_id"]] = r
                if done_by_id:
                    print(f"  [{config['config_id']}] resuming: {len(done_by_id)}/{len(gold_rows)} already done")

            results = list(done_by_id.values())
            for g in gold_rows:
                if g["gold_id"] in done_by_id:
                    continue
                if args.mock:
                    r = call_judge_mock(config, g, rng)
                else:
                    print(f"  [{config['config_id']}] {g['gold_id']}...", end=" ", flush=True)
                    r = call_judge_real(config, g["source_text"], g["mt_text"], direction)
                    print("malformed" if r["malformed"] else r["judge_score"])
                results.append({"gold_id": g["gold_id"], "config_id": config["config_id"], **r})
                write_jsonl(out_path, results)  # save after every sentence, not just at the end

            malformed_n = sum(1 for r in results if r["malformed"])
            print(f"  [{config['config_id']}] done. malformed: {malformed_n}/{len(results)} -> {out_path}")


if __name__ == "__main__":
    main()