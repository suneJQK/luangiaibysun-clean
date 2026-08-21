from tuvi_engine.van_tieu_van_patch import build_tieu_van_source_mapping


BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


def check(value: int) -> int:
    return (int(value) - 1) % 12 + 1


def chi_name(value: int) -> str:
    return BRANCHES[check(value) - 1]


def test_binh_ty_male_2026_uses_rule_not_hardcoded_year():
    # Bính Tý 1996, 2026 là tuổi mụ 31.
    # Thân/Tý/Thìn khởi Tuất; nam đi thuận:
    # Tý -> Tuất, Sửu -> Hợi, ..., Ngọ -> Thìn.
    result = build_tieu_van_source_mapping(
        check,
        chi_name,
        birth_branch=1,
        target_branch=7,
        gender="Nam",
        age=31,
    )

    assert result["cung_dia_chi_ten"] == "Thìn"
    assert result["cung_khoi_ten"] == "Tuất"
    assert result["chi_ten"] == "Ngọ"
    assert result["tuoi"] == 31
    assert result["huong"] == "thuận"


def test_same_birth_chart_changes_with_viewing_year():
    # Cùng Bính Tý nam nhưng khác tuổi/năm => cung Tiểu vận thay đổi.
    age_30 = build_tieu_van_source_mapping(check, chi_name, 1, 6, "Nam", age=30)
    age_31 = build_tieu_van_source_mapping(check, chi_name, 1, 7, "Nam", age=31)

    assert age_30["cung_dia_chi_ten"] == "Mão"
    assert age_31["cung_dia_chi_ten"] == "Thìn"
    assert age_30["cung_dia_chi_ten"] != age_31["cung_dia_chi_ten"]


def test_female_direction_is_reverse():
    result = build_tieu_van_source_mapping(
        check,
        chi_name,
        birth_branch=1,
        target_branch=7,
        gender="Nữ",
        age=31,
    )

    assert result["cung_dia_chi_ten"] == "Mùi"
    assert result["cung_khoi_ten"] == "Tuất"
    assert result["huong"] == "nghịch"


def test_all_birth_groups_have_expected_start_branch():
    expected = {
        "Tý": "Tuất", "Thìn": "Tuất", "Thân": "Tuất",
        "Tỵ": "Mùi", "Dậu": "Mùi", "Sửu": "Mùi",
        "Dần": "Thìn", "Ngọ": "Thìn", "Tuất": "Thìn",
        "Hợi": "Sửu", "Mão": "Sửu", "Mùi": "Sửu",
    }
    for branch_name, start_name in expected.items():
        birth_branch = BRANCHES.index(branch_name) + 1
        result = build_tieu_van_source_mapping(
            check,
            chi_name,
            birth_branch=birth_branch,
            target_branch=birth_branch,
            gender="Nam",
            age=1,
        )
        assert result["cung_khoi_ten"] == start_name
        assert result["cung_dia_chi_ten"] == start_name
