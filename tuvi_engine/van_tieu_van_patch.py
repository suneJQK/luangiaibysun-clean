"""Tính Tiểu vận theo đúng quy tắc khởi cung và chiều nam/nữ.

Quy tắc:
- Thân/Tý/Thìn khởi tại Tuất.
- Tỵ/Dậu/Sửu khởi tại Mùi.
- Dần/Ngọ/Tuất khởi tại Thìn.
- Hợi/Mão/Mùi khởi tại Sửu.
- Chi năm sinh là mốc của tuổi 1 tại cung khởi.
- Nam đi thuận; Nữ đi nghịch.
- Từ Chi năm sinh đếm đến Chi năm xem; Chi năm xem nằm ở cung nào
  thì đó là cung Tiểu vận/Tiểu hạn của năm đang xét.

Không dùng tuổi mụ để quyết định vị trí Tiểu vận; tuổi chỉ giữ để hiển thị/đối chiếu.
Không hard-code kết quả của một năm cụ thể.
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
    """Tính Tiểu vận theo mốc Chi năm sinh -> Chi năm xem.

    Vị trí chính được tính trực tiếp bằng khoảng cách giữa Chi năm sinh và
    Chi năm xem, sau đó áp khoảng cách đó lên cung khởi của nhóm Tam hợp.
    Tuổi chỉ là dữ liệu đối chiếu/hiển thị.
    """
    birth_branch = check_fn(birth_branch)
    target_branch = check_fn(target_branch)
    is_male = str(gender).strip().casefold() in {"nam", "male", "m", "1"}
    direction = 1 if is_male else -1

    if birth_branch not in START_BRANCH_BY_BIRTH_GROUP:
        raise ValueError(f"Không xác định được cung khởi Tiểu vận cho Chi sinh {birth_branch}")

    start_branch_name = START_BRANCH_BY_BIRTH_GROUP[birth_branch]
    start_branch = branch_number(start_branch_name)

    # Khoảng cách từ Chi năm sinh đến Chi năm xem.
    target_offset = (
        (target_branch - birth_branch) % 12
        if is_male
        else (birth_branch - target_branch) % 12
    )

    if age is None:
        age = target_offset + 1
    age = max(1, int(age))

    # Chi năm sinh = mốc tuổi 1 tại cung khởi; từ đó đếm tới Chi năm xem.
    palace_branch = check_fn(start_branch + direction * target_offset)
    palace_branch_name = chi_name_fn(palace_branch)

    sequence: list[dict[str, Any]] = []
    for step in range(12):
        year_branch = check_fn(birth_branch + direction * step)
        palace = check_fn(start_branch + direction * step)
        sequence.append({
            "thu_tu": step + 1,
            "tuoi_trong_chu_ky": step + 1,
            "chi_nam": year_branch,
            "chi_nam_ten": chi_name_fn(year_branch),
            "cung_dia_chi": palace,
            "cung_dia_chi_ten": chi_name_fn(palace),
        })

    return {
        "cung_dia_chi": palace_branch,
        "cung_dia_chi_ten": palace_branch_name,
        "cung_so": palace_branch,
        "chi_nam": target_branch,
        "chi_ten": chi_name_fn(target_branch),
        "chi_nam_sinh": birth_branch,
        "chi_nam_sinh_ten": chi_name_fn(birth_branch),
        "khoang_cach_chi": target_offset,
        "tuoi": age,
        "huong": "thuận" if direction == 1 else "nghịch",
        "cung_khoi": start_branch,
        "cung_khoi_ten": start_branch_name,
        "phuong_phap": (
            "Lấy Chi năm sinh làm mốc tuổi 1 tại cung khởi; từ Chi năm sinh "
            "đếm thuận (Nam) hoặc nghịch (Nữ) đến Chi năm xem; Chi năm xem "
            "nằm ở cung nào thì đó là Tiểu vận."
        ),
        "source_formula": {
            "mo_c": "Chi năm sinh -> cung khởi",
            "vi_tri_nam": "check(cung_khoi + direction * khoang_cach_chi)",
            "khoang_cach_chi_nam": "Nam: (Chi_nam_xem - Chi_nam_sinh) mod 12; Nữ: (Chi_nam_sinh - Chi_nam_xem) mod 12",
        },
        "sequence": sequence,
    }
