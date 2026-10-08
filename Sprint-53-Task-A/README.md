# Sprint 53 Task A

Explore and analyze common failure cases that occur when using LLM-as-a-Judge to evaluate English-to-Mandarin translations. Identify situations where judge outputs may be inconsistent, inaccurate, biased, or sensitive to evaluation setup.

# User Story

As an ML Engineer, I want to investigate failure cases when using LLM-as-a-Judge for English-to-Mandarin translation evaluation so that we can understand where automated LLM-based evaluation becomes unreliable or inconsistent.

# Description

Research and experimentally explore common failure modes that occur when an LLM evaluates English-to-Mandarin translations.
The investigation will focus on identifying cases where the judge produces inconsistent scores, incorrect assessments, or judgments that do not adequately reflect translation quality.
Potential areas to investigate include:

- Sensitivity to prompt wording and instruction changes
- Variability across repeated evaluations of the same translation
- Semantic equivalence despite different Mandarin wording
- Literal versus natural/fluent translations
- Handling of idioms, cultural expressions, and context-dependent language
- Simplified versus Traditional Chinese variations
- Proper nouns, terminology, and named entities
- Over-reliance on lexical similarity to a reference translation
- Fluency versus semantic-accuracy trade-offs
- Position/order bias when comparing multiple translations
- Score calibration and inconsistent interpretation of evaluation scales
- Reasoning or explanation inconsistencies
- Cases where multiple translations are valid but receive substantially different judgments

# Acceptance Criteria

- Major LLM-as-a-Judge failure categories are identified and documented.
- English-to-Mandarin examples are used to demonstrate relevant failure cases.
- Repeated evaluations are performed to investigate consistency.
- Observed inconsistencies and potential causes are documented.
- Findings clearly identify areas that can be investigated through prompt engineering.
- Research findings and experimental observations are summarized in Notion.
