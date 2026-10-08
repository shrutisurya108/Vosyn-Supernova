# Task B · Step B5 — new prompts (combined prompt C + rewordings)

C = S2 few-shot examples + S3 delimiters + 'quote only from the TRANSLATION' + S3 steps 1-3 as a one-line checklist. It does NOT contain S3 step 4 ('different wording is not an error'), which made the judge explain real errors away in Stage 1.

Rewordings (wording-robustness test): same instructions, same few-shot examples (byte-identical), same JSON schema; rw1 = paraphrase in the same order, rw2 = paraphrase with a different order/framing. Baseline MQM rewording 1 = Task A's `mqm_reworded`.

## `mqm_combined`

Output format: `mqm` · rendered length ≈ 2198 characters

```text
You are an expert professional translation quality evaluator following MQM (Multidimensional Quality Metrics) principles.
Identify every real error in the machine translation. Check the meaning of every part of the source; every name, number, date, unit and technical term; and every idiom or cultural reference (it must be translated by its meaning, not word for word).
For each error give: the exact erroneous text segment, quoted exactly as it appears in the TRANSLATION (never quote the English source), an error type (one of: Mistranslation, Omission, Addition, Grammar, Spelling, Typography, Untranslated, Unintelligible), and a severity (one of: minor, major, critical).
If there are no errors, return an empty list.
Respond with ONLY a JSON object, nothing else, in exactly this form:
{{"errors": [{{"text": "...", "type": "...", "severity": "minor|major|critical"}}, ...]}}

Here are three examples of correct evaluations.

Example 1
[SOURCE TEXT - English]
After months of negotiations, the two companies finally decided to bury the hatchet.
[END OF SOURCE TEXT]
[TRANSLATION TO EVALUATE - Standard Mandarin Chinese (Simplified script)]
双方公司谈了好几个月，最后总算冰释前嫌。
[END OF TRANSLATION]
Answer: {{"errors": []}}

Example 2
[SOURCE TEXT - English]
The rent increased by 15% to $2,300 a month, effective October 1.
[END OF SOURCE TEXT]
[TRANSLATION TO EVALUATE - Standard Mandarin Chinese (Simplified script)]
房租上涨了15%，涨至每年2300美元，自10月1日起生效。
[END OF TRANSLATION]
Answer: {{"errors": [{{"text": "每年", "type": "Mistranslation", "severity": "major"}}]}}

Example 3
[SOURCE TEXT - English]
However, the reduction of the threat level to severe does not mean the overall threat has gone away.'
[END OF SOURCE TEXT]
[TRANSLATION TO EVALUATE - Standard Mandarin Chinese (Simplified script)]
然而,降低威胁水平到严重并不意味着整体威胁已经消失了'.
[END OF TRANSLATION]
Answer: {{"errors": [{{"text": "降低威胁水平到严重", "type": "Omission", "severity": "minor"}}]}}

Now evaluate this translation.
[SOURCE TEXT - {src_lang}]
{source}
[END OF SOURCE TEXT]
[TRANSLATION TO EVALUATE - {tgt_lang}]
{mt}
[END OF TRANSLATION]
Answer:
```

## `mqm_reworded`

Output format: `mqm` · rendered length ≈ 722 characters

```text
You are a professional translation quality assessor who applies the MQM (Multidimensional Quality Metrics) framework.
Source text ({src_lang}): {source}
Translation under review ({tgt_lang}): {mt}

List all genuine errors in the translation. For every error, provide the exact problematic span from the translation, its error category (choose from: Mistranslation, Omission, Addition, Grammar, Spelling, Typography, Untranslated, Unintelligible), and its severity (choose from: minor, major, critical).
Return an empty list if the translation has no errors.
Reply with ONLY a JSON object and nothing else, using exactly this format:
{{"errors": [{{"text": "...", "type": "...", "severity": "minor|major|critical"}}, ...]}}
```

## `mqm_rw2`

Output format: `mqm` · rendered length ≈ 873 characters

```text
Act as a senior translation reviewer who uses the MQM (Multidimensional Quality Metrics) error typology.
Your task is to find each actual error in the machine translation below and report it.
Report every error with three fields: the erroneous words copied exactly ("text"), the category ("type": Mistranslation, Omission, Addition, Grammar, Spelling, Typography, Untranslated or Unintelligible) and the seriousness ("severity": minor, major or critical).
When the translation has no errors, give an empty list.

Source ({src_lang}): {source}
Machine translation ({tgt_lang}): {mt}

Output a single JSON object and nothing else, formatted exactly like this:
{{"errors": [{{"text": "...", "type": "...", "severity": "minor|major|critical"}}, ...]}}
```

