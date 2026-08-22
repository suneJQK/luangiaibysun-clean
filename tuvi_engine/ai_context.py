"""Build deterministic AI context and route it through the payload filter."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from .ai_payload_filter import build_filtered_ai_payload
from .data_loader import load_cach_cuc, load_json

_RELATION_DATA = load_json("data/relationships_ai.json")


def load_relationship_knowledge() -> dict[str, Any]:
    return deepcopy(_RELATION_DATA)


def _index_cach_cuc(items: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {int(item["id"]): item for item in items if isinstance(item, dict) and item.get("id") is not None}


def _normalize_matched_cach_cuc(chart: dict[str, Any], catalog: list[dict[str, Any]]) -> list[dict[str, Any]]:
    index = _index_cach_cuc(catalog)
    matched = chart.get("cach_cuc", [])
    result: list[dict[str, Any]] = []
    if not isinstance(matched, list):
        return result
    for item in matched:
        if isinstance(item, int) and item in index:
            result.append(deepcopy(index[item]))
        elif isinstance(item, dict):
            item_id = item.get("id")
            try:
                item_id_int = int(item_id) if item_id is not None else None
            except (TypeError, ValueError):
                item_id_int = None
            if item_id_int is not None and item_id_int in index:
                base = deepcopy(index[item_id_int])
                base.update(deepcopy(item))
                result.append(base)
            else:
                result.append(deepcopy(item))
    return result


def _question_scope(question: str) -> dict[str, Any]:
    q = (question or "").strip().casefold()
    if any(x in q for x in ("đại vận", "đại hạn", "10 năm", "mười năm")):
        return {"id": "dai_van", "focus": "dai_van", "weights": {"dai_van": 0.80, "relations_and_stars": 0.20}}
    if any(x in q for x in ("lưu niên đại vận", "lưu đại hạn", "lưu đại vận")):
        return {"id": "luu_nien_dai_van", "focus": "luu_nien_dai_van", "weights": {"dai_van": 0.25, "luu_nien_dai_van": 0.50, "tieu_van": 0.10, "luu_nien_nam": 0.15}}
    if any(x in q for x in ("tiểu hạn", "tiểu vận")):
        return {"id": "tieu_van", "focus": "tieu_van", "weights": {"dai_van": 0.20, "luu_nien_dai_van": 0.20, "tieu_van": 0.40, "luu_nien_nam": 0.20}}
    if any(x in q for x in ("lưu niên năm", "lưu thái tuế", "thái tuế")):
        return {"id": "luu_nien_nam", "focus": "luu_nien_nam", "weights": {"dai_van": 0.20, "luu_nien_dai_van": 0.15, "tieu_van": 0.20, "luu_nien_nam": 0.45}}
    return {"id": "tong_hop_nam", "focus": "tong_hop_nam", "weights": {"dai_van": 0.55, "luu_nien_dai_van": 0.18, "tieu_van": 0.15, "luu_nien_nam": 0.12}}


def build_ai_context(
    chart: dict[str, Any],
    *,
    van: dict[str, Any] | None = None,
    question: str = "",
) -> dict[str, Any]:
    """Build the model-facing context from the deterministic filter."""
    if not isinstance(chart, dict):
        raise TypeError("chart phải là dict")

    cach_cuc_catalog = load_cach_cuc()
    filtered = build_filtered_ai_payload(chart, van or {}, question)
    scope = _question_scope(question)
    context: dict[str, Any] = {
        "schema_version": "3.2-ai-context-filtered-four-layer",
        "input": deepcopy(chart.get("input", {})),
        "thien_ban": deepcopy(chart.get("thien_ban", {})),
        "palaces": deepcopy(filtered.get("selected_palaces", {})),
        "ai_payload": filtered,
        "relationship_knowledge": load_relationship_knowledge(),
        "matched_cach_cuc": _normalize_matched_cach_cuc(chart, cach_cuc_catalog),
        "question_scope": scope,
        "reasoning_contract": {
            "ai_payload_source_of_truth": "ai_payload",
            "use_only_provided_relations": True,
            "use_only_matched_cach_cuc": True,
            "do_not_invent_missing_stars_or_relations": True,
            "separate_facts_from_interpretation": True,
            "dynamic_van_source_of_truth": "van_han",
            "never_read_static_tieu_van_from_palaces": True,
            "four_han_layers_required_for_van_questions": True,
            "four_han_layers": ["dai_van", "luu_nien_dai_van", "tieu_van", "luu_nien_nam"],
            "tam_hop_must_include_all_three_palaces": True,
            "name_each_influential_star_and_event": True,
            "filter_never_interprets": True,
            "scope_driven_weighting": True,
            "weights": scope["weights"],
            "convergence_rule": {
                "two_layers": "tang_do_tin_cay",
                "three_layers": "su_kien_manh",
                "four_layers_plus_root_transit_star_repetition": "su_kien_trong_diem",
                "not_additive_probability": True,
            },
        },
    }
    if van is not None:
        context["van_han"] = deepcopy(van)
    return context


__all__ = ["build_ai_context", "load_relationship_knowledge"]
