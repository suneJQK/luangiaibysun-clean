"""Tính các lớp vận theo bộ quy tắc đã đối chiếu từ nguồn tham khảo.

Phạm vi module:
- Đại vận Tử Vi: đọc trực tiếp tuổi bắt đầu Đại vận đã được engine an vào 12 cung.
- Tiểu vận: port quy tắc ánh xạ năm Chi -> cung theo mẫu mã nguồn tham khảo.
- Lưu niên: cung có Địa Chi của năm xem.
- Lưu nguyệt: dùng tháng Tiết khí, không lấy tháng âm lịch thuần túy.
- Lưu nhật/Lưu thời: Can Chi ngày/giờ theo Julian Day.

Không thay đổi giới hạn năm 1800-2200 của API/engine.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

CAN_NAMES = ["", "Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
CHI_NAMES = ["", "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
CHI_ID = {name: idx for idx, name in enumerate(CHI_NAMES) if name}


def check(value: int) -> int:
    value = (int(value) - 1) % 12 + 1
    return value


def check_can(value: int) -> int:
    value = (int(value) - 1) % 10 + 1
    return value


def can_name(value: int) -> str:
    return CAN_NAMES[check_can(value)]


def chi_name(value: int) -> str:
    return CHI_NAMES[check(value)]


def _jd_from_date(day: int, month: int, year: int) -> int:
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    # Dùng cùng nhánh Gregorian như nguồn đang tham khảo vì app hiện giới hạn 1800-2200.
    return day + ((153 * m + 2) // 5) + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def _solar_longitude(jd: float) -> float:
    import math

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
    """Trả tháng tiết khí 1..12 theo công thức Solar Longitude của nguồn tham khảo.

    Engine hiện không nhận phút sinh/xem trong API V2, vì vậy dùng 00:00 địa phương của ngày.
    Điều này đủ cho phần lớn ngày, nhưng gần thời điểm chuyển tiết khí có thể cần phút chính xác.
    """
    jd = _jd_from_date(day, month, year)
    local_midnight_jd = jd - 0.5 - float(time_zone) / 24.0
    solar_longitude = _solar_longitude(local_midnight_jd)
    shifted = solar_longitude - 315.0
    if shifted < 30.0:
        shifted += 360.0
    return check(int(shifted // 30.0) + 1)


def can_chi_year(year: int) -> tuple[int, int]:
    can = check_can(year - 1983 + 360)
    chi = check(year - 1983 + 360)
    return can, chi


def can_chi_day(day: int, month: int, year: int) -> tuple[int, int]:
    jd = _jd_from_date(day, month, year)
    return check_can(jd), check(jd + 2)


def can_chi_hour(day_can: int, hour_branch: int) -> tuple[int, int]:
    chi = check(hour_branch)
    can = check_can(2 * day_can + chi - 2)
    return can, chi


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


def _direction_from_year_can(can_year: int | None, gender: str) -> int:
    """Dương Nam/Âm Nữ thuận; Âm Nam/Dương Nữ nghịch."""
    if can_year is None:
        return 1
    yang = check_can(can_year) % 2 == 1
    male = str(gender).strip().casefold() in {"nam", "male", "m", "1"}
    return 1 if yang == male else -1


def _find_palace_by_branch(chart: dict[str, Any], branch: int) -> int | None:
    target = chi_name(branch)
    for palace in chart.get("12_cung", {}).values():
        if palace.get("dia_chi") == target:
            return palace.get("cung_so")
    return None


def _tiểu_van_palace(birth_branch: int, target_branch: int, gender: str) -> int | None:
    """Port quy tắc ánh xạ Tiểu vận từ mã nguồn tham khảo.

    start palace mapping:
      Tý/Ngọ/Tuất-group: 11
      Sửu/Tỵ/Dậu-group: 8
      Dần/Ngọ? theo bảng nguồn: (3,7,11)->5; (4,8,12)->2
    Đây là mapping theo chỉ số Chi của mã nguồn, sau đó chạy thuận nam/nghịch nữ.
    """
    if birth_branch in (1, 5, 9):
        start = 11
    elif birth_branch in (2, 6, 10):
        start = 8
    elif birth_branch in (3, 7, 11):
        start = 5
    else:
        start = 2

    forward = str(gender).strip().casefold() in {"nam", "male", "m", "1"}
    direction = 1 if forward else -1
    palace = check(start + 10)
    for offset in range(12):
        mapped_branch = check(birth_branch + offset * direction)
        if mapped_branch == target_branch:
            return palace
        palace = check(palace + 1)
    return None


def _dai_van_layers(chart: dict[str, Any], target_year: int | None) -> dict[str, Any]:
    input_data = chart.get("input", {})
    birth_year = int(input_data.get("nam"))
    gender = str(input_data.get("gioi_tinh", "Nam"))
    age = None if target_year is None else int(target_year) - birth_year + 1

    items: list[dict[str, Any]] = []
    for palace in chart.get("12_cung", {}).values():
        start = palace.get("dai_van", {}).get("tuoi_bat_dau")
        try:
            start_int = int(start)
        except (TypeError, ValueError):
            continue
        items.append({
            "cung_so": palace.get("cung_so"),
            "cung": palace.get("cung"),
            "dia_chi": palace.get("dia_chi"),
            "tuoi_bat_dau": start_int,
            "tuoi_ket_thuc": start_int + 9,
            "can_chi": palace.get("can_chi"),
        })
    items.sort(key=lambda x: (x["tuoi_bat_dau"], x.get("cung_so") or 99))
    current = None
    if age is not None:
        current = next((item for item in items if item["tuoi_bat_dau"] <= age <= item["tuoi_ket_thuc"]), None)

    return {
        "tuoi_xem": age,
        "huong": "thuận" if _direction_from_year_can(_birth_year_can(chart), gender) == 1 else "nghịch",
        "cac_dai_van": items,
        "dang_xet": current,
    }


def calculate_van_layers(
    chart: dict[str, Any],
    *,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
    hour: int | None = None,
    time_zone: float | None = None,
) -> dict[str, Any]:
    input_data = chart.get("input", {})
    birth_year = int(input_data.get("nam"))
    target_year = birth_year if year is None else int(year)
    tz = float(input_data.get("time_zone", 7.0) if time_zone is None else time_zone)
    gender = str(input_data.get("gioi_tinh", "Nam"))

    year_can, year_branch = can_chi_year(target_year)
    birth_branch = _birth_year_branch(chart)
    tiểu_cung = _tiểu_van_palace(birth_branch or 1, year_branch, gender) if birth_branch else None

    result: dict[str, Any] = {
        "year": {
            "nam": target_year,
            "can": year_can,
            "can_ten": can_name(year_can),
            "chi": year_branch,
            "chi_ten": chi_name(year_branch),
            "cung_luu_nien": _find_palace_by_branch(chart, year_branch),
        },
        "dai_van": _dai_van_layers(chart, target_year),
        "tieu_van": {
            "cung_so": tiểu_cung,
            "chi_nam": year_branch,
            "chi_ten": chi_name(year_branch),
            "phuong_phap": "ánh xạ Tiểu vận theo mã nguồn tham khảo",
        },
    }

    if month is not None:
        month_int = int(month)
        month_branch = tiet_khi_month(1, month_int, target_year, tz)
        month_can = check_can(2 * year_can + month_branch)
        result["luu_nguyet"] = {
            "thang_duong": month_int,
            "thang_tiet_khi": month_branch,
            "thang_tiet_khi_ten": chi_name(check(month_branch + 2)),
            "can_thang": month_can,
            "can_thang_ten": can_name(month_can),
            "chi_thang": check(month_branch + 2),
            "chi_thang_ten": chi_name(month_branch + 2),
            "cung_so": _find_palace_by_branch(chart, check(month_branch + 2)),
            "ghi_chu": "Tháng dùng Tiết khí; ngày trong API hiện chưa truyền phút nên mốc chuyển tiết gần biên có thể cần phút chính xác.",
        }

    if month is not None and day is not None:
        day_int = int(day)
        day_can, day_branch = can_chi_day(day_int, month_int, target_year)
        result["luu_nhat"] = {
            "ngay": day_int,
            "can": day_can,
            "can_ten": can_name(day_can),
            "chi": day_branch,
            "chi_ten": chi_name(day_branch),
            "cung_so": _find_palace_by_branch(chart, day_branch),
            "nhat_than_cung_so": _find_palace_by_branch(chart, day_branch),
        }

        if hour is not None:
            hour_can, hour_branch = can_chi_hour(day_can, int(hour))
            result["luu_thoi"] = {
                "chi_gio": hour_branch,
                "chi_gio_ten": chi_name(hour_branch),
                "can_gio": hour_can,
                "can_gio_ten": can_name(hour_can),
                "cung_so": _find_palace_by_branch(chart, hour_branch),
            }

    return result