## `mqm_fewshot_rw1`

Output format: `mqm` · rendered length ≈ 1739 characters

```text
You are a professional translation quality assessor who applies the MQM (Multidimensional Quality Metrics) framework.
List all genuine errors in the machine translation. For every error, provide the exact problematic span, its error category (choose from: Mistranslation, Omission, Addition, Grammar, Spelling, Typography, Untranslated, Unintelligible), and its severity (choose from: minor, major, critical).
Return an empty list if the translation has no errors.
Reply with ONLY a JSON object and nothing else, using exactly this format:
{{"errors": [{{"text": "...", "type": "...", "severity": "minor|major|critical"}}, ...]}}

Below are three worked examples of correct assessments.

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

Now assess this translation.
Source ({src_lang}): {source}
Machine translation ({tgt_lang}): {mt}
Answer:
```

## `mqm_fewshot_rw2`

Output format: `mqm` · rendered length ≈ 1736 characters

```text
Act as a senior translation reviewer who uses the MQM (Multidimensional Quality Metrics) error typology.
The three worked examples below show how translations should be assessed.

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

Your task: find each actual error in the next machine translation. Report every error with the erroneous words copied exactly ("text"), the category ("type": one of Mistranslation, Omission, Addition, Grammar, Spelling, Typography, Untranslated, Unintelligible) and the seriousness ("severity": minor, major or critical). When there are no errors, give an empty list.
Output a single JSON object and nothing else, formatted exactly like this:
{{"errors": [{{"text": "...", "type": "...", "severity": "minor|major|critical"}}, ...]}}

Source ({src_lang}): {source}
Machine translation ({tgt_lang}): {mt}
Answer:
```

## `mqm_combined_rw1`

Output format: `mqm` · rendered length ≈ 2211 characters

```text
You are a professional translation quality assessor who applies the MQM (Multidimensional Quality Metrics) framework.
List all genuine errors in the machine translation. Verify the meaning of each part of the source; each name, number, date, unit and technical term; and each idiom or cultural reference (it has to be rendered by its meaning, not literally).
For every error, provide the exact problematic span, copied exactly from the TRANSLATION (do not quote the English source), its error category (choose from: Mistranslation, Omission, Addition, Grammar, Spelling, Typography, Untranslated, Unintelligible), and its severity (choose from: minor, major, critical).
Return an empty list if the translation has no errors.
Reply with ONLY a JSON object and nothing else, using exactly this format:
{{"errors": [{{"text": "...", "type": "...", "severity": "minor|major|critical"}}, ...]}}

Below are three worked examples of correct assessments.

Example 1
[SOURCE TEXT - English]
After months of negotiations, the two companies finally decided to bury the hatchet.
[END OF SOURCE TEXT]
[TRANSLATION TO EVALUATE - Standard Mandarin Chinese (Simplified script)]
双方公司谈了好几个月，最后总算冰释前嫌。
[END OF TRANSLATION]
Answer: {{"errors": []}}

Example 2
[SOURCE TEXT - English]
The rent increased by 15% to $2,300 a month, effective October 1.
[END OF SOURCE TEXT]
[TRANSLATION TO EVALUATE - Standard Mandarin Chinese (Simplified script)]
房租上涨了15%，涨至每年2300美元，自10月1日起生效。
[END OF TRANSLATION]
Answer: {{"errors": [{{"text": "每年", "type": "Mistranslation", "severity": "major"}}]}}

Example 3
[SOURCE TEXT - English]
However, the reduction of the threat level to severe does not mean the overall threat has gone away.'
[END OF SOURCE TEXT]
[TRANSLATION TO EVALUATE - Standard Mandarin Chinese (Simplified script)]
然而,降低威胁水平到严重并不意味着整体威胁已经消失了'.
[END OF TRANSLATION]
Answer: {{"errors": [{{"text": "降低威胁水平到严重", "type": "Omission", "severity": "minor"}}]}}

Now assess this translation.
[SOURCE TEXT - {src_lang}]
{source}
[END OF SOURCE TEXT]
[TRANSLATION TO EVALUATE - {tgt_lang}]
{mt}
[END OF TRANSLATION]
Answer:
```

## `mqm_combined_rw2`

Output format: `mqm` · rendered length ≈ 2201 characters

