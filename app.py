#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ứng dụng Tử Vi: engine Python local -> dữ liệu sạch -> chat AI."""
from __future__ import annotations
import json, os
from datetime import date
from pathlib import Path
import streamlit as st
from google import genai
from google.genai import types
from tuvi_lap_so_engine import lap_la_so
from tu_vi_calculator import calculate_chart
from chart_sanitizer import normalize_engine_chart
from tuvi_engine.rules.analysis import analyze_chart

st.set_page_config(page_title="Tử Vi Đẩu Số", page_icon="☯️", layout="wide", initial_sidebar_state="collapsed")
BASE_DIR=Path(__file__).resolve().parent
BOOKS_FILE=BASE_DIR/"books_cache.json"; PROMPT_DIR=BASE_DIR/"system_prompts"; ROOT_PROMPT_FILE=BASE_DIR/"system_prompt_tuvi.txt"
st.markdown("""
<style>
#MainMenu,footer{visibility:hidden}.block-container{max-width:1200px;padding:1rem 1.2rem 2rem}h1{font-size:1.65rem!important;margin:.1rem 0 .2rem!important}h2{font-size:1.15rem!important;margin:.7rem 0 .45rem!important}h3{font-size:1rem!important;margin:.4rem 0 .25rem!important}[data-testid="stCaptionContainer"]{font-size:.78rem}[data-testid="stMetric"]{padding:.45rem .6rem;border:1px solid rgba(128,128,128,.22);border-radius:10px}[data-testid="stDataFrame"]{border-radius:10px;overflow:hidden}div.stButton>button,div.stFormSubmitButton>button{border-radius:9px;min-height:2.2rem}.compact-note{font-size:.76rem;opacity:.72;margin:.1rem 0 .45rem}@media(max-width:700px){.block-container{padding:.7rem .55rem 1.5rem}h1{font-size:1.35rem!important}}
</style>""",unsafe_allow_html=True)

def secret(n):
    try:
        if n in st.secrets:return str(st.secrets[n])
    except Exception:pass
    return os.environ.get(n,"") or ""
API_KEY=secret("GEMINI_API_KEY")
@st.cache_resource
def get_client(k):
    if not k:raise ValueError("Thiếu GEMINI_API_KEY")
    return genai.Client(api_key=k)
@st.cache_data(ttl=3600)
def load_json(p):
    try:return (json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}),None
    except Exception as e:return {},str(e)
@st.cache_data(ttl=3600)
def load_prompt():
    files=[]
    if ROOT_PROMPT_FILE.exists():files.append(ROOT_PROMPT_FILE)
    if PROMPT_DIR.exists():files.extend(sorted(PROMPT_DIR.glob("*.txt")))
    try:
        parts=[];seen=set()
        for p in files:
            rp=p.resolve()
            if rp in seen:continue
            seen.add(rp);text=p.read_text(encoding="utf-8").strip()
            if text:parts.append(text)
        return ("\n\n".join(parts) if parts else "Bạn là chuyên gia Tử Vi Đẩu Số."),None
    except Exception as e:return "Bạn là chuyên gia Tử Vi Đẩu Số.",str(e)
books,_=load_json(BOOKS_FILE);system_prompt,_=load_prompt()
def compact(v,limit=90000):
    s=v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,separators=(",",":"))
    return s if len(s)<=limit else s[:limit]+"..."
