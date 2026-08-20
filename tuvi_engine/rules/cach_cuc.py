"""Detect configured Cách Cục against a normalized V2 chart."""
from __future__ import annotations

from typing import Any

from tuvi_engine.data_loader import load_cach_cuc

from .evaluator import evaluate_condition


def detect_cach_cuc(chart: dict[str, Any]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for rule in load_cach_cuc():
        conditions = rule.get("conditions")
        if isinstance(conditions, dict) and evaluate_condition(chart, conditions):
            matches.append({
                "id": rule.get("id"),
                "name": rule.get("name"),
                "category": rule.get("category"),
                "description": rule.get("description", ""),
                "reason": rule.get("reason", ""),
            })
    return matches
