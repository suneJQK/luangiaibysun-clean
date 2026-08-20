from tuvi_engine.ai_context import build_ai_context, load_relationship_knowledge


def test_relationship_knowledge_contains_four_relations():
    data = load_relationship_knowledge()
    relations = data["relations"]
    assert set(relations) == {"xung_chieu", "tam_hop", "nhi_hop", "giap_cung"}
    assert relations["xung_chieu"]["offset"] == 6
    assert relations["tam_hop"]["offsets"] == [4, 8]
    assert relations["giap_cung"]["offsets"] == [-1, 1]


def test_build_ai_context_uses_explicit_cach_cuc_match():
    chart = {
        "input": {"nam": 1990},
        "thien_ban": {"menh": "Mệnh"},
        "12_cung": [],
        "cach_cuc": [],
    }
    payload = build_ai_context(chart)
    assert payload["schema_version"] == "2.0-ai-context"
    assert payload["relationship_knowledge"]["relations"]["xung_chieu"]["label"] == "Xung Chiếu"
    assert payload["matched_cach_cuc"] == []
    assert payload["reasoning_contract"]["use_only_matched_cach_cuc"] is True
