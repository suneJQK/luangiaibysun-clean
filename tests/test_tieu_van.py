from tuvi_engine.van_tieu_van_patch import build_tieu_van_source_mapping


BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


def check(value: int) -> int:
    return (int(value) - 1) % 12 + 1


def chi_name(value: int) -> str:
    return BRANCHES[check(value) - 1]


def test_2026_binh_ty_male_tieu_van_is_thin():
    # Bính Tý 1996 -> năm 2026 là tuổi mụ 31.
    # Thân/Tý/Thìn khởi Tiểu vận tại Tuất; Nam đi thuận.
    result = build_tieu_van_source_mapping(
        check,
        chi_name,
        birth_branch=1,   # Tý
        target_branch=7,  # Ngọ
        gender="Nam",
        age=31,
    )

    assert result["cung_so"] == 5
    assert result["chi_nam"] == 7
    assert result["chi_ten"] == "Ngọ"
    assert result["tuoi"] == 31
    assert result["cung_khoi"] == 11  # Tuất
    assert result["huong"] == "thuận"


def test_female_direction_is_reverse():
    result = build_tieu_van_source_mapping(
        check,
        chi_name,
        birth_branch=1,
        target_branch=7,
        gender="Nữ",
        age=31,
    )

    # Tuổi 31: Tuất đi nghịch 30 bước -> Mùi.
    assert result["cung_so"] == 8
    assert result["huong"] == "nghịch"
