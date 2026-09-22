# Task A: Judge and Scoring Research

User story: As a team relying on judge scores to guide our translation optimization, we want to research the best judge setup and scoring method, so that we have a more reliable and cost effective evaluation signal for GEPA to optimize against.

Note: This task does not depend on paid API access. GLM runs locally, and COMET and chrF++ do not require an LLM provider at all. This makes it the priority task for the sprint while the credit blocker is unresolved.

Acceptance criteria:
Test GLM as a judge on English to Mandarin translations and compare its scores against our current judge.
Test GLM as a judge on English to Cantonese translations and compare its scores against our current judge and, where possible, human review.
Test a combined multi judge setup, two or three judges scored together, against the current single judge setup, on the same set of translations.
Record whether the multi judge setup catches errors, especially Cantonese specific ones, that a single judge misses.
Design and test a severity weighted scoring approach, distinguishing critical errors from minor ones, compared against the current flat score.
Add at least one reference free automatic metric, such as COMET or chrF++, alongside the LLM judge score, and note where it agrees or disagrees with the judge.
Document one clear final recommendation: which judge or judges to use, for which language direction, and which scoring method to use going forward.