def ask_ai(q,chart,calc,year):
    analyzed_chart=analyze_chart(chart)
    ai_chart=normalize_engine_chart(analyzed_chart,for_ai=True)
    ai_context=analyzed_chart.get("ai_context",{})
    cach_cuc_analysis=analyzed_chart.get("cach_cuc_analysis",{})
    prompt=f'''Năm luận: {year}\n\nCÂU HỎI:\n{q}\n\nDỮ LIỆU LÁ SỐ ĐÃ CHUẨN HÓA TỪ ENGINE PYTHON LOCAL:\n{compact(ai_chart)}\n\nBẰNG CHỨNG CÁCH CỤC ĐÃ MATCH:\n{compact(cach_cuc_analysis,30000)}\n\nQUAN HỆ CUNG DÙNG CHO LUẬN GIẢI:\n{compact(ai_context.get("relationship_knowledge",{}),20000)}\n\nCONTEXT LUẬN GIẢI AI:\n{compact(ai_context,50000)}\n\nQUAN HỆ TÍNH BẰNG PYTHON:\n{compact(calc,30000)}\n\nTÀI LIỆU:\n{compact(books,40000)}\n\nQUY TẮC BẮT BUỘC:\n- Cách Cục đã match là một phần bắt buộc của luận giải, phải nêu rõ Cách Cục nào được xét và dùng điều kiện/bằng chứng tương ứng.\n- Chỉ sử dụng Cách Cục có trong BẰNG CHỨNG CÁCH CỤC ĐÃ MATCH; không tự tạo Cách Cục mới.\n- Đối chiếu Cách Cục với sao đồng cung, Tam Hợp, Xung Chiếu, Nhị Hợp, Giáp Cung và Tuần/Triệt trước khi kết luận mức độ ảnh hưởng.\n- Phân biệt rõ dữ kiện của engine với phần diễn giải suy luận.\n- Không đọc ảnh/OCR, không tự an sao, không tự thêm hoặc sửa sao/Can-Chi.\n- Dùng đầy đủ chính tinh, phụ tinh, Tứ Hóa, Tràng Sinh, Tuần/Triệt, Đại vận, Tiểu vận và hạn nếu có.\n- Trạng thái M/V/Đ/B/H phải được giữ nguyên theo dữ liệu engine.\n- Nếu không có Cách Cục nào match, nói rõ là không có Cách Cục được xác định từ bộ điều kiện hiện tại.\n- Nếu thiếu dữ liệu thì nói rõ.'''
    cfg=types.GenerateContentConfig(system_instruction=system_prompt+"\nAI chỉ diễn giải dữ liệu từ engine Python local và tuyệt đối không thay đổi dữ liệu đầu vào. Cách Cục đã match là bằng chứng bắt buộc cần xét trong phần luận giải.",temperature=.2,max_output_tokens=30000)
    return get_client(API_KEY).models.generate_content(model="gemini-3.6-flash",contents=prompt,config=cfg).text
st.session_state.setdefault("chart_json",None);st.session_state.setdefault("chat_history",[])
st.title("☯️ Tử Vi Đẩu Số");st.markdown('<div class="compact-note">Engine Python local → lá số chuẩn hóa → Cách Cục + quan hệ cung → AI luận giải</div>',unsafe_allow_html=True)
with st.container(border=True):
    st.markdown("**① Thông tin sinh**")
    with st.form("lap_la_so_form"):
        c1,c2,c3,c4=st.columns([1.25,1.1,1.35,.8])
        with c1:
            lich=st.radio("Lịch",["Dương lịch","Âm lịch"],horizontal=True);ns=st.date_input("Ngày sinh",date(1996,1,1),min_value=date(1900,1,1),max_value=date(2100,12,31),format="DD/MM/YYYY")
        with c2:
            gt=st.radio("Giới tính",["Nam","Nữ"],horizontal=True);ten=st.text_input("Họ tên","")
        with c3:
            labels=["Tý (23:00–00:59)","Sửu (01:00–02:59)","Dần (03:00–04:59)","Mão (05:00–06:59)","Thìn (07:00–08:59)","Tỵ (09:00–10:59)","Ngọ (11:00–12:59)","Mùi (13:00–14:59)","Thân (15:00–16:59)","Dậu (17:00–18:59)","Tuất (19:00–20:59)","Hợi (21:00–22:59)"];gl=st.selectbox("Giờ sinh",labels,index=6)
        with c4:
            tz=st.number_input("Múi giờ",-12,14,7,1);lap=st.form_submit_button("🧭 LẬP LÁ SỐ",type="primary",use_container_width=True)
if lap:
    try:
        branch=gl.split(" ",1)[0];chart=lap_la_so(ns.day,ns.month,ns.year,branch,gt,ten,lich=="Dương lịch",int(tz))
        if len(chart.get("12_cung",{}))!=12:raise ValueError("Engine không tạo đủ 12 cung")
        chart=analyze_chart(chart)
        chart.setdefault("input",{})["gio_hien_thi"]=gl;chart["input"]["lich"]=lich;st.session_state.chart_json=normalize_engine_chart(chart);st.session_state.chat_history=[];st.success("Đã lập lá số và chuẩn bị Cách Cục/quan hệ cung cho AI.")
    except Exception as e:st.error(f"Không thể lập lá số: {type(e).__name__}: {e}")
