# Sprint 53 · Task B · Step B7 — Recommended prompt structure and guidelines

**Scope:** English → Mandarin (Simplified) translation, judged by glm4:latest and qwen2.5:7b (Ollama, 4-bit, Colab T4).
**Evidence:** Stage 1 screening (development half, 2,840 calls), Stage 1b (combined prompt, 436 calls) and Stage 2
confirmation (held-out half, 4,478 calls). Every strategy was compared with the Sprint 50 baseline prompts re-run in the
same session, under success rules written before any Task B run (`taskB/BASELINE_AND_METRICS.md`).
**Status labels used below:** **Confirmed** = passed the pre-registered held-out rule · **Directional** = consistent
improvement, some of it statistically supported, but not confirmed by the rule · **Avoid** = made things worse ·
**Untested** = proposed, needs a future experiment.

---

## 1. Recommendation in one page

| Use case | Recommended prompt | Status | Why |
|---|---|---|---|
| **Comparing two translations** | **S5 pairwise with a tie definition**, judged in **both orders** | **Confirmed (glm4)**, neutral for qwen | glm4 first-position picks 70% → 31%, verdicts matching the expected answer 38% → 61%, flawed translation preferred 13% → 5% (all 95% CIs exclude 0) |
| **Error annotation (MQM-style lists)** | **S2 few-shot MQM** (3 examples incl. one correct translation with no errors) — **plus a multi-error example (future work)** | **Directional** | False errors on correct translations ↓ for both judges (CIs exclude 0); run-to-run consistency and wording robustness improved by a large margin (CIs exclude 0). Not confirmed: glm4 agreement with human scores fell (0.55 → 0.16; 95% CI of the change −0.91 to +0.19) |
| **A single quality score to rank translations** | **Keep the Sprint 50 flat 0–100 prompt** (temperature 0) | Baseline retained | Most stable prompt (88–95% of items identical over 3 runs at T = 0) and best at ranking Set B (ρ 0.55–0.58 vs ≤ 0.32 for any MQM prompt) — Task A finding F1 holds on new data |
| Not recommended | S1 scoring rubric, S3 step-by-step, S4 accuracy + fluency, combined prompt C | Avoid / not adopted | See §4 |

**Recommended judge set-up:** temperature 0, fixed seed, num_ctx 4096, no forced JSON with a tolerant parser, MQM score
computed in code (100 − Σ minor 1 / major 5 / critical 25, floor 0), malformed-output guardrail ≤ 5%. Record Ollama
version and model digests every session (T = 0 is still not fully reproducible: 81–96% of baseline scores were identical
between the Task A and Task B runs).

---

## 2. Recommended prompt structures

### 2.1 Pairwise comparison — S5 (Confirmed for glm4)

```text
You are an expert professional translation quality evaluator.
Source ({src_lang}): {source}
Translation A ({tgt_lang}): {a}
Translation B ({tgt_lang}): {b}

First assess each translation on its own: note any meaning errors (mistranslation, omission, addition) and any
problems with naturalness. Then compare them.
- Answer "A" or "B" only if that translation is clearly better: it has fewer or less serious meaning errors, or,
  when both are accurate, it is clearly more natural.
- Answer "tie" if both are equally good or equally flawed - including when both are correct but worded differently.
- The order in which the translations are shown is random and must not affect your decision.
Respond with ONLY a JSON object, nothing else, in exactly this form:
{"assessment_a": "...", "assessment_b": "...", "better": "A|B|tie"}
```

**How to run it:** judge every pair in both orders (A,B) and (B,A). Map each verdict back to the original translations;
if the two orders disagree, record a **tie** (or "uncertain") rather than either side.
**Building blocks and what each does:** a short assessment of each translation before the verdict; an explicit tie
definition that includes "both correct, worded differently"; the statement that the order is random.

### 2.2 Error annotation — S2 few-shot MQM (Directional)

