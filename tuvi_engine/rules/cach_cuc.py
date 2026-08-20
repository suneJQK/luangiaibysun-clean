"""Detect Cách Cục with explicit palace-relationship evidence."""
from __future__ import annotations

from typing import Any

from tuvi_engine.data_loader import load_cach_cuc

from .evaluator import _normalize_names, _scope_stars, evaluate_condition, related_palaces


def _evidence(chart: dict[str, Any], condition: dict[str, Any]) -> dict[str, Any]:
    target_name = str(condition.get("target", "Mệnh"))
    target = next(
        (
            p
            for p in (chart.get("12_cung") or {}).values()
            if isinstance(p, dict) and (p.get("cung") == target_name or p.get("cung_ten") == target_name)
        ),
        None,
    )
    if target is None:
        return {}

    rels = related_palaces(chart, target)
    evidence: dict[str, Any] = {"target": target_name}
    for relation_name in ("dong_cung", "tam_phuong_tu_chinh", "tam_hop", "xung_chieu", "nhi_hop", "giap_cung"):
        rule = condition.get(relation_name)
        if not isinstance(rule, dict):
            continue
        palaces = rels.get(relation_name, [])
        required = _normalize_names(rule.get("stars_required", rule.get("stars_all", [])))
        stars_by_palace = []
        for palace in palaces:
            names = _scope_stars([palace])
            matched = sorted(required & names)
            if matched:
                stars_by_palace.append({
                    "cung_so": palace.get("cung_so"),
                    "cung": palace.get("cung") or palace.get("cung_ten"),
                    "dia_chi": palace.get("dia_chi") or palace.get("chi"),
                    "matched_stars": matched,
                })
        if stars_by_palace:
            evidence[relation_name] = stars_by_palace
    return evidence


def _match_rule(chart: dict[str, Any], rule: dict[str, Any]) -> list[dict[str, Any]]:
    conditions = rule.get("conditions")
    if not isinstance(conditions, dict):
        return []
    branches = conditions.get("any_of") if isinstance(conditions.get("any_of"), list) else [conditions]
    matches = []
    for branch in branches:
        if isinstance(branch, dict) and evaluate_condition(chart, branch):
            matches.append(_evidence(chart, branch))
    return matches


def detect_cach_cuc(chart: dict[str, Any]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for rule in load_cach_cuc():
        evidence = _match_rule(chart, rule)
        if not evidence:
            continue
        matches.append({
            "id": rule.get("id"),
            "name": rule.get("name"),
            "category": rule.get("category"),
            "description": rule.get("description", ""),
            "reason": rule.get("reason", ""),
            "conditions": rule.get("conditions", {}),
            "evidence": evidence,
        })
    return matches


__all__ = ["detect_cach_cuc"]
