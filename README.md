# TV AI V3 — dự án sạch và độc lập

Đây là nhánh V3 được tách từ nền Engine của dự án cũ nhưng chỉ có **một frontend canonical** ở root.

## Kiến trúc
- Frontend duy nhất: `index.html`, `style.css`, `app.js`, `van10.css`, `van10.js`.
- Backend duy nhất: `api/index.py`.
- Engine authoritative: `tuvi_engine/`, `tuvi_lap_so_engine.py`, `tu_vi_calculator.py`.
- Rule/Cách Cục/Evidence: `tuvi_engine/rules/` + `data/cach_cuc*.json`.
- AI: `ai_providers/`, `ai_modes/`, `system_prompts/`.
- Google Sheets: `google_sheets_storage.py`.

## Nguyên tắc
1. Không có `new-ui`, `frontend` hoặc UI thứ hai trong đường chạy.
2. Không có frontend injection mới trong backend; frontend tự quản lý giao diện.
3. Engine là nguồn dữ liệu authoritative.
4. Tam Hợp/Xung/Nhị Hợp/Giáp Cung lấy từ Rule Engine.
5. Vận hạn 10 năm lấy từ Engine.
6. Cách Cục chỉ hiển thị khi có Rule ID/Evidence.
7. AI chỉ nhận context đã audit.
