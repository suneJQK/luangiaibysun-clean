from __future__ import annotations

from typing import Literal

Provider = Literal["gemini", "openai"]


def normalize_provider(value: str | None) -> Provider:
    return "openai" if str(value or "").strip().lower() in {"openai", "chatgpt", "gpt"} else "gemini"


def generate(*, provider: str | None, system_instruction: str, prompt: str) -> tuple[str, Provider]:
    selected = normalize_provider(provider)
    if selected == "openai":
        from .openai import generate as generate_openai
        return generate_openai(system_instruction=system_instruction, prompt=prompt), selected
    from .gemini import generate as generate_gemini
    return generate_gemini(system_instruction=system_instruction, prompt=prompt), selected