```text
You are an expert professional translation quality evaluator following MQM (Multidimensional Quality Metrics) principles.
Identify every real error in the machine translation. For each error give: the exact erroneous text segment, an error
type (one of: Mistranslation, Omission, Addition, Grammar, Spelling, Typography, Untranslated, Unintelligible), and a
severity (one of: minor, major, critical).
If there are no errors, return an empty list.
Respond with ONLY a JSON object, nothing else, in exactly this form:
{"errors": [{"text": "...", "type": "...", "severity": "minor|major|critical"}, ...]}

Here are three examples of correct evaluations.

Example 1   correct translation, worded differently (冰释前嫌)            -> {"errors": []}
Example 2   one major meaning error ('a month' -> 每年)                  -> 1 error, Mistranslation, major
Example 3   one minor omission from a real MT output (… 到严重, 级别 missing) -> 1 error, Omission, minor

Now evaluate this translation.
Source ({src_lang}): {source}
Machine translation ({tgt_lang}): {mt}
Answer:
```

(The examples are given in full in `taskB/PROMPTS_FOR_REVIEW.md`; all three were checked by a native Mainland reviewer.)

**Required change before production use (Untested, see §6):** add a fourth example of a real machine translation with
**several** errors of different severities. All three current examples have at most one error, and glm4 learned that:
on held-out machine translations with 5 or more human-marked errors it listed 3.2 errors on average with S2 against
4.8 with the baseline prompt, and scored the two worst items (human 65 and 70) at 84 and 89.

### 2.3 Single score for ranking — Sprint 50 flat 0–100 (baseline retained)

Unchanged Sprint 50 prompt. None of the flat-score strategies (S1 rubric, S4 accuracy + fluency) passed screening.

---

## 3. Guidelines

| # | Guideline | Status | Evidence (held-out unless marked "dev") |
|---|---|---|---|
| G1 | **Calibrate with few-shot examples, and include a correct translation with *no* errors.** It is the single most effective change for consistency and for false errors. | Directional (several parts CI-backed) | False errors on correct translations: glm4 100% → 90%, qwen 60% → 43% (CIs exclude 0). Inconsistent at T = 0.7 × 5: glm4 98% → 57%, qwen 53% → 28%; mean spread 50 → 19 and 13 → 6 points; qwen fully stable at T = 0 (10% → 0%) (all CIs exclude 0) |
| G2 | **Cover the range of errors in the examples**, including one with several errors and mixed severities, so the judge does not learn "at most one error". | Untested — future work | glm4 + S2 under-listed errors on heavily flawed real MT (4.8 → 3.2 per item) and lost agreement with human scores (0.55 → 0.16) |
| G3 | **Take few-shot examples only from development data**, have a native speaker check them, and exclude their sources from scoring. | Method | All 3 examples reviewer-approved; held-out text never appears in a prompt (automated check) |
| G4 | **Do not tell the judge that "different wording is not an error" as a separate step.** Show it with an example instead (G1). | Avoid | S3 (dev): false errors 94% → 3%, but planted-error detection 58% → 17% and glm4 human agreement 0.73 → 0.36 — the judge explained real errors away (密码**不**是 "Muiriel" called "a different sentence structure") |
| G5 | **Do not give score-band anchors to glm4.** It snaps to the bottom of a band and stops separating translations. | Avoid (glm4) | S1 (dev): glm4 gave exactly 85 to 125 of 158 items; flawed versions below their correct version 78% → 44%. qwen became more consistent (53% → 21% inconsistent) — a judge-specific result |
| G6 | **Do not split accuracy and fluency** into two sub-scores for these judges. | Avoid | S4 (dev): small gains, qwen less consistent (53% → 68%) |
| G7 | **Pairwise: define "tie", say the order is random, ask for a short assessment of each translation first, and always judge both orders.** | Confirmed (glm4) | First-position picks glm4 70% → 31%; matches expected 38% → 61%; flawed preferred 13% → 5% (CIs exclude 0). qwen: no significant change |
| G8 | **Show the output format with concrete values, not a placeholder like `"A|B|tie"`.** Example: `{"better": "B"}` and list the allowed values in words. | Directional | glm4 copied the placeholder literally in 39% of answers to one reworded pairwise prompt (25/64) and 14% of another — 36 unreadable answers, all from this |
| G9 | **Use a single quality score (flat 0–100) when the goal is to rank translations; use MQM lists for diagnosis.** | Baseline | Set B ranking ρ: flat 0.55–0.58 vs MQM ≤ 0.11, S2 ≤ 0.32 |
| G10 | **Run at temperature 0, fixed seed and context, and record versions.** For decisions that matter, run 3 times and use the median. | Method | T = 0.7 multiplies inconsistency (e.g. baseline MQM glm4: 20% at T = 0 vs 98% at T = 0.7); T = 0 still varies (0–20% of items inconsistent over 3 runs, depending on prompt and judge) |
| G11 | **Validate a prompt per judge before adopting it.** Effects differ by model. | Method | S5 helps glm4 only; S1 helps qwen only; S2 human agreement rises for qwen (0.37 → 0.66) and falls for glm4 |
| G12 | **Test every new prompt with two rewordings before adopting it.** | Method | Baseline MQM scores moved 9.4 (glm4) / 6.1 (qwen) points on average when only the wording changed; S2 halved this (4.5 / 1.85, CIs exclude 0) |
| G13 | **Quote error spans from the translation only.** Instruct it explicitly and check it in code. | Directional | Baseline glm4: 48% of quoted spans not in the translation (S2 cut it to 12%). In Stage 1b the explicit instruction cut it further (dev 14% → 5%), but the combined prompt was not adopted (§4) |
| G14 | **Compute scores in code and keep a malformed-output guardrail (≤ 5%).** | Method | All main prompts ≤ 0.5% malformed |
| G15 | **Keep a held-out split and write the success rule down before testing.** | Method | Several Stage 1 gains (e.g. qwen human agreement 0.22 → 0.81 for S2) were smaller or reversed on held-out data |