if st.session_state.chart_json:
    chart=normalize_engine_chart(st.session_state.chart_json);st.session_state.chart_json=chart
    st.markdown("**② Lá số**")
    tabs=st.tabs(["Thiên bàn","12 cung","Hạn","Cách Cục","Dữ liệu AI"])
    with tabs[0]:
        with st.expander("Xem chi tiết thiên bàn",expanded=False):st.json(chart.get("thien_ban",{}))
    with tabs[1]:
        rows=[]
        def star_label(x):
            if not isinstance(x,dict):return ""
            ten_sao=x.get("ten","");dt=x.get("dac_tinh");return f"{ten_sao} [{dt}]" if dt else ten_sao
        def names(xs):return "; ".join(star_label(x) for x in xs if isinstance(x,dict) and x.get("ten")) or "—"
        for name,d in chart.get("12_cung",{}).items():
            if not isinstance(d,dict):continue
            flags=d.get("tuan_triet") or ", ".join(x for x,ok in [("Tuần",d.get("tuan")),("Triệt",d.get("triet"))] if ok) or "—";chinh_tinh=d.get("chinh_tinh",[]);phu_tinh=d.get("phu_tinh",[]);main_names={x.get("ten") for x in chinh_tinh if isinstance(x,dict)};seen=set();clean_phu=[]
            for x in phu_tinh:
                if not isinstance(x,dict) or not x.get("ten") or x.get("ten") in main_names:continue
                key=x.get("id") if x.get("id") is not None else x.get("ten")
                if key in seen:continue
                seen.add(key);clean_phu.append(x)
            rows.append({"Cung":name+(" · Thân cư" if d.get("than_cu") else ""),"Can-Chi":d.get("can_chi") or "—","Ngũ hành":d.get("ngu_hanh") or "—","Tràng sinh":d.get("vong_trang_sinh") or "—","Tuần/Triệt":flags,"Chính tinh":names(chinh_tinh),"Phụ tinh":names(clean_phu)})
        st.dataframe(rows,use_container_width=True,hide_index=True,height=470);st.markdown('<div class="compact-note">M = Miếu · V = Vượng · Đ = Đắc · B = Bình · H = Hãm</div>',unsafe_allow_html=True)
    with tabs[2]:
        with st.expander("Đại vận / Tiểu vận",expanded=False):st.json({n:{"dai_van":d.get("dai_van",{}),"tieu_van":d.get("tieu_van",{})} for n,d in chart.get("12_cung",{}).items()})
    with tabs[3]:
        st.markdown("### Cách Cục được áp dụng")
        cach=chart.get("cach_cuc_analysis",{})
        if not cach.get("matched"):
            st.info("Chưa có Cách Cục nào được engine xác định từ điều kiện hiện tại.")
        else:
            st.write(f"Đã match **{cach.get('matched_count',0)} Cách Cục**. Đây là bằng chứng bắt buộc khi AI luận giải.")
            for item in cach.get("matched",[]):
                with st.expander(f"{item.get('name','Cách Cục')} · {item.get('category','')}",expanded=False):
                    st.write(item.get("description", ""));
                    if item.get("reason"):st.caption(f"Lý do: {item['reason']}")
                    if item.get("conditions"):st.json(item["conditions"])
                    if item.get("binh_chu"):st.markdown(item["binh_chu"])
    with tabs[4]:
        with st.expander("JSON chuẩn gửi AI",expanded=False):st.json(chart.get("ai_context",normalize_engine_chart(chart,for_ai=True)))
    st.download_button("⬇️ Tải JSON",json.dumps(chart,ensure_ascii=False,indent=2),"la_so_tu_vi.json","application/json",use_container_width=True)
    st.markdown("**③ Chat AI**");st.markdown('<div class="compact-note">Lịch sử cuộn riêng; ô nhập luôn nằm dưới cùng của khung chat.</div>',unsafe_allow_html=True)
    with st.container(border=True):
        with st.container(height=400,border=False):
            if not st.session_state.chat_history:st.info("Nhập câu hỏi để bắt đầu luận giải.")
            else:
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):st.markdown(msg["content"])
        with st.form("tuvi_ai_chat_form",clear_on_submit=True):
            q1,q2=st.columns([7,1])
            with q1:q=st.text_input("Câu hỏi",placeholder="Ví dụ: Luận cung Mệnh và công danh…",label_visibility="collapsed",key="tuvi_ai_question")
            with q2:send=st.form_submit_button("Gửi",type="primary",use_container_width=True)
    if send and q.strip():
        q=q.strip();st.session_state.chat_history.append({"role":"user","content":q})
        try:
            with st.spinner("AI đang luận giải…"):ans=ask_ai(q,chart,calculate_chart(chart),date.today().year)
        except Exception as e:ans=f"Không thể gọi AI: {type(e).__name__}: {e}"
        st.session_state.chat_history.append({"role":"assistant","content":ans});st.rerun()
else:st.info("Nhập thông tin sinh và bấm LẬP LÁ SỐ để bắt đầu.")