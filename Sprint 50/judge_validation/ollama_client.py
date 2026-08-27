"""
Tiny wrapper around Ollama's local HTTP API. No paid API keys anywhere.

Prereqs on your Mac (one-time):
    1. Install Ollama:      https://ollama.com/download  (free)
    2. Pull the model(s):   ollama pull qwen2.5:7b
                             ollama pull glm4
    3. Make sure the app / `ollama serve` is running (it auto-starts after install).

This uses only the stdlib `urllib` + `json` - no extra pip install needed just
to talk to Ollama.
"""

import json
import urllib.request

from config import OLLAMA_HOST, OLLAMA_TIMEOUT


def ollama_generate(model, prompt, temperature=0.0):
    """Single-shot call to /api/generate. Returns the raw text response."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body.get("response", "")


def check_ollama_available():
    try:
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return True, [m["name"] for m in data.get("models", [])]
    except Exception as e:
        return False, str(e)
