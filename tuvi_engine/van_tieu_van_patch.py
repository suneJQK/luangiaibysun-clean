"""Tính Tiểu vận theo quy tắc tuổi năm: khởi cung theo tam hợp năm sinh,
nam đi thuận, nữ đi nghịch.

Quy tắc kiểm chứng:
- Thân/Tý/Thìn: khởi Tuất
- Tỵ/Dậu/Sửu: khởi Mùi
- Dần/Ngọ/Tuất: khởi Thìn
- Hợi/Mão/Mùi: khởi Sửu
- Tuổi 1 ở cung khởi; mỗi năm dịch 1 cung theo chiều giới tính.
"""
from __future__ import annotations

from typing import Any


# Cung số của 12 địa chi trên địa bàn cố định.
# 1=Tý, 2=Sửu, 3=Dần, 4=Mão, 5=Thìn, 6=Tỵ,
# 7=Ngọ, 8=Mùi, 9=Thân, 10=Dậu, 11=Tuất, 12=Hợi.
START_PALACE_BY_BIRTH_GROUP = {
    1: 11,  # Tý -> Tuất
    5: 11,  # Thìn -> Tuất
    9: 11,  # Thân -> Tuất
    6: 8,   # Tỵ -> Mùi
    10: 8,  # Dậu -> Mùi
    2: 8,   # Sửu -> Mùi
    3: 5,   # Dần -> Thìn
    7: 5,   # Ngọ -> Thìn
    11: 5,  # Tuất -> Thìn
    12: 2,  # Hợi -> Sửu
    4: 2,   # Mão -> Sửu
    8: 2,   # Mùi -> Sửu
}


def build_tieu_van_source_mapping(
    check,
    chi_name,
    birth_branch: int,
    target_branch: int,
    gender: str,
    age: int | None = None,
) -> dict[str, Any]:
    """Trả về cung Tiểu vận cho năm đang xét.

    ``age`` là tuổi mụ của năm xem. Tuổi 1 nằm tại cung khởi của nhóm
    tam hợp năm sinh; các năm sau dịch từng cung. Khi không truyền ``age``,
    hàm suy ra khoảng cách từ Chi năm sinh đến Chi năm đang xét.
    """
    birth_branch = check(birth_branch)
    target_branch = check(target_branch)

    start_palace = START_PALACE_BY_BIRTH_GROUP[birth_branch]
    is_male = str(gender).strip().casefold() in {"nam", "male", "m", "1"}
    direction = 1 if is_male else -1

    if age is None:
        # Hai Chi cách nhau bao nhiêu bước thì tương ứng số năm đã đi qua
        # trong chu kỳ 12 năm. Cộng 1 để chuyển từ số bước sang tuổi mụ.
        branch_delta = (target_branch - birth_branch) % 12
        age = branch_delta + 1
    age = max(1, int(age))

    offset = (age - 1) % 12
    cung_so = check(start_palace + direction * offset)

    sequence: list[dict[str, int]] = []
    for step in range(12):
        sequence.append({
            "cung_so": check(start_palace + direction * step),
            "chi": check(birth_branch + direction * step),
            "tuoi": step + 1,
            "thu_tu": step + 1,
        })

    return {
        "cung_so": cung_so,
        "chi_nam": target_branch,
        "chi_ten": chi_name(target_branch),
        "tuoi": age,
        "huong": "thuận" if direction == 1 else "nghịch",
        "cung_khoi": start_palace,
        "phuong_phap": "Khởi cung theo nhóm Thân-Tý-Thìn/Tỵ-Dậu-Sửu/Dần-Ngọ-Tuất/Hợi-Mão-Mùi; tuổi 1 tại cung khởi; Nam thuận, Nữ nghịch",
        "source_formula": {
            "tuoi_1": "cung_khoi",
            "tuoi_n": "check(cung_khoi + direction * (tuoi - 1))",
            "nam": "+1 cung mỗi năm",
            "nu": "-1 cung mỗi năm",
        },
        "sequence": sequence,
    }
