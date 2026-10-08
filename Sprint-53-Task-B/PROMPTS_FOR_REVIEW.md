# Task B — all prompts (for review)

Placeholders: {src_lang} = English · {tgt_lang} = Standard Mandarin Chinese (Simplified script) · {source}, {mt}, {a}, {b} = the item being judged. Doubled braces {{ }} print as single braces.

## Baseline · flat 0–100 (Sprint 50, verbatim)

Output format: `flat` · length ≈ 497 characters

```text
You are an expert professional translation quality evaluator.
Source ({src_lang}): {source}
Machine translation ({tgt_lang}): {mt}

Rate the machine translation's quality from 0 to 100, where 100 is a perfect, publication-quality translation and 0 is completely unusable.
Respond with ONLY a JSON object, nothing else, in exactly this form:
{{"score": <integer 0-100>}}
```

## Baseline · MQM (Sprint 50, verbatim)

Output format: `mqm` · length ≈ 801 characters

```text
You are an expert professional translation quality evaluator following MQM (Multidimensional Quality Metrics) principles.
Source ({src_lang}): {source}
Machine translation ({tgt_lang}): {mt}

Identify every real error in the machine translation. For each error give: the exact erroneous text segment, an error type (one of: Mistranslation, Omission, Addition, Grammar, Spelling, Typography, Untranslated, Unintelligible), and a severity (one of: minor, major, critical).
If there are no errors, return an empty list.
Respond with ONLY a JSON object, nothing else, in exactly this form:
{{"errors": [{{"text": "...", "type": "...", "severity": "minor|major|critical"}}, ...]}}
```

## Baseline · pairwise (Task A)

Output format: `pairwise` · length ≈ 407 characters

```text
You are an expert professional translation quality evaluator.
Source ({src_lang}): {source}
Translation A ({tgt_lang}): {a}
Translation B ({tgt_lang}): {b}

Which translation is better? Answer "A", "B", or "tie" if they are equally good.
Respond with ONLY a JSON object, nothing else, in exactly this form:
{{"better": "A|B|tie"}}
```

## S1 · `flat_rubric` (compared with baseline `flat`)

Output format: `flat` · length ≈ 1140 characters

```text
You are an expert professional translation quality evaluator.
Source ({src_lang}): {source}
Machine translation ({tgt_lang}): {mt}

Rate the machine translation's quality from 0 to 100 using this scoring rubric:
- 85-100: The meaning is fully preserved and the Chinese is natural. At most a trivial wording issue.
- 60-84: The meaning is preserved, but there are noticeable issues that do not mislead the reader (stiff or word-for-word phrasing, awkward word order, slightly wrong tone).
- 40-59: One meaning error that misleads the reader about a secondary detail, or several small issues together.
- 20-39: A meaning error on a central point (for example a wrong number, name, negation, time or place, or an idiom translated word for word), or the sentence is hard to understand.
- 0-19: Mostly wrong, nonsensical, or largely untranslated.
First decide which band fits best, then choose a score within that band.
Respond with ONLY a JSON object, nothing else, in exactly this form:
{{"score": <integer 0-100>}}
```

## S2 · `mqm_fewshot` (compared with baseline `mqm`)

Output format: `mqm` · length ≈ 1709 characters

```text
You are an expert professional translation quality evaluator following MQM (Multidimensional Quality Metrics) principles.
Identify every real error in the machine translation. For each error give: the exact erroneous text segment, an error type (one of: Mistranslation, Omission, Addition, Grammar, Spelling, Typography, Untranslated, Unintelligible), and a severity (one of: minor, major, critical).
If there are no errors, return an empty list.
Respond with ONLY a JSON object, nothing else, in exactly this form:
{{"errors": [{{"text": "...", "type": "...", "severity": "minor|major|critical"}}, ...]}}

Here are three examples of correct evaluations.

Example 1
Source (English): After months of negotiations, the two companies finally decided to bury the hatchet.
Machine translation (Standard Mandarin Chinese (Simplified script)): 双方公司谈了好几个月，最后总算冰释前嫌。
Answer: {{"errors": []}}

Example 2
Source (English): The rent increased by 15% to $2,300 a month, effective October 1.
Machine translation (Standard Mandarin Chinese (Simplified script)): 房租上涨了15%，涨至每年2300美元，自10月1日起生效。
Answer: {{"errors": [{{"text": "每年", "type": "Mistranslation", "severity": "major"}}]}}

Example 3
Source (English): However, the reduction of the threat level to severe does not mean the overall threat has gone away.'
Machine translation (Standard Mandarin Chinese (Simplified script)): 然而,降低威胁水平到严重并不意味着整体威胁已经消失了'.
Answer: {{"errors": [{{"text": "降低威胁水平到严重", "type": "Omission", "severity": "minor"}}]}}

Now evaluate this translation.
Source ({src_lang}): {source}
Machine translation ({tgt_lang}): {mt}
Answer:
```

