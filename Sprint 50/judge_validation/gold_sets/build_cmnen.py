"""
Builds gold_cmn_en.jsonl from Google's wmt-mqm-human-evaluation repo: real MQM
error-span annotations done by professional translators on WMT21 zh-en system
outputs. This is genuine human-labeled data, free and public - not something
we're generating ourselves.

Format note: the 'target' column has error spans marked inline as <v>...</v>.
Each (system, doc, doc_id, seg_id) segment was annotated by one or more raters;
we take one rater per segment (deterministic - lowest rater id) to avoid
double counting the same sentence's errors twice, same as a single annotator
pass would look in your own review process.

Run:
    python3 gold_sets/build_cmnen.py
"""

import csv
import os
import re
import sys
import urllib.request
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import WMT_MQM_ZHEN_URL, DATA_DIR, GOLD_DIR, GOLD_SET_SIZE, RANDOM_SEED
from common import write_jsonl, human_mqm_score, stratified_sample

SPAN_RE = re.compile(r"<v>(.*?)</v>")


def download(url, dest):
    if os.path.exists(dest):
        print(f"  already have {dest}")
        return
    print(f"  downloading {url}")
    urllib.request.urlretrieve(url, dest)


def strip_tags(text):
    return text.replace("<v>", "").replace("</v>", "")


def main():
    tsv_path = os.path.join(DATA_DIR, "wmt_mqm_zhen_2021.tsv")
    print("Downloading source data...")
    download(WMT_MQM_ZHEN_URL, tsv_path)

    rows = list(csv.DictReader(open(tsv_path, encoding="utf-8"), delimiter="\t"))
    # keep only real MT system output, not the human reference systems (those
    # are labeled "ref.*" and aren't representative of what a judge will see)
    rows = [r for r in rows if not r["system"].startswith("ref")]

    by_segment = defaultdict(list)
    for r in rows:
        key = (r["system"], r["doc"], r["doc_id"], r["seg_id"])
        by_segment[key].append(r)

    segments = []
    for key, seg_rows in by_segment.items():
        # deterministically pick one rater's pass over this segment
        raters = sorted(set(r["rater"] for r in seg_rows))
        chosen_rater = raters[0]
        chosen = [r for r in seg_rows if r["rater"] == chosen_rater]

        source_zh = chosen[0]["source"]
        target_en_tagged = chosen[0]["target"]
        target_en = strip_tags(target_en_tagged)

        spans = []
        for r in chosen:
            if r["severity"] == "No-error":
                continue
            m = SPAN_RE.search(r["target"])
            span_text = m.group(1) if m else ""
            spans.append({
                "error_text_segment": span_text,
                "error_type": r["category"],
                "error_severity": r["severity"],
            })

        segments.append({
            "system": key[0], "doc": key[1], "doc_id": key[2], "seg_id": key[3],
            "source_zh": source_zh,
            "target_en": target_en,
            "spans": spans,
        })

    print(f"  {len(segments)} unique (system, segment) MT outputs available")

    def score_fn(s):
        return human_mqm_score(s["spans"])

    sample = stratified_sample(segments, score_fn, GOLD_SET_SIZE, seed=RANDOM_SEED)

    gold = []
    for i, s in enumerate(sample):
        gold.append({
            "gold_id": f"cmn_to_en_{s['doc_id']}_{s['seg_id']}_{s['system']}_{i}",
            "direction": "cmn_to_en",
            "source_text": s["source_zh"],       # Mandarin
            "mt_text": s["target_en"],             # MT output being judged (English)
            "reference_text": None,                 # WMT MQM doesn't ship a matching clean reference per row
            "human_error_spans": s["spans"],
            "human_score": score_fn(s),
            "provenance": "Google wmt-mqm-human-evaluation, newstest2021 zh-en (professional translators)",
        })

    out_path = os.path.join(GOLD_DIR, "gold_cmn_en.jsonl")
    write_jsonl(out_path, gold)
    scores = [g["human_score"] for g in gold]
    print(f"  wrote {len(gold)} sentences -> {out_path}")
    print(f"  human_score range: min={min(scores)} max={max(scores)} mean={sum(scores)/len(scores):.1f}")


if __name__ == "__main__":
    main()
