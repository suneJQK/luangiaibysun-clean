"""Tính Tiểu vận theo quy tắc khởi cung và chiều nam/nữ.

Quy tắc:
- Thân/Tý/Thìn khởi tại Tuất.
- Tỵ/Dậu/Sửu khởi tại Mùi.
- Dần/Ngọ/Tuất khởi tại Thìn.
- Hợi/Mão/Mùi khởi tại Sửu.
- Tuổi 1 ở cung khởi; mỗi tuổi dịch một cung.
- Nam đi thuận; Nữ đi nghịch.

Hàm không gán cứng năm 2026 hay một tên cung cụ thể. Nó chỉ tính ra
Địa Chi của cung Tiểu vận cho lá số/năm đang xét; tầng calculator sẽ
tra Địa Chi đó vào 12 cung thực tế của chính lá số để lấy tên cung.
"""
from __future__ import annotations

from typing import Any

BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

# Địa Chi cung khởi, không phải tên cung chức năng của lá số.
START_BRANCH_BY_BIRTH_GROUP = {
    1: "Tuất",  # Tý
    5: "Tuất",  # Thìn
    9: "Tuất",  # Thân
    6: "Mùi",   # Tỵ
    10: "Mùi",  # Dậu
    2: "Mùi",   # Sửu
    3: "Thìn",  # Dần
    7: "Thìn",  # Ngọ
    11: "Thìn", # Tuất
    12: "Sửu",  # Hợi
    4: "Sửu",  # Mão
    8: "Sửu",  # Mùi
}


def check(value: int) -> int:
    return (int(value) - 1) % 12 + 1


def branch_number(name: str) -> int:
    try:
        return BRANCHES.index(name) + 1
    except ValueError as exc:
        raise ValueError(f"Địa Chi không hợp lệ: {name!r}") from exc


def chi_name(value: int) -> str:
    return BRANCHES[check(value) - 1]


def build_tieu_van_source_mapping(
    check_fn,
    chi_name_fn,
    birth_branch: int,
    target_branch: int,
    gender: str,
    age: int | None = None,
) -> dict[str, Any]:
    """Tính vị trí Tiểu vận động theo đúng quy tắc khởi cung.

    ``target_branch`` chỉ là Chi của năm đang xem để ghi nhận/kiểm tra.
    Vị trí Tiểu vận được xác định bởi tuổi mụ + cung khởi + chiều giới tính,
    không phụ thuộc vào một năm cụ thể.
    """
    birth_branch = check_fn(birth_branch)
    target_branch = check_fn(target_branch)
    is_male = str(gender).strip().casefold() in {"nam", "male", "m", "1"}
    direction = 1 if is_male else -1

    if birth_branch not in START_BRANCH_BY_BIRTH_GROUP:
        raise ValueError(f"Không xác định được cung khởi Tiểu vận cho Chi sinh {birth_branch}")

    start_branch_name = START_BRANCH_BY_BIRTH_GROUP[birth_branch]
    start_branch = branch_number(start_branch_name)

    if age is None:
        # Khoảng cách Chi theo chu kỳ 12 năm; đây chỉ là fallback khi caller
        # chưa cung cấp tuổi mụ thực tế.
        delta = (target_branch - birth_branch) % 12 if is_male else (birth_branch - target_branch) % 12
        age = delta + 1
    age = max(1, int(age))

    offset = (age - 1) % 12
    palace_branch = check_fn(start_branch + direction * offset)
    palace_branch_name = chi_name_fn(palace_branch)

    sequence: list[dict[str, Any]] = []
    for step in range(12):
        branch = check_fn(start_branch + direction * step)
        sequence.append({
            "tuoi": step + 1,
            "cung_dia_chi": branch,
            "cung_dia_chi_ten": chi_name_fn(branch),
            "thu_tu": step + 1,
        })

    return {
        "cung_dia_chi": palace_branch,
        "cung_dia_chi_ten": palace_branch_name,
        "cung_so": palace_branch,
        "chi_nam": target_branch,
        "chi_ten": chi_name_fn(target_branch),
        "tuoi": age,
        "huong": "thuận" if direction == 1 else "nghịch",
        "cung_khoi": start_branch,
        "cung_khoi_ten": start_branch_name,
        "phuong_phap": "Khởi cung theo nhóm Thân-Tý-Thìn/Tỵ-Dậu-Sửu/Dần-Ngọ-Tuất/Hợi-Mão-Mùi; tuổi 1 tại cung khởi; Nam thuận, Nữ nghịch",
        "source_formula": {
            "tuoi_1": f"{start_branch_name}",
            "tuoi_n": "dịch (tuổi - 1) cung theo chiều Nam thuận / Nữ nghịch",
            "nam": "+1 Địa Chi cung mỗi tuổi",
            "nu": "-1 Địa Chi cung mỗi tuổi",
        },
        "sequence": sequence,
    }
