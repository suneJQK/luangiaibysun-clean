from __future__ import annotations

import json
from pathlib import Path

PATH = Path("data/cach_cuc.json")

REPAIRS: dict[int, dict] = {
    # Source note limits the hội chiếu variant to Sửu/Mùi.
    2: {
        "any_of": [
            {"cung_menh": {"stars_all": ["Văn Xương", "Văn Khúc"]}},
            {
                "cung_menh": {"branches_in": ["Sửu", "Mùi"]},
                "tam_phuong_tu_chinh": {
                    "stars_required": ["Văn Xương", "Văn Khúc"],
                    "min_count": 2,
                },
            },
        ]
    },
    # The detailed source text identifies Dần/Thân for Tử Phủ đồng cung.
    7: {"cung_menh": {"stars_all": ["Tử Vi", "Thiên Phủ"], "branches_in": ["Dần", "Thân"]}},
    # Quân Thần Khánh Hội needs Tử Vi at Mệnh; supporting cát tinh must actually hội.
    10: {
        "cung_menh": {"stars_all": ["Tử Vi"]},
        "tam_phuong_tu_chinh_aux": {
            "stars_required": ["Tả Phù", "Hữu Bật", "Thiên Khôi", "Thiên Việt", "Văn Xương", "Văn Khúc", "Lộc Tồn"],
            "min_count": 2,
        },
    },
    # Cơ Nguyệt Đồng Lương explicitly requires all four stars.
    11: {
        "tam_phuong_tu_chinh": {
            "stars_required": ["Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"],
            "min_count": 4,
        }
    },
    14: {"cung_menh": {"stars_all": ["Cự Môn", "Thái Dương"], "branches_in": ["Dần", "Thân"]}},
    # Detailed note specifies Ất and the four-star pattern around Mão.
    17: {
        "cung_menh": {"branches_in": ["Mão"]},
        "tam_phuong_tu_chinh": {
            "stars_required": ["Thái Dương", "Thiên Lương", "Văn Xương"],
            "min_count": 3,
        },
        "tam_phuong_tu_chinh_loc": {"stars_required": ["Lộc Tồn"], "min_count": 1},
        "stem_contains": "Ất",
    },
    # The source describes two Tý cases: Mệnh Tý or Điền Trạch Tý, with both stars there.
    21: {
        "any_of": [
            {"cung_menh": {"branches_in": ["Tý"], "stars_all": ["Thái Âm", "Thiên Đồng"]}},
            {"cung_dien": {"branches_in": ["Tý"], "stars_all": ["Thái Âm", "Thiên Đồng"]}},
        ]
    },
    # The detailed note restricts the strong cases to Tân/Quý.
    24: {
        "any_of": [
            {"cung_menh": {"stars_all": ["Cự Môn"], "branches_in": ["Tý", "Ngọ"]}, "stem_contains": "Tân"},
            {"cung_menh": {"stars_all": ["Cự Môn"], "branches_in": ["Tý", "Ngọ"]}, "stem_contains": "Quý"},
        ]
    },
    # Add the cát-tinh support explicitly described in the source note.
    25: {
        "cung_menh": {"stars_all": ["Thất Sát"], "branches_in": ["Tý", "Ngọ", "Dần", "Thân"]},
        "tam_phuong_tu_chinh_aux": {
            "stars_required": ["Lộc Tồn", "Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Tả Phù", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"],
            "min_count": 1,
        },
    },
    # Mã Đầu Đới Tiễn: the detailed source requires Bính/Mậu and specifies two Mệnh-star variants.
    26: {
        "any_of": [
            {"cung_menh": {"branches_in": ["Ngọ"], "stars_all": ["Kình Dương", "Thiên Đồng", "Thái Âm"]}, "stem_contains": "Bính"},
            {"cung_menh": {"branches_in": ["Ngọ"], "stars_all": ["Kình Dương", "Thiên Đồng", "Thái Âm"]}, "stem_contains": "Mậu"},
            {"cung_menh": {"branches_in": ["Ngọ"], "stars_all": ["Kình Dương", "Tham Lang"]}, "stem_contains": "Bính"},
            {"cung_menh": {"branches_in": ["Ngọ"], "stars_all": ["Kình Dương", "Tham Lang"]}, "stem_contains": "Mậu"},
        ]
    },
    # The detailed note explicitly excludes Dậu for Cự Cơ đồng cung.
    27: {"cung_menh": {"stars_all": ["Cự Môn", "Thiên Cơ"], "branches_in": ["Mão"]}},
    # Require at least one of Khôi/Việt at Mệnh and the pair to be present in the Mệnh triad.
    28: {
        "cung_menh": {"stars_any": ["Thiên Khôi", "Thiên Việt"]},
        "tam_phuong_tu_chinh": {
            "stars_required": ["Thiên Khôi", "Thiên Việt"],
            "min_count": 2,
        },
    },
    # Either đồng cung or hội chiếu; keep both forms explicit.
    29: {
        "any_of": [
            {"cung_menh": {"stars_all": ["Hóa Quyền", "Hóa Lộc"]}},
            {"tam_phuong_tu_chinh": {"stars_required": ["Hóa Quyền", "Hóa Lộc"], "min_count": 2}},
        ]
    },
    # Two distinct adjacent sides, not merely two of the three stars in the same side.
    30: {
        "giap_cung_pairs": [
            ["Hóa Khoa", "Hóa Quyền"],
            ["Hóa Khoa", "Hóa Lộc"],
            ["Hóa Quyền", "Hóa Lộc"],
        ]
    },
    31: {"giap_cung_pairs": [["Lộc Tồn", "Hóa Lộc"]]},
    # Include the Thìn/Tuất variant described in the source text; Sửu/Mùi remains the đồng-cung form.
    32: {
        "any_of": [
            {"cung_menh": {"stars_all": ["Tham Lang", "Vũ Khúc"], "branches_in": ["Sửu", "Mùi"]}},
            {
                "cung_menh": {"branches_in": ["Thìn", "Tuất"], "stars_any": ["Tham Lang", "Vũ Khúc"]},
                "tam_phuong_tu_chinh": {"stars_required": ["Tham Lang", "Vũ Khúc"], "min_count": 2},
            },
        ]
    },
    # Add the Tử Vi/Thiên Phủ giáp-mệnh variant mentioned in the source.
    35: {
        "giap_cung_pairs": [
            ["Tử Vi", "Thiên Phủ"],
            ["Thái Dương", "Thái Âm"],
            ["Tả Phù", "Hữu Bật"],
            ["Thiên Khôi", "Thiên Việt"],
        ]
    },
    # "Không gặp sát tinh" is a Tam Phương Tứ Chính condition, not only đồng cung.
    38: {
        "cung_menh": {"stars_all": ["Liêm Trinh"], "branches_in": ["Thân", "Mùi"]},
        "tam_phuong_tu_chinh": {
            "stars_none": ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh"]
        },
    },
    # Sát tinh must affect Mệnh; Thất Sát and cát hóa must actually hội in the Mệnh field.
    39: {
        "cung_menh": {
            "stars_any": ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh"]
        },
        "tam_phuong_tu_chinh": {"stars_required": ["Thất Sát"], "min_count": 1},
        "tam_phuong_loc": {"stars_required": ["Hóa Lộc", "Hóa Quyền", "Lộc Tồn"], "min_count": 1},
    },
    # The detailed note describes the opposite-side Sửu/Mùi arrangement, not đồng cung.
    44: {
        "any_of": [
            {"cung_menh": {"branches_in": ["Sửu"]}, "tam_phuong_tu_chinh": {"stars_required": ["Thái Dương", "Thái Âm"], "min_count": 2}},
            {"cung_menh": {"branches_in": ["Mùi"]}, "tam_phuong_tu_chinh": {"stars_required": ["Thái Dương", "Thái Âm"], "min_count": 2}},
        ]
    },
}


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    by_id = {int(item["id"]): item for item in data}
    changed = []
    for rule_id, conditions in REPAIRS.items():
        if rule_id not in by_id:
            raise KeyError(f"Missing Cách Cục id={rule_id}")
        by_id[rule_id]["conditions"] = conditions
        changed.append(rule_id)

    ordered = [by_id[int(item["id"])] for item in data]
    PATH.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("repaired ids:", changed)


if __name__ == "__main__":
    main()
