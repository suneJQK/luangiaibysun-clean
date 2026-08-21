"""Structured reasoning layer for Tử Vi vận hạn.

Module này KHÔNG tự đoán sự kiện bằng AI. Nó biến các tầng vận đã tính thành
một ``reasoning_context`` có thứ tự, bằng chứng và mức ưu tiên để AI luận giải.

Nguyên tắc:
1. Xác định tầng thời gian đang xét.
2. Xác định cung bị kích hoạt ở từng tầng.
3. Đọc đồng cung trước.
4. Đọc Tam Hợp + Xung Chiếu.
5. Đọc Nhị Hợp và Giáp Cung như quan hệ bổ trợ, không thay thế Tam Hợp.
6. Kiểm tra Tuần/Triệt.
7. Kiểm tra Can Chi / Tứ Hóa của năm-tháng khi engine đã có dữ liệu.
8. Chồng các tầng theo trọng số: Nguyên cục -> Đại vận -> Lưu niên ->
   Tiểu vận -> Lưu nguyệt -> Lưu nhật -> Lưu thời.
9. Tách ``nền tảng`` khỏi ``kích hoạt`` để tránh luận hạn từ một dấu hiệu đơn lẻ.
"""
from __future__ import annotations

from typing import Any

BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

LAYER_WEIGHTS = {
    "nguyen_cuc": 100,
    "dai_van": 80,
    "luu_nien": 70,
    "tieu_van": 60,
    "luu_nguyet": 45,
    "luu_nhat": 30,
    "luu_thoi": 20,
}

PALACE_ALIASES = {
    "Mệnh": {"mệnh", "menh"},
    "Phụ mẫu": {"phụ mẫu", "phu mau"},
    "Phúc đức": {"phúc đức", "phuc duc"},
    "Điền trạch": {"điền trạch", "dien trach"},
    "Quan lộc": {"quan lộc", "quan loc"},
    "Nô bộc": {"nô bộc", "no boc"},
    "Thiên di": {"thiên di", "thien di"},
    "Tật ách": {"tật ách", "tat ach"},
    "Tài bạch": {"tài bạch", "tai bach"},
    "Tử tức": {"tử tức", "tu tuc"},
    "Phu thê": {"phu thê", "phu the"},
    "Huynh đệ": {"huynh đệ", "huynh de"},
}


def _norm(s: Any) -> str:
    return str(s or "").strip().casefold()


def _branch_index(name: str) -> int | None:
    try:
        return BRANCHES.index(name)
    except ValueError:
        return None


def _cung_map(chart: dict[str, Any]) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    for palace in chart.get("12_cung", {}).values():
        number = palace.get("cung_so")
        if isinstance(number, int):
            result[number] = palace
    return result


def _palace_by_number(chart: dict[str, Any], number: int | None) -> dict[str, Any] | None:
    if number is None:
        return None
    return _cung_map(chart).get(int(number))


def _palace_by_name(chart: dict[str, Any], name: str) -> dict[str, Any] | None:
    wanted = _norm(name)
    for palace in chart.get("12_cung", {}).values():
        if _norm(palace.get("cung")) == wanted:
            return palace
    return None


def _palace_by_branch(chart: dict[str, Any], branch: str) -> dict[str, Any] | None:
    wanted = _norm(branch)
    for palace in chart.get("12_cung", {}).values():
        if _norm(palace.get("dia_chi")) == wanted:
            return palace
    return None


def _stars(palace: dict[str, Any] | None) -> list[str]:
    if not palace:
        return []
    names: list[str] = []
    for star in palace.get("sao", []) or []:
        if isinstance(star, dict) and star.get("ten"):
            names.append(str(star["ten"]))
    return names


def _relation(a: str, b: str) -> str:
    """Quan hệ theo Địa Chi; Nhị hợp và Giáp cung có định nghĩa riêng."""
    ia = _branch_index(a)
    ib = _branch_index(b)
    if ia is None or ib is None or ia == ib:
        return "dong_cung" if ia == ib and ia is not None else "khac"
    d = (ib - ia) % 12
    if d in (4, 8):
        return "tam_hop"
    if d == 6:
        return "xung_chieu"
    if {a, b} in [
        {"Tý", "Sửu"}, {"Dần", "Hợi"}, {"Mão", "Tuất"},
        {"Thìn", "Dậu"}, {"Tỵ", "Thân"}, {"Ngọ", "Mùi"},
    ]:
        return "nhi_hop"
    return "khac"


