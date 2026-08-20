"""High-level V2 rule orchestration with mandatory Cách Cục reasoning."""
from __future__ import annotations

from typing import Any

from ..ai_context import build_ai_context
from .cach_cuc import detect_cach_cuc


def _build_cach_cuc_analysis(matched: list[dict[str, Any]]) -> dict[str, Any]:
    analyses: list[dict[str, Any]] = []
    for item in matched:
        if not isinstance(item, dict):
            continue
        analyses.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "category": item.get("category"),
                "description": item.get("description"),
                "reason": item.get("reason"),
                "conditions": item.get("conditions", {}),
                "binh_chu": item.get("binh_chu", ""),
                "uu_khuyet_diem": item.get("uu_khuyet_diem", ""),
                "ai_instruction": (
                    "Dùng Cách Cục này như một kết luận có bằng chứng. "
                    "Đối chiếu với sao đồng cung, Tam Hợp, Xung Chiếu, Nhị Hợp, "
                    "Giáp Cung và Tuần/Triệt trước khi luận; không khẳng định "
                    "ngoài điều kiện đã được match."
                ),
            }
        )
    return {"matched_count": len(analyses), "matched": analyses, "required_in_reasoning": True}


def analyze_chart(chart: dict[str, Any]) -> dict[str, Any]:
    result = dict(chart)
    matched = detect_cach_cuc(chart)
    result["cach_cuc"] = matched
    result["cach_cuc_analysis"] = _build_cach_cuc_analysis(matched)

    tb = chart.get("thien_ban") or {}
    result["luan_giai"] = {
        "menh": {
            "cung": "Mệnh",
            "chu_menh": tb.get("menh_chu") or tb.get("menh"),
            "ban_menh": tb.get("ban_menh"),
            "menh_chu": tb.get("menh_chu"),
        },
        "than": {"than_chu": tb.get("than_chu")},
        "cach_cuc": result["cach_cuc_analysis"],
        "van_han": {
            "dai_han": "Đang sử dụng dữ liệu đại vận của từng cung khi engine nguồn cung cấp.",
            "tieu_han": "Đang sử dụng dữ liệu tiểu hạn của từng cung khi engine nguồn cung cấp.",
            "luu_nien": "Rule layer sẵn sàng mở rộng khi bổ sung bảng lưu niên.",
        },
    }

    ai_context = build_ai_context(result)
    ai_context["cach_cuc_analysis"] = result["cach_cuc_analysis"]
    ai_context["reasoning_contract"]["cach_cuc_is_mandatory"] = True
    ai_context["reasoning_contract"]["cach_cuc_evidence_first"] = True
    result["ai_context"] = ai_context
    return result
