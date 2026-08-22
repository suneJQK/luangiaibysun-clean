# TV AI V3 — dự án tách biệt

Đây là nhánh dự án V3, lấy Engine, dữ liệu và API của `luangiaibysun-clean` làm nền nhưng tách frontend khỏi UI legacy.

## Source of truth
- Engine: `tuvi_engine/` + `tuvi_lap_so_engine.py` + `tu_vi_calculator.py`
- Chuẩn hóa chart: `chart_sanitizer.py`
- Quan hệ cung: `tuvi_engine/rules/relationships.py`
- Cách Cục: `tuvi_engine/rules/` + `data/cach_cuc*.json`
- API: `api/index.py`
- AI providers: `ai_providers/`
- Google Sheets: `google_sheets_storage.py`
- Frontend V3: `v3/frontend/`

## Nguyên tắc
1. Một frontend duy nhất: `v3/frontend/`.
2. Không nhúng HTML/CSS/JS frontend vào backend.
3. Engine là nguồn dữ liệu authoritative; frontend chỉ hiển thị.
4. Cách Cục phải có Rule ID + Evidence.
5. Tam Hợp/Xung/Nhị Hợp/Giáp Cung lấy từ dữ liệu Địa Chi/cung số, không để AI tự suy luận.
6. Vận hạn 10 năm lấy dữ liệu từ Engine, không tính lại trong UI.
7. AI chỉ nhận context đã audit.

Nhánh này không sửa `main`.
