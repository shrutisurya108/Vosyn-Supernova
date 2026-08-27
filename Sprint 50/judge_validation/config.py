"""
Central config. Change values here rather than hunting through the other files.
Everything runs locally and free: Ollama for the judge LLMs, stdlib for stats.
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
GOLD_DIR = os.path.join(PROJECT_ROOT, "gold_sets", "output")
JUDGE_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "judge_runs")
FINAL_DIR = os.path.join(PROJECT_ROOT, "outputs", "final")

for d in (DATA_DIR, GOLD_DIR, JUDGE_OUTPUT_DIR, FINAL_DIR):
    os.makedirs(d, exist_ok=True)

# --- Source data locations ---
SINITIC_MANDARIN_URL = "https://raw.githubusercontent.com/hannliu/SiniticMTError/main/mandarin.jsonl"
SINITIC_CANTONESE_URL = "https://raw.githubusercontent.com/hannliu/SiniticMTError/main/cantonese.jsonl"
WMT_MQM_ZHEN_URL = "https://raw.githubusercontent.com/google/wmt-mqm-human-evaluation/main/newstest2021/zhen/mqm_newstest2021_zhen.tsv"

# --- The 4 language directions this project tracks ---
DIRECTIONS = ["en_to_cmn", "en_to_yue", "cmn_to_en", "yue_to_en"]

DIRECTION_DISPLAY = {
    "en_to_cmn": "English -> Mandarin",
    "en_to_yue": "English -> Cantonese",
    "cmn_to_en": "Mandarin -> English",
    "yue_to_en": "Cantonese -> English",
}

# How each direction's gold set is sourced (for documentation / transparency)
GOLD_SOURCE = {
    "en_to_cmn": "SiniticMTError (mandarin.jsonl) - human bilingual annotator error spans",
    "en_to_yue": "SiniticMTError (cantonese.jsonl) - human bilingual annotator error spans",
    "cmn_to_en": "Google wmt-mqm-human-evaluation (newstest2021 zh-en) - professional translator MQM",
    "yue_to_en": "Locally built by you: Cantonese source (from SiniticMTError ref field) + your own "
                 "local MT output + your own bilingual error annotation (no free public dataset exists "
                 "for this direction)",
}

GOLD_SET_SIZE = 40          # target sentences per direction (within the 30-50 range asked for)
GOLD_SET_MIN = 30
GOLD_SET_MAX = 50
RANDOM_SEED = 42

# --- MQM-style severity weights (Freitag et al. 2021 convention, same as WMT's own weighting) ---
SEVERITY_WEIGHTS = {
    "minor": 1,
    "major": 5,
    "critical": 25,   # not present in SiniticMTError but judges may still emit it
    "neutral": 0,
}

# --- Ollama (local, free) settings ---
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_TIMEOUT = 180
JUDGE_MAX_RETRIES = 3

# --- Score buckets used for the coarse "does the judge land in the right ballpark" agreement check ---
SCORE_BUCKETS = [(85, 101, "clean"), (60, 85, "moderate"), (0, 60, "poor")]

# --- Aggregation guardrails ---
MAX_ACCEPTABLE_MALFORMED_RATE = 0.05     # a config with >5% unparseable output is disqualified
ZERO_SCORE_SUSPICION_THRESHOLD = 5        # a judge score <= this, with 0 reported errors, is "suspicious"
INTER_JUDGE_DISAGREEMENT_SPREAD = 25      # point spread across judges on one sentence that triggers a flag
