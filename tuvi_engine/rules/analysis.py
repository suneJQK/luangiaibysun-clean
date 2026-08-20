"""High-level V2 rule orchestration.

This module intentionally builds on the existing deterministic chart output;
it does not replace the low-level an-sao algorithm.
"""
from __future__ import annotations

from typing import Any

from ..ai_context import build_ai_context
from .cach_cuc import detect_cach_cuc


def analyze_chart(chart: dict[str, Any]) -> dict[str, Any]:
    result = dict(chart)
    result["cach_cuc"] = detect_cach_cuc(chart)
    tb = chart.get("thien_ban") or {}
    result["luan_giai"] = {
        "menh": {
            "cung": "Mệnh",
            "chu_menh": tb.get("menh_chu") or tb.get("menh"),
            "ban_menh": tb.get("ban_menh"),
            "menh_chu": tb.get("menh_chu"),
        },
        "than": {"than_chu": tb.get("than_chu")},
        "van_han": {
            "dai_han": "Đang sử dụng dữ liệu đại vận của từng cung khi engine nguồn cung cấp.",
            "tieu_han": "Đang sử dụng dữ liệu tiểu hạn của từng cung khi engine nguồn cung cấp.",
            "luu_nien": "Rule layer sẵn sàng mở rộng khi bổ sung bảng lưu niên.",
        },
    }
    result["ai_context"] = build_ai_context(result)
    return result