---

## 4. What did not work, and why

| Strategy | Stage reached | Outcome |
|---|---|---|
| S1 defined scoring rubric (flat) | Stage 1 | FAIL — glm4 collapsed onto band anchors; good for qwen consistency only |
| S3 step-by-step criteria (MQM) | Stage 1 | FAIL — over-corrected to leniency; real errors explained away |
| S4 separate accuracy + fluency (flat) | Stage 1 | FAIL — gains small; qwen less consistent |
| C combined (S2 examples + S3 delimiters + "quote only from the translation" + checklist) | Stage 1b | Passed vs baseline, but clearly worse than S2 on qwen human agreement (0.81 → 0.59), glm4 detection (72% → 58%) and glm4 consistency (63% → 74% inconsistent) → not taken to Stage 2 |
| S2 few-shot (MQM) | Stage 2 | NOT CONFIRMED by the pre-registered rule (guard flags: glm4 human agreement 0.55 → 0.16; qwen literal-correct over fluent-wrong 70% → 55%; both CIs include 0) despite CI-backed gains in false errors, consistency, robustness, span validity and glm4 detection |
| S5 pairwise + tie | Stage 2 | PROMISING (glm4-specific) |

---

## 5. Limitations

* **Small samples.** 20 English sources and 20 human-scored items per half; correlations with human scores have very
  wide intervals (e.g. glm4 + S2: 0.16, CI −0.36 to 0.68). Effects below roughly 15–20 percentage points cannot be
  confirmed.
* **Two small open models, 4-bit.** Results may not transfer to larger or API judges, or to other quantisations.
* **Single language pair and domain mix.** English → Mandarin (Simplified) only; Set B sentences are short and were
  built around specific error types.
* **Set B ground truth is constructed.** Planted errors and quality bands were authored and reviewer-checked, not
  produced by a full MQM annotation; "detected" is a span-matching lower bound.
* **Temperature 0 is not fully deterministic** on Ollama/T4 (81–96% identical scores across sessions); Ollama 0.35.1
  in Task B vs 0.35.0 in Task A.
