from __future__ import annotations

import os
import random
import time


def _is_transient_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(token in text for token in ("503", "unavailable", "high demand", "429", "resource exhausted", "rate limit"))


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
    model = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
    last_error: Exception | None = None

    # Gemini đôi khi trả 503 khi model đang quá tải. Retry ngắn giúp các spike ngắn
    # không làm hỏng toàn bộ phiên luận giải.
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            text = getattr(response, "text", None)
            if not text:
                raise RuntimeError("Gemini không trả về nội dung")
            return text
        except Exception as exc:
            last_error = exc
            if attempt >= 2 or not _is_transient_error(exc):
                raise
            time.sleep((1.0 * (2 ** attempt)) + random.uniform(0.0, 0.4))

    raise RuntimeError(f"Gemini lỗi tạm thời: {last_error}") from last_error
