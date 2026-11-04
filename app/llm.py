"""Ollama wrapper: fixed temperature/seed (NFR-2) and token counts."""
import os

import ollama


def chat(messages: list[dict], model: str | None = None) -> tuple[str, int, int]:
    r = ollama.chat(
        model=model or os.getenv("OLLAMA_APP_MODEL", "qwen2.5:3b"),
        messages=messages,
        options={"temperature": 0, "seed": 42},
    )
    return r.message.content or "", r.prompt_eval_count or 0, r.eval_count or 0
