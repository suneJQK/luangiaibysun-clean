from __future__ import annotations

import os


def generate(*, system_instruction: str, prompt: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Thiếu OPENAI_API_KEY")
    try:
        import httpx
        from openai import OpenAI
    except Exception as exc:
        raise RuntimeError(f"Thiếu thư viện OpenAI/httpx: {type(exc).__name__}: {exc}") from exc

    model = os.environ.get("OPENAI_MODEL", "gpt-5.6").strip()
    timeout_seconds = float(os.environ.get("OPENAI_TIMEOUT_SECONDS", "90"))

    # Vercel/Python runtimes can expose proxy-related environment variables.
    # Disable inherited proxy settings for a direct HTTPS connection to OpenAI.
    http_client = httpx.Client(
        timeout=httpx.Timeout(timeout_seconds, connect=20.0),
        trust_env=False,
    )
    try:
        client = OpenAI(api_key=api_key, http_client=http_client)
        response = client.responses.create(
            model=model,
            instructions=system_instruction,
            input=prompt,
        )
    except Exception as exc:
        raise RuntimeError(
            f"OpenAI request failed ({type(exc).__name__}): {exc}"
        ) from exc
    finally:
        http_client.close()

    text = getattr(response, "output_text", None)
    if not text:
        raise RuntimeError("OpenAI không trả về nội dung")
    return text
