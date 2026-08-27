"""
The judge configurations this sprint is trying to choose between. Edit this
list to match whatever configs you actually proposed - the pipeline doesn't
care how many there are, it just scores every one of them against the gold
sets and tells you which wins per direction.

Two axes are varied here, since that's what the earlier GLM-judge work was
comparing:
  - model:          which local Ollama model does the judging
  - scoring_method: "flat"  -> judge gives one holistic 0-100 number directly
                     "mqm"   -> judge lists errors (type+severity); WE compute
                                the severity-weighted score deterministically
                                in Python (never trust the model's arithmetic)

Add/remove entries freely - e.g. add a third model, a different temperature,
or an ensemble entry (handled specially in aggregate.py).
"""

LANG_DISPLAY_NAME = {
    "en_to_cmn": "Standard Mandarin Chinese (Simplified script)",
    "en_to_yue": "Cantonese (Hong Kong written vernacular)",
    "cmn_to_en": "English",
    "yue_to_en": "English",
}

FLAT_PROMPT = """You are an expert professional translation quality evaluator.
Source ({src_lang}): {source}
Machine translation ({tgt_lang}): {mt}

Rate the machine translation's quality from 0 to 100, where 100 is a perfect, publication-quality translation and 0 is completely unusable.
Respond with ONLY a JSON object, nothing else, in exactly this form:
{{"score": <integer 0-100>}}"""

MQM_PROMPT = """You are an expert professional translation quality evaluator following MQM (Multidimensional Quality Metrics) principles.
Source ({src_lang}): {source}
Machine translation ({tgt_lang}): {mt}

Identify every real error in the machine translation. For each error give: the exact erroneous text segment, an error type (one of: Mistranslation, Omission, Addition, Grammar, Spelling, Typography, Untranslated, Unintelligible), and a severity (one of: minor, major, critical).
If there are no errors, return an empty list.
Respond with ONLY a JSON object, nothing else, in exactly this form:
{{"errors": [{{"text": "...", "type": "...", "severity": "minor|major|critical"}}, ...]}}"""


JUDGE_CONFIGS = [
    {"config_id": "glm4_flat", "model": "glm4", "scoring_method": "flat", "temperature": 0.0},
    {"config_id": "glm4_mqm", "model": "glm4", "scoring_method": "mqm", "temperature": 0.0},
    {"config_id": "qwen_flat", "model": "qwen2.5:7b", "scoring_method": "flat", "temperature": 0.0},
    {"config_id": "qwen_mqm", "model": "qwen2.5:7b", "scoring_method": "mqm", "temperature": 0.0},
    # Ensemble: score with both models under the MQM prompt, combine robustly.
    # aggregate.py detects this by the "ensemble_of" key.
    {"config_id": "glm4_qwen_ensemble_mqm", "ensemble_of": ["glm4_mqm", "qwen_mqm"]},
]


def prompt_for(config, source, mt, direction):
    src_lang = "English" if direction.startswith("en_to") else LANG_DISPLAY_NAME[direction]
    tgt_lang = LANG_DISPLAY_NAME[direction] if direction.startswith("en_to") else "English"
    template = FLAT_PROMPT if config["scoring_method"] == "flat" else MQM_PROMPT
    return template.format(src_lang=src_lang, tgt_lang=tgt_lang, source=source, mt=mt)
