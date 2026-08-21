"""Tính Tiểu hạn/Tiểu vận theo Tam hợp năm sinh và chiều Nam/Nữ.

Quy tắc:
- Thân – Tý – Thìn: khởi tại Tuất.
- Dần – Ngọ – Tuất: khởi tại Thìn.
- Tỵ – Dậu – Sửu: khởi tại Mùi.
- Hợi – Mão – Mùi: khởi tại Sửu.
- Nam: đi thuận.
- Nữ: đi nghịch.
- Chi năm sinh được đặt tại cung khởi (tuổi 1).
- Từ Chi năm sinh đếm theo chiều Nam/Nữ đến Chi năm xem;
  Chi năm xem đang nằm ở cung nào thì đó là cung Tiểu hạn/Tiểu vận.

Không hard-code kết quả của một năm cụ thể. Hàm này chỉ xác định vị trí
Tiểu hạn động từ năm sinh, năm xem và giới tính; tầng calculator mới ánh xạ
vị trí đó vào cung chức năng thực tế của từng lá số.
"""
from __future__ import annotations

from typing import Any, Callable

BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

# Cung khởi được quy định theo 4 nhóm Tam hợp của Chi năm sinh.
# Dùng tên Chi thay vì số để tránh nhầm thứ tự/ánh xạ.
START_BRANCH_BY_BIRTH_BRANCH = {
    # Thân – Tý – Thìn
    "Tý": "Tuất",
    "Thìn": "Tuất",
    "Thân": "Tuất",
    # Tỵ – Dậu – Sửu
    "Tỵ": "Mùi",
    "Dậu": "Mùi",
    "Sửu": "Mùi",
    # Dần – Ngọ – Tuất
    "Dần": "Thìn",
    "Ngọ": "Thìn",
    "Tuất": "Thìn",
    # Hợi – Mão – Mùi
    "Hợi": "Sửu",
    "Mão": "Sửu",
    "Mùi": "Sửu",
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


def _gender_direction(gender: str) -> tuple[int, str]:
    normalized = str(gender).strip().casefold()
    if normalized in {"nam", "male", "m", "1"}:
        return 1, "thuận"
    if normalized in {"nữ", "nu", "female", "f", "0", "2"}:
        return -1, "nghịch"
    raise ValueError(f"Giới tính không hợp lệ để tính Tiểu hạn: {gender!r}")


def build_tieu_van_source_mapping(
    check_fn: Callable[[int], int],
    chi_name_fn: Callable[[int], str],
    birth_branch: int,
    target_branch: int,
    gender: str,
    age: int | None = None,
) -> dict[str, Any]:
    """Tính vị trí Tiểu hạn từ Chi năm sinh -> Chi năm xem.

    Quy trình:
      1. Xác định nhóm Tam hợp của Chi năm sinh.
      2. Lấy cung khởi của nhóm đó.
      3. Đặt Chi năm sinh tại cung khởi (tuổi 1).
      4. Nam đi thuận, nữ đi nghịch.
      5. Đếm từ Chi năm sinh đến Chi năm xem.
      6. Cung mà Chi năm xem rơi vào là cung Tiểu hạn/Tiểu vận.

    ``age`` chỉ được giữ làm dữ liệu đối chiếu/hiển thị. Nó không quyết định
    vị trí chính, tránh xung đột giữa phép tính theo tuổi và phép tính theo Chi.
    """
    birth_branch = check_fn(birth_branch)
    target_branch = check_fn(target_branch)

    birth_name = chi_name_fn(birth_branch)
    target_name = chi_name_fn(target_branch)
    start_branch_name = START_BRANCH_BY_BIRTH_BRANCH.get(birth_name)
    if start_branch_name is None:
        raise ValueError(f"Không xác định được cung khởi Tiểu hạn cho Chi sinh {birth_name!r}")

    direction, direction_name = _gender_direction(gender)
    start_branch = branch_number(start_branch_name)

    # Khoảng cách Chi từ năm sinh đến năm xem theo chiều đang xét.
    target_offset = (
        (target_branch - birth_branch) % 12
        if direction == 1
        else (birth_branch - target_branch) % 12
    )

    if age is None:
        age = target_offset + 1
    age = max(1, int(age))

    # Cung mà Chi năm xem rơi vào chính là cung Tiểu hạn/Tiểu vận.
    palace_branch = check_fn(start_branch + direction * target_offset)
    palace_branch_name = chi_name_fn(palace_branch)

    sequence: list[dict[str, Any]] = []
    for step in range(12):
        year_branch_at_step = check_fn(birth_branch + direction * step)
        palace_at_step = check_fn(start_branch + direction * step)
        sequence.append({
            "thu_tu": step + 1,
            "tuoi_trong_chu_ky": step + 1,
            "chi_nam": year_branch_at_step,
            "chi_nam_ten": chi_name_fn(year_branch_at_step),
            "cung_dia_chi": palace_at_step,
            "cung_dia_chi_ten": chi_name_fn(palace_at_step),
        })

    return {
        "cung_dia_chi": palace_branch,
        "cung_dia_chi_ten": palace_branch_name,
        "cung_so": palace_branch,
        "chi_nam": target_branch,
        "chi_ten": target_name,
        "chi_nam_sinh": birth_branch,
        "chi_nam_sinh_ten": birth_name,
        "khoang_cach_chi": target_offset,
        "tuoi": age,
        "huong": direction_name,
        "cung_khoi": start_branch,
        "cung_khoi_ten": start_branch_name,
        "tam_hop_nam_sinh": [k for k, v in START_BRANCH_BY_BIRTH_BRANCH.items() if v == start_branch_name],
        "phuong_phap": (
            "Chi năm sinh đặt tại cung khởi (tuổi 1); Nam đếm thuận, Nữ đếm nghịch; "
            "đến Chi năm xem, cung mà Chi năm xem nằm tại đó là cung Tiểu hạn"
        ),
        "source_formula": {
            "cung_khoi": "tra theo Tam hợp Chi năm sinh",
            "vi_tri_nam": "check(cung_khoi + direction * khoang_cach_chi)",
            "khoang_cach_chi_nam": (
                "Nam: (Chi_nam_xem - Chi_nam_sinh) mod 12; "
                "Nữ: (Chi_nam_sinh - Chi_nam_xem) mod 12"
            ),
        },
        "sequence": sequence,
    }
