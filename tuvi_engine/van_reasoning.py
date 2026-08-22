"""Structured reasoning layer for Tử Vi vận hạn.

Module này KHÔNG tự đoán sự kiện bằng AI. Nó biến các tầng vận đã tính thành
một reasoning_context có thứ tự, bằng chứng và mức ưu tiên để AI luận giải.
"""
from __future__ import annotations

from typing import Any
import re
import unicodedata

BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

TAM_PHUONG_GROUPS = (
    frozenset(("Thân", "Tý", "Thìn")),
    frozenset(("Dần", "Ngọ", "Tuất")),
    frozenset(("Tỵ", "Dậu", "Sửu")),
    frozenset(("Hợi", "Mão", "Mùi")),
)

NHI_HOP = {
    frozenset(("Tý", "Sửu")),
    frozenset(("Hợi", "Dần")),
    frozenset(("Tuất", "Mão")),
    frozenset(("Thìn", "Dậu")),
    frozenset(("Tỵ", "Thân")),
    frozenset(("Ngọ", "Mùi")),
}

LAYER_WEIGHTS = {
    "nguyen_cuc": 100,
    "dai_van": 80,
    "luu_dai_van": 75,
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


def _branch_name(value: Any) -> str | None:
    """Chuẩn hóa Tý/Tỵ và mã nội bộ ty1/ty2 về cùng một tên chuẩn."""
    if value is None:
        return None
    raw = str(value).strip().casefold()
    direct = {
        "tý": "Tý", "tỵ": "Tỵ", "sửu": "Sửu", "dần": "Dần", "mão": "Mão",
        "thìn": "Thìn", "ngọ": "Ngọ", "mùi": "Mùi", "thân": "Thân",
        "dậu": "Dậu", "tuất": "Tuất", "hợi": "Hợi",
        "ty1": "Tý", "ty2": "Tỵ", "suu": "Sửu", "dan": "Dần", "mao": "Mão",
        "thin": "Thìn", "ngo": "Ngọ", "mui": "Mùi", "than": "Thân", "dau": "Dậu",
        "tuat": "Tuất", "hoi": "Hợi",
    }
    if raw in direct:
        return direct[raw]
    no_marks = unicodedata.normalize("NFD", raw)
    no_marks = "".join(c for c in no_marks if unicodedata.category(c) != "Mn")
    no_marks = re.sub(r"\d+$", "", no_marks)
    fallback = {
        "ty": "Tý", "suu": "Sửu", "dan": "Dần", "mao": "Mão", "thin": "Thìn",
        "ngo": "Ngọ", "mui": "Mùi", "than": "Thân", "dau": "Dậu", "tuat": "Tuất", "hoi": "Hợi",
    }
    return fallback.get(no_marks)


def _branch_index(name: Any) -> int | None:
    branch = _branch_name(name)
    try:
        return BRANCHES.index(branch) if branch else None
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


def _stars(palace: dict[str, Any] | None) -> list[str]:
    if not palace:
        return []
    return [str(s["ten"]) for s in palace.get("sao", []) or [] if isinstance(s, dict) and s.get("ten")]


def _relation(a: Any, b: Any) -> str:
    """Quan hệ Địa Chi thuần túy: Tam phương, Xung chiếu, Nhị hợp."""
    a_name = _branch_name(a)
    b_name = _branch_name(b)
    ia = _branch_index(a_name)
    ib = _branch_index(b_name)
    if a_name is None or b_name is None or ia is None or ib is None:
        return "khac"
    if a_name == b_name:
        return "dong_cung"
    if any({a_name, b_name}.issubset(group) for group in TAM_PHUONG_GROUPS):
        return "tam_hop"
    if (ib - ia) % 12 == 6:
        return "xung_chieu"
    if frozenset((a_name, b_name)) in NHI_HOP:
        return "nhi_hop"
    return "khac"


def _relation_between_palaces(base: dict[str, Any], other: dict[str, Any]) -> str:
    """Quan hệ đầy đủ giữa hai cung; Giáp cung dùng cung_so +/-1."""
    base_no = base.get("cung_so")
    other_no = other.get("cung_so")
    if base_no == other_no:
        return "dong_cung"
    if isinstance(base_no, int) and isinstance(other_no, int):
        diff = (other_no - base_no) % 12
        if diff in (1, 11):
            return "giap_cung"
    return _relation(base.get("dia_chi"), other.get("dia_chi"))


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

    add("luu_nien", van.get("luu_nien") or van.get("year", {}))
    add("dai_van", van.get("dai_van", {}).get("dang_xet"))
    add("luu_dai_van", van.get("luu_dai_van", {}))
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
                "dia_chi_chuan": _branch_name(palace.get("dia_chi")),
                "can_chi": palace.get("can_chi"),
                "stars": _stars(palace),
            })
    order = {"tam_hop": 0, "xung_chieu": 1, "nhi_hop": 2, "giap_cung": 3}
    interactions.sort(key=lambda x: (order.get(x["quan_he"], 99), int(x.get("cung_so") or 0)))
    return interactions


