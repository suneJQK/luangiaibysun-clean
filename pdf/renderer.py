from __future__ import annotations

from io import BytesIO
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def render_chart_pdf(chart: dict[str, Any]) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 48
    pdf.setTitle("Lá Số Tử Vi V2")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, y, "Lá Số Tử Vi V2")
    y -= 28
    pdf.setFont("Helvetica", 10)
    meta = chart.get("meta", {})
    pdf.drawString(40, y, f"Schema: {meta.get('schema_version', '2.0')}  Engine: {meta.get('engine', 'luangiaibysun-v2')}")
    y -= 22
    tb = chart.get("thien_ban", {})
    for key in ("ten", "can_nam", "chi_nam", "menh", "ban_menh", "ten_cuc", "menh_chu", "than_chu"):
        if y < 60:
            pdf.showPage(); y = height - 48
        pdf.drawString(40, y, f"{key}: {tb.get(key, '')}")
        y -= 16
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
