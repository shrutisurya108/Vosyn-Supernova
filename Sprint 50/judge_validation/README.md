# Judge Validation & Finalization

Locks in one final GEPA judge configuration per language direction, backed by
a human-labeled gold set, instead of the several competing judge configs
currently in play. Runs entirely locally and free (Ollama for the LLM judges,
Python standard library for everything else — no numpy/pandas/scipy, no API
keys, no virtual env required).

## What data this actually uses (read this first)

| Direction | Gold-set source | Real human labels? |
|---|---|---|
| English → Mandarin | [SiniticMTError](https://github.com/hannliu/SiniticMTError) `mandarin.jsonl` | Yes — bilingual annotators, published dataset |
| English → Cantonese | SiniticMTError `cantonese.jsonl` | Yes — bilingual annotators, published dataset |
| Mandarin → English | [google/wmt-mqm-human-evaluation](https://github.com/google/wmt-mqm-human-evaluation), newstest2021 zh-en | Yes — professional translators, published dataset |
| Cantonese → English | Built by **you**, with help from this repo's scripts | You are the bilingual reviewer — no free public dataset exists for this direction |

I looked: SiniticMTError only has annotations for translation *into* Mandarin/
Cantonese (source is always English). Google's WMT MQM set covers Mandarin→
English with real professional annotations, but nothing exists for Cantonese→
English anywhere I could find, free or otherwise. So for that one direction,
`gold_sets/prepare_yueen_candidates.py` generates candidate MT output locally
with your own Ollama model, and `gold_sets/annotate_yueen.py` is a small
terminal tool where you mark the actual errors yourself — same annotation
schema as the other three directions, so everything downstream treats all
four directions identically.

## One-time setup (no venv, plain Python 3.14)

```bash
# 1. Install Ollama (free, local LLM runner)
#    https://ollama.com/download

# 2. Pull the two models the default judge configs use
ollama pull glm4
ollama pull qwen2.5:7b

# 3. Nothing else to install — everything here uses only the Python
#    standard library (urllib, json, csv, statistics/math). No pip installs.
```

Ollama needs to be running before any script that calls a model
(`prepare_yueen_candidates.py`, `judges/run_judges.py`). It normally
auto-starts after install; if not, run `ollama serve` in a terminal and
leave it open.

## Run order

```bash
cd judge_validation

# Step 1 — build the 3 gold sets that come from real existing data
# (already run once for you; gold_sets/output/*.jsonl are included.
#  Re-run any time to re-download and re-sample.)
python3 gold_sets/build_ecmn_eyue.py     # -> gold_en_cmn.jsonl, gold_en_yue.jsonl
python3 gold_sets/build_cmnen.py         # -> gold_cmn_en.jsonl

# Step 2 — build the 4th gold set yourself (Cantonese -> English)
python3 gold_sets/prepare_yueen_candidates.py --model qwen2.5:7b --n 50
python3 gold_sets/annotate_yueen.py
#   For each sentence: type "clean" if there are no errors, or one line per
#   error as   <exact text> | <type> | <minor/major/critical>   then a blank
#   line when done with that sentence. Ctrl+C or "q" saves and quits anytime
#   — it resumes where you left off next time. Aim for the full 30-50 range;
#   the more sentences, the more trustworthy the agreement numbers below.

# Step 3 — score every judge config against every gold set
python3 judges/run_judges.py
#   This is the slow step — real Ollama calls, retried up to 3x on
#   malformed JSON. With 2 models x 2 prompt styles x 4 directions x 40
#   sentences, expect several hundred model calls. Time depends entirely on
#   your Mac / model size; a 7-9B model on an M3 Air is usually a few
#   seconds per call.
#
#   Want to see the rest of the pipeline first without waiting on real
#   inference? Run `python3 judges/run_judges.py --mock` instead — it fakes
#   judge output (including some deliberately malformed and suspicious-zero
#   cases) so you can sanity check steps 4-5 immediately.

# Step 4 — aggregate: compute agreement with human labels, explicitly
# handling malformed output, suspicious zero scores, and judge disagreement
python3 aggregate/aggregate.py

# Step 5 — pick the final config per direction + write the team doc
python3 aggregate/select_final.py
```

## What you get at the end

- `outputs/final/FINAL_JUDGE_CONFIG.md` — the one document to point the team
  at. States, per direction: which config won, its agreement numbers, every
  competing config's numbers side by side, and which configs were
  disqualified and why.
- `outputs/final/final_judge_config.json` — same result, machine-readable,
  meant to be loaded directly by whatever wires the judge into GEPA.
- `outputs/final/agreement_detail.json` — full per-sentence detail (every
  judge's score vs. the human score, malformed/suspicious/disagreement flags)
  for anyone who wants to audit a specific disagreement.

## How "final" is decided

For each direction: any config with a malformed-output rate above 5% is
disqualified outright, no matter how well it otherwise scores — an
unreliable judge isn't usable in an automated loop. Among what's left, the
config with the highest **Spearman rank correlation** to the human MQM score
wins (rank correlation, not raw score matching, because what GEPA needs is
"does the judge correctly say translation A is better than B," not an exact
0-100 match to the human formula). Ties break on mean absolute error, then
malformed rate.

## Editing the judge configs being compared

`judges/configs.py` — `JUDGE_CONFIGS` is the literal list of "judge
configurations proposed this sprint." Add, remove, or edit entries there
(different model, different prompt, different temperature, a 3-model
ensemble, etc.) and re-run from Step 3. Nothing else needs to change — the
aggregation and selection logic is generic over however many configs you
list.

## Adjusting the guardrails

All thresholds live in `config.py`:
- `MAX_ACCEPTABLE_MALFORMED_RATE` — disqualification cutoff (default 5%)
- `ZERO_SCORE_SUSPICION_THRESHOLD` — score-and-error-count contradiction
  threshold (default: score ≤ 5 with 0 reported errors)
- `INTER_JUDGE_DISAGREEMENT_SPREAD` — point spread across ensemble judges
  that flags a sentence for review (default 25 points)
- `GOLD_SET_SIZE` / `GOLD_SET_MIN` / `GOLD_SET_MAX` — gold set sizing
