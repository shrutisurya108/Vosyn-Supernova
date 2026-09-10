# Sprint 51 Task A: Build a Reproducible Mandarin Data and Fine-Tuning Pipeline

Description
Build a reusable pipeline that prepares English→Mandarin data, runs fine-tuning experiment and creates loadable candidate checkpoint. Cantonese is excluded for now.

User Story
As a Machine Learning Engineer, we want a reproducible fine-tuning pipeline, so that we can create versioned translation candidates.

Acceptance Criteria
The model, dataset, language direction, training method, seed, training settings and output paths must be configurable. The method must be selected after a hardware smoke test; LoRA, QLoRA or another feasible method may be used. Data must be validated, versioned and hashed. Fine-tuning, judge-calibration, prompt-validation and sealed final-test data must remain separate. The pipeline must support dry runs, logging, checkpoints and resume. Mandarin run must complete on Kaggle, Colab or local resources. The resulting checkpoint must load successfully and generate a Mandarin translation. Its configuration, data version and hashes must be saved in candidate_manifest.json. The submission must include tested code, configurations, manifests, logs, report, working notebook, exact GitHub link and the loadable candidate or download path.
