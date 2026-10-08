# Sprint 53 · Step 2 — Judge harness and Colab GPU setup

**Goal of this step:** have both Sprint 50 judges (glm4 and qwen2.5:7b) running on a free Colab GPU, prove that
every prompt we will use works with both of them and can be parsed, measure the real speed, and have a runner that
can stop at any moment and continue in a later session without losing work. **No experiment results are produced
in Step 2** — only the smoke test.

## New files

| Path | What it is |
|---|---|
| `judge/settings.py` | Every setting in one place (models, decoding, scoring, time budgets) |
| `judge/prompts.py` | Sprint 50 FLAT and MQM prompts **verbatim** (checked character-for-character) + 10 controlled variants |
| `judge/ollama_client.py` | Sprint 50's Ollama client, extended with seed / num_ctx / num_predict and timing |
| `judge/parsing.py` | Turns raw judge text into scores; computes MQM scores in Python (never trusts model arithmetic) |
| `judge/plan.py` | The 11 phases: which model × prompt × item × temperature × run each contains |
| `run_experiments.py` | `--check`, `--status`, `--smoke`, `--run` (resumable, time-boxed) |
| `colab/setup_ollama.sh` | Installs + starts Ollama on Colab and downloads both models |
| `notebooks/Sprint53_Colab.ipynb` | The Colab notebook used in Step 2 and Step 4 (no Google Drive) |
| `tests/mock_ollama.py` | Fake Ollama server used to test the harness without a GPU |

## Settings, why they were chosen, and alternatives

| Setting | Value | Why | Alternatives |
|---|---|---|---|
| Judge models | `glm4` (glm4:9b, q4_0) and `qwen2.5:7b` (q4_K_M) | Same tags as Sprint 50 → results comparable | 8-bit versions (more accurate, ~2× memory, both can't share a T4) |
| Prompts | Sprint 50 text verbatim + 10 one-change variants | Each variant changes exactly one thing, so its effect is measurable | — |
| Output format | Free text, parsed by us (no Ollama `format: json`) | Same as Sprint 50; malformed output is a failure mode we measure | Forced JSON (near-zero malformed, but changes decoding) |
| MQM score | 100 − Σ(minor 1, major 5, critical 25), floor 0; unknown severity = minor | Sprint 50 formula, computed in Python | — |
| Temperatures / runs | 0.0 ×3, 0.7 ×5, 1.0 ×5 (repeatability); 0.0 ×1 elsewhere | Your choice; each temperature is its own phase | — |
| Seed | 1000 + run index; retries add 100 | Reproducible runs; a retry with the same seed at T=0 would repeat the same bad output | Unseeded (not reproducible) |
| Attempts | up to 3 if unparseable | Sprint 50 `JUDGE_MAX_RETRIES = 3`; first-attempt success is also recorded | 1 attempt (stricter malformed rate) |
| `num_ctx` | 4096 | Longest prompt ≈ 1,000 tokens; Ollama's default can be 2048 depending on version | 2048 (less memory) |
| `num_predict` | flat 256, MQM 1024, MQM+analysis 1536, rationale 512, pairwise 256 | Stops runaway outputs; a truncated answer is flagged (`done_reason = length`) | Unlimited (Sprint 50 default) |
| Timeout | 180 s per call; 3 network retries | Sprint 50's final value | — |
| Workers | 1 (one call at a time) | Parallel requests are batched on the GPU, which can change outputs slightly and would confound the determinism test | 2–4 workers: ~2–3× faster; decided in Step 3 from the smoke-test speed |
| Ollama version | latest at install time (recorded by `--check`) | Sprint 50's version was not recorded | Pin with `OLLAMA_VERSION=x.y.z` before the installer |

## The experiment plan (built now, run in Step 4)

| Phase | Exp. | Data | Prompts | Temp | Runs | Calls |
|---|---|---|---|---|---|---|
| P01_E1_T00 | E1 repeatability | Set A (40) | mqm, flat | 0.0 | 3 | 480 |
| P02_E1_T07 | E1 | Set A | mqm, flat | 0.7 | 5 | 800 |
| P03_E1_T10 | E1 | Set A | mqm, flat | 1.0 | 5 | 800 |
| P04_E2_prompts | E2 wording (+E10) | Set A | 4 MQM variants | 0.0 | 1 | 320 |
| P05_E3_scales | E3 scales | Set A | flat 1–5, 1–10 | 0.0 | 1 | 160 |
| P06_E4_setB_mqm | E4–E7 | Set B (275) | mqm | 0.0 | 1 | 550 |
| P07_E4_mqm_ref | E4 reference | Set A + B | mqm + reference | 0.0 | 1 | 630 |
| P08_E5_setB_flat | E5–E7 | Set B | flat | 0.0 | 1 | 550 |
| P09_E8_script | E8 script | 44 Traditional + 30 golds | mqm, neutral label | 0.0 | 1 | 148 |
| P10_E9_pairwise | E9 position | 60 pairs × 2 orders | pairwise | 0.0 | 1 | 240 |
| P11_E10_rationale | E10 reasoning | Set A | flat + rationale | 0.0 | 1 | 80 |
| **Total** | | | | | | **4,758** |

(Every call is made once per judge; counts include both judges.) This is more than the ~3,300 I estimated earlier:
that estimate did not count running the flat prompt at all three temperatures and scoring Set B with both the flat
and the reference-based prompt. The smoke test gives the real time; if it is too long we can trim in Step 3
(e.g. flat prompt at T = 0.7 / 1.0 with 3 runs instead of 5 saves 640 calls).

## How stopping and resuming works
* Every finished call is written to `results/<phase>.jsonl` immediately, with a unique key
  (phase | model | prompt | item | temperature | run | order).
* On start, the runner skips every key already saved, so any stop — the time budget, Ctrl-C, a crash, a Colab
  disconnect — loses at most the call(s) in flight. A half-written last line is detected and ignored.
* Calls that fail because the Ollama server is down are not saved, so they are retried next time.
* The Step 4 cell runs 30-minute chunks and downloads a checkpoint zip after each one, and stops itself after
  3 h 15 min. Tested here against a fake server: budget stops, kill mid-run, truncated last line, server dying
  mid-run, and 1–4 workers — no duplicates and no lost rows in any case.