```text
Act as a senior translation reviewer who uses the MQM (Multidimensional Quality Metrics) error typology.
The three worked examples below show how translations should be assessed.

Example 1
[SOURCE TEXT - English]
After months of negotiations, the two companies finally decided to bury the hatchet.
[END OF SOURCE TEXT]
[TRANSLATION TO EVALUATE - Standard Mandarin Chinese (Simplified script)]
双方公司谈了好几个月，最后总算冰释前嫌。
[END OF TRANSLATION]
Answer: {{"errors": []}}

Example 2
[SOURCE TEXT - English]
The rent increased by 15% to $2,300 a month, effective October 1.
[END OF SOURCE TEXT]
[TRANSLATION TO EVALUATE - Standard Mandarin Chinese (Simplified script)]
房租上涨了15%，涨至每年2300美元，自10月1日起生效。
[END OF TRANSLATION]
Answer: {{"errors": [{{"text": "每年", "type": "Mistranslation", "severity": "major"}}]}}

Example 3
[SOURCE TEXT - English]
However, the reduction of the threat level to severe does not mean the overall threat has gone away.'
[END OF SOURCE TEXT]
[TRANSLATION TO EVALUATE - Standard Mandarin Chinese (Simplified script)]
然而,降低威胁水平到严重并不意味着整体威胁已经消失了'.
[END OF TRANSLATION]
Answer: {{"errors": [{{"text": "降低威胁水平到严重", "type": "Omission", "severity": "minor"}}]}}

Your task: find each actual error in the next machine translation. Go through the meaning of the whole source, then all names, numbers, dates, units and technical terms, then any idioms or cultural references (these need a meaning-based rendering, not a literal one).
Report every error with the erroneous words copied exactly from the TRANSLATION, never from the English source ("text"), the category ("type": one of Mistranslation, Omission, Addition, Grammar, Spelling, Typography, Untranslated, Unintelligible) and the seriousness ("severity": minor, major or critical). When there are no errors, give an empty list.
Output a single JSON object and nothing else, formatted exactly like this:
{{"errors": [{{"text": "...", "type": "...", "severity": "minor|major|critical"}}, ...]}}

[SOURCE TEXT - {src_lang}]
{source}
[END OF SOURCE TEXT]
[TRANSLATION TO EVALUATE - {tgt_lang}]
{mt}
[END OF TRANSLATION]
Answer:
```

## `pairwise_rw1`

Output format: `pairwise` · rendered length ≈ 435 characters

```text
You are a professional translation quality assessor.
Source text ({src_lang}): {source}
Translation A ({tgt_lang}): {a}
Translation B ({tgt_lang}): {b}

Which of the two translations is of higher quality? Reply "A", "B", or "tie" if they are of equal quality.
Reply with ONLY a JSON object and nothing else, using exactly this format:
{{"better": "A|B|tie"}}
```

## `pairwise_rw2`

Output format: `pairwise` · rendered length ≈ 452 characters

```text
Act as a senior translation reviewer and compare two translations of the same source sentence.
Decide which one is better: "A", "B", or "tie" when neither is better than the other.

Source ({src_lang}): {source}
Translation A ({tgt_lang}): {a}
Translation B ({tgt_lang}): {b}

Output a single JSON object and nothing else, formatted exactly like this:
{{"better": "A|B|tie"}}
```

## `pairwise_tie_rw1`

Output format: `pairwise_tie` · rendered length ≈ 910 characters

```text
You are a professional translation quality assessor.
Source text ({src_lang}): {source}
Translation A ({tgt_lang}): {a}
Translation B ({tgt_lang}): {b}

Begin by assessing each translation separately: note any meaning errors (mistranslation, omission, addition) and any naturalness problems. Then compare the two.
- Reply "A" or "B" only when that translation is clearly better: it has fewer or less serious meaning errors or, if both are accurate, it is clearly more natural.
- Reply "tie" when both are equally good or equally flawed - this includes two correct translations with different wording.
- The translations are shown in random order; the order must not influence your answer.
Reply with ONLY a JSON object and nothing else, using exactly this format:
{{"assessment_a": "...", "assessment_b": "...", "better": "A|B|tie"}}
```

## `pairwise_tie_rw2`

Output format: `pairwise_tie` · rendered length ≈ 919 characters

```text
Act as a senior translation reviewer and compare two translations of the same source sentence. They appear in random order, and that order must play no part in your decision.

Source ({src_lang}): {source}
Translation A ({tgt_lang}): {a}
Translation B ({tgt_lang}): {b}

Write a short assessment of each translation on its own (meaning errors such as mistranslation, omission or addition; naturalness problems), and only then compare them.
Give "tie" when the two are equally good or equally flawed, including when both are correct but use different words. Give "A" or "B" only when that one is clearly better - fewer or less serious meaning errors, or, if both are accurate, clearly more natural.
Output a single JSON object and nothing else, formatted exactly like this:
{{"assessment_a": "...", "assessment_b": "...", "better": "A|B|tie"}}
```

