from tuvi_engine.engine.date_handler import normalize_birth_input
from tuvi_engine.engine.geometry import palace_relations, relation
from tuvi_engine.engine.chart_builder import lap_la_so


def test_normalize_birth_input():
    value = normalize_birth_input(1, 1, 2000, "Tý", "Nam", timezone=7)
    assert value.hour == 1
    assert value.gender == 1


def test_geometry():
    assert relation("Tý", "Ngọ") == "xung_chieu"
    result = palace_relations("Tý")
    assert result["xung_chieu"] == "Ngọ"
    assert result["nhi_hop"] == "Sửu"


def test_lap_la_so_schema():
    chart = lap_la_so(1, 1, 2000, "Tý", "Nam", "Test", True, 7)
    assert chart["schema_version"] == "engine_2.1"
    assert len(chart["12_cung"]) == 12
    assert "thien_ban" in chart
