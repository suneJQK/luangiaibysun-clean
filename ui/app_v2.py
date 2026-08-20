from __future__ import annotations

import streamlit as st

from tuvi_engine.engine.chart_builder import lap_la_so
from tuvi_engine.rules.analysis import analyze_chart

st.set_page_config(page_title="Lá Số Tử Vi V2", layout="wide")
st.title("Lá Số Tử Vi — V2")

with st.form("birth"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        ngay = st.number_input("Ngày", 1, 31, 1)
        nam = st.number_input("Năm", 1800, 2200, 2000)
    with col2:
        thang = st.number_input("Tháng", 1, 12, 1)
        gio_sinh = st.text_input("Giờ sinh", "Tý")
    with col3:
        gioi_tinh = st.selectbox("Giới tính", ["Nam", "Nữ"])
        duong_lich = st.checkbox("Dương lịch", True)
    with col4:
        time_zone = st.number_input("Timezone", -12.0, 14.0, 7.0)
        ten = st.text_input("Họ tên", "")
    submitted = st.form_submit_button("Lập lá số")

if submitted:
    try:
        chart = analyze_chart(lap_la_so(ngay, thang, nam, gio_sinh, gioi_tinh, ten, duong_lich, time_zone))
        st.success("Đã lập lá số")
        st.json(chart)
        if chart.get("cach_cuc"):
            st.subheader("Cách cục")
            for item in chart["cach_cuc"]:
                st.write(f"**{item.get('name')}** — {item.get('category')}")
    except (ValueError, TypeError) as exc:
        st.error(str(exc))
