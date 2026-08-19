#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ứng dụng Tử Vi: lập lá số bằng engine Python local -> dữ liệu sạch -> chat AI."""
from __future__ import annotations
import json, os
from datetime import date
from pathlib import Path
import streamlit as st
from google import genai
from google.genai import types
from tuvi_lap_so_engine import lap_la_so
from tu_vi_calculator import calculate_chart

st.set_page_config(page_title="Tử Vi Đẩu Số", page_icon="☯️", layout="wide")
BASE_DIR = Path(__file__).resolve().parent
BOOKS_FILE = BASE_DIR / "books_cache.json"
PROMPT_DIR = BASE_DIR / "system_prompts"
ROOT_PROMPT_FILE = BASE_DIR / "system_prompt_tuvi.txt"

def secret(n):
    try:
        if n in st.secrets:
            return str(st.secrets[n])
    except Exception:
        pass
    return os.environ.get(n, "") or ""

API_KEY = secret("GEMINI_API_KEY")

@st.cache_resource
def get_client(k):
    if not k:
        raise ValueError("Thiếu GEMINI_API_KEY")
    return genai.Client(api_key=k)

@st.cache_data(ttl=3600)
def load_json(p):
    try:
        return (json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}), None
    except Exception as e:
        return {}, str(e)

@st.cache_data(ttl=3600)
def load_prompt():
    """Nạp system prompt từ file root và các prompt bổ sung."""
    files = []
    if ROOT_PROMPT_FILE.exists():
        files.append(ROOT_PROMPT_FILE)
    if PROMPT_DIR.exists():
        files.extend(sorted(PROMPT_DIR.glob("*.txt")))
    try:
        parts = []
        seen = set()
        for p in files:
            rp = p.resolve()
            if rp in seen:
                continue
            seen.add(rp)
            text = p.read_text(encoding="utf-8").strip()
            if text:
                parts.append(text)
        return ("\n\n".join(parts) if parts else "Bạn là chuyên gia Tử Vi Đẩu Số."), None
    except Exception as e:
        return "Bạn là chuyên gia Tử Vi Đẩu Số.", str(e)

books, _ = load_json(BOOKS_FILE)
system_prompt, _ = load_prompt()

def compact(v, limit=90000):
    s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, separators=(",", ":"))
    return s if len(s) <= limit else s[:limit] + "..."

def ask_ai(q, chart, calc, year):
    prompt = f'''Năm luận: {year}\n\nCÂU HỎI:\n{q}\n\nDỮ LIỆU LÁ SỐ TỪ ENGINE PYTHON LOCAL:\n{compact(chart)}\n\nQUAN HỆ TÍNH BẰNG PYTHON:\n{compact(calc,30000)}\n\nTÀI LIỆU:\n{compact(books,40000)}\n\nChỉ diễn giải dữ liệu được cung cấp. Không đọc ảnh/OCR, không tự an sao, không tự thêm hoặc sửa sao/Can-Chi. Dùng đầy đủ chính tinh, phụ tinh, Tứ Hóa, Tràng Sinh, Tuần/Triệt, Đại vận, Tiểu vận và hạn nếu có. Trạng thái sao M/V/Đ/B/H tương ứng Miếu/Vượng/Đắc/Bình/Hãm phải được giữ nguyên theo dữ liệu engine, không tự suy diễn lại. Nếu thiếu dữ liệu thì nói rõ.'''
    cfg = types.GenerateContentConfig(
        system_instruction=system_prompt + "\nAI chỉ diễn giải dữ liệu từ engine Python local và tuyệt đối không thay đổi dữ liệu đầu vào.",
        temperature=.2,
        max_output_tokens=30000,
    )
    return get_client(API_KEY).models.generate_content(
        model="gemini-3.6-flash", contents=prompt, config=cfg
    ).text

st.session_state.setdefault("chart_json", None)
st.session_state.setdefault("chat_history", [])
st.title("☯️ TỬ VI ĐẨU SỐ")
st.caption("Lập lá số bằng engine Python local → dữ liệu chuẩn → AI luận giải")
st.header("① Lập lá số")

