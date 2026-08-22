"""Build deterministic AI context and route it through the payload filter."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from .ai_payload_filter import build_filtered_ai_payload
from .data_loader import load_cach_cuc, load_json

_RELATION_DATA = load_json("data/relationships_ai.json")
_DYNAMIC_PALACE_FIELDS = {
    "dai_van", "tieu_van", "luu_nien", "luu_dai_van", "luu_nguyet", "luu_nhat", "luu_thoi"
}


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
            if item_id is not None and int(item_id) in index:
                base = deepcopy(index[int(item_id)])
                base.update(deepcopy(item))
                result.append(base)
            else:
                result.append(deepcopy(item))
    return result


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
    context: dict[str, Any] = {
        "schema_version": "3.1-ai-context-filtered-four-layer",
        "input": deepcopy(chart.get("input", {})),
        "thien_ban": deepcopy(chart.get("thien_ban", {})),
        "palaces": deepcopy(filtered.get("selected_palaces", {})),
        "ai_payload": filtered,
        "relationship_knowledge": load_relationship_knowledge(),
        "matched_cach_cuc": _normalize_matched_cach_cuc(chart, cach_cuc_catalog),
        "reasoning_contract": {
            "ai_payload_source_of_truth": "ai_payload",
            "use_only_provided_relations": True,
            "use_only_matched_cach_cuc": True,
            "do_not_invent_missing_stars_or_relations": True,
            "separate_facts_from_interpretation": True,
            "dynamic_van_source_of_truth": "van_han",
            "never_read_static_tieu_van_from_palaces": True,
            "four_han_layers_required_for_van_questions": True,
            "tam_hop_must_include_all_three_palaces": True,
            "name_each_influential_star_and_event": True,
            "filter_never_interprets": True,
        },
    }
    if van is not None:
        context["van_han"] = deepcopy(van)
    return context


__all__ = ["build_ai_context", "load_relationship_knowledge"]
