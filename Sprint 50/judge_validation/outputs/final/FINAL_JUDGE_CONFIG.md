# Final Judge Configuration

_Generated 2026-08-20. Selection method, gold sets, and full per-sentence scores are in `agreement_detail.json` and `final_judge_config.json` next to this file._

## Summary

| Direction | Final judge config | Spearman rho vs human | MAE | Malformed rate | Gold set size |
|---|---|---|---|---|---|
| English -> Mandarin | `glm4_qwen_ensemble_mqm` | 0.598 | 8.43 | 0.0 | 40 |
| English -> Cantonese | `qwen_flat` | 0.485 | 15.7 | 0.0 | 40 |
| Mandarin -> English | `glm4_qwen_ensemble_mqm` | 0.649 | 7.56 | 0.0 | 40 |
| Cantonese -> English | `qwen_flat` | 0.476 | 14.24 | 0.0 | 49 |

## English -> Mandarin (`en_to_cmn`)

**Gold set source:** SiniticMTError (mandarin.jsonl) - human bilingual annotator error spans

**Selected config:** `glm4_qwen_ensemble_mqm` — Ensemble of glm4_mqm, qwen_mqm, combined by median score (robust to a single outlier judge)

**All configs evaluated on this direction's gold set:**

| Config | Spearman rho | Pearson r | MAE | Bucket agreement | Malformed % | Suspicious-zero % | Disagreement % | Disqualified |
|---|---|---|---|---|---|---|---|---|
| `glm4_qwen_ensemble_mqm` | 0.598 | 0.502 | 8.43 | 0.65 | 0.0 | 0.0 | 0.1 | <- selected |
| `glm4_mqm` | 0.586 | 0.454 | 9.28 | 0.6 | 0.0 | 0.0 | 0.0 |  |
| `qwen_flat` | 0.58 | 0.558 | 23.1 | 0.4 | 0.0 | 0.0 | 0.0 |  |
| `qwen_mqm` | 0.479 | 0.291 | 10.93 | 0.6 | 0.0 | 0.0 | 0.0 |  |
| `glm4_flat` | 0.433 | 0.382 | 11.0 | 0.5 | 0.0 | 0.0 | 0.0 |  |

## English -> Cantonese (`en_to_yue`)

**Gold set source:** SiniticMTError (cantonese.jsonl) - human bilingual annotator error spans

**Selected config:** `qwen_flat` — model=qwen2.5:7b, scoring_method=flat, temperature=0.0

**All configs evaluated on this direction's gold set:**

| Config | Spearman rho | Pearson r | MAE | Bucket agreement | Malformed % | Suspicious-zero % | Disagreement % | Disqualified |
|---|---|---|---|---|---|---|---|---|
| `qwen_flat` | 0.485 | 0.284 | 15.7 | 0.6 | 0.0 | 0.0 | 0.0 | <- selected |
| `qwen_mqm` | 0.394 | 0.319 | 10.78 | 0.65 | 0.0 | 0.0 | 0.0 |  |
| `glm4_flat` | 0.339 | 0.227 | 10.68 | 0.625 | 0.0 | 0.0 | 0.0 |  |
| `glm4_qwen_ensemble_mqm` | 0.175 | 0.266 | 10.7 | 0.55 | 0.0 | 0.0 | 0.025 |  |
| `glm4_mqm` | -0.035 | 0.094 | 11.82 | 0.4 | 0.0 | 0.0 | 0.0 |  |

## Mandarin -> English (`cmn_to_en`)

**Gold set source:** Google wmt-mqm-human-evaluation (newstest2021 zh-en) - professional translator MQM

**Selected config:** `glm4_qwen_ensemble_mqm` — Ensemble of glm4_mqm, qwen_mqm, combined by median score (robust to a single outlier judge)

**All configs evaluated on this direction's gold set:**

| Config | Spearman rho | Pearson r | MAE | Bucket agreement | Malformed % | Suspicious-zero % | Disagreement % | Disqualified |
|---|---|---|---|---|---|---|---|---|
| `glm4_qwen_ensemble_mqm` | 0.649 | 0.433 | 7.56 | 0.7 | 0.0 | 0.0 | 0.1 | <- selected |
| `glm4_mqm` | 0.59 | 0.317 | 9.92 | 0.641 | 0.025 | 0.0 | 0.0 |  |
| `glm4_flat` | 0.489 | 0.486 | 6.1 | 0.675 | 0.0 | 0.0 | 0.0 |  |
| `qwen_mqm` | 0.478 | 0.375 | 7.65 | 0.65 | 0.0 | 0.0 | 0.0 |  |
| `qwen_flat` | 0.41 | 0.385 | 9.0 | 0.55 | 0.0 | 0.0 | 0.0 |  |

## Cantonese -> English (`yue_to_en`)

**Gold set source:** Locally built by you: Cantonese source (from SiniticMTError ref field) + your own local MT output + your own bilingual error annotation (no free public dataset exists for this direction)

**Selected config:** `qwen_flat` — model=qwen2.5:7b, scoring_method=flat, temperature=0.0

**All configs evaluated on this direction's gold set:**

| Config | Spearman rho | Pearson r | MAE | Bucket agreement | Malformed % | Suspicious-zero % | Disagreement % | Disqualified |
|---|---|---|---|---|---|---|---|---|
| `qwen_flat` | 0.476 | 0.712 | 14.24 | 0.776 | 0.0 | 0.0 | 0.0 | <- selected |
| `glm4_flat` | 0.437 | 0.644 | 7.0 | 0.98 | 0.0 | 0.0 | 0.0 |  |
| `glm4_qwen_ensemble_mqm` | 0.243 | 0.043 | 10.01 | 0.796 | 0.0 | 0.0 | 0.041 |  |
| `glm4_mqm` | 0.164 | -0.05 | 12.31 | 0.755 | 0.0 | 0.0 | 0.0 |  |
| `qwen_mqm` | 0.082 | 0.123 | 8.2 | 0.878 | 0.0 | 0.0 | 0.0 |  |

## Aggregation guardrails applied

- **Malformed output:** any judge response that fails to parse as valid JSON after retries is excluded from correlation math and counted separately as `malformed_rate`. A config with malformed_rate above the threshold in `config.py` is automatically disqualified, regardless of how well it scores when it does work.
- **Suspicious zero scores:** a score <= 5 with zero reported error spans is a self-contradiction (the judge's number and its own reasoning disagree) and is excluded from correlation math, tracked separately as `suspicious_zero_rate`.
- **Judge disagreement (ensemble configs only):** per sentence, if the underlying judges' valid scores differ by more than the configured spread, the sentence is flagged `high_disagreement` and the ensemble score is the median (not the mean) of valid judge scores, so one outlier judge can't silently skew the combined score. The disagreement rate is reported per config.
- **Selection is by rank correlation (Spearman), not raw score matching**, since what matters for GEPA is that the judge ranks better/worse translations correctly, not that its 0-100 scale matches the human MQM formula exactly.