with st.form("lap_la_so_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        lich = st.radio("Loại lịch", ["Dương lịch", "Âm lịch"], horizontal=True)
        ns = st.date_input("Ngày sinh", date(1996, 1, 1), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY")
    with c2:
        gt = st.radio("Giới tính", ["Nam", "Nữ"], horizontal=True)
        ten = st.text_input("Họ tên", "")
    with c3:
        labels = [
            "Tý (23:00–00:59)", "Sửu (01:00–02:59)", "Dần (03:00–04:59)",
            "Mão (05:00–06:59)", "Thìn (07:00–08:59)", "Tỵ (09:00–10:59)",
            "Ngọ (11:00–12:59)", "Mùi (13:00–14:59)", "Thân (15:00–16:59)",
            "Dậu (17:00–18:59)", "Tuất (19:00–20:59)", "Hợi (21:00–22:59)"
        ]
        gl = st.selectbox("Giờ sinh", labels, index=6)
        tz = st.number_input("Múi giờ", -12, 14, 7, 1)
    lap = st.form_submit_button("🧭 LẬP LÁ SỐ", type="primary", use_container_width=True)

if lap:
    try:
        branch = gl.split(" ", 1)[0]
        chart = lap_la_so(ns.day, ns.month, ns.year, branch, gt, ten, lich == "Dương lịch", int(tz))
        if len(chart.get("12_cung", {})) != 12:
            raise ValueError("Engine không tạo đủ 12 cung")
        chart.setdefault("input", {})["gio_hien_thi"] = gl
        chart["input"]["lich"] = lich
        st.session_state.chart_json = chart
        st.session_state.chat_history = []
        st.success("Đã lập lá số và an sao bằng engine local.")
    except Exception as e:
        st.error(f"Không thể lập lá số: {type(e).__name__}: {e}")

if st.session_state.chart_json:
    chart = st.session_state.chart_json
    tb = chart.get("thien_ban", {})
    st.header("② Dữ liệu lập lá số")
    m = st.columns(5)
    m[0].metric("Nguồn", "LOCAL")
    m[1].metric("12 cung", len(chart.get("12_cung", {})))
    m[2].metric("Cục", tb.get("ten_cuc") or "—")
    m[3].metric("Mệnh", tb.get("menh") or "—")
    m[4].metric("Thân", tb.get("than_chu") or "—")
    tabs = st.tabs(["Thiên bàn", "12 cung", "Hạn", "JSON gửi AI"])
    with tabs[0]:
        st.json(tb)
    with tabs[1]:
        rows = []
        def star_label(x):
            if not isinstance(x, dict):
                return ""
            ten_sao = x.get("ten", "")
            dt = x.get("dac_tinh")
            return f"{ten_sao} [{dt}]" if dt else ten_sao
        def names(xs):
            vals = [star_label(x) for x in xs if isinstance(x, dict) and x.get("ten")]
            return "; ".join(vals) or "—"
        for name, d in chart.get("12_cung", {}).items():
            if not isinstance(d, dict):
                continue
            flags = ", ".join(x for x, ok in [("Tuần", d.get("tuan")), ("Triệt", d.get("triet"))] if ok) or "—"
            rows.append({
                "Cung": name + (" (Thân cư)" if d.get("than_cu") else ""),
                "Can-Chi": d.get("can_chi") or "—",
                "Ngũ hành": d.get("ngu_hanh") or "—",
                "Tràng sinh": d.get("vong_trang_sinh") or "—",
                "Tuần/Triệt": flags,
                "Chính tinh": names(d.get("chinh_tinh", [])),
                "Phụ tinh": names(d.get("sao", [])),
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.caption("M = Miếu · V = Vượng · Đ = Đắc · B = Bình · H = Hãm; sao không có đặc tính vẫn được hiển thị.")
    with tabs[2]:
        st.json({n: {"dai_van": d.get("dai_van", {}), "tieu_van": d.get("tieu_van", {})} for n, d in chart.get("12_cung", {}).items()})
    with tabs[3]:
        st.json(chart)
    st.download_button("⬇️ Tải JSON lá số", json.dumps(chart, ensure_ascii=False, indent=2), "la_so_tu_vi.json", "application/json", use_container_width=True)
    st.header("③ Chat với AI")
    st.caption("AI chỉ nhận dữ liệu lập lá số từ engine Python local; không nhận ảnh/OCR.")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    q = st.chat_input("Nhập câu hỏi về lá số…")
    if q:
        st.session_state.chat_history.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        with st.chat_message("assistant"):
            try:
                with st.spinner("AI đang luận giải…"):
                    ans = ask_ai(q, chart, calculate_chart(chart), date.today().year)
                st.markdown(ans)
                st.session_state.chat_history.append({"role": "assistant", "content": ans})
            except Exception as e:
                ans = f"Không thể gọi AI: {type(e).__name__}: {e}"
                st.error(ans)
                st.session_state.chat_history.append({"role": "assistant", "content": ans})
else:
    st.info("Nhập thông tin sinh và bấm LẬP LÁ SỐ. Sau đó phần Chat với AI sẽ xuất hiện.")