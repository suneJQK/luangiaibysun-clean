"""Local Tu Vi engine for generating charts without MCP/server dependencies.

The legacy low-level API remains exported from ``tuvi_engine._engine`` while
V2 orchestration and schema helpers are available from ``tuvi_engine.engine``.
"""
from ._engine import *
from .ai_context import build_ai_context, load_relationship_knowledge
from .engine import cached_lap_la_so, clear_chart_cache, lap_la_so
from .schema import SCHEMA_VERSION, build_meta, to_v2_chart, validate_v2_chart

# Patch Tiểu vận trước khi bất kỳ caller nào lấy calculate_van_layers.
# Module này port đúng thứ tự rl=check(rl) của mã nguồn tham khảo.
from . import van_calculator as _van_calculator
from .van_tieu_van_patch import build_tieu_van_source_mapping
_van_calculator._tieu_van_source_mapping = lambda birth_branch, target_branch, gender: build_tieu_van_source_mapping(
    _van_calculator.check,
    _van_calculator.chi_name,
    birth_branch,
    target_branch,
    gender,
)

__all__ = [
    "lap_la_so",
    "cached_lap_la_so",
    "clear_chart_cache",
    "SCHEMA_VERSION",
    "build_meta",
    "to_v2_chart",
    "validate_v2_chart",
    "build_ai_context",
    "load_relationship_knowledge",
]