def _relation_between_palaces(base: dict[str, Any], other: dict[str, Any]) -> str:
    if base.get("cung_so") == other.get("cung_so"):
        return "dong_cung"
    if isinstance(base.get("cung_so"), int) and isinstance(other.get("cung_so"), int):
        diff = (int(other["cung_so"]) - int(base["cung_so"])) % 12
        if diff in (1, 11):
            return "giap_cung"
    return _relation(str(base.get("dia_chi", "")), str(other.get("dia_chi", "")))


def _activated_palace_refs(chart: dict[str, Any], van: dict[str, Any]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []

    def add(layer: str, data: dict[str, Any] | None) -> None:
        if not data:
            return
        palace = _palace_by_number(chart, data.get("cung_so"))
        if palace:
            refs.append({
                "layer": layer,
                "cung_so": palace.get("cung_so"),
                "cung": palace.get("cung"),
                "dia_chi": palace.get("dia_chi"),
                "can_chi": palace.get("can_chi"),
                "source": data,
            })

    add("luu_nien", van.get("year", {}))
    add("dai_van", van.get("dai_van", {}).get("dang_xet"))
    add("tieu_van", van.get("tieu_van", {}))
    add("luu_nguyet", van.get("luu_nguyet", {}))
    add("luu_nhat", van.get("luu_nhat", {}))
    add("luu_thoi", van.get("luu_thoi", {}))
    return refs


def _interactions(chart: dict[str, Any], target: dict[str, Any]) -> list[dict[str, Any]]:
    interactions: list[dict[str, Any]] = []
    for palace in chart.get("12_cung", {}).values():
        if palace.get("cung_so") == target.get("cung_so"):
            continue
        relation = _relation_between_palaces(target, palace)
        if relation in {"tam_hop", "xung_chieu", "nhi_hop", "giap_cung"}:
            interactions.append({
                "quan_he": relation,
                "cung_so": palace.get("cung_so"),
                "cung": palace.get("cung"),
                "dia_chi": palace.get("dia_chi"),
                "stars": _stars(palace),
            })
    order = {"tam_hop": 0, "xung_chieu": 1, "nhi_hop": 2, "giap_cung": 3}
    interactions.sort(key=lambda x: order.get(x["quan_he"], 99))
    return interactions


def _tieu_van_tam_phuong_tu_chinh(chart: dict[str, Any], van: dict[str, Any]) -> dict[str, Any]:
    """Xác định Tam phương Tứ chính của CHÍNH CUNG TIỂU VẬN.

    Đây là nguồn authoritative cho luận hạn. Không lấy Quan/Tài/Tật/Di theo
    tên chức năng. Trước hết phải lấy đúng vị trí ``cung_so`` của Tiểu vận,
    sau đó xác định quan hệ hình học từ chính cung đó.
    """
    tieu = van.get("tieu_van") or {}
    target_number = tieu.get("cung_so")
    target = _palace_by_number(chart, target_number)
    if not target:
        return {"cung_tieu_van": None, "tam_phuong": [], "xung_chieu": None, "nhi_hop": None, "giap_cung": []}

    tam_phuong: list[dict[str, Any]] = []
    xung_chieu: dict[str, Any] | None = None
    nhi_hop: dict[str, Any] | None = None
    giap_cung: list[dict[str, Any]] = []

    for palace in chart.get("12_cung", {}).values():
        if palace.get("cung_so") == target.get("cung_so"):
            continue
        relation = _relation_between_palaces(target, palace)
        item = {
            "cung_so": palace.get("cung_so"),
            "cung": palace.get("cung"),
            "dia_chi": palace.get("dia_chi"),
            "can_chi": palace.get("can_chi"),
            "stars": _stars(palace),
        }
        if relation == "tam_hop":
            tam_phuong.append(item)
        elif relation == "xung_chieu":
            xung_chieu = item
        elif relation == "nhi_hop":
            nhi_hop = item
        elif relation == "giap_cung":
            giap_cung.append(item)

    tam_phuong.sort(key=lambda x: int(x.get("cung_so") or 0))
    giap_cung.sort(key=lambda x: int(x.get("cung_so") or 0))

    return {
        "cung_tieu_van": {
            "cung_so": target.get("cung_so"),
            "cung": target.get("cung"),
            "dia_chi": target.get("dia_chi"),
            "can_chi": target.get("can_chi"),
            "stars": _stars(target),
        },
        "tam_phuong": tam_phuong,
        "xung_chieu": xung_chieu,
        "nhi_hop": nhi_hop,
        "giap_cung": giap_cung,
        "rule": "Lấy chính cung_so của Tiểu vận; Tam hợp = Địa Chi cách 4/8; Xung chiếu = cách 6; Nhị hợp = cặp Địa Chi cố định; Giáp cung = vị trí cung_so kề nhau.",
        "anti_confusion": "Không được chọn cung Quan/Tài/Tật/Di chỉ vì tên chức năng; phải xác định quan hệ thực tế từ cung Tiểu vận trước, sau đó mới gắn tên cung chức năng.",
    }


def _tuan_triet(palace: dict[str, Any]) -> dict[str, bool]:
    return {"tuan": bool(palace.get("tuan")), "triet": bool(palace.get("triet"))}


def build_reasoning_context(chart: dict[str, Any], van: dict[str, Any]) -> dict[str, Any]:
    """Tạo cây suy luận vận hạn có thể đưa thẳng cho AI."""
    active = _activated_palace_refs(chart, van)
    evidence: list[dict[str, Any]] = []

    for ref in active:
        palace = _palace_by_number(chart, ref.get("cung_so")) or {}
        layer = str(ref["layer"])
        evidence.append({
            "layer": layer,
            "priority": LAYER_WEIGHTS.get(layer, 0),
            "cung_so": palace.get("cung_so"),
            "cung": palace.get("cung"),
            "dia_chi": palace.get("dia_chi"),
            "chinh_tinh": [s.get("ten") for s in palace.get("chinh_tinh", []) if isinstance(s, dict)],
            "phu_tinh": [s.get("ten") for s in palace.get("phu_tinh", []) if isinstance(s, dict)],
            "stars": _stars(palace),
            "tuan_triet": _tuan_triet(palace),
            "interactions": _interactions(chart, palace),
        })

    evidence.sort(key=lambda x: -x["priority"])
    tieu_van_ttp = _tieu_van_tam_phuong_tu_chinh(chart, van)

    workflow = [
        "Xác định tuổi/năm và tầng vận đang kích hoạt.",
        "Xác định cung bị kích hoạt ở đúng tầng vận; không thay thế bằng cung chức năng khác.",
        "Đọc đồng cung: chính tinh -> phụ tinh -> sát tinh/bại tinh -> Tứ Hóa/Tuần/Triệt nếu có.",
        "Với Tiểu vận: bắt buộc lấy chính cung_so của Tiểu vận để xác định Tam phương Tứ chính.",
        "Tam hợp = hai cung có Địa Chi cách 4 hoặc 8; Xung chiếu = cách 6; Nhị hợp = cặp Địa Chi cố định; Giáp cung = vị trí cung_so kề nhau.",
        "Chỉ sau khi xác định quan hệ hình học mới gọi tên cung chức năng Quan/Tài/Tật/Di...",
        "Đọc Nhị Hợp và Giáp Cung như lớp bổ trợ.",
        "Đối chiếu với Mệnh/Thân và các cung chức năng liên quan đến câu hỏi.",
        "Xét Lưu nguyệt/Lưu nhật/Lưu thời chỉ sau khi nền Đại vận + Lưu niên đã rõ.",
        "Chỉ kết luận sự kiện khi có hội đủ nền + kích hoạt; không kết luận từ một sao hoặc một quan hệ đơn lẻ.",
    ]

    return {
        "engine": "van_reasoning_v2",
        "workflow": workflow,
        "active_layers": evidence,
        "tieu_van_tam_phuong_tu_chinh": tieu_van_ttp,
        "principles": {
            "dai_van": "lớp nền dài hạn",
            "luu_nien": "kích hoạt chủ đề trong năm",
            "tieu_van": "lớp hạn năm theo quy tắc Tiểu vận của hệ thống",
            "luu_nguyet": "kích hoạt theo tháng Tiết khí",
            "luu_nhat": "vi mô theo ngày",
            "luu_thoi": "vi mô theo giờ",
            "nhieu_tang": "một kết luận mạnh cần nhiều lớp cùng chỉ về một chủ đề",
        },
        "anti_error_rules": [
            "Không gọi Giáp Cung là Nhị Hợp.",
            "Không gọi Xung Chiếu là Tam Hợp.",
            "Không dùng Lưu nguyệt để phủ định nền Đại vận nếu không có bằng chứng tầng cao.",
            "Không luận một sự kiện chắc chắn chỉ từ một sát tinh.",
            "Phải ghi rõ lớp nào tạo nền và lớp nào tạo kích hoạt.",
            "Tam phương Tứ chính của Tiểu vận phải lấy theo vị trí thực tế của cung Tiểu vận, không lấy theo danh xưng Quan/Tài/Tật/Di.",
        ],
    }
