"""
Builds gold_en_cmn.jsonl and gold_en_yue.jsonl from the real, human-annotated
SiniticMTError dataset (bilingual annotators labeled error spans + severity
on real MT output). No LLM involved anywhere in this file - these are the
ground-truth labels the judges will be checked against.

Run:
    python3 gold_sets/build_ecmn_eyue.py
"""

import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    SINITIC_MANDARIN_URL, SINITIC_CANTONESE_URL, DATA_DIR, GOLD_DIR,
    GOLD_SET_SIZE, RANDOM_SEED,
)
from common import read_jsonl, write_jsonl, human_mqm_score, stratified_sample


def download(url, dest):
    if os.path.exists(dest):
        print(f"  already have {dest}")
        return
    print(f"  downloading {url}")
    urllib.request.urlretrieve(url, dest)


def build_direction(src_path, direction, out_name):
    rows = read_jsonl(src_path)
    print(f"  loaded {len(rows)} annotated sentences for {direction}")

    def score_fn(r):
        spans = r.get("annotations", {}).get("annotatedSpans", [])
        return human_mqm_score(spans)

    sample = stratified_sample(rows, score_fn, GOLD_SET_SIZE, seed=RANDOM_SEED)

    gold = []
    for r in sample:
        spans = r.get("annotations", {}).get("annotatedSpans", [])
        gold.append({
            "gold_id": f"{direction}_{r['id']}",
            "direction": direction,
            "source_text": r["src"],          # English
            "mt_text": r["mt"],                # the erroneous MT output being judged
            "reference_text": r["ref"],        # clean human reference
            "human_error_spans": spans,        # real bilingual-annotator labels
            "human_score": score_fn(r),        # deterministic MQM score from those labels
            "provenance": "SiniticMTError (human bilingual annotators)",
        })

    out_path = os.path.join(GOLD_DIR, out_name)
    write_jsonl(out_path, gold)
    scores = [g["human_score"] for g in gold]
    print(f"  wrote {len(gold)} sentences -> {out_path}")
    print(f"  human_score range: min={min(scores)} max={max(scores)} mean={sum(scores)/len(scores):.1f}")


def main():
    mandarin_path = os.path.join(DATA_DIR, "mandarin.jsonl")
    cantonese_path = os.path.join(DATA_DIR, "cantonese.jsonl")

    print("Downloading source data...")
    download(SINITIC_MANDARIN_URL, mandarin_path)
    download(SINITIC_CANTONESE_URL, cantonese_path)

    print("\nBuilding English -> Mandarin gold set...")
    build_direction(mandarin_path, "en_to_cmn", "gold_en_cmn.jsonl")

    print("\nBuilding English -> Cantonese gold set...")
    build_direction(cantonese_path, "en_to_yue", "gold_en_yue.jsonl")


if __name__ == "__main__":
    main()
