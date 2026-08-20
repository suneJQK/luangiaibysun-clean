from __future__ import annotations

import os
from typing import Any


def generate(*, system_instruction: str, prompt: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Thiếu OPENAI_API_KEY")
    try:
        from openai import OpenAI
    except Exception as exc:
        raise RuntimeError(f"Thiếu thư viện OpenAI: {type(exc).__name__}: {exc}") from exc

    client = OpenAI(api_key=api_key)
    model = os.environ.get("OPENAI_MODEL", "gpt-5.6")
    response = client.responses.create(
        model=model,
        instructions=system_instruction,
        input=prompt,
    )
    text = getattr(response, "output_text", None)
    if not text:
        raise RuntimeError("OpenAI không trả về nội dung")
    return text
