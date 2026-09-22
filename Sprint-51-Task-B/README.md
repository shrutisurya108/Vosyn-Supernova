# Sprint 51 Task B: Build an Automated Mandarin Inference, Evaluation and Rollback Pipeline

Description

Build an independent pipeline that loads a candidate checkpoint, compares it with the DSPy/GEPA baseline, runs automated readiness checks and verifies rollback.

User Story

As a Machine Learning Engineer, I want an automated evaluation and rollback pipeline, so that we can decide whether a candidate should advance, be revised or be rejected.

Acceptance Criteria

The pipeline must accept configurable model, adapter, candidate and DSPy/GEPA baseline locations. It may use its own candidate fixture and must run through documented command. New baseline and candidate outputs must be generated on the same examples. A reconstructed baseline must be clearly labelled and versioned. Qwen3 judge must score both systems. Qwen3 8B is primary and Qwen3 4B is the local fallback. Before scoring baseline and candidate outputs, the Qwen3 configuration must be checked on the Sprint 50 golden judge-calibration dataset and frozen in judge_registry.json. Golden-set results must remain separate from candidate evaluation results. Evaluation data must remain separate, and the sealed final test must remain closed. The pipeline must check quality, wrong-language and invalid outputs, safety, memorization, domain regression, format, latency and failures. Metrics and decision rules must be frozen in readiness_policy.json. The result must be advance, review-revise or reject and keep baseline. Critical safety, leakage, contamination or rollback failures require rejection. The submission must include tested code, configurations, outputs, readiness report, rollback evidence, working notebook and exact GitHub link.
