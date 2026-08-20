from __future__ import annotations

import os


def generate(*, system_instruction: str, prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Thiếu GEMINI_API_KEY")
    try:
        from google import genai
        from google.genai import types
    except Exception as exc:
        raise RuntimeError(f"Thiếu thư viện Gemini: {type(exc).__name__}: {exc}") from exc

    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.2,
        max_output_tokens=30000,
    )
    response = client.models.generate_content(
        model=os.environ.get("GEMINI_MODEL", "gemini-3.6-flash"),
        contents=prompt,
        config=config,
    )
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini không trả về nội dung")
    return text
