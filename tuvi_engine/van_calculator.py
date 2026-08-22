"""Bộ tính vận hạn Tử Vi theo logic từ mã nguồn tham khảo người dùng cung cấp.

PHẠM VI DUY NHẤT: TỬ VI.
- Đại vận
- Lưu Đại vận
- Tiểu vận
- Lưu niên trong Đại vận
- Lưu nguyệt theo Tiết khí
- Lưu nhật
- Lưu thời

KHÔNG áp dụng Tứ Trụ/Bát Tự, không tính tuổi nhập vận Tứ Trụ và không dùng
các phép hợp-hóa/ngũ hành của module Tứ Trụ để thay thế vận hạn Tử Vi.
"""
from __future__ import annotations

import math
from typing import Any

CAN_NAMES = ["", "Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
CHI_NAMES = ["", "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


def check(value: int) -> int:
    return (int(value) - 1) % 12 + 1


def check_can(value: int) -> int:
    return (int(value) - 1) % 10 + 1


def can_name(value: int) -> str:
    return CAN_NAMES[check_can(value)]


def chi_name(value: int) -> str:
    return CHI_NAMES[check(value)]


def _normalize_branch_text(value: Any) -> str:
    """Chuẩn hóa tên Địa Chi trong chart để mapping không phụ thuộc kiểu ghi."""
    text = str(value or "").strip().casefold()
    aliases = {
        "tý": "ty", "ty": "ty", "ty1": "ty", "ty2": "ty",
        "sửu": "suu", "suu": "suu",
        "dần": "dan", "dan": "dan",
        "mão": "mao", "mao": "mao",
        "thìn": "thin", "thin": "thin",
        "tỵ": "ty", "tị": "ty", "ti": "ty",
        "ngọ": "ngo", "ngo": "ngo",
        "mùi": "mui", "mui": "mui",
        "thân": "than", "than": "than",
        "dậu": "dau", "dau": "dau",
        "tuất": "tuat", "tuat": "tuat",
        "hợi": "hoi", "hoi": "hoi",
    }
    return aliases.get(text, text)


def _branch_number_from_palace(palace: dict[str, Any]) -> int | None:
    """Lấy số Chi từ cung, hỗ trợ cả tên chuẩn và key nội bộ ty1/ty2."""
    raw = palace.get("dia_chi")
    if isinstance(raw, int):
        return check(raw)
    normalized = _normalize_branch_text(raw)
    branch_aliases = {
        "ty": 1,
        "suu": 2,
        "dan": 3,
        "mao": 4,
        "thin": 5,
        "ty2": 6,
        "ngo": 7,
        "mui": 8,
        "than": 9,
        "dau": 10,
        "tuat": 11,
        "hoi": 12,
    }
    # Nếu nguồn dùng ty1/ty2, cung có địa chi Tỵ phải ưu tiên ty2.
    raw_text = str(raw or "").strip().casefold()
    if raw_text in {"ty2", "tỵ", "tị"}:
        return 6
    if raw_text in {"ty1", "tý"}:
        return 1
    return branch_aliases.get(normalized)


def _is_male(gender: str) -> bool:
    return str(gender).strip().casefold() in {"nam", "male", "m", "1"}


def _jd_from_date(day: int, month: int, year: int) -> int:
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + ((153 * m + 2) // 5) + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def _jd_to_gregorian(jd: int) -> tuple[int, int, int]:
    if jd > 2299160:
        a = jd + 32044
        b = (4 * a + 3) // 146097
        c = a - (b * 146097) // 4
    else:
        b = 0
        c = jd + 32082
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = b * 100 + d - 4800 + m // 10
    return day, month, year


def _solar_longitude(jd: float) -> float:
    """Port solarLongitude() từ mã nguồn tham khảo."""
    T = (jd - 2451545.0) / 36525.0
    T2 = T * T
    dr = math.pi / 180.0
    M = 357.52910 + 35999.05030 * T - 0.0001559 * T2 - 0.00000048 * T * T2
    L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T2
    C = (1.914600 - 0.004817 * T - 0.000014 * T2) * math.sin(dr * M)
    C += (0.019993 - 0.000101 * T) * math.sin(dr * 2 * M)
    C += 0.000290 * math.sin(dr * 3 * M)
    theta = L0 + C
    omega = 125.04 - 1934.136 * T
    lam = theta - 0.00569 - 0.00478 * math.sin(omega * dr)
    return lam - 360.0 * math.floor(lam / 360.0)


def tiet_khi_month(day: int, month: int, year: int, time_zone: float = 7.0) -> int:
    """Trả mã tháng Tiết khí 1..12 theo logic thangtk của nguồn."""
    jd = _jd_from_date(day, month, year)
    local_jd = jd - 0.5 - float(time_zone) / 24.0
    sl = _solar_longitude(local_jd) - 315.0
    if sl < 30.0:
        sl += 360.0
    return check(int(sl // 30.0) + 1)


def can_chi_year(year: int) -> tuple[int, int]:
    return check_can(year - 1983 + 360), check(year - 1983 + 360)


def can_chi_day(day: int, month: int, year: int) -> tuple[int, int]:
    jd = _jd_from_date(day, month, year)
    return check_can(jd), check(jd + 2)


def can_chi_hour(day_can: int, hour_branch: int) -> tuple[int, int]:
    chi = check(hour_branch)
    return check_can(2 * day_can + chi - 2), chi


def _birth_year_can(chart: dict[str, Any]) -> int | None:
    raw = chart.get("thien_ban", {}).get("can_nam")
    if isinstance(raw, int):
        return check_can(raw)
    text = str(raw or "").strip()
    for idx, name in enumerate(CAN_NAMES):
        if name and text.startswith(name):
            return idx
    return None


def _birth_year_branch(chart: dict[str, Any]) -> int | None:
    raw = chart.get("thien_ban", {}).get("chi_nam")
    if isinstance(raw, int):
        return check(raw)
    text = str(raw or "").strip()
    for idx, name in enumerate(CHI_NAMES):
        if name and text.startswith(name):
            return idx
    return None


def _dv_direction(can_year: int | None, gender: str) -> int:
    """Dương Nam/Âm Nữ thuận; Âm Nam/Dương Nữ nghịch."""
    if can_year is None:
        return 1
    can_yang = check_can(can_year) % 2 == 1
    return 1 if can_yang == _is_male(gender) else -1


def _palace_by_branch(chart: dict[str, Any], branch: int) -> int | None:
    """Tìm đúng cung có Địa Chi của năm/giờ/ngày/tháng.

    Đây là mapping bắt buộc cho Lưu niên: năm 2026 = Bính Ngọ (Chi Ngọ=7)
    thì Lưu niên phải nằm tại chính cung có Địa Chi Ngọ, không lấy cung Tiểu vận.
    """
    target = check(branch)
    for palace in chart.get("12_cung", {}).values():
        palace_branch = _branch_number_from_palace(palace)
        if palace_branch == target:
            value = palace.get("cung_so")
            if isinstance(value, int):
                return value
    return None


def _palace_detail_by_branch(chart: dict[str, Any], branch: int) -> dict[str, Any] | None:
    """Trả toàn bộ thông tin cung được kích hoạt bởi một Địa Chi."""
    target = check(branch)
    for palace in chart.get("12_cung", {}).values():
        if _branch_number_from_palace(palace) == target:
            return {
                "cung_so": palace.get("cung_so"),
                "cung": palace.get("cung"),
                "dia_chi": palace.get("dia_chi"),
                "can_chi": palace.get("can_chi"),
            }
    return None


def _engine_dai_van_items(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """Đọc các khoảng Đại vận đã được an vào 12 cung bởi engine lá số."""
    items: list[dict[str, Any]] = []
    for palace in chart.get("12_cung", {}).values():
        dv = palace.get("dai_van") or {}
        start = dv.get("tuoi_bat_dau")
        try:
            start_i = int(start)
        except (TypeError, ValueError):
            continue
        items.append({
            "cung_so": palace.get("cung_so"),
            "cung": palace.get("cung"),
            "dia_chi": palace.get("dia_chi"),
            "tuoi_bat_dau": start_i,
            "tuoi_ket_thuc": start_i + 9,
            "can_chi_engine": palace.get("can_chi"),
        })
    items.sort(key=lambda x: (x["tuoi_bat_dau"], x.get("cung_so") or 99))
    return items


def _tuoi_xem(birth_year: int, target_year: int) -> int:
    return target_year - birth_year + 1


def _current_dai_van(chart: dict[str, Any], target_year: int) -> dict[str, Any] | None:
    inp = chart.get("input", {})
    age = _tuoi_xem(int(inp["nam"]), target_year)
    items = _engine_dai_van_items(chart)
    current = next((x for x in items if x["tuoi_bat_dau"] <= age <= x["tuoi_ket_thuc"]), None)
    if current is None or current.get("cung_so") is None:
        return None

    can_year = _birth_year_can(chart)
    gender = str(inp.get("gioi_tinh", "Nam"))
    direction = _dv_direction(can_year, gender)
    cung = int(current["cung_so"])

    fl = check(cung - 2)
    yl = check_can(2 * (can_year or 1) + 1)
    dv_can = check_can(fl + yl - 1)
    dv_chi = check(cung + 10)

    return {
        **current,
        "tuoi_xem": age,
        "huong": "thuận" if direction == 1 else "nghịch",
        "can": dv_can,
        "can_ten": can_name(dv_can),
        "chi": dv_chi,
        "chi_ten": chi_name(dv_chi),
        "cung_so": cung,
        "source_formula": {
            "Fl": fl,
            "yl": yl,
            "can_dai_van": "checkcan(Fl + yl - 1)",
        },
    }


def _source_lndv(tuoi: int, cung_dai_van: int, bat_dau: int, step: int) -> int | None:
    """Port nguyên hàm lndv(tuoi,chicungdaivan,bddaivan,step)."""
    khoi = tuoi - bat_dau
    x = cung_dai_van
    if khoi == 0:
        return x
    if khoi == 1:
        return check(x + 6)
    if khoi == 2:
        return check(x + 6 - step)
    if khoi == 3:
        return check(x + 6)
    if khoi == 4:
        return check(x + 6 + step)
    if khoi == 5:
        return check(x + 6 + 2 * step)
    if khoi == 6:
        return check(x + 6 + 3 * step)
    if khoi == 7:
        return check(x + 6 + 4 * step)
    if khoi == 8:
        return check(x + 6 + 5 * step)
    if khoi == 9:
        return check(x + 6 + 6 * step)
    return None


def _tieu_van_source_mapping(birth_branch: int, target_branch: int, gender: str) -> dict[str, Any]:
    """Port block ánh xạ Tiểu vận theo Chi của mã nguồn."""
    if birth_branch in (1, 5, 9):
        i = 11
    elif birth_branch in (2, 6, 10):
        i = 8
    elif birth_branch in (3, 7, 11):
        i = 5
    else:
        i = 2

    direction = 1 if _is_male(gender) else -1
    palace = check(i + 10)
    sequence: list[dict[str, int]] = []
    for offset in range(12):
        mapped_branch = check(birth_branch + offset * direction)
        sequence.append({"cung_so": palace, "chi": mapped_branch, "thu_tu": offset + 1})
        palace = check(palace + 1)

    selected = next((x for x in sequence if x["chi"] == target_branch), None)
    return {
        "cung_so": selected["cung_so"] if selected else None,
        "chi_nam": target_branch,
        "chi_ten": chi_name(target_branch),
        "huong": "thuận" if direction == 1 else "nghịch",
        "cung_khoi": check(i + 10),
        "sequence": sequence,
    }


def _source_luu_dai_van_can(dv_can: int, cung_dv: int) -> list[dict[str, Any]]:
    """Can của 12 cung lớp Lưu Đại vận theo ctieuvan của nguồn."""
    i = check_can(2 * dv_can + 1)
    out: list[dict[str, Any]] = []
    for offset in range(12):
        cung = check(cung_dv + offset)
        can = check_can((offset + 1) + i - 1)
        out.append({"cung_so": cung, "can": can, "can_ten": can_name(can)})
    return out


def _valid_date(day: int, month: int, year: int) -> bool:
    if month < 1 or month > 12 or day < 1 or day > 31:
        return False
    jd = _jd_from_date(day, month, year)
    return _jd_to_gregorian(jd) == (day, month, year)


def calculate_van_layers(
    chart: dict[str, Any],
    *,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
    hour: int | None = None,
    time_zone: float | None = None,
) -> dict[str, Any]:
    """Tính toàn bộ lớp vận hạn Tử Vi."""
    inp = chart.get("input", {})
    birth_year = int(inp["nam"])
    birth_can = _birth_year_can(chart)
    birth_branch = _birth_year_branch(chart)
    gender = str(inp.get("gioi_tinh", "Nam"))
    tz = float(inp.get("time_zone", 7.0) if time_zone is None else time_zone)
    target_year = birth_year if year is None else int(year)

    year_can, year_branch = can_chi_year(target_year)
    age = _tuoi_xem(birth_year, target_year)
    direction = _dv_direction(birth_can, gender)
    dv = _current_dai_van(chart, target_year)

    tieu_van = None
    if birth_branch is not None:
        tieu_van = _tieu_van_source_mapping(birth_branch, year_branch, gender)

    luu_nien_dv = None
    if dv is not None:
        luu_nien_dv = _source_lndv(age, int(dv["cung_so"]), int(dv["tuoi_bat_dau"]), direction)

    luu_dai_van = None
    if dv is not None:
        luu_dai_van = {
            "cung_dai_van": dv["cung_so"],
            "can_dai_van": dv["can"],
            "can_dai_van_ten": dv["can_ten"],
            "chi_dai_van": dv["chi"],
            "chi_dai_van_ten": dv["chi_ten"],
            "can_12_cung": _source_luu_dai_van_can(int(dv["can"]), int(dv["cung_so"])),
        }

    luu_nien_cung_so = _palace_by_branch(chart, year_branch)
    luu_nien_cung_detail = _palace_detail_by_branch(chart, year_branch)

    result: dict[str, Any] = {
        "algorithm_version": "tuvi-source-v5-luu-nien-chi-cung",
        "age": age,
        "direction": "thuận" if direction == 1 else "nghịch",
        "year": {
            "nam": target_year,
            "can": year_can,
            "can_ten": can_name(year_can),
            "chi": year_branch,
            "chi_ten": chi_name(year_branch),
            "cung_luu_nien": luu_nien_cung_so,
        },
        "dai_van": {
            "huong": "thuận" if direction == 1 else "nghịch",
            "dang_xet": dv,
            "cac_dai_van": _engine_dai_van_items(chart),
        },
        "luu_dai_van": luu_dai_van,
        "tieu_van": tieu_van,
        "luu_nien": {
            "nam": target_year,
            "can_nam": year_can,
            "can_nam_ten": can_name(year_can),
            "chi_nam": year_branch,
            "chi_nam_ten": chi_name(year_branch),
            "cung_so": luu_nien_cung_so,
            "cung_nam": luu_nien_cung_so,
            "cung_detail": luu_nien_cung_detail,
            "cung_luu_nien_trong_dai_van": luu_nien_dv,
            "phuong_phap": "Lưu niên an trực tiếp tại cung có Địa Chi trùng Chi năm xem; ví dụ 2026 Bính Ngọ -> cung Ngọ.",
        },
    }

    if month is None:
        return result
    month_int = int(month)
    day_int = None if day is None else int(day)
    if not 1 <= month_int <= 12:
        raise ValueError("thang_xem phải nằm trong 1..12")
    if day_int is not None and not _valid_date(day_int, month_int, target_year):
        raise ValueError("ngay_xem không hợp lệ")

    solar_day = day_int if day_int is not None else 1
    tk = tiet_khi_month(solar_day, month_int, target_year, tz)
    month_can = check_can(2 * year_can + tk)
    month_branch = check(tk + 2)
    result["luu_nguyet"] = {
        "thang_duong": month_int,
        "ngay_moc_tinh": day_int,
        "thang_tiet_khi": tk,
        "can": month_can,
        "can_ten": can_name(month_can),
        "chi": month_branch,
        "chi_ten": chi_name(month_branch),
        "cung": _palace_by_branch(chart, month_branch),
        "is_tiet_khi_based": True,
        "phuong_phap": "solarLongitude -> thangtk -> Can Chi tháng",
        "warning": "Nếu sát thời điểm giao tiết khí, cần giờ/phút chính xác để phân định tuyệt đối.",
    }

    if day_int is None:
        return result

    day_can, day_branch = can_chi_day(day_int, month_int, target_year)
    result["luu_nhat"] = {
        "ngay": day_int,
        "can": day_can,
        "can_ten": can_name(day_can),
        "chi": day_branch,
        "chi_ten": chi_name(day_branch),
        "cung": _palace_by_branch(chart, day_branch),
        "phuong_phap": "Julian Day -> checkcan(jd), check(jd + 2)",
    }

    if hour is not None:
        hour_branch = int(hour)
        hour_can, hour_chi = can_chi_hour(day_can, hour_branch)
        result["luu_thoi"] = {
            "chi": hour_chi,
            "chi_ten": chi_name(hour_chi),
            "can": hour_can,
            "can_ten": can_name(hour_can),
            "cung": _palace_by_branch(chart, hour_chi),
            "phuong_phap": "Can giờ = checkcan(2*Can ngày + Chi giờ - 2)",
        }

    return result