def _tieu_van_tam_phuong_tu_chinh(chart: dict[str, Any], van: dict[str, Any]) -> dict[str, Any]:
    """Tam phương Tứ chính của đúng cung Tiểu vận."""
    tieu = van.get("tieu_van") or {}
    target = _palace_by_number(chart, tieu.get("cung_so"))
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
            "dia_chi_chuan": _branch_name(palace.get("dia_chi")),
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
            "dia_chi_chuan": _branch_name(target.get("dia_chi")),
            "can_chi": target.get("can_chi"),
            "stars": _stars(target),
        },
        "tam_phuong": tam_phuong,
        "xung_chieu": xung_chieu,
        "nhi_hop": nhi_hop,
        "giap_cung": giap_cung,
        "rule": {
            "tam_phuong": ["Thân-Tý-Thìn", "Dần-Ngọ-Tuất", "Tỵ-Dậu-Sửu", "Hợi-Mão-Mùi"],
            "xung_chieu": "Cung đối diện cung đang xét, cung_so cách 6; ví dụ Tý-Ngọ, Sửu-Mùi, Dần-Thân.",
            "giap_cung": "Cung trước và sau của cung gốc, cung_so +1 và -1 theo vòng 12 cung; ví dụ cung Hợi giáp Tý và Tuất.",
            "nhi_hop": ["Tý-Sửu", "Hợi-Dần", "Tuất-Mão", "Thìn-Dậu", "Tỵ-Thân", "Ngọ-Mùi"],
        },
        "anti_confusion": "Không được chọn Quan/Tài/Tật/Di chỉ vì tên chức năng; phải xác định cung thực tế trước rồi mới gắn tên cung chức năng.",
    }


def _tuan_triet(palace: dict[str, Any]) -> dict[str, bool]:
    return {"tuan": bool(palace.get("tuan")), "triet": bool(palace.get("triet"))}


def build_reasoning_context(chart: dict[str, Any], van: dict[str, Any]) -> dict[str, Any]:
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
            "dia_chi_chuan": _branch_name(palace.get("dia_chi")),
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
        "Tam phương phải lấy theo 4 tổ hợp Địa Chi: Thân-Tý-Thìn; Dần-Ngọ-Tuất; Tỵ-Dậu-Sửu; Hợi-Mão-Mùi.",
        "Xung chiếu là cung đối diện, cung_so cách 6.",
        "Giáp cung là cung trước và sau của cung gốc, cung_so +1 và -1 theo vòng 12 cung.",
        "Nhị hợp là các cặp ngang hàng: Tý-Sửu; Hợi-Dần; Tuất-Mão; Thìn-Dậu; Tỵ-Thân; Ngọ-Mùi.",
        "Chỉ sau khi xác định quan hệ hình học mới gắn tên cung chức năng Quan/Tài/Tật/Di...",
        "Đọc Nhị Hợp và Giáp Cung như lớp bổ trợ.",
        "Chồng các tầng: Nguyên cục -> Đại vận -> Lưu Đại vận -> Lưu niên -> Tiểu vận -> Lưu nguyệt -> Lưu nhật -> Lưu thời.",
        "Chỉ kết luận sự kiện khi có hội đủ nền + kích hoạt; không kết luận từ một sao hoặc một quan hệ đơn lẻ.",
    ]

    return {
        "engine": "van_reasoning_v3",
        "workflow": workflow,
        "active_layers": evidence,
        "tieu_van_tam_phuong_tu_chinh": tieu_van_ttp,
        "principles": {
            "dai_van": "lớp nền dài hạn",
            "luu_dai_van": "lớp chuyển động trong Đại vận",
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
            "Không trộn Tam phương với Giáp cung.",
            "Không chọn cung Quan/Tài/Tật/Di theo tên chức năng thay cho vị trí cung thực tế.",
            "Không dùng Lưu nguyệt để phủ định nền Đại vận nếu không có bằng chứng tầng cao.",
            "Không luận một sự kiện chắc chắn chỉ từ một sát tinh.",
            "Phải ghi rõ lớp nào tạo nền và lớp nào tạo kích hoạt.",
        ],
    }
