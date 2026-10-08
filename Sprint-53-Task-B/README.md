# Sprint 53 Task B

Investigate prompt-engineering techniques that can improve the consistency and reliability of LLM-as-a-Judge outputs for English-to-Mandarin translation evaluation. Compare different prompt structures and identify promising approaches for more stable evaluation results.

# User Story

As an ML Engineer, I want to explore prompt-engineering strategies for LLM-as-a-Judge evaluation so that English-to-Mandarin translation assessments produce more consistent and reliable outputs.

# Description

Explore and test prompt-engineering approaches designed to reduce variability in LLM-as-a-Judge evaluation of English-to-Mandarin translations.
The experiments will build on the failure cases identified in User Story 1 and investigate whether clearer evaluation instructions, structured rubrics, output constraints, and other prompting strategies improve consistency.
Potential strategies include:

- Explicit evaluation criteria
- Clearly defined scoring rubrics
- Structured JSON outputs
- Separating semantic accuracy and fluency evaluation
- Few-shot evaluation examples
- Reference-based versus reference-free evaluation prompts
- Explicit instructions for handling valid translation variations
- Instructions for idioms and culturally appropriate translations
- Score definitions and calibration examples
- Step-by-step evaluation criteria
- Pairwise evaluation versus absolute scoring
- Randomized candidate ordering to investigate position bias
- Lower-variance prompt structures and deterministic output constraints

# Acceptance Criteria

- A baseline evaluation prompt is established.
- Multiple prompt-engineering approaches are designed and tested.
- Experiments use representative English-to-Mandarin translation examples.
- Each selected prompt configuration is evaluated across repeated runs.
- Consistency of scores or rankings is compared across prompt approaches.
- Improvements and remaining limitations are documented.
- A recommended prompt structure or set of prompting guidelines is proposed based on experimental findings.
