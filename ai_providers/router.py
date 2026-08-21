from __future__ import annotations

from typing import Literal

Provider = Literal["gemini", "openai"]


def normalize_provider(value: str | None) -> Provider:
    return "openai" if str(value or "").strip().lower() in {"openai", "chatgpt", "gpt"} else "gemini"


def _load_provider(provider: Provider):
    if provider == "openai":
        from .openai import generate as generate_openai
        return generate_openai
    from .gemini import generate as generate_gemini
    return generate_gemini


def _is_transient_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(token in text for token in (
        "503", "unavailable", "high demand", "429", "resource exhausted", "rate limit", "temporarily",
    ))


def generate(*, provider: str | None, system_instruction: str, prompt: str) -> tuple[str, Provider]:
    selected = normalize_provider(provider)
    fallback: Provider = "openai" if selected == "gemini" else "gemini"

    try:
        return _load_provider(selected)(
            system_instruction=system_instruction,
            prompt=prompt,
        ), selected
    except Exception as first_error:
        # Chỉ tự chuyển provider khi lỗi có tính tạm thời. Lỗi cấu hình/quota cố định
        # vẫn được giữ nguyên để báo đúng nguyên nhân.
        if not _is_transient_error(first_error):
            raise

        fallback_key = "OPENAI_API_KEY" if fallback == "openai" else "GEMINI_API_KEY"
        import os
        if not os.environ.get(fallback_key, "").strip():
            raise RuntimeError(
                f"{selected.title()} đang lỗi tạm thời ({first_error}), "
                f"và provider dự phòng {fallback.title()} chưa được cấu hình ({fallback_key})."
            ) from first_error

        try:
            return _load_provider(fallback)(
                system_instruction=system_instruction,
                prompt=prompt,
            ), fallback
        except Exception as fallback_error:
            raise RuntimeError(
                f"{selected.title()} lỗi tạm thời: {first_error}; "
                f"đã thử {fallback.title()} nhưng cũng lỗi: {fallback_error}"
            ) from fallback_error
