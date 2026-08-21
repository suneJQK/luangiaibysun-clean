"""Port chính xác block chitieuvan[] của mã nguồn tham khảo."""
from __future__ import annotations
from typing import Any

def build_tieu_van_source_mapping(check, chi_name, birth_branch: int, target_branch: int, gender: str) -> dict[str, Any]:
    # Bảng khởi cung i trong nguồn.
    if birth_branch in (1, 5, 9):
        i = 11
    elif birth_branch in (2, 6, 10):
        i = 8
    elif birth_branch in (3, 7, 11):
        i = 5
    else:
        i = 2

    is_male = str(gender).strip().casefold() in {"nam", "male", "m", "1"}
    direction = 1 if is_male else -1

    # Quan trọng: nguồn đặt rl=i+10, sau đó mỗi vòng lặp thực hiện
    # rl=check(rl) TRƯỚC khi gán chitieuvan[rl].
    rl = i + 10
    sequence: list[dict[str, int]] = []
    for order in range(1, 13):
        rl = check(rl)
        mapped_branch = check(birth_branch + (order - 1) * direction)
        sequence.append({"cung_so": rl, "chi": mapped_branch, "thu_tu": order})

    target = check(target_branch)
    selected = next((item for item in sequence if item["chi"] == target), None)
    return {
        "cung_so": selected["cung_so"] if selected else None,
        "chi_nam": target,
        "chi_ten": chi_name(target),
        "huong": "thuận" if is_male else "nghịch",
        "cung_khoi": sequence[0]["cung_so"],
        "source_formula": {
            "rl_ban_dau": "i + 10",
            "moi_vong": "rl = check(rl) trước khi gán",
            "nam": "check(e + O - 1)",
            "nu": "check(e - O + 13)",
        },
        "sequence": sequence,
    }