## S3 · `mqm_steps` (compared with baseline `mqm`)

Output format: `mqm_steps` · length ≈ 1633 characters

```text
You are an expert professional translation quality evaluator following MQM (Multidimensional Quality Metrics) principles.

[SOURCE TEXT - {src_lang}]
{source}
[END OF SOURCE TEXT]

[TRANSLATION TO EVALUATE - {tgt_lang}]
{mt}
[END OF TRANSLATION]

Evaluate the translation step by step:
Step 1 - Meaning: compare each part of the source with the translation. Is anything mistranslated, missing, or added?
Step 2 - Names, numbers and terms: check every name, number, date, unit and technical term.
Step 3 - Idioms and culture: idioms and cultural references must be translated by their meaning, not word for word. Check any that appear.
Step 4 - Valid variation: different wording, word order or sentence structure that keeps the same meaning is NOT an error. Drop any problem from steps 1-3 that is only a difference in wording.
Step 5 - List the remaining errors. Quote each error exactly as it appears in the TRANSLATION - never quote the English source. For each error give an error type (one of: Mistranslation, Omission, Addition, Grammar, Spelling, Typography, Untranslated, Unintelligible) and a severity (one of: minor, major, critical).
Write one short sentence for each of steps 1-4. If there are no errors, return an empty list.
Respond with ONLY a JSON object, nothing else, in exactly this form:
{{"steps": {{"meaning": "...", "names_numbers_terms": "...", "idioms_culture": "...", "valid_variation": "..."}}, "errors": [{{"text": "...", "type": "...", "severity": "minor|major|critical"}}, ...]}}
```

## S4 · `flat_accflu` (compared with baseline `flat`)

Output format: `accflu` · length ≈ 912 characters

```text
You are an expert professional translation quality evaluator.
Source ({src_lang}): {source}
Machine translation ({tgt_lang}): {mt}

Rate the machine translation on two separate criteria, each from 0 to 100:
1. Accuracy - does the translation convey exactly the meaning of the source? 100 = the same meaning, nothing wrong, missing or added; 0 = the meaning is completely wrong. Judge accuracy only: ignore how natural the Chinese sounds.
2. Fluency - is the Chinese natural, grammatical and appropriate in tone, as a native speaker would write it? 100 = perfectly natural; 0 = unreadable. Judge fluency only: ignore whether the meaning matches the source.
Respond with ONLY a JSON object, nothing else, in exactly this form:
{{"accuracy": <integer 0-100>, "fluency": <integer 0-100>}}
```

## S5 · `pairwise_tie` (compared with baseline `pairwise`)

Output format: `pairwise_tie` · length ≈ 903 characters

```text
You are an expert professional translation quality evaluator.
Source ({src_lang}): {source}
Translation A ({tgt_lang}): {a}
Translation B ({tgt_lang}): {b}

First assess each translation on its own: note any meaning errors (mistranslation, omission, addition) and any problems with naturalness. Then compare them.
- Answer "A" or "B" only if that translation is clearly better: it has fewer or less serious meaning errors, or, when both are accurate, it is clearly more natural.
- Answer "tie" if both are equally good or equally flawed - including when both are correct but worded differently.
- The order in which the translations are shown is random and must not affect your decision.
Respond with ONLY a JSON object, nothing else, in exactly this form:
{{"assessment_a": "...", "assessment_b": "...", "better": "A|B|tie"}}
```

## S4 combination rule

final score = 0.8 × accuracy + 0.2 × fluency (computed in code)

## Few-shot examples and why

1. `B::N_IDI1::paraphrase` — Correct and natural; the idiom is rendered by meaning (冰释前嫌). Different wording is not an error.
2. `B::N_NUM1::fluent_wrong` — 'A month' was translated as 'a year' (每年 instead of 每月) - the reader is misinformed about the amount.
3. `A::en_to_cmn_258` — 'To severe' refers to a threat level (严重级别); the word 级别 is missing. The meaning is still clear, so it is minor.

Left out of Stage 1 scoring for every prompt: sources ['N_IDI1', 'N_NUM1'], Set A ['A::en_to_cmn_258'].
