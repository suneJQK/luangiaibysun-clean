"""Build a compact, deterministic context payload for AI interpretation."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from .data_loader import load_cach_cuc, load_json


_RELATION_DATA = load_json("data/relationships_ai.json")

# Các lớp vận năm/tháng/ngày/giờ phải lấy từ `van` đã tính cho đúng năm xem.
# Không cho AI đọc bản vận hạn tĩnh được an sẵn trong từng cung của lá số.
_DYNAMIC_PALACE_FIELDS = {
    "dai_van",
    "tieu_van",
    "luu_nien",
    "luu_dai_van",
    "luu_nguyet",
    "luu_nhat",
    "luu_thoi",
}


def load_relationship_knowledge() -> dict[str, Any]:
    return deepcopy(_RELATION_DATA)


def _index_cach_cuc(items: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {
        int(item["id"]): item
        for item in items
        if isinstance(item, dict) and item.get("id") is not None
    }


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


def _palaces_for_ai(chart: dict[str, Any]) -> dict[str, Any] | list[Any]:
    """Return immutable natal palace facts only.

    Dynamic vận layers are deliberately removed here. The authoritative
    current-year result is attached separately as `van_han`.
    """
    source = chart.get("12_cung", chart.get("dia_ban", {}))
    if isinstance(source, dict):
        result: dict[str, Any] = {}
        for name, raw in source.items():
            if not isinstance(raw, dict):
                continue
            item = deepcopy(raw)
            for field in _DYNAMIC_PALACE_FIELDS:
                item.pop(field, None)
            result[name] = item
        return result
    if isinstance(source, list):
        result_list: list[Any] = []
        for raw in source:
            if not isinstance(raw, dict):
                result_list.append(deepcopy(raw))
                continue
            item = deepcopy(raw)
            for field in _DYNAMIC_PALACE_FIELDS:
                item.pop(field, None)
            result_list.append(item)
        return result_list
    return {}


def build_ai_context(
    chart: dict[str, Any],
    *,
    van: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Combine natal structure, authoritative vận layers, relationships and Cách Cục.

    The function never copies static `tieu_van`/`dai_van` fields from individual
    palaces into the AI evidence set. Current vận data must come from `van`.
    """
    if not isinstance(chart, dict):
        raise TypeError("chart phải là dict")

    cach_cuc_catalog = load_cach_cuc()
    context: dict[str, Any] = {
        "schema_version": "2.1-ai-context-authoritative-van",
        "input": deepcopy(chart.get("input", {})),
        "thien_ban": deepcopy(chart.get("thien_ban", {})),
        "palaces": _palaces_for_ai(chart),
        "relationship_knowledge": load_relationship_knowledge(),
        "matched_cach_cuc": _normalize_matched_cach_cuc(chart, cach_cuc_catalog),
        "reasoning_contract": {
            "use_only_provided_relations": True,
            "use_only_matched_cach_cuc": True,
            "do_not_invent_missing_stars_or_relations": True,
            "separate_facts_from_interpretation": True,
            "dynamic_van_source_of_truth": "van_han",
            "never_read_static_tieu_van_from_palaces": True,
        },
    }
    if van is not None:
        context["van_han"] = deepcopy(van)
    return context


__all__ = ["build_ai_context", "load_relationship_knowledge"]
