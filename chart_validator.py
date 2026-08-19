# -*- coding: utf-8 -*-
"""Deterministic validation before an LLM call or UI rendering."""
from __future__ import annotations

PALACES={"Mệnh","Phụ Mẫu","Phúc Đức","Điền Trạch","Quan Lộc","Nô Bộc","Thiên Di","Tật Ách","Tài Bạch","Tử Tức","Phu Thê","Huynh Đệ"}
BRANCHES={"Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"}
CANS={"Giáp","Ất","Bính","Đinh","Mậu","Kỷ","Canh","Tân","Nhâm","Quý"}
MAIN_STAR_IDS=set(range(1,15))
KEY_STARS={"Thiên không","Thiên đức","Nguyệt đức","Thiên quan","Thiên phúc","Thiên giải"}


def validate_chart(data):
    errors=[];warnings=[];cungs=data.get("cungs",{}) if isinstance(data,dict) else {}
    if len(cungs)!=12:warnings.append(f"Nhận được {len(cungs)}/12 ô cung OCR.")
    seen=set()
    for key,p in cungs.items():
        if not isinstance(p,dict):errors.append(f"{key}: dữ liệu cung không hợp lệ.");continue
        name=p.get("cung") or key
        if name in seen:errors.append(f"Trùng cung: {name}")
        seen.add(name)
        if name not in PALACES:warnings.append(f"{key}: chưa xác định chắc tên cung; không được dùng địa chi làm tên cung.")
        if p.get("dia_chi") and p["dia_chi"] not in BRANCHES:warnings.append(f"{name}: địa chi không chuẩn.")
        if p.get("can") and p["can"] not in CANS:warnings.append(f"{name}: thiên can không chuẩn.")
        if p.get("can") and p.get("dia_chi") and not p.get("can_chi"):warnings.append(f"{name}: thiếu Can-Chi đầy đủ.")
        if p.get("tuan") and p.get("triet"):warnings.append(f"{name}: đồng thời có Tuần và Triệt, cần kiểm tra ảnh.")
        age=p.get("dai_van",{}).get("tuoi_bat_dau") if isinstance(p.get("dai_van"),dict) else None
        if age is not None and not 1<=int(age)<=120:warnings.append(f"{name}: tuổi bắt đầu Đại vận {age} bất thường.")
        month=p.get("luu_nguyet",{}).get("thang") if isinstance(p.get("luu_nguyet"),dict) else None
        if month is not None and not 1<=int(month)<=12:warnings.append(f"{name}: tháng Lưu nguyệt bất thường.")
    if isinstance(data,dict):
        for r in data.get("review",[]):warnings.append(f"{r.get('cung')}: OCR cần kiểm tra '{r.get('text')}'.")
    return {"valid":not errors,"errors":errors,"warnings":warnings,"needs_review":bool(warnings)}


def validate_engine_chart(data):
    """Kiểm tra schema local engine trước khi hiển thị/gửi AI."""
    errors=[];warnings=[]
    if not isinstance(data,dict):
        return {"valid":False,"errors":["Chart engine không phải object."],"warnings":[],"needs_review":True}
    cungs=data.get("12_cung",{})
    if not isinstance(cungs,dict) or len(cungs)!=12:
        errors.append(f"Engine phải có đúng 12 cung, nhận {len(cungs) if isinstance(cungs,dict) else 0}.")
    seen_names=set();key_counts={name:0 for name in KEY_STARS}
    for key,p in cungs.items() if isinstance(cungs,dict) else []:
        if not isinstance(p,dict):
            errors.append(f"{key}: dữ liệu cung không hợp lệ.");continue
        name=p.get("cung") or key
        if name in seen_names:warnings.append(f"Trùng tên cung engine: {name}")
        seen_names.add(name)
        main=p.get("chinh_tinh",[]) or []
        support=p.get("phu_tinh",[]) or []
        main_ids={x.get("id") for x in main if isinstance(x,dict)}
        support_ids={x.get("id") for x in support if isinstance(x,dict)}
        overlap=main_ids & support_ids
        if overlap:errors.append(f"{name}: chính tinh bị lặp vào phụ tinh: {sorted(overlap)}")
        if any(x not in MAIN_STAR_IDS for x in main_ids if x is not None):warnings.append(f"{name}: chinh_tinh có ID ngoài 1..14.")
        for star in (main+support):
            if isinstance(star,dict) and star.get("ten") in key_counts:key_counts[star["ten"]]+=1
    for star,count in key_counts.items():
        if count!=1:errors.append(f"{star}: phải được an đúng 1 lần, hiện {count}.")
    return {"valid":not errors,"errors":errors,"warnings":warnings,"needs_review":bool(warnings)}
