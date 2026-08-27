"""
Cantonese -> English has NO free public human-error-annotated dataset anywhere
(checked: SiniticMTError only annotates *into* Cantonese; WMT/Google's MQM sets
don't cover Cantonese at all). So for this one direction, you have to be the
bilingual reviewer, same as the acceptance criteria asks for.

This script does the unglamorous setup work for you:
  1. Takes real, clean Cantonese sentences (the human-quality 'ref' field from
     SiniticMTError's cantonese.jsonl - these are correct Cantonese, written by
     the dataset's bilingual annotators).
  2. Uses your local Ollama model to translate each one into English. That
     translation is intentionally NOT edited or cleaned up - it's exactly the
     kind of real MT output (with real MT mistakes) a judge would have to score.
  3. Writes candidates_yue_en.jsonl for you to review with annotate_yueen.py.

Run:
    python3 gold_sets/prepare_yueen_candidates.py --model qwen2.5:7b --n 50
"""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATA_DIR, GOLD_DIR, RANDOM_SEED
from common import read_jsonl, write_jsonl
from ollama_client import ollama_generate, check_ollama_available

TRANSLATE_PROMPT = """Translate the following Cantonese (Hong Kong written vernacular) sentence into natural English.
Output ONLY the English translation, nothing else - no quotes, no notes, no explanation.

Cantonese: {yue}
English:"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:7b", help="Ollama model to generate candidate translations with")
    ap.add_argument("--n", type=int, default=50, help="how many candidates to generate (aim high; you'll only keep 30-50 after review)")
    args = ap.parse_args()

    ok, info = check_ollama_available()
    if not ok:
        print("Could not reach Ollama at http://localhost:11434.")
        print("Start it first: run the Ollama app, or `ollama serve` in a terminal, then re-run this.")
        print(f"(detail: {info})")
        return
    print(f"Ollama is up. Installed models: {info}")
    if args.model not in info and not any(args.model in m for m in info):
        print(f"WARNING: '{args.model}' not found in `ollama list`. Run: ollama pull {args.model}")

    cantonese_path = os.path.join(DATA_DIR, "cantonese.jsonl")
    if not os.path.exists(cantonese_path):
        print("cantonese.jsonl not found - run gold_sets/build_ecmn_eyue.py first (it downloads this file).")
        return

    rows = read_jsonl(cantonese_path)
    rng = random.Random(RANDOM_SEED + 1)  # different seed from the en_to_yue sample so sentences don't overlap
    rng.shuffle(rows)
    chosen = rows[: args.n]

    candidates = []
    for i, r in enumerate(chosen):
        yue_source = r["ref"]  # clean, human-quality Cantonese
        print(f"[{i+1}/{len(chosen)}] translating...", end=" ", flush=True)
        try:
            mt_en = ollama_generate(args.model, TRANSLATE_PROMPT.format(yue=yue_source)).strip()
        except Exception as e:
            print(f"FAILED ({e}), skipping")
            continue
        print("ok")
        candidates.append({
            "candidate_id": f"yue_to_en_{r['id']}",
            "source_yue": yue_source,
            "mt_en_candidate": mt_en,
            "generated_by_model": args.model,
        })

    out_path = os.path.join(GOLD_DIR, "candidates_yue_en.jsonl")
    write_jsonl(out_path, candidates)
    print(f"\nWrote {len(candidates)} candidates -> {out_path}")
    print("Next: python3 gold_sets/annotate_yueen.py")


if __name__ == "__main__":
    main()