* **The held-out half has now been used,** so any further prompt changes need fresh test items (see §6).
* **Ties in pairwise judging** increase with S5 (glm4 0% → 23%); whether a tie is the right answer was only defined for
  the pair types in the dataset.

---

## 6. Future work

**FW1 — S2b: few-shot MQM with a multi-error example (highest priority).**
* *Problem:* with S2, glm4 under-lists errors on heavily flawed machine translations (4.8 → 3.2 per item on items with
  5 or more human-marked errors) and its agreement with human scores fell (0.55 → 0.16).
* *Change:* add a fourth example — a real machine translation with 3–5 human-annotated errors of mixed severity
  (from SiniticMTError, development material only), reviewed by the Mandarin reviewer. Keep examples 1–3 unchanged.
* *Test:* the held-out half has been looked at, so S2b needs **fresh items**: e.g. 30–40 new SiniticMTError items
  with human MQM scores not used in Sprints 50–53, plus new Set B-style variants for 15–20 new sources. Compare S2b with
  S2 and the baseline MQM prompt, same session, same metrics and pre-registered rule; T = 0 on all items, 5 runs at
  T = 0.7 and 2 rewordings on a 40-item subset. Rough cost ≈ 2,500–3,000 calls (about 1.5–2 h on a Colab T4).
* *Success:* glm4 agreement with human scores at least back to the baseline level, with S2's gains in false errors and
  consistency kept.

**Other follow-ups**
* FW2 — Re-test the "quote errors only from the translation" instruction on its own (it improved glm4 span validity in
  Stage 1b) on top of S2b.
* FW3 — S1 rubric for qwen only (its consistency gain was large: 53% → 21% inconsistent on dev).
* FW4 — Fix the output-format placeholder (G8) in all prompts and re-measure malformed rates under rewording.
* FW5 — Larger human-scored sample (≥ 60 items) so human-agreement changes of ~0.15 can be confirmed.
* FW6 — Check whether the S5 and S2 results hold for a larger or API judge.

---

## 7. Acceptance criteria — where each is met

| Criterion | Where |
|---|---|
| A baseline prompt is established | Sprint 50 flat + MQM and Task A pairwise, verbatim; re-run in every Task B session (`taskB/BASELINE_AND_METRICS.md` §1) |
| Multiple approaches designed and tested | S1–S5 + combined prompt C (`judge/prompts_taskb.py`, `taskB/PROMPTS_FOR_REVIEW.md`, `taskB/PROMPTS_B5_FOR_REVIEW.md`) |
| Representative English → Mandarin examples | Set A (40 SiniticMTError items with human MQM scores) + Set B (275 reviewer-checked variants of 40 sources, 8 categories) + 60 pairs; split 20/20 by source |
| Each selected configuration evaluated across repeated runs | Stage 1: 3 runs at T = 0.7 for all 6 absolute prompts (+ C); Stage 2: 3 runs at T = 0 and 5 at T = 0.7 (absolute), 3 runs at T = 0.7 (pairwise), 2 rewordings each |
| Consistency compared across approaches | `analysis_taskB/stage1/S1_consistency_T07.csv`, `analysis_taskB/stage2/T2_consistency.csv`, `T5_pairwise_T07.csv`, `T6_wording_robustness.csv` |
| Improvements and limitations documented | §3–§5 of this document; `analysis_taskB/stage2/T3_deltas_vs_baseline.csv` |
| Recommended prompt structure or guidelines | §1–§3 of this document |

## 8. Reproduce

```bash
python taskB/make_split.py && python taskB/validate_split.py        # B1 split
python taskB/check_prompts.py && python taskB/check_prompts_b5.py   # B2 / B5 prompt checks
python taskB/run_taskb.py --run --stage 1|1b|2 --budget 30m         # GPU runs (Colab T4 notebooks in notebooks/)
python taskB/analyze_stage1.py                                       # B4 / B5 analysis -> analysis_taskB/stage1/
python taskB/analyze_stage2.py                                       # B6 analysis      -> analysis_taskB/stage2/
```
Raw results: `results_taskB/` (final checkpoint `sprint53_taskB_run_20261003_2105.zip`).
